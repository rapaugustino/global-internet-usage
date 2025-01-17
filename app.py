import pandas as pd
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

# ------------------------------------------------------------------------------
# GLOBAL DEFAULTS
# ------------------------------------------------------------------------------
# More vibrant color template & palette
px.defaults.template = "plotly"
px.defaults.color_continuous_scale = px.colors.sequential.Sunset  # For better contrast


# ------------------------------------------------------------------------------
# 1. DATA LOADING & MERGING
# ------------------------------------------------------------------------------
def load_and_merge_data():
    """
    1) Load the main internet usage dataset (internet_usage.csv).
    2) Load the economic indicators dataset (economic_indicators.csv).
    3) Remove region-based rows & years outside 2000–2023 in the economic dataset.
    4) Convert all numeric columns properly.
    5) Merge on (Country Name == country_name) and (Year == year).
    6) Return a single merged DataFrame.
    """
    # ---- Internet Usage Data ----
    df_internet = pd.read_csv("data/internet_usage.csv")

    # Reshape wide to long
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
        .astype(str)
        .replace(r"[^0-9\.]+", "", regex=True)
    )
    df_internet["Internet Usage (%)"] = pd.to_numeric(df_internet["Internet Usage (%)"], errors="coerce")
    df_internet.dropna(subset=["Internet Usage (%)"], inplace=True)

    # ---- Economic Indicators Data ----
    df_econ = pd.read_csv("data/economic_indicators.csv")

    # Remove region rows
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

    # Keep only 2000-2023
    df_econ["year"] = pd.to_numeric(df_econ["year"], errors="coerce")
    df_econ = df_econ[df_econ["year"].between(2000, 2023)]

    # Convert numeric columns
    df_econ["gdp_per_capita"] = pd.to_numeric(df_econ["gdp_per_capita"], errors="coerce")
    df_econ["access_to_electricity"] = pd.to_numeric(df_econ["access_to_electricity"], errors="coerce")
    df_econ["population_total"] = pd.to_numeric(df_econ["population_total"], errors="coerce")

    # Select relevant columns
    keep_cols = ["country_name", "year", "gdp_per_capita", "access_to_electricity", "population_total"]
    df_econ = df_econ[keep_cols]

    # Merge
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
# 2. INITIALIZE THE APP
# ------------------------------------------------------------------------------
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
server = app.server
app.config.suppress_callback_exceptions = True

# ------------------------------------------------------------------------------
# NAVBAR
# ------------------------------------------------------------------------------
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("Global Internet & Economic Dashboard", className="fw-bold"),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Home", href="/", active="exact")),
                    dbc.NavItem(dbc.NavLink("Country Analysis", href="/country-analysis", active="exact")),
                    dbc.NavItem(dbc.NavLink("Compare Countries", href="/compare-countries", active="exact")),
                    dbc.NavItem(dbc.NavLink("Country Ranking", href="/country-ranking", active="exact")),
                    dbc.NavItem(dbc.NavLink("Regional Insights", href="/regional-insights", active="exact")),
                    dbc.NavItem(dbc.NavLink("Economic Insights", href="/economic-insights", active="exact")),
                ],
                navbar=True
            ),
        ]
    ),
    color="primary",
    dark=True,
    className="mb-4 shadow"
)


