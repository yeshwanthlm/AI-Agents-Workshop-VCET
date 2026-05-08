# Gemma 4 Strands Agent (Local via Ollama)

A Jupyter notebook that runs a conversational AI agent powered by **Gemma 4** locally using **Ollama** and the **Strands Agents** framework. No cloud API keys needed, everything runs on your machine.

---

## What's Inside

| File | Purpose |
|---|---|
| `agent.ipynb` | Main notebook with all agent blocks |
| `requirements.txt` | Python dependencies |

---

## Prerequisites

- Python 3.10+
- Ollama installed and running locally
- A pulled Gemma 4 model variant

---

## Step 1 — Install Ollama

Ollama lets you run large language models locally with minimal compute resources. It uses quantized GGUF model files so you can run Gemma even on a laptop without a GPU.

### Download & Install

1. Go to [https://ollama.com/download](https://ollama.com/download)
2. Select your OS and follow the instructions:
   - **macOS**: Unpack the zip and move the Ollama app to your `/Applications` folder
   - **Windows**: Run the `.exe` installer and follow the prompts
   - **Linux**: Run the bash script installer from the download page

3. Confirm the install worked:

```bash
ollama --version
```

You should see something like `ollama version is 0.x.xx`.

---

## Step 2 — Pull a Gemma 4 Model

Ollama doesn't bundle any models by default. Pull the one you want:

```bash
# Default Gemma 4 (recommended to start)
ollama pull gemma4

# Or pick a specific size variant:
ollama pull gemma4:e2b   # ~2B params — fastest, least memory
ollama pull gemma4:e4b   # ~4B params
ollama pull gemma4:26b   # ~26B params
ollama pull gemma4:31b   # ~31B params — most capable, needs more RAM
```

Confirm the model is available:

```bash
ollama list
```

---

## Step 3 — Set Up the Python Environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

`requirements.txt` includes:

```
strands-agents
strands-agents-tools
ollama
```

---

## Step 4 — Run the Notebook

Make sure Ollama is running in the background (it starts automatically after install on most systems). Then open the notebook:

```bash
jupyter notebook agent.ipynb
```

Run the cells in order.

---

## Notebook Walkthrough

### Block 1 — Install Dependencies
Installs all packages from `requirements.txt` directly inside the notebook.

### Block 2 — Import Libraries
```python
from strands import Agent
from strands.models.ollama import OllamaModel
```

### Block 3 — Initialize the Model
```python
model = OllamaModel(
    model_id="gemma4",          # swap to "gemma4:e2b" etc. if needed
    host="http://localhost:11434"
)
```
Connects to the Ollama local server running on port `11434`.

### Block 4 — Create the Agent
```python
agent = Agent(
    model=model,
    system_prompt="You are a helpful assistant powered by Gemma 4 running locally via Ollama."
)
```

### Block 5 — Single Query
```python
response = agent("What is the capital of India, and give me 3 fun facts about it.")
print(response)
```

### Block 6 — Multi-turn Conversation
Tests that the agent retains context across turns within the same session:
```python
agent("My name is Yeshwanth. Remember this.")
response = agent("What is my name?")  # should recall "Yeshwanth"
```

### Block 7 — Agent with Tools (Calculator)
```python
from strands_tools import calculator

agent_with_tools = Agent(
    model=model,
    system_prompt="You are a helpful assistant. Use tools when needed.",
    tools=[calculator]
)

response = agent_with_tools("What is 1234 * 5678?")
```
Demonstrates tool use — the agent calls the `calculator` tool instead of guessing the answer.

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'ollama'`**
Run `pip install ollama` inside your venv, or reinstall from `requirements.txt`.

**`Connection refused` on `localhost:11434`**
Ollama isn't running. Start it with:
```bash
ollama serve
```

**Model not found error**
Make sure you've pulled the model first: `ollama pull gemma4`

---

## References

- [Strands Agents Docs](https://strandsagents.com)
- [Run Gemma with Ollama — Google AI](https://ai.google.dev/gemma/docs/integrations/ollama)
- [Ollama](https://ollama.com)
