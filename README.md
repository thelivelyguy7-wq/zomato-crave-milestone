# AI-Powered Restaurant Recommendation System

Zomato-inspired restaurant recommendations combining structured Hugging Face data with **Llama 3 70B** (Groq) for personalized ranking and explanations.

## Documentation

- [context.md](./context.md) — product requirements
- [architecture.md](./architecture.md) — system design
- [implementation-plan.md](./implementation-plan.md) — phased build plan
- [edge-case.md](./edge-case.md) — corner scenarios

## Prerequisites

- Python 3.10+
- Internet access (for Hugging Face dataset, from Phase 1)
- [Groq API key](https://console.groq.com/keys) for Llama 3 70B (required from Phase 2)

## Setup

```bash
# Clone or open the project, then create a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (copy and edit)
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
```

Edit `.env` and set `GROQ_API_KEY` when you reach Phase 2 (Groq integration).

## Verify installation (Phase 0)

```bash
python -c "import src; from src.config import get_settings; print(get_settings().llm_model)"
```

Expected output: `llama3-70b-8192`

## Project structure

```
zomato-milestone/
├── src/
│   ├── config.py          # Environment settings
│   ├── models/            # Data models (Phase 1)
│   ├── data/              # Dataset loader & repository (Phase 1)
│   ├── services/          # Filter, prompts, recommendations (Phase 1–2)
│   │   └── llm/           # Groq client (Phase 2)
│   └── ui/                # Streamlit app (Phase 3)
├── tests/
├── data/                  # Cached dataset (gitignored)
├── requirements.txt
└── .env.example
```

## Run application

| Phase | Command |
|-------|---------|
| Phase 3+ | `streamlit run src/ui/streamlit_app.py` |

*The Streamlit UI is added in Phase 3.*

## Run tests

```bash
pytest tests/ -v
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | Groq API key for Llama 3 70B |
| `LLM_MODEL` | `llama3-70b-8192` | Model identifier |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | Groq API base URL |
| `LLM_TEMPERATURE` | `0.3` | Sampling temperature |
| `MAX_CANDIDATES` | `20` | Max restaurants sent to LLM after filtering |

## Development status

- [x] **Phase 0** — Project setup and configuration
- [x] **Phase 1** — Data ingestion, models, filtering
- [x] **Phase 2** — Groq integration (Llama 3 70B)
- [x] **Phase 3** — Streamlit UI
- [ ] Phase 4 — Hardening and tests

## License

Educational / milestone project.