# ------------------------------------------------------------------------------
# 3. PAGES
# ------------------------------------------------------------------------------
#
# 3.1 HOME PAGE (Hero, Global Trends & Year-over-Year Growth)
# ------------------------------------------------------------------------------
def home_page():
    latest_year = int(df["Year"].max())
    df_latest = df[df["Year"] == latest_year]

    avg_usage = df_latest["Internet Usage (%)"].mean().round(2)
    top_row = df_latest.sort_values("Internet Usage (%)", ascending=False).head(1)
    bottom_row = df_latest.sort_values("Internet Usage (%)").head(1)
    top_country = top_row["Country Name"].values[0]
    top_rate = round(top_row["Internet Usage (%)"].values[0], 2)
    low_country = bottom_row["Country Name"].values[0]
    low_rate = round(bottom_row["Internet Usage (%)"].values[0], 2)

    min_year = int(df["Year"].min())
    max_year = int(df["Year"].max())

    # Hero Section
    hero_section = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H1(
                                    "Global Internet Usage & Economic Context",
                                    className="display-4 text-center text-primary fw-bold"
                                ),
                                html.P(
                                    "Discover global internet adoption from 2000 to 2023, including how "
                                    "GDP per capita and electricity access impact usage. Compare countries, "
                                    "view rankings, and explore interactive maps.",
                                    className="lead text-center"
                                )
                            ]
                        ),
                        md=12
                    )
                ],
                className="py-4 bg-light rounded-3 shadow mb-4"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Global Average Usage", className="fw-bold"),
                                dbc.CardBody(
                                    [
                                        html.H3(f"{avg_usage}%", className="card-title"),
                                        html.P(f"Average in {latest_year}", className="text-secondary")
                                    ]
                                )
                            ],
                            className="mb-3 shadow"
                        ),
                        md=4
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Top Country", className="fw-bold"),
                                dbc.CardBody(
                                    [
                                        html.H3(top_country, className="card-title"),
                                        html.P(f"{top_rate}%", className="text-secondary")
                                    ]
                                )
                            ],
                            className="mb-3 shadow"
                        ),
                        md=4
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Lowest Country", className="fw-bold"),
                                dbc.CardBody(
                                    [
                                        html.H3(low_country, className="card-title"),
                                        html.P(f"{low_rate}%", className="text-secondary")
                                    ]
                                )
                            ],
                            className="mb-3 shadow"
                        ),
                        md=4
                    ),
                ]
            )
        ],
        fluid=True,
        className="mb-4"
    )

    # Global Trend + Range Slider
    trends_section = dbc.Container(
        [
            html.H2("Global Average Usage Over Time", className="text-center mb-3 fw-bold"),
            dcc.RangeSlider(
                id="global-year-range",
                min=min_year,
                max=max_year,
                step=1,
                value=[min_year, max_year],
                marks={y: str(y) for y in range(min_year, max_year + 1, 3)},
                allowCross=False,
                className="mb-3"
            ),
            dcc.Graph(id="global-trend-graph", style={"height": "400px"})
        ],
        fluid=True,
        className="mb-4"
    )

    # YoY Growth
    yoy_section = dbc.Container(
        [
            html.H2("Year-over-Year Growth", className="text-center mb-3 fw-bold"),
            dcc.Graph(id="yoy-growth-graph", style={"height": "400px"})
        ],
        fluid=True
    )

    return html.Div([hero_section, trends_section, yoy_section])


@app.callback(
    [Output("global-trend-graph", "figure"),
     Output("yoy-growth-graph", "figure")],
    [Input("global-year-range", "value")]
)
def update_home_charts(range_value):
    start_year, end_year = range_value
    dff_range = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

    # 1) Global average usage line chart
    df_global = dff_range.groupby("Year")["Internet Usage (%)"].mean().reset_index()
    fig1 = px.line(
        df_global,
        x="Year",
        y="Internet Usage (%)",
        title="Global Average Internet Usage"
    )
    fig1.update_layout(transition_duration=500)

    # 2) Year-over-Year growth (bar chart)
    df_global = df_global.sort_values("Year")  # ensure ascending
    df_global["YoY Growth (%)"] = df_global["Internet Usage (%)"].pct_change() * 100
    # Drop first row if NaN
    df_global = df_global.dropna(subset=["YoY Growth (%)"])

    fig2 = px.bar(
        df_global,
        x="Year",
        y="YoY Growth (%)",
        title="Year-over-Year Growth in Global Usage"
    )
    fig2.update_layout(transition_duration=500)

    return fig1, fig2


