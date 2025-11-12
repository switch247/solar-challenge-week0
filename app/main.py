"""Streamlit dashboard focused on cross-country irradiance comparisons.

Default behavior: when the data/ CSVs for Benin, Sierra Leone and Togo exist
in the repository, load them automatically and show boxplots, summary
tables and simple statistical tests per irradiance metric (GHI, DNI, DHI).
Users can also upload CSVs to override.
"""

from typing import List
import pandas as pd

try:
	import streamlit as st
except Exception:
	st = None  # allow imports in test env

from utils import (
	REQUIRED_IRRADIANCE,
	DataValidator,
	DataMerger,
	DataCleaner,
	SummaryService,
	StatTests,
	Visualizer,
)
from utils import generate_sample_df




def load_df_from_path(path: str) -> pd.DataFrame:
	return pd.read_csv(path)


def run_app():
	if st is None:
		raise RuntimeError("Streamlit not available")

	st.set_page_config(layout="wide")
	st.title("🌍 Cross-Country Irradiance Comparator")
	st.write("Compare GHI, DNI and DHI distributions and statistics across Benin, Sierra Leone, and Togo.")

	# Data sources: allow the user to manage a list of countries and upload CSVs
	st.sidebar.header("Data Sources")

	# persistent list of countries (names)
	if "countries" not in st.session_state:
		st.session_state["countries"] = []
	if "generated_frames" not in st.session_state:
		st.session_state["generated_frames"] = {}

	new_country = st.sidebar.text_input("Add country name", key="new_country_name")
	if st.sidebar.button("Add country") and new_country:
		if new_country not in st.session_state["countries"]:
			st.session_state["countries"].append(new_country)

	st.sidebar.markdown("**Current countries**")
	# show each country with controls to clear its data or remove the country
	for c in list(st.session_state["countries"]):
		cols = st.sidebar.columns([3, 1, 1])
		cols[0].write(f"- {c}")
		# clear loaded/generated data for this country (keep the country in the list)
		if cols[1].button("Clear data", key=f"clear_{c}"):
			st.session_state.get("generated_frames", {}).pop(c, None)
			st.session_state.pop(f"uploader_{c}", None)
			st.sidebar.success(f"Cleared data for {c}")
		# remove the country from the list entirely
		if cols[2].button("Remove", key=f"remove_{c}"):
			st.session_state.get("generated_frames", {}).pop(c, None)
			st.session_state.pop(f"uploader_{c}", None)
			try:
				st.session_state["countries"].remove(c)
			except ValueError:
				pass
			st.sidebar.success(f"Removed {c}")

	# File uploaders for each country in the list
	uploaded = {}
	for country in st.session_state["countries"]:
		uploaded[country] = st.sidebar.file_uploader(f"Upload {country} CSV", type="csv", key=f"uploader_{country}")

	# Quick random generation controls (no default files will be used)
	st.sidebar.header("Quick generate")
	num_random = st.sidebar.slider("Random countries to generate", 1, 6, 3)
	gen_days = st.sidebar.slider("Days of data", 1, 180, 30)
	gen_seed = st.sidebar.number_input("Generator seed", min_value=0, max_value=999999, value=42, step=1)
	if st.sidebar.button("Generate random countries"):
		# create simple unique country names and generate in-memory frames
		generated = {}
		for i in range(num_random):
			name = f"Country_{len(st.session_state['countries']) + i + 1}"
			# ensure uniqueness in the session countries list
			if name not in st.session_state["countries"]:
				st.session_state["countries"].append(name)
			df = generate_sample_df(name, n_days=gen_days, freq="H", seed=int(gen_seed + i))
			generated[name] = df
		# store generated frames in session state
		st.session_state["generated_frames"].update(generated)

	# Clear all generated/uploaded data for all countries
	if st.sidebar.button("Clear all data"):
		st.session_state["generated_frames"] = {}
		# clear any uploader entries from session state
		for c in st.session_state.get("countries", []):
			st.session_state.pop(f"uploader_{c}", None)
		st.sidebar.success("Cleared generated and uploaded data for all countries")

	# Load either uploaded files or generated frames
	frames = []
	countries: List[str] = []
	for country in st.session_state["countries"]:
		try:
			uploader = uploaded.get(country)
			if uploader is not None:
				df = pd.read_csv(uploader)
			else:
				# try generated frames only; do NOT load any repository default files
				df = st.session_state["generated_frames"].get(country)
				if df is None:
					st.sidebar.warning(f"No data for {country}; upload a CSV or generate data for it.")
					continue
			ok, missing = DataValidator.validate_columns(df, REQUIRED_IRRADIANCE)
			if not ok:
				st.sidebar.error(f"{country}: missing columns {missing}")
				continue
			frames.append(df)
			countries.append(country)
		except Exception as e:
			st.sidebar.error(f"Error loading {country}: {e}")

	if not frames:
		st.info("Upload at least one country's CSV or use 'Generate random countries' to begin. (No repository defaults are used.)")
		return

	combined = DataMerger.combine(frames, countries, timestamp_col="Timestamp")

	# Options
	st.sidebar.header("Analysis Options")
	daylight_only = st.sidebar.checkbox("Filter daylight only (GHI>0)", value=True)
	metrics = st.sidebar.multiselect("Metrics to analyze", REQUIRED_IRRADIANCE, default=REQUIRED_IRRADIANCE)

	if daylight_only:
		combined = DataCleaner.daylight_only(combined, ghi_col="GHI")

	st.header("Per-Metric Visuals & Stats")
	for metric in metrics:
		st.subheader(metric)
		cols = st.columns([2, 1])
		# tabs showing all plot types so users can inspect multiple views at once
		tabs = cols[0].tabs(["Box", "Violin", "Histogram", "Bar (mean)", "Timeseries"])
		for tab_name, tab in zip(["Box", "Violin", "Histogram", "Bar (mean)", "Timeseries"], tabs):
			with tab:
				try:
					if tab_name == "Box":
						fig = Visualizer.box_by_country(combined, metric)
					elif tab_name == "Violin":
						fig = Visualizer.violin_by_country(combined, metric)
					elif tab_name == "Histogram":
						fig = Visualizer.histogram_by_country(combined, metric)
					elif tab_name == "Bar (mean)":
						fig = Visualizer.mean_bar_by_country(combined, metric)
					elif tab_name == "Timeseries":
						fig = Visualizer.timeseries_by_country(combined, metric, ts_col="Timestamp")
					else:
						fig = Visualizer.box_by_country(combined, metric)
					st.plotly_chart(fig, use_container_width=True)
				except Exception as e:
					st.error(f"{tab_name} plot failed: {e}")
					if "plotly" in str(e).lower():
						st.info("Plotly not available. Install with 'pip install plotly' to see interactive charts.")
					st.write(SummaryService.by_country(combined, [metric]))

		with cols[1]:
			st.markdown("**Summary statistics**")
			st.dataframe(SummaryService.by_country(combined, [metric]))
			st.markdown("**Statistical tests (ANOVA / Kruskal-Wallis)**")
			res = StatTests.run(combined, metric)
			st.json(res)

	with st.expander("Show combined (sample) data"):
		st.dataframe(combined.head(200))


if __name__ == "__main__":
	if st is None:
		print("Streamlit not installed; run with 'streamlit run src/main.py'")
	else:
		run_app()

