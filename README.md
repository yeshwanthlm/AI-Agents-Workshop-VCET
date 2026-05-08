# AWS AgentCore with Strands — Workshop

A hands-on workshop that takes you from a single-line "Hello World" agent all the way to a production-ready, memory-enabled, guardrail-protected AI agent deployed on Amazon Bedrock AgentCore.

## Follow me:
* YouTube: https://www.youtube.com/@TechWithYeshwanth/videos
* Follow my GitHub here: https://github.com/yeshwanthlm
* Follow my blogs here: https://dev.to/yeshwanthlm/
* Follow me on Instagram: https://www.instagram.com/techwithyeshwanth/
* Follow me on LinkedIn: https://www.linkedin.com/in/yeshwanth-l-m/
* Book 1:1 Meeting with me: https://topmate.io/techwithyeshwanth

---

## What you'll build

By the end of this workshop you'll have built **FoodieBuddy** — a food recommendation agent that:

- Answers food questions using live web search
- Remembers your dietary preferences and allergies across sessions using AWS AgentCore Memory
- Refuses off-topic requests using Amazon Bedrock Guardrails
- Is deployable as a REST endpoint on AWS Bedrock AgentCore Runtime

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.10+ | Check with `python --version` |
| AWS account | Free tier works for most of this workshop |
| Amazon Bedrock access | Enable Claude 3.5 Haiku in your region |
| AWS credentials configured | `aws configure` or IAM role |
| Kiro IDE (recommended) | Download at https://kiro.dev |

### Enable Bedrock Model Access

