import streamlit as st
import pandas as pd
import plotly.express as px
from data_acquisition import WorldBankDataset

st.set_page_config(page_title="Climate Change Data Visualizer", page_icon="🌍", layout="wide")
st.title("🌍 Climate Change Data Visualizer")
st.markdown("Compare climate and environmental indicators across multiple countries interactively.")

# Sidebar Config and Data Selection
st.sidebar.header("Select Data Options")

countries = {
    "World": "WLD","Kenya": "KEN","Uganda": "UGA","Tanzania": "TZA","United States": "USA",
    "South Africa": "ZAF","India": "IND","China": "CHN","Brazil": "BRA","Germany": "DEU",
    "France": "FRA","United Kingdom": "GBR","Canada": "CAN","Australia": "AUS","Japan": "JPN",
    "Mexico": "MEX","Russia": "RUS","Nigeria": "NGA","Egypt": "EGY","Argentina": "ARG"
}

country_names = st.sidebar.multiselect("Select Countries (one or more)", sorted(list(countries.keys())), default=["World", "Kenya"])
if not country_names:
    st.warning("Please select at least one country.")
    st.stop()

indicators = {
    "CO₂ emissions (metric tons per capita)": "EN.ATM.CO2E.PC",
    "CO₂ emissions (kt)": "EN.ATM.CO2E.KT",
    "Forest area (% of land area)": "AG.LND.FRST.ZS",
    "PM2.5 air pollution (µg/m³)": "EN.ATM.PM25.MC.M3",
    "Total greenhouse gas emissions (kt CO₂e)": "EN.ATM.GHGT.KT.CE",
    "Renewable energy consumption (% of total)": "EG.FEC.RNEW.ZS",
    "Access to electricity (% of population)": "EG.ELC.ACCS.ZS",
    "Population, total": "SP.POP.TOTL",
    "Agricultural land (% of land area)": "AG.LND.AGRI.ZS",
    "Urban population (% of total)": "SP.URB.TOTL.IN.ZS"
}

indicator_name = st.sidebar.selectbox("Select Indicator", sorted(list(indicators.keys())))
indicator_code = indicators[indicator_name]

# Caching World Bank API Calls to improve performance
@st.cache_data(show_spinner=True)
def fetch_country_data(country_code, indicator_code):
    dataset = WorldBankDataset(country=country_code, indicator=indicator_code)
    return dataset.load_data()

# Loading data for all countries 
all_data = []
for name in country_names:
    code = countries[name]
    df_country = fetch_country_data(code, indicator_code)
    if df_country.empty or 'value' not in df_country.columns:
        st.warning(f"No data for {name} and {indicator_name}. Skipping.")
        continue
    if 'date' not in df_country.columns and 'year' in df_country.columns:
        df_country = df_country.rename(columns={'year': 'date'})
    df_country['date'] = pd.to_numeric(df_country['date'], errors='coerce')
    df_country = df_country.dropna(subset=['date', 'value'])
    df_country['country'] = name
    all_data.append(df_country)

if not all_data:
    st.error("No data available for selected countries/indicator.")
    st.stop()

df_all = pd.concat(all_data).sort_values('date')

# Date Range Selector
min_year, max_year = int(df_all['date'].min()), int(df_all['date'].max())
start_year, end_year = st.sidebar.slider("Select Date Range", min_year, max_year, (min_year, max_year))
df_filtered = df_all[(df_all['date'] >= start_year) & (df_all['date'] <= end_year)]

# Plot
st.subheader(f"{indicator_name} Comparison")
fig = px.line(
    df_filtered,
    x='date',
    y='value',
    color='country',
    markers=True,
    title=f"{indicator_name} Comparison",
    labels={'date': 'Year', 'value': indicator_name, 'country': 'Country'},
    template='plotly_white'
)
st.plotly_chart(fig, use_container_width=True)

# Summary Stats
st.subheader("📊 Summary Statistics by Country")
st.dataframe(df_filtered.groupby('country')['value'].describe())

# Raw Data Viewer
with st.expander("Show Raw Data"):
    st.dataframe(df_filtered)

st.success("✅ Data loaded and visualized successfully!")