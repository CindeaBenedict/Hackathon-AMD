# Hackathon-AMD

**ProbePilot** is an agentic electronics debugging copilot aimed at **AMD Developer Cloud (MI300X / ROCm)** for long-context RAG, tool-heavy reasoning, and optional vLLM serving.

## KiCad + standalone split

| Surface | What it is | Role |
|--------|------------|------|
| **KiCad plugin** | `kicad-plugin/probepilot_pcbnew.py` (pcbnew ActionPlugin) | Runs inside KiCad, exports the **active PCB** (refs, values, footprints, pad nets) to `POST /api/kicad/analyze` for **checks + agent reasoning** tied to what you actually laid out. |
| **Standalone app** | `frontend/` + `backend/` | Richer lab UI: streaming chat, voice, charts, tool timeline, instrument JSON, measurement feeds. |

Schematic-heavy flows can still use **SPICE / netlist export** (or `kicad-cli` on KiCad 8) into the standalone uploader until you add an eeschema plugin for your target KiCad major.

## Architecture

| Layer | Stack | Role |
|-------|--------|------|
| UI | Next.js 15, TypeScript, Tailwind, Framer Motion, Recharts | Circuit upload, chat, voice, charts, tool timeline, JSON viewer |
| API | FastAPI, Pydantic | `/api/chat`, `/api/kicad/analyze`, `/api/tools/validate`, `/api/rag/query`, `/ws/diagnostics` |
| Knowledge | `data/rag/*.md` (YAML frontmatter) | Metadata filters + lexical retrieval (swap for embeddings + Qdrant/Milvus on MI300X) |
| Bench / speed | C++ (`cpp/`) | SCPI, CSV parse, safety-critical paths; expose via pybind11 / gRPC / ZMQ / REST |
| GPU | ROCm, PyTorch, HF, Optimum-AMD, vLLM, QLoRA | See `docs/AMD_GPU.md` |

**Agent loop (target):** Observe ? Reason ? Retrieve ? Simulate ? Measure ? Diagnose ? Act. The Python agent implements a **demo LED / base-drive scenario** plus generic retrieve + SPICE-stub comparison.

**Safety:** Models never touch hardware directly. Commands go through **Pydantic parsing** and **`validate_tool_call`** before execution; risky paths require **human confirmation**.

## Docker (recommended for ìdonít break my machineî)

From the repo root (requires [Docker](https://docs.docker.com/get-docker/) + Compose v2):

```powershell
docker compose up --build
```

- API: `http://127.0.0.1:8000` (health: `/health`)
- Web: `http://127.0.0.1:3000`

Build images only: `docker compose build`. Run API alone: `docker compose up api`.

The KiCad plugin on your host should use `PROBEPILOT_API_URL=http://127.0.0.1:8000` when the API port is published as above.

## Quick start

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### KiCad plugin

See `kicad-plugin/README.md`. Set `PROBEPILOT_API_URL` if the API is not on `http://127.0.0.1:8000`.

### Frontend (standalone)

```powershell
cd frontend
npm install
$env:NEXT_PUBLIC_API_URL = "http://127.0.0.1:8000"
npm run dev
```

Open `http://localhost:3000`. Try: "The LED does not turn on." with demo measurements (low TP5).

### Git (if `git` is on your PATH)

```powershell
git init
git add .
git commit -m "Add ProbePilot scaffold"
git branch -M main
git remote add origin git@github.com:CindeaBenedict/Hackathon-AMD.git
git push -u origin main
```

## Fine-tuning data shape

See `data/finetune/sample.train.jsonl` ù train adapters on **diagnostic style and tool JSON**, not raw textbooks (facts stay in RAG).

## Lab Professor Mode

Custom teacher voice is **opt-in only** with explicit written consent (see footer in the web UI).