1. Open the [AWS Console → Amazon Bedrock](https://console.aws.amazon.com/bedrock)
2. Go to **Model access** in the left sidebar
3. Request access to **Claude 3.5 Haiku** (`anthropic.claude-3-5-haiku-20241022-v1:0`)
4. Approval is usually instant in `us-east-1`

### Why Kiro?

Kiro is an AI-powered IDE purpose-built for agent development. It gives you:
- Inline AI assistance as you write agent code
- Spec-driven development for complex features
- Hooks to automate workflows (e.g., run tests on file save)
- MCP server integrations out of the box

Download: **https://kiro.dev**

---

## Setup

```bash
# 1. Clone or download this workshop folder and open it in Kiro (or any IDE)

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure AWS credentials (if not already done)
aws configure
```

Verify everything works by running the first cell in `00_setup.ipynb`.

---

## Workshop Structure

Work through the notebooks in order. Each one introduces exactly one new concept and builds on the previous.

```
00_setup.ipynb          Prerequisites, installation, credential verification
01_hello_agent.ipynb    Your first Strands agent — one import, one call
02_tools.ipynb          Giving the agent real capabilities with @tool
03_system_prompt.ipynb  Shaping agent behavior with system prompts
04_hooks.ipynb          Reacting to lifecycle events (init, after invocation)
05_memory.ipynb         Persistent memory with AWS AgentCore
06_full_agent.ipynb     Full FoodieBuddy agent with guardrails
```

---

## Module Breakdown

### 00 — Setup
Environment setup, Kiro installation, AWS credential verification, and a quick sanity check that all packages are installed correctly.

### 01 — Hello Agent
The absolute minimum to run a Strands agent. You'll learn:
- How to import and instantiate `Agent`
- How to choose a Bedrock model
- How multi-turn conversation history works
- How to inspect `agent.messages`

```python
from strands import Agent
agent = Agent(model="us.anthropic.claude-3-5-haiku-20241022-v1:0")
agent("Hello!")
```

### 02 — Tools
Tools are what make agents *act* rather than just chat. You'll learn:
- How to decorate a Python function with `@tool`
- Why the docstring and type hints matter (they generate the JSON schema)
- How the model decides when to call a tool
- How to use multiple tools together
- How to use built-in tools from `strands-agents-tools`

```python
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city using the Open-Meteo API."""
    ...

agent = Agent(tools=[get_weather])
```

### 03 — System Prompts
The system prompt is the agent's instruction manual. You'll learn:
- How to give the agent a persona and constraints
- How to inject dynamic context (date, user info) using f-strings
- How to update `agent.system_prompt` at runtime
- How the `name` parameter helps with logging and multi-agent systems

### 04 — Hooks
Hooks let you run custom code at lifecycle events without touching the agent's core logic. You'll learn:
- The three main events: `AgentInitializedEvent`, `MessageAddedEvent`, `AfterInvocationEvent`
- How to implement `HookProvider` and `register_hooks`
- Patterns: logging, context injection, conversation saving
- How to compose multiple hooks

```python
class LoggingHook(HookProvider):
    def on_agent_initialized(self, event: AgentInitializedEvent):
        print(f"Agent '{event.agent.name}' started")

    def register_hooks(self, registry: HookRegistry):
        registry.add_callback(AgentInitializedEvent, self.on_agent_initialized)
```

### 05 — Memory
In-process state disappears when the process ends. AWS AgentCore Memory provides two tiers of persistence. You'll learn:
- How to create a `MemoryClient` and a named Memory resource
- **Short-term memory** — saving raw conversation events with `create_event`
- **Long-term memory** — querying extracted preferences with `retrieve_memories`
- How AgentCore automatically extracts structured facts from raw conversations in the background
- How to inject retrieved preferences into the system prompt at session start

```
Short-term:  create_event()       → raw conversation turns
Long-term:   retrieve_memories()  → extracted facts ("user is vegetarian")
```

> Note: Long-term memory extraction is asynchronous. Wait ~30 seconds after saving events before querying.

### 06 — Full Agent + Guardrails
Everything comes together. You'll learn:
- How to create a Bedrock Guardrail with topic blocking, content filters, and PII redaction
- How to test a guardrail directly with `apply_guardrail` before wiring it into an agent
- How to attach a guardrail to a Strands agent via `BedrockModel`
- How guardrails enforce policies at the API level, independent of your prompt

```python
from strands.models import BedrockModel

model = BedrockModel(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    guardrail_id=guardrail_id,
    guardrail_version=guardrail_version,
    guardrail_trace="enabled"
)
agent = Agent(model=model, ...)
```

---

## Deployment

`foodie_buddy_agent.py` is the production-ready version of the notebook — a single Python file deployable on AWS Bedrock AgentCore Runtime.

### Required environment variables

| Variable | Description | Example |
|---|---|---|
| `MEMORY_ID` | AgentCore memory ID from module 05 | `FoodAgentMemory-Dkm2Ve6eDw` |
| `GUARDRAIL_ID` | Bedrock guardrail ID from module 06 | `jagz3r63m2jx` |
| `GUARDRAIL_VERSION` | Guardrail version | `1` or `DRAFT` |
| `AWS_REGION` | AWS region | `us-east-1` (default) |

### Test locally

```bash
export MEMORY_ID="FoodAgentMemory-Dkm2Ve6eDw"
export GUARDRAIL_ID="your-guardrail-id"
export GUARDRAIL_VERSION="1"

python foodie_buddy_agent.py
```

### Deploy to AgentCore Runtime

```bash
bedrock-agentcore deploy foodie_buddy_agent.py
```

### Invoke after deployment

```bash
bedrock-agentcore invoke --payload '{
  "user_message": "What should I eat tonight?",
  "actor_id": "user-123",
  "session_id": "session-abc"
}'
```

### Request / Response format

**Input:**
```json
{
  "user_message": "I love spicy food. What do you recommend?",
  "actor_id": "user-123",
  "session_id": "session-abc"
}
```

**Output:**
```json
{
  "response": "Based on your love of spicy food...",
  "session_id": "session-abc",
  "stop_reason": "end_turn"
}
```

`actor_id` is used as the memory namespace key — use a consistent ID per user to enable cross-session memory. `session_id` is optional; one is auto-generated if not provided.

---

## Architecture

```
User request
    │
    ▼
BedrockAgentCoreApp (handler)
    │
    ├── create_food_agent(actor_id, session_id)
    │       │
    │       ├── FoodMemoryHookProvider
    │       │       ├── on_agent_initialized → retrieve_memories() → inject into system_prompt
    │       │       └── on_after_invocation  → create_event() → save to short-term memory
    │       │
    │       ├── BedrockModel (Claude 3.5 Haiku + Guardrail)
    │       │       └── Guardrail: topic block + content filter + PII redaction
    │       │
    │       └── search_food tool (DDGS web search)
    │
    ▼
AgentCore Memory (background)
    └── Extracts preferences from events → long-term memory
```

---

## Key Concepts Reference

| Concept | What it does | Where it's taught |
|---|---|---|
| `Agent` | Core primitive — manages the conversation loop | Module 01 |
| `@tool` | Exposes a Python function to the model | Module 02 |
| `system_prompt` | Defines agent persona and constraints | Module 03 |
| `HookProvider` | Runs code at lifecycle events | Module 04 |
| `MemoryClient` | Interface to AgentCore persistent memory | Module 05 |
| `create_event` | Saves a conversation turn (short-term memory) | Module 05 |
| `retrieve_memories` | Queries extracted preferences (long-term memory) | Module 05 |
| `BedrockModel` | Explicit model config including guardrails | Module 06 |
| `create_guardrail` | Defines safety policies | Module 06 |
| `BedrockAgentCoreApp` | Runtime wrapper for deployment | Deployment |

---

## Troubleshooting

**`AttributeError: module 'strands' has no attribute '__version__'`**
Use `importlib.metadata.version('strands-agents')` instead.

**`TypeError: Agent.__init__() got an unexpected keyword argument 'guardrail_config'`**
Guardrails go on `BedrockModel`, not `Agent`. See module 06.

**`ResourceNotFoundException: Memory not found: FoodAgentMemory-XXXXXXXXXX`**
You forgot to replace the placeholder `MEMORY_ID`. Copy the real ID from the output of module 05.

**Long-term memory returns no results**
AgentCore extracts preferences asynchronously. Wait 30–60 seconds after saving events, then query again.

**Guardrail not blocking expected topics**
Topic policies use semantic matching, not keywords. Make the `definition` more explicit and add more diverse `examples` that clearly represent the topic you want to block. See module 06 for guidance.

**`ConflictException` when creating a guardrail**
The guardrail already exists. The notebook handles this automatically and reuses the existing one. If you want to update it, call `bedrock.delete_guardrail(guardrailIdentifier=guardrail_id)` first.

---

## What's Next

- **Multi-agent systems** — have FoodieBuddy delegate to specialist agents (nutrition, recipes, restaurants)
- **Grounding checks** — use guardrail grounding to detect hallucinations in recipe suggestions
- **Provisioned throughput** — for production workloads with consistent latency requirements
- **Kiro hooks** — automate agent workflows directly in your IDE (e.g., run tests on every file save)
- **Streaming responses** — enable `streaming=True` on `BedrockModel` for real-time token output

---

## Resources

- [Strands Agents documentation](https://strandsagents.com)
- [AWS AgentCore documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html)
- [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
- [Open-Meteo API](https://open-meteo.com) — free weather API used in module 02
- [Kiro IDE](https://kiro.dev)

## Questions? 
```sh
Write to techwithyeshwanth@gmail.com
```
