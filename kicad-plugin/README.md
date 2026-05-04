# ProbePilot KiCad integration

ProbePilot is split into two cooperating surfaces:

1. **KiCad plugin (this folder)** — runs *inside* KiCad, reads the **active PCB**, and POSTs a structured snapshot to your ProbePilot API for **static checks + agent reasoning** grounded in what you actually laid out (refs, values, footprints, pad nets).
2. **Standalone app** (`frontend/` + `backend/`) — richer lab UI: streaming chat, voice, measurement charts, tool timeline, instrument JSON, and long-running RAG sessions.

Schematic-only workflows today:

- Export **SPICE netlist** or use **`kicad-cli`** (KiCad 8+) to emit a netlist, then drop it into the standalone uploader / future schematic parser, **or**
- Extend this repo with an **eeschema** ActionPlugin once you standardize on a KiCad major version (the schematic Python API moves more quickly than `pcbnew`).

## Install (pcbnew)

1. Start the API from the repo root:

   ```powershell
   cd backend
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. Copy `probepilot_pcbnew.py` into KiCad’s **scripting plugins** directory, for example:

   - **Windows (KiCad 8):** `%USERPROFILE%\Documents\KiCad\8.0\scripting\plugins\`
   - **Linux:** `~/.local/share/kicad/8.0/scripting/plugins/`

3. Restart KiCad, open **pcbnew**, then **Tools → External Plugins → ProbePilot** (toolbar button may also appear depending on theme).

4. Optional: point to a remote API:

   ```text
   PROBEPILOT_API_URL=https://your-bench-host:8000
   ```

   Set a user or system environment variable before launching KiCad.

## API contract

`POST {PROBEPILOT_API_URL}/api/kicad/analyze`

Body matches `KiCadAnalyzeRequest` in `backend/app/schemas/kicad_payload.py`. Response includes:

- `checks` — deterministic issues (duplicate refs, empty values, heuristic power/ground hints, …)
- `stats` — counts
- `agent` — same shape as `/api/chat` (`reply`, `rag_hits`, `tool_timeline`, …)

The standalone UI can poll or deep-link into a session using the returned `agent.session_id` in a future iteration.