# ------------------------------------------------------------------------------
# 3.2 COUNTRY ANALYSIS PAGE
# ------------------------------------------------------------------------------
def country_analysis_page():
    countries_sorted = sorted(df["Country Name"].unique())
    layout = dbc.Container(
        [
            html.H2("Country Analysis", className="mb-4 fw-bold"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Select a Country:", className="fw-bold"),
                            dcc.Dropdown(
                                id="country-dropdown",
                                options=[{"label": c, "value": c} for c in countries_sorted],
                                value="United States",
                                clearable=False
                            )
                        ],
                        md=4
                    )
                ],
                className="mb-4"
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="country-trend", style={"height": "400px"}), md=6),
                    dbc.Col(dcc.Graph(id="country-global-compare", style={"height": "400px"}), md=6),
                ]
            )
        ],
        fluid=True
    )
    return layout


@app.callback(
    [Output("country-trend", "figure"),
     Output("country-global-compare", "figure")],
    [Input("country-dropdown", "value")]
)
def update_country_analysis(selected_country):
    dff_country = df[df["Country Name"] == selected_country]

    # Single-country usage
    fig1 = px.line(
        dff_country,
        x="Year",
        y="Internet Usage (%)",
        title=f"{selected_country} - Internet Usage Over Time",
        markers=True
    )
    fig1.update_layout(transition_duration=500)

    # Compare with global average
    global_avg = df.groupby("Year")["Internet Usage (%)"].mean().reset_index()
    fig2 = px.line(
        global_avg,
        x="Year",
        y="Internet Usage (%)",
        title="Comparison: Country vs Global Avg",
        markers=True
    )
    fig2.add_trace(px.line(dff_country, x="Year", y="Internet Usage (%)").data[0])
    fig2.data[0].name = "Global Avg"
    fig2.data[1].name = selected_country
    fig2.update_layout(transition_duration=500, hovermode="x unified")

    return fig1, fig2


# ------------------------------------------------------------------------------
# 3.3 COMPARE MULTIPLE COUNTRIES
# ------------------------------------------------------------------------------
def compare_countries_page():
    countries_sorted = sorted(df["Country Name"].unique())
    min_year = int(df["Year"].min())
    max_year = int(df["Year"].max())

    layout = dbc.Container(
        [
            html.H2("Compare Multiple Countries", className="mb-4 fw-bold"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Select Countries:", className="fw-bold"),
                            dcc.Dropdown(
                                id="multi-country-dropdown",
                                options=[{"label": c, "value": c} for c in countries_sorted],
                                value=["United States", "China"],
                                multi=True
                            )
                        ],
                        md=6
                    ),
                    dbc.Col(
                        [
                            html.Label("Year Range:", className="fw-bold"),
                            dcc.RangeSlider(
                                id="compare-year-range",
                                min=min_year,
                                max=max_year,
                                value=[2005, max_year],
                                marks={y: str(y) for y in range(min_year, max_year + 1, 3)},
                                allowCross=False
                            )
                        ],
                        md=6
                    )
                ],
                className="mb-4"
            ),
            dcc.Graph(id="multi-country-comparison", style={"height": "450px"})
        ],
        fluid=True
    )
    return layout


@app.callback(
    Output("multi-country-comparison", "figure"),
    [Input("multi-country-dropdown", "value"),
     Input("compare-year-range", "value")]
)
def update_compare_countries(selected_countries, year_range):
    start_year, end_year = year_range
    dff_sub = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]
    dff_sub = dff_sub[dff_sub["Country Name"].isin(selected_countries)]

    fig = px.line(
        dff_sub,
        x="Year",
        y="Internet Usage (%)",
        color="Country Name",
        markers=True,
        title="Internet Usage Comparison"
    )
    fig.update_layout(transition_duration=500)
    return fig


