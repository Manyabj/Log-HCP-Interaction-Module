# Log HCP Interaction Module

An AI-first "Log HCP Interaction" screen (Veeva-CRM style) where the **only**
way to populate the structured interaction form is by chatting with an AI
assistant. The assistant (LangGraph + Groq) extracts entities, edits fields,
clears fields, summarizes, and validates — then the React/Redux form updates
automatically. Nothing on the form is manually editable.

```
React → Redux → FastAPI → LangGraph → Groq LLM → Tool Execution →
Structured JSON → Redux Update → Form Auto-Updates → Save → PostgreSQL
```

## Folder Structure

```
hcp-crm/
├── backend/
│   ├── app/
│   │   ├── main.py                 FastAPI app entrypoint
│   │   ├── config.py               Settings (env vars)
│   │   ├── database.py             SQLAlchemy engine/session
│   │   ├── seed.py                 Optional sample data loader
│   │   ├── models/                 SQLAlchemy models (hcp, interaction, chat_messages, products, materials)
│   │   ├── schemas/                Pydantic schemas
│   │   ├── routes/                 FastAPI routers (chat, interaction, hcp, product)
│   │   └── langgraph_agent/
│   │       ├── llm.py              Groq client wrapper
│   │       ├── state.py            Shared LangGraph state
│   │       ├── graph.py            StateGraph wiring router + 5 tools
│   │       ├── agents/             Intent-classification (router) agent
│   │       └── tools/              5 tools: Log, Edit, ClearField, Summarize, Validate
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── redux/                  Redux Toolkit store + slices
    │   ├── services/               Axios API client
    │   ├── components/             InteractionForm, ChatWindow, Message
    │   └── pages/LogInteraction/   Split-screen page
    ├── package.json
    └── vite.config.js
```

## 1. Database (PostgreSQL)

Create a database and set `DATABASE_URL` in `backend/.env` (copy from `.env.example`):

```bash
createdb hcp_crm
```

Tables (`hcp`, `interaction`, `chat_messages`, `products`, `materials`) are
auto-created on backend startup via `Base.metadata.create_all`. To load sample
products/materials:

```bash
cd backend
python -m app.seed
```

## 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then set GROQ_API_KEY and DATABASE_URL
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000` (docs at `/docs`).

Get a Groq API key at https://console.groq.com. Models used:
- `gemma2-9b-it` — conversational replies
- `llama-3.3-70b-versatile` — structured extraction / reasoning (JSON mode)

## 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` and proxies `/api/*` to the FastAPI
backend on port 8000 (see `vite.config.js`).

## 4. Using the app

1. Open `http://localhost:5173`.
2. Type a message in the right-hand AI Assistant panel, e.g.:
   > Today I met Dr. Smith and discussed Product X. The doctor showed positive sentiment and I shared brochures.
3. Watch the left-hand form populate automatically.
4. Send corrections ("Actually the doctor was Dr. John and the sentiment was negative"),
   removals ("Remove the brochures"), or ask for a summary ("Summarize this interaction").
5. Say "Save this interaction" (or click **Save Interaction**) — the agent validates
   mandatory fields (HCP name, date, product, sentiment) first and asks follow-up
   questions if anything is missing.

## API Endpoints

| Method | Path                 | Purpose                                   |
|--------|----------------------|--------------------------------------------|
| POST   | `/chat`              | Send a chat message, run the LangGraph agent |
| GET    | `/interaction`        | Fetch current draft/saved interaction for a session |
| POST   | `/interaction/update` | Direct structured patch (internal/API use) |
| POST   | `/interaction/save`   | Validate + persist interaction, upsert HCP |
| GET    | `/hcps`               | List HCP master data |
| GET    | `/products`           | List Product master data |

## Notes

- The LangGraph router classifies every message into one of: `log`, `edit`,
  `clear`, `summarize`, `save`, `chat` — purely via LLM reasoning, no keyword
  hardcoding.
- Each of the 5 required tools lives in its own file under
  `backend/app/langgraph_agent/tools/`.
- The interaction form component (`InteractionForm.jsx`) renders **read-only**
  fields sourced from `state.interaction.fields` in Redux — there is no input,
  textarea, or select element bound to user edits anywhere in that component.
