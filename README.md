# Claude Code Replica

Streamlit Cloud application that provides a Claude Code style software engineering workspace powered by a dynamic hierarchical multi-agent runtime.

## Goals

- Reproduce the core capability domains of Claude Code
- Dynamic agent decomposition and parallel execution
- Context partitioning so prompts stay small
- User control over providers, models, credentials and permissions
- Runs on Streamlit Cloud constraints

## Stack

- Python 3.11+
- Streamlit
- Pydantic v2
- asyncio
- Provider adapters for Ollama, Groq, Gemini and OpenAI compatible endpoints

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Configuration

Provider credentials and tokens are entered in the Settings panel. Nothing is stored in source files.

## License

MIT
