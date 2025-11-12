# 🌞 Solar Challenge Week 0

---

## 🚀 Challenge Experience

This week involves exploring and analyzing solar farm data from Benin, Sierra Leone, and Togo as part of the 12-week training program selection for Data Engineering (DE), Financial Analytics (FA), and Machine Learning Engineering (MLE).

Completing the tasks provides valuable project experience to showcase in a professional profile.  
**Put your best effort into completing as many tasks as possible!**

---

## 🎯 Business Objective

As an Analytics Engineer at MoonLight Energy Solutions, the goal is to analyze environmental measurements and translate observations into a strategy report.

Analysis focuses on:
- Identifying key trends and insights
- Recommending high-potential regions for solar installation
- Aligning with the company's long-term sustainability goals

---

## 📊 Dataset Description

The data is extracted and aggregated from Solar Radiation Measurement Data.

**Columns include:**
- `Timestamp (yyyy-mm-dd hh:mm)`: Date and time of observation
- `GHI (W/m²)`: Global Horizontal Irradiance
- `DNI (W/m²)`: Direct Normal Irradiance
- `DHI (W/m²)`: Diffuse Horizontal Irradiance
- `ModA`, `ModB (W/m²)`: Module/sensor measurements
- `Tamb (°C)`: Ambient Temperature
- `RH (%)`: Relative Humidity
- `WS (m/s)`: Wind Speed
- `WSgust (m/s)`: Max Wind Gust Speed
- `WSstdev (m/s)`: Wind Speed Std Dev
- `WD (°N (to east))`: Wind Direction
- `WDstdev`: Wind Direction Std Dev
- `BP (hPa)`: Barometric Pressure
- `Cleaning (1 or 0)`: Cleaning event indicator
- `Precipitation (mm/min)`: Precipitation rate
- `TModA`, `TModB (°C)`: Module Temperatures
- `Comments`: Additional notes

---

## 📦 Dataset Access

The dataset for this challenge is available at the following link:  
[Request access to the data](https://drive.google.com/file/d/1exEwhddciCUZ-osTeElnc6gUlNj9m8yt/view?usp=sharing)

> **Note:** Access to the dataset may require permission. Please request access using the link above.

---

## 🗂️ Project Structure

```
├── .vscode/
│   └── settings.json
├── .github/
│   └── workflows/
│       └── unittests.yml
├── .gitignore
├── requirements.txt
├── README.md
├── app/
├── notebooks/
│   ├── __init__.py
│   └── README.md
├── tests/
│   ├── __init__.py
└── scripts/
    ├── __init__.py
    └── README.md
```

---

## ⚙️ Environment Setup & Reproduction

### 1️⃣ Create and Activate a Virtual Environment (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2️⃣ Install Development and Test Dependencies

```powershell
pip install -r requirements.txt
```

### 3️⃣ Run Unit Tests

```powershell
pytest
```

---

## 📝 Topics Covered

- **Python Programming:** Task-specific assignments
- **GitHub Commands:** Continuous committing & repo management
- **Data Understanding & Exploration:** EDA techniques
- **CI/CD:** Continuous integration & deployment
- **Streamlit:** Dashboard creation


---

## 📺 Streamlit Dashboard — Development & Usage

I built an interactive Streamlit dashboard at `app/main.py` that reproduces the
cross-country comparisons from the notebooks. Key features:

- Load default cleaned country CSVs from `data/` (Benin, Sierra Leone, Togo).
- Upload additional country CSVs via the sidebar.
- Choose which irradiance metric to analyze (GHI, DNI, DHI).
- Switch between Boxplot and Average Bar views.
- Filter to daylight-only rows (GHI > 0) for more representative comparisons.
- View per-country summary stats (mean/median/std) and simple statistical
    tests (one-way ANOVA and Kruskal–Wallis when SciPy is available).
- See a "Top months" table (average metric per month × country) and download it as CSV.

Files added/updated for the dashboard:

- `app/main.py` — Streamlit app entry point (interactive UI and visuals).
- `src/utils.py` — Helpers for merging, cleaning, summary stats and tests.
- `scripts/start_streamlit.ps1` — Updated to launch `app/main.py`.
- `scripts/generate_sample_data.py` — Generate demo irradiance CSVs (GHI/DNI/DHI).

How to run the dashboard (PowerShell)

1. Create and activate the virtual environment (if not already active):

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

2. Install dependencies (first time):

```powershell
pip install -r requirements.txt
```

3. Start the Streamlit app (two options):

- Using the provided script:

```powershell
.\scripts\start_streamlit.ps1
```

- Or directly:

```powershell
streamlit run app/main.py --server.port=8501
```

4. Open http://localhost:8501 in your browser (Streamlit will also print the URL).

Developer notes (design & process)

- I mirrored the analysis in `notebook/compare_countries.ipynb` and encapsulated
    data logic in `src/utils.py` so unit tests can exercise core functionality
    without running Streamlit.
- The app is intentionally thin and focuses on declarative widget wiring and
    using `src.utils` for computations, filtering and tests.
- Unit tests live under `tests/`. Run `pytest -q` to run the test suite.

If you'd like, I can now:

- Add more visualizations (monthly timeseries, seasonal decomposition).
- Implement pairwise post-hoc tests (Tukey HSD / Dunn) with corrected p-values.
- Add a CI workflow to run tests and optionally build a small demo site.

