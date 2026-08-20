# ♻️ MaterialLoop Local

Construction Material Reuse Matcher — a local-first Streamlit decision-support dashboard for matching reusable demolition/deconstruction materials with construction demand.

## Features
- 0–100 explainable reuse-screening score
- Material, grade, quantity and timing compatibility
- Quality, condition and reusability analytics
- Transport-distance and logistics-fit signals
- Storage and buyer readiness
- Processing and contamination-risk signals
- Indicative carbon-saving analytics
- Candidate match queue with CSV export
- Interactive Plotly dashboards
- Local CSV validation
- No external APIs
- Synthetic demonstration dataset

## Run
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```
Open http://localhost:8501

## Responsible use
This is planning decision support, not certification of structural suitability, regulatory compliance, contamination status, ownership, legal transferability, or actual lifecycle carbon savings. Final decisions require qualified professionals.