# ------------------------------------------------------------------------------
# 3.4 COUNTRY RANKING
# ------------------------------------------------------------------------------
def country_ranking_page():
    all_years = sorted(df["Year"].unique())
    layout = dbc.Container(
        [
            html.H2("Country Ranking", className="mb-4 fw-bold"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Select Year:", className="fw-bold"),
                            dcc.Dropdown(
                                id="ranking-year-dropdown",
                                options=[{"label": str(y), "value": y} for y in all_years],
                                value=all_years[-1],
                                clearable=False
                            )
                        ],
                        md=4
                    )
                ],
                className="mb-4"
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="top10-bar", style={"height": "400px"}), md=6),
                    dbc.Col(dcc.Graph(id="bottom10-bar", style={"height": "400px"}), md=6),
                ]
            )
        ],
        fluid=True
    )
    return layout


@app.callback(
    [Output("top10-bar", "figure"),
     Output("bottom10-bar", "figure")],
    [Input("ranking-year-dropdown", "value")]
)
def update_country_ranking(selected_year):
    dff_year = df[df["Year"] == selected_year]
    dff_sorted = dff_year.sort_values("Internet Usage (%)", ascending=False)

    top10 = dff_sorted.head(10)
    bottom10 = dff_sorted.tail(10).sort_values("Internet Usage (%)", ascending=True)

    fig_top = px.bar(
        top10,
        x="Internet Usage (%)",
        y="Country Name",
        orientation="h",
        color="Internet Usage (%)",
        title=f"Top 10 Countries in {int(selected_year)}"
    )
    fig_top.update_layout(yaxis={"categoryorder": "total ascending"}, transition_duration=500)

    fig_bottom = px.bar(
        bottom10,
        x="Internet Usage (%)",
        y="Country Name",
        orientation="h",
        color="Internet Usage (%)",
        title=f"Bottom 10 Countries in {int(selected_year)}"
    )
    fig_bottom.update_layout(yaxis={"categoryorder": "total ascending"}, transition_duration=500)

    return fig_top, fig_bottom


# ------------------------------------------------------------------------------
# 3.5 REGIONAL INSIGHTS (Animated Choropleth + Bubble Map)
# ------------------------------------------------------------------------------
def regional_insights_page():
    dff_map = df.rename(columns={"Country Code": "iso_alpha"})

    animated_fig = px.choropleth(
        dff_map,
        locations="iso_alpha",
        color="Internet Usage (%)",
        hover_name="Country Name",
        animation_frame="Year",
        range_color=[0, 100],
        title="Animated Internet Usage Over Time (2000–2023)"
    )
    animated_fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0}, transition_duration=500)

    layout = dbc.Container(
        [
            html.H2("Regional Insights", className="mb-4 fw-bold"),
            html.P(
                "Below is an animated global map showing internet usage from 2000 to 2023. "
                "Press the play button to watch adoption change over time.",
                className="mb-3"
            ),
            dcc.Graph(figure=animated_fig, style={"height": "500px"}),

            html.Hr(),

            html.P(
                "Below is a Bubble Map for the latest available year. Circle size corresponds to usage, "
                "and color scale can be changed for better contrast.",
                className="mt-3"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Select Year:", className="fw-bold"),
                            dcc.Dropdown(
                                id="bubble-year-dropdown",
                                options=[
                                    {"label": str(y), "value": y}
                                    for y in sorted(df["Year"].unique())
                                ],
                                value=df["Year"].max(),
                                clearable=False,
                                className="mb-3"
                            )
                        ],
                        md=3
                    ),
                    dbc.Col(
                        [
                            html.Label("Color Scale:", className="fw-bold"),
                            dcc.Dropdown(
                                id="bubble-color-scale",
                                options=[
                                    {"label": scale, "value": scale}
                                    for scale in px.colors.named_colorscales()
                                ],
                                value="Sunset",
                                clearable=False,
                                className="mb-3"
                            )
                        ],
                        md=3
                    )
                ],
                className="mb-3"
            ),
            dcc.Graph(id="bubble-map", style={"height": "500px"})
        ],
        fluid=True
    )
    return layout


