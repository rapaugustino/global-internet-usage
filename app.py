from tempfile import template

import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------------------------
# 1. PAGE CONFIG & GLOBAL SETTINGS
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Global Internet & Economic Dashboard",
    layout="wide"
)

# Custom CSS for layout & basic styling
CUSTOM_CSS = """
<style>

    /* Center all headings, override color to a greenish tone */
    h1, h2, h3, h4, h5, h6 {
        text-align: center !important;
        color: #5c7829 !important; 
        margin-bottom: 0.8rem !important;
    }
    /* Paragraph text color */
    .stMarkdown p {
        color: #b7b327;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Force Plotly's default template to be white and color scale to Plasma
px.defaults.template = "plotly_white"
px.defaults.color_continuous_scale = px.colors.sequential.Viridis

# ------------------------------------------------------------------------------
# 2. DATA LOADING & MERGING
# ------------------------------------------------------------------------------
@st.cache_data
def load_and_merge_data():
    df_internet = pd.read_csv("data/internet_usage.csv")
    year_cols = [str(y) for y in range(2000, 2024)]
    df_internet = pd.melt(
        df_internet,
        id_vars=["Country Name", "Country Code"],
        value_vars=year_cols,
        var_name="Year",
        value_name="Internet Usage (%)"
    )
    df_internet["Year"] = pd.to_numeric(df_internet["Year"], errors="coerce")
    df_internet["Internet Usage (%)"] = (
        df_internet["Internet Usage (%)"]
        .astype(str).replace(r"[^0-9\.]+", "", regex=True)
    )
    df_internet["Internet Usage (%)"] = pd.to_numeric(df_internet["Internet Usage (%)"], errors="coerce")
    df_internet.dropna(subset=["Internet Usage (%)"], inplace=True)

    df_econ = pd.read_csv("data/economic_indicators.csv")
    regions = [
        "Africa Eastern and Southern", "Africa Western and Central", "Arab World",
        "Caribbean small states", "Central Europe and the Baltics", "Early-demographic dividend",
        "East Asia & Pacific", "East Asia & Pacific (IDA & IBRD countries)",
        "East Asia & Pacific (excluding high income)", "Euro area", "Europe & Central Asia",
        "Europe & Central Asia (IDA & IBRD countries)", "Europe & Central Asia (excluding high income)",
        "European Union", "Fragile and conflict affected situations",
        "Heavily indebted poor countries (HIPC)", "High income", "IBRD only", "IDA & IBRD total",
        "IDA blend", "IDA only", "IDA total", "Late-demographic dividend",
        "Latin America & Caribbean", "Latin America & Caribbean (excluding high income)",
        "Latin America & the Caribbean (IDA & IBRD countries)",
        "Least developed countries: UN classification", "Low & middle income", "Low income",
        "Lower middle income", "Middle East & North Africa",
        "Middle East & North Africa (IDA & IBRD countries)",
        "Middle East & North Africa (excluding high income)",
        "Middle income", "North America", "Not classified", "OECD members",
        "Other small states", "Pacific island small states", "Post-demographic dividend",
        "Pre-demographic dividend", "Small states", "South Asia", "South Asia (IDA & IBRD)",
        "Sub-Saharan Africa", "Sub-Saharan Africa (IDA & IBRD countries)",
        "Sub-Saharan Africa (excluding high income)", "Upper middle income", "World"
    ]
    df_econ = df_econ[~df_econ["country_name"].isin(regions)]
    df_econ["year"] = pd.to_numeric(df_econ["year"], errors="coerce")
    df_econ = df_econ[df_econ["year"].between(2000, 2023)]
    df_econ["gdp_per_capita"] = pd.to_numeric(df_econ["gdp_per_capita"], errors="coerce")
    df_econ["access_to_electricity"] = pd.to_numeric(df_econ["access_to_electricity"], errors="coerce")
    df_econ["population_total"] = pd.to_numeric(df_econ["population_total"], errors="coerce")
    keep_cols = ["country_name", "year", "gdp_per_capita", "access_to_electricity", "population_total"]
    df_econ = df_econ[keep_cols]

    df_merged = pd.merge(
        df_internet, df_econ,
        left_on=["Country Name", "Year"],
        right_on=["country_name", "year"],
        how="inner"
    )
    df_merged.drop(columns=["country_name", "year"], inplace=True)
    return df_merged

df = load_and_merge_data()

# ------------------------------------------------------------------------------
# 3. HELPER / UTILITY FUNCTIONS
# ------------------------------------------------------------------------------
def render_card(title, value, subtext, color="#5c7829"):
    st.markdown(f"""
    <div style="
        background-color:#f0f0f0;
        border-radius:10px;
        padding:1rem;
        margin-bottom:1rem;
        border: 1px solid #dddddd;
        text-align:center;">
        <h4 style="margin-bottom:0.5rem; color:{color};">{title}</h4>
        <p style="font-size:1.7rem; font-weight:bold; margin:0; color:#333333;">{value}</p>
        <p style="color:#777777; margin:0;">{subtext}</p>
    </div>
    """, unsafe_allow_html=True)

def apply_white_layout(fig):
    """
    Force a white background explicitly.
    """
    fig.update_layout(
        template="ggplot2",
    )
    return fig

# ------------------------------------------------------------------------------
# 4. PAGE SECTIONS
# ------------------------------------------------------------------------------
def page_home(df):
    st.markdown("<h1>Global Internet Usage & Economic Context</h1>", unsafe_allow_html=True)
    st.write(
        "<span style='color:#555555;'>Discover global internet adoption from 2000 to 2023, including how GDP per capita and "
        "electricity access impact usage. Compare countries, view rankings, and explore interactive maps.</span>",
        unsafe_allow_html=True
    )

    # Key Stats
    latest_year = int(df["Year"].max())
    df_latest = df[df["Year"] == latest_year]
    avg_usage = df_latest["Internet Usage (%)"].mean().round(2)
    top_row = df_latest.sort_values("Internet Usage (%)", ascending=False).head(1)
    bottom_row = df_latest.sort_values("Internet Usage (%)").head(1)
    top_country = top_row["Country Name"].values[0]
    top_rate = round(top_row["Internet Usage (%)"].values[0], 2)
    low_country = bottom_row["Country Name"].values[0]
    low_rate = round(bottom_row["Internet Usage (%)"].values[0], 2)

    col1, col2, col3 = st.columns(3)
    with col1:
        render_card("Global Average Usage", f"{avg_usage}%", f"Average in {latest_year}")
    with col2:
        render_card("Top Country", top_country, f"{top_rate}%")
    with col3:
        render_card("Lowest Country", low_country, f"{low_rate}%")

    st.markdown("---")

    # Global Trend + Range Slider
    st.markdown("<h3>Global Average Usage Over Time</h3>", unsafe_allow_html=True)
    min_year = int(df["Year"].min())
    max_year = int(df["Year"].max())
    year_range = st.slider(
        "Select year range:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1,
        key="global_trend_range"
    )
    start_year, end_year = year_range
    dff_range = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]
    df_global = dff_range.groupby("Year")["Internet Usage (%)"].mean().reset_index()

    fig1 = px.line(
        df_global,
        x="Year",
        y="Internet Usage (%)",
        title="Global Average Internet Usage",
    )
    fig1 = apply_white_layout(fig1)
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("<h3>Year-over-Year Growth</h3>", unsafe_allow_html=True)
    df_global = df_global.sort_values("Year")  # ensure ascending
    df_global["YoY Growth (%)"] = df_global["Internet Usage (%)"].pct_change() * 100
    df_global = df_global.dropna(subset=["YoY Growth (%)"])
    fig2 = px.bar(
        df_global,
        x="Year",
        y="YoY Growth (%)",
        title="Year-over-Year Growth in Global Usage"
    )
    fig2 = apply_white_layout(fig2)
    st.plotly_chart(fig2, use_container_width=True)


def page_country_analysis(df):
    st.markdown("<h1>Country Analysis</h1>", unsafe_allow_html=True)
    countries_sorted = sorted(df["Country Name"].unique())
    selected_country = st.selectbox(
        "Select a Country:",
        options=countries_sorted,
        index=countries_sorted.index("United States") if "United States" in countries_sorted else 0,
        key="country_analysis_select"
    )

    # Single-country usage
    dff_country = df[df["Country Name"] == selected_country]
    fig_country = px.line(
        dff_country,
        x="Year",
        y="Internet Usage (%)",
        title=f"{selected_country} - Internet Usage Over Time",
        markers=True
    )
    fig_country = apply_white_layout(fig_country)
    st.plotly_chart(fig_country, use_container_width=True)

    # Compare with global average
    global_avg = df.groupby("Year")["Internet Usage (%)"].mean().reset_index()
    fig_compare = px.line(
        global_avg,
        x="Year",
        y="Internet Usage (%)",
        title="Comparison: Country vs Global Avg",
        markers=True
    )
    fig_compare.add_trace(px.line(dff_country, x="Year", y="Internet Usage (%)").data[0])
    fig_compare.data[0].name = "Global Avg"
    fig_compare.data[1].name = selected_country
    fig_compare = apply_white_layout(fig_compare)
    fig_compare.update_layout(hovermode="x unified")
    st.plotly_chart(fig_compare, use_container_width=True)


def page_compare_countries(df):
    st.markdown("<h1>Compare Multiple Countries</h1>", unsafe_allow_html=True)
    countries_sorted = sorted(df["Country Name"].unique())
    multi_countries = st.multiselect(
        "Select Countries:",
        options=countries_sorted,
        default=["United States", "China"],
        key="compare_countries_multi"
    )

    min_year = int(df["Year"].min())
    max_year = int(df["Year"].max())
    compare_year_range = st.slider(
        "Select Year Range:",
        min_value=min_year,
        max_value=max_year,
        value=(2000, max_year),
        step=1,
        key="compare_countries_range"
    )
    start_year, end_year = compare_year_range
    dff_sub = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]
    dff_sub = dff_sub[dff_sub["Country Name"].isin(multi_countries)]

    fig_compare_multi = px.line(
        dff_sub,
        x="Year",
        y="Internet Usage (%)",
        color="Country Name",
        markers=True,
        title="Internet Usage Comparison"
    )
    fig_compare_multi = apply_white_layout(fig_compare_multi)
    st.plotly_chart(fig_compare_multi, use_container_width=True)


def page_country_ranking(df):
    st.markdown("<h1>Country Ranking</h1>", unsafe_allow_html=True)
    all_years = sorted(df["Year"].unique())
    selected_year_rank = st.selectbox(
        "Select Year:",
        options=all_years,
        index=len(all_years) - 1,
        key="ranking_year_select"
    )
    dff_year = df[df["Year"] == selected_year_rank]
    dff_sorted = dff_year.sort_values("Internet Usage (%)", ascending=False)

    top10 = dff_sorted.head(10)
    bottom10 = dff_sorted.tail(10).sort_values("Internet Usage (%)", ascending=True)

    col_left, col_right = st.columns(2)
    with col_left:
        fig_top = px.bar(
            top10,
            x="Internet Usage (%)",
            y="Country Name",
            orientation="h",
            color="Internet Usage (%)",
            title=f"Top 10 Countries in {int(selected_year_rank)}"
        )
        fig_top.update_layout(yaxis={"categoryorder": "total ascending"}, template="plotly_white")
        st.plotly_chart(fig_top, use_container_width=True)

    with col_right:
        fig_bottom = px.bar(
            bottom10,
            x="Internet Usage (%)",
            y="Country Name",
            orientation="h",
            color="Internet Usage (%)",
            title=f"Bottom 10 Countries in {int(selected_year_rank)}"
        )
        fig_bottom.update_layout(yaxis={"categoryorder": "total ascending"})
        fig_bottom = apply_white_layout(fig_bottom)
        fig_bottom.update_layout(template="plotly_white")
        st.plotly_chart(fig_bottom, use_container_width=True)


def page_regional_insights(df):
    st.markdown("<h1>Regional Insights</h1>", unsafe_allow_html=True)
    st.write(
        "<span style='color:#555555;'>Explore how internet usage and population distribution have changed around the globe. "
        "This animated bubble map shows internet usage by color and population by bubble size, over the years.</span>",
        unsafe_allow_html=True
    )

    dff_map = df.rename(columns={"Country Code": "iso_alpha"})
    dff_map["Internet Usage (%)"] = dff_map["Internet Usage (%)"].fillna(0)
    dff_map["population_total"] = dff_map["population_total"].fillna(0)

    fig_map = px.scatter_geo(
        dff_map,
        locations="iso_alpha",
        color="Internet Usage (%)",
        size="population_total",
        hover_name="Country Name",
        animation_frame="Year",
        projection="natural earth",
        range_color=[0, 100],
        size_max=40,
        title="Global Internet Usage & Population (2000–2023)"
    )
    fig_map.update_layout(
        margin={"r":0,"t":50,"l":0,"b":0},
        height=700,
    )
    fig_map = apply_white_layout(fig_map)
    st.plotly_chart(fig_map, use_container_width=True)


def page_economic_insights(df):
    st.markdown("<h1>Economic Insights</h1>", unsafe_allow_html=True)
    st.write(
        "<span style='color:#555555;'>Investigate how internet adoption correlates with GDP per capita, "
        "access to electricity, and population.</span>",
        unsafe_allow_html=True
    )
    all_years = sorted(df["Year"].unique())
    econ_year = st.selectbox(
        "Select Year:",
        options=all_years,
        index=len(all_years) - 1,
        key="econ_insights_year"
    )
    dff_econ = df[df["Year"] == econ_year].copy()
    dff_econ["population_total"] = dff_econ["population_total"].fillna(0)
    dff_econ["access_to_electricity"] = dff_econ["access_to_electricity"].fillna(0)
    dff_econ["gdp_per_capita"] = dff_econ["gdp_per_capita"].fillna(0)

    max_gdp = dff_econ["gdp_per_capita"].quantile(0.99)
    fig_econ = px.scatter(
        dff_econ,
        x="gdp_per_capita",
        y="Internet Usage (%)",
        size="population_total",
        color="access_to_electricity",
        hover_name="Country Name",
        labels={
            "gdp_per_capita": "GDP per Capita",
            "Internet Usage (%)": "Internet Usage (%)",
            "access_to_electricity": "Access to Electricity (%)"
        },
        title=f"Internet Usage vs. GDP per Capita ({int(econ_year)})"
    )
    fig_econ.update_xaxes(range=[0, max_gdp])
    fig_econ = apply_white_layout(fig_econ)
    st.plotly_chart(fig_econ, use_container_width=True)


def page_correlations(df):
    st.markdown("<h1>Correlation Analysis</h1>", unsafe_allow_html=True)
    st.write(
        "<span style='color:#555555;'>Gain deeper insights by analyzing correlations among key variables: "
        "Internet Usage, GDP per Capita, Access to Electricity, and Population.</span>",
        unsafe_allow_html=True
    )

    all_years = sorted(df["Year"].unique())
    selected_year = st.selectbox(
        "Select Year to Explore Correlations:",
        options=all_years,
        index=len(all_years) - 1,
        key="correlations_year"
    )

    dff_corr = df[df["Year"] == selected_year][
        ["Internet Usage (%)", "gdp_per_capita", "access_to_electricity", "population_total"]
    ].dropna()
    rename_map = {
        "Internet Usage (%)": "Internet Usage",
        "gdp_per_capita": "GDP per Capita",
        "access_to_electricity": "Access to Electricity",
        "population_total": "Population Total"
    }
    dff_corr = dff_corr.rename(columns=rename_map)

    if len(dff_corr) < 2:
        st.warning("Not enough data to compute correlations for this year. Try another year.")
        return

    corr_matrix = dff_corr.corr()
    fig_corr = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu",
        range_color=[-1, 1],
        title=f"Correlation Matrix ({int(selected_year)})"
    )
    fig_corr.update_layout(margin=dict(l=0,r=0,b=0,t=50))
    fig_corr = apply_white_layout(fig_corr)
    st.plotly_chart(fig_corr, use_container_width=True)

# ------------------------------------------------------------------------------
# 5. MAIN APP FUNCTION
# ------------------------------------------------------------------------------
def main():
    st.markdown("---")

    tabs = st.tabs([
        "Home",
        "Country Analysis",
        "Compare Countries",
        "Country Ranking",
        "Regional Insights",
        "Economic Insights",
        "Correlation Analysis"
    ])

    with tabs[0]:
        page_home(df)
    with tabs[1]:
        page_country_analysis(df)
    with tabs[2]:
        page_compare_countries(df)
    with tabs[3]:
        page_country_ranking(df)
    with tabs[4]:
        page_regional_insights(df)
    with tabs[5]:
        page_economic_insights(df)
    with tabs[6]:
        page_correlations(df)

    st.markdown("---")
    st.markdown(
        "<p style='text-align:center; color:#888888;'>"
        "© 2025 Global Internet & Economic Dashboard — All Rights Reserved"
        "</p>",
        unsafe_allow_html=True
    )


# ------------------------------------------------------------------------------
# 6. RUN
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    st.markdown("<h1>Global Internet Usage & Economic Dashboard</h1>", unsafe_allow_html=True)
    main()

