"""
FoodieBuddy — Deployable AgentCore Runtime Script
==================================================
Deploy with:
    bedrock-agentcore deploy foodie_buddy_agent.py

Environment variables (set in AgentCore runtime config or .env):
    AWS_REGION          - AWS region (default: us-east-1)
    MEMORY_ID           - AgentCore memory ID from 05_memory.ipynb
    GUARDRAIL_ID        - Bedrock guardrail ID
    GUARDRAIL_VERSION   - Bedrock guardrail version
"""

import os
import logging
from datetime import datetime

from strands import Agent, tool
from strands.models import BedrockModel
from strands.hooks import (
    AgentInitializedEvent,
    AfterInvocationEvent,
    HookProvider,
    HookRegistry,
)
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from ddgs import DDGS
from ddgs.exceptions import RatelimitException

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("foodie-buddy")

# ---------------------------------------------------------------------------
# Configuration — all values come from environment variables
# ---------------------------------------------------------------------------
REGION           = "us-east-1"
MEMORY_ID        = "FoodAgentMemory-*********"         # required
GUARDRAIL_ID      = "********"       # required
GUARDRAIL_VERSION = "1"  # required

# ---------------------------------------------------------------------------
# Shared clients (created once at startup)
# ---------------------------------------------------------------------------
memory_client = MemoryClient(region_name=REGION)

# ---------------------------------------------------------------------------
# Memory hook
# ---------------------------------------------------------------------------
class FoodMemoryHookProvider(HookProvider):
    """Loads preferences on agent init; saves conversation turns after each invocation."""

    def __init__(self, memory_client: MemoryClient, memory_id: str):
        self.memory_client = memory_client
        self.memory_id = memory_id

    def on_agent_initialized(self, event: AgentInitializedEvent):
        try:
            actor_id = event.agent.state.get("actor_id")
            if not actor_id:
                return
            preferences = self.memory_client.retrieve_memories(
                memory_id=self.memory_id,
                namespace=f"user/{actor_id}/food_preferences",
                query="food preferences cuisines dietary restrictions favorites allergies",
                top_k=5,
            )
            if preferences:
                lines = []
                for pref in preferences:
                    text = pref.get("content", {}).get("text", "").strip()
                    if text:
                        lines.append(f"- {text}")
                if lines:
                    event.agent.system_prompt += (
                        "\n\n## User's Food Preferences:\n" + "\n".join(lines)
                    )
                    logger.info(f"Loaded {len(lines)} preferences from memory")
            else:
                logger.info("No previous preferences found")
        except Exception as e:
            logger.error(f"Error loading preferences: {e}")

    def on_after_invocation(self, event: AfterInvocationEvent):
        try:
            messages = event.agent.messages
            if len(messages) < 2:
                return
            actor_id = event.agent.state.get("actor_id")
            session_id = event.agent.state.get("session_id")
            if not actor_id or not session_id:
                return
            user_msg = assistant_msg = None
            for msg in reversed(messages):
                if msg["role"] == "assistant" and not assistant_msg:
                    c = msg.get("content", [])
                    if c and "text" in c[0]:
                        assistant_msg = c[0]["text"]
                elif msg["role"] == "user" and not user_msg:
                    c = msg.get("content", [])
                    if c and "text" in c[0] and "toolResult" not in c[0]:
                        user_msg = c[0]["text"]
                        break
            if user_msg and assistant_msg:
                self.memory_client.create_event(
                    memory_id=self.memory_id,
                    actor_id=actor_id,
                    session_id=session_id,
                    messages=[(user_msg, "USER"), (assistant_msg, "ASSISTANT")],
                )
                logger.info("Saved conversation turn to memory")
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")

    def register_hooks(self, registry: HookRegistry):
        registry.add_callback(AgentInitializedEvent, self.on_agent_initialized)
        registry.add_callback(AfterInvocationEvent, self.on_after_invocation)


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------
@tool
def search_food(query: str, max_results: int = 5) -> str:
    """Search for food information, recipes, cuisines, or restaurant recommendations.

    Args:
        query: Search query about food
        max_results: Maximum number of results to return

    Returns:
        Search results with food information
    """
    try:
        results = DDGS().text(
            f"{query} food recipe restaurant", region="us-en", max_results=max_results
        )
        if not results:
            return "No results found."
        return "\n\n".join(
            f"{i}. {r.get('title', '')}\n   {r.get('body', '')}"
            for i, r in enumerate(results, 1)
        )
    except RatelimitException:
        return "Rate limit reached. Please try again in a moment."
    except Exception as e:
        return f"Search error: {e}"


# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------
def create_food_agent(actor_id: str, session_id: str) -> Agent:
    system_prompt = (
        f"You are FoodieBuddy, a friendly food assistant.\n"
        f"Help users discover new foods and remember their preferences.\n"
        f"Today's date: {datetime.today().strftime('%Y-%m-%d')}\n"
        f"Always respect dietary restrictions and allergies.\n"
        f"Keep responses concise and practical."
    )
    model = BedrockModel(
        model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
        guardrail_id=GUARDRAIL_ID,
        guardrail_version=GUARDRAIL_VERSION,
        guardrail_trace="enabled",
    )
    return Agent(
        name="FoodieBuddy",
        model=model,
        system_prompt=system_prompt,
        hooks=[FoodMemoryHookProvider(memory_client, MEMORY_ID)],
        tools=[search_food],
        state={"actor_id": actor_id, "session_id": session_id},
    )


# ---------------------------------------------------------------------------
# AgentCore runtime app
# ---------------------------------------------------------------------------
app = BedrockAgentCoreApp()

@app.entrypoint
def handler(input: dict, context: dict) -> dict:
    """
    AgentCore runtime entrypoint.

    Expected input payload:
        {
            "prompt": "What should I eat tonight?",   # or "user_message"
            "actor_id": "user-123",                   # optional, defaults to 'default-user'
            "session_id": "session-abc"               # optional, auto-generated if missing
        }
    """
    # Accept either "prompt" or "user_message" as the message key
    user_message = input.get("prompt") or input.get("user_message", "")
    actor_id     = input.get("actor_id", "default-user")
    session_id   = input.get("session_id") or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    if not user_message:
        return {"error": "prompt (or user_message) is required"}

    logger.info(f"Request — actor={actor_id} session={session_id} msg={user_message[:60]}")

    agent = create_food_agent(actor_id, session_id)
    result = agent(user_message)

    return {
        "response": result.message["content"][0]["text"],
        "session_id": session_id,
        "stop_reason": result.stop_reason,
    }


# ---------------------------------------------------------------------------
# Entrypoint — starts the HTTP server (used by container and `python -m`)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run()