@app.callback(
    Output("bubble-map", "figure"),
    [Input("bubble-year-dropdown", "value"),
     Input("bubble-color-scale", "value")]
)
def update_bubble_map(selected_year, chosen_scale):
    dff_year = df[df["Year"] == selected_year].copy()
    dff_year.rename(columns={"Country Code": "iso_alpha"}, inplace=True)

    # Fill missing usage with zero
    dff_year["Internet Usage (%)"] = dff_year["Internet Usage (%)"].fillna(0)

    fig = px.scatter_geo(
        dff_year,
        locations="iso_alpha",
        size="Internet Usage (%)",
        color="Internet Usage (%)",
        hover_name="Country Name",
        color_continuous_scale=chosen_scale,
        projection="natural earth",
        title=f"Global Usage in {int(selected_year)}"
    )
    fig.update_layout(transition_duration=500)
    return fig


# ------------------------------------------------------------------------------
# 3.6 ECONOMIC INSIGHTS (Scatter w/ limited X-range)
# ------------------------------------------------------------------------------
def economic_insights_page():
    all_years = sorted(df["Year"].unique())
    layout = dbc.Container(
        [
            html.H2("Economic Insights", className="mb-4 fw-bold"),
            html.P(
                "Investigate how internet adoption correlates with GDP per capita, "
                "access to electricity, and population. Select a year below.",
                className="mb-3"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Select Year:", className="fw-bold"),
                            dcc.Dropdown(
                                id="econ-year-dropdown",
                                options=[{"label": str(y), "value": y} for y in all_years],
                                value=all_years[-1],
                                clearable=False,
                                className="mb-3",
                                style={"width": "250px"}
                            )
                        ],
                        md=4
                    )
                ],
                className="mb-4"
            ),
            dcc.Graph(id="econ-scatter", style={"height": "500px"})
        ],
        fluid=True
    )
    return layout


@app.callback(
    Output("econ-scatter", "figure"),
    [Input("econ-year-dropdown", "value")]
)
def update_econ_scatter(selected_year):
    dff_econ = df[df["Year"] == selected_year].copy()
    # Replace NaNs with 0
    dff_econ["population_total"] = dff_econ["population_total"].fillna(0)
    dff_econ["access_to_electricity"] = dff_econ["access_to_electricity"].fillna(0)
    dff_econ["gdp_per_capita"] = dff_econ["gdp_per_capita"].fillna(0)

    # Limit the x-range to 99th percentile to avoid blank space due to extreme outliers
    max_gdp = dff_econ["gdp_per_capita"].quantile(0.99)

    fig = px.scatter(
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
        title=f"Internet Usage vs GDP per Capita ({int(selected_year)})"
    )
    # Zoom in on 99th percentile for x-axis
    fig.update_xaxes(range=[0, max_gdp])
    fig.update_layout(transition_duration=500)
    return fig


# ------------------------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------------------------
footer = dbc.Container(
    [
        html.Hr(),
        dbc.Row(
            dbc.Col(
                html.P(
                    "© 2025 Global Internet & Economic Dashboard — All Rights Reserved",
                    className="text-center text-muted"
                )
            )
        )
    ],
    fluid=True
)

# ------------------------------------------------------------------------------
# 4. APP LAYOUT & ROUTING
# ------------------------------------------------------------------------------
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        navbar,
        html.Div(id="page-content", className="mb-5"),
        footer
    ]
)


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/country-analysis":
        return country_analysis_page()
    elif pathname == "/compare-countries":
        return compare_countries_page()
    elif pathname == "/country-ranking":
        return country_ranking_page()
    elif pathname == "/regional-insights":
        return regional_insights_page()
    elif pathname == "/economic-insights":
        return economic_insights_page()
    else:
        # Default is Home
        return home_page()


# ------------------------------------------------------------------------------
# 5. RUN
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True)