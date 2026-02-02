## Diagnosis Copilot

Lightweight Streamlit-based prototype that uses CrewAI agents and LLM backends to analyze CSV datasets, generate Python code for user queries, validate the code against the dataset schema, and return runnable outputs (text, saved DataFrame CSV, or saved image).

This repository wires together:
- `app.py` — Streamlit frontend and orchestration (file upload, metadata extraction, chat UI, code execution and output rendering).
- `agents.py` — Agent factory and LLM configurations (creates schema, code-generation, evaluation and finalization agents). Also includes `StreamToExpander` helper used to stream and prettify agent logs for the UI.
- `tasks.py` — Task definitions used by the Crew orchestration (schema analysis, code generation, code evaluation, final packaging).
- `crew.py` — High-level crew composition: instantiates agents and tasks, creates a Crew and kicks off the process.
- sample CSVs: `heart.csv` — example datasets used during development.

Goal
------
Help a data practitioner or clinician quickly ask questions against CSV datasets (for example: compute statistics, create a plot) by having LLM agents produce, verify and finalize Python code that runs locally against the uploaded CSV.

Quick contract
--------------
- Input: a CSV file uploaded through the Streamlit UI and a user query entered in the chat input.
- Output: one of: textual result printed to the UI, `output.csv` (DataFrame saved by generated code and rendered), or `output.png` (plot saved by generated code and displayed).
- Error modes: exceptions while executing generated code are caught and surfaced to the UI. If code execution fails, user is asked to retry.

Requirements and dependencies
---------------------------
Install dependencies in a Python 3.10+ environment. The repository includes `requirements.txt` with the needed packages. Key packages:
- streamlit
- crewai
- groq (used for hosted LLM in examples)
- streamlit-chat
- pandas, scikit-learn, pillow, pyyaml, transformers

Install (recommended in a venv):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Environment variables
---------------------
This project uses a GROQ API key in `.env` (example key placeholder in `.env`).

- Required: `GROQ_API_KEY` — your Groq API key if you plan to use the remote Groq models configured in `agents.py`.


Running the app (development)
-----------------------------
1. Activate your virtual environment.
2. Ensure your `.env` file contains valid keys (or comment out the Groq-backed LLMs if you don't have a key).
3. Run Streamlit:

```bash
streamlit run app.py
```

Open the URL shown by Streamlit (usually http://localhost:8501) and upload a CSV (for example `heart.csv` ).

How it works (high level)
-------------------------
1. You upload a CSV. `app.py` saves it locally and calls `generate_metadata()` to infer column names, dtypes and sample records.
2. The UI sends your natural-language query to the Crew (`crew.DiagnosisCrew`), which builds a crew of agents created in `agents.DiagnosisCopilotAgents` and tasks from `tasks.DiagnosisCopilotTasks`.
3. Agents perform: schema analysis -> code generation -> code evaluation -> finalization into an interpreter-ready function.
4. `app.py` extracts Python code returned by the assistant (a fenced ```python block), runs it locally via `exec()` and captures the output. If the generated code saves `output.png` or `output.csv`, the UI shows those artifacts.

Development notes and safety
----------------------------
- The app executes arbitrary Python code returned by LLM agents via `exec()` — this is powerful but dangerous. Only run this locally and with trusted models / inputs. Do not deploy this mechanism to shared or untrusted servers.
- If you don't have valid LLM credentials, you can replace or stub the LLMs in `agents.py` with local or simple deterministic mocks for development/testing.
- The project currently expects CSVs small enough to load into memory with pandas.


Troubleshooting
---------------
- Missing package errors: re-run `pip install -r requirements.txt` inside the virtualenv.
- Groq model errors or auth failures: verify `GROQ_API_KEY` in `.env` and that you can reach the Groq endpoint. Alternatively, comment out Groq LLM lines in `agents.py` and configure a local LLM backend.
- If the UI shows "Error!!.. Retry Once Again" on code execution, check the assistant's produced code in the UI (the app prints the assistant code block). You can copy it, review, and run it locally to debug.
