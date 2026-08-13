# Career Compass — Streamlit MVP

Minimal application layer for the processed German labour-market dataset.

## Structure

```text
career_compass_mvp/
├── app.py
├── requirements.txt
└── data/
    └── german_labour_market.parquet
```

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app reads the processed parquet only. It does not run or import ETL code.
