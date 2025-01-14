import pandas as pd
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

# ------------------------------------------------------------------------------
# GLOBAL SETTINGS FOR PLOTLY
# ------------------------------------------------------------------------------
# This sets the default template to "ggplot2" for all figures
px.defaults.template = "ggplot2"
px.defaults.color_continuous_scale = px.colors.sequential.Viridis


# ------------------------------------------------------------------------------
# 1. DATA LOADING & CLEANING
# ------------------------------------------------------------------------------
def load_data():
    """
    Load and clean the internet usage dataset:
      - Replaces weird string patterns (multiple dots, etc.) with numeric-friendly text
      - Converts to float
      - Drops rows that remain NaN
    """
    data = pd.read_csv("data/internet_usage.csv")

    # Identify columns for years 2000-2023
    year_cols = [str(y) for y in range(2000, 2024)]

    # Melt wide data into long format
    df_melted = pd.melt(
        data,
        id_vars=["Country Name", "Country Code"],
        value_vars=year_cols,
        var_name="Year",
        value_name="Internet Usage (%)"
    )

    # Convert 'Year' to numeric
    df_melted["Year"] = pd.to_numeric(df_melted["Year"], errors="coerce")

    # Clean 'Internet Usage (%)' (remove non-digit/dot chars)
    df_melted["Internet Usage (%)"] = df_melted["Internet Usage (%)"].astype(str)
    df_melted["Internet Usage (%)"] = df_melted["Internet Usage (%)"].replace(
        r"[^0-9\.]+", "", regex=True
    )
    df_melted["Internet Usage (%)"] = pd.to_numeric(
        df_melted["Internet Usage (%)"], errors="coerce"
    )
    df_melted.dropna(subset=["Internet Usage (%)"], inplace=True)

    return df_melted


df = load_data()

# ------------------------------------------------------------------------------
# 2. INITIALIZE THE DASH APP (FLATLY THEME)
# ------------------------------------------------------------------------------
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY]  # A polished, modern light theme
)
app.config.suppress_callback_exceptions = True
server = app.server

# ------------------------------------------------------------------------------
# 3. NAVBAR
# ------------------------------------------------------------------------------
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("Global Internet Usage Dashboard"),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Home", href="/", active="exact")),
                    dbc.NavItem(dbc.NavLink("Country Analysis", href="/country-analysis", active="exact")),
                    dbc.NavItem(dbc.NavLink("Compare Countries", href="/compare-countries", active="exact")),
                    dbc.NavItem(dbc.NavLink("Country Ranking", href="/country-ranking", active="exact")),
                    dbc.NavItem(dbc.NavLink("Regional Insights", href="/regional-insights", active="exact")),
                ],
                navbar=True
            ),
        ]
    ),
    color="primary",
    dark=True,
    className="mb-4"
)


# ------------------------------------------------------------------------------
# 4. PAGE LAYOUTS
# ------------------------------------------------------------------------------
#
# 4.1 HOME PAGE (GLOBAL TRENDS)
# ------------------------------------------------------------------------------
def home_page():
    """
    Displays:
    - A Hero-like header with key stats for the latest year
    - Global Trends with a range slider
    """
    latest_year = int(df["Year"].max())
    df_latest = df[df["Year"] == latest_year]
    avg_internet = df_latest["Internet Usage (%)"].mean().round(2)
    top_country = df_latest.sort_values(by="Internet Usage (%)", ascending=False).iloc[0]
    bottom_country = df_latest.sort_values(by="Internet Usage (%)").iloc[0]

    min_year = int(df["Year"].min())
    max_year = int(df["Year"].max())

    # Hero-like stats section
    hero_section = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H1("Global Internet Usage: 2000–2023", className="mb-3"),
                                html.P(
                                    "Explore how internet adoption has grown over the years. "
                                    "Use the slider below to filter the global trend chart, or use "
                                    "the navigation bar for more detailed analyses.",
                                    className="lead"
                                )
                            ]
                        ),
                        md=12
                    )
                ],
                className="py-4"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Global Average"),
                                dbc.CardBody(
                                    [
                                        html.H3(f"{avg_internet}%", className="card-title"),
                                        html.P(f"Average in {latest_year}", className="card-text"),
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
                                dbc.CardHeader("Top Country"),
                                dbc.CardBody(
                                    [
                                        html.H3(top_country["Country Name"], className="card-title"),
                                        html.P(f"{top_country['Internet Usage (%)']:.2f}%", className="card-text"),
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
                                dbc.CardHeader("Lowest Country"),
                                dbc.CardBody(
                                    [
                                        html.H3(bottom_country["Country Name"], className="card-title"),
                                        html.P(f"{bottom_country['Internet Usage (%)']:.2f}%", className="card-text"),
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

    # Global trends section
    trends_section = dbc.Container(
        [
            html.H2("Global Trends Over Time", className="text-center mb-3"),
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
            dcc.Graph(id="global-trend-graph", style={"height": "500px"})
        ],
        fluid=True
    )

    return html.Div([hero_section, trends_section])


@app.callback(
    Output("global-trend-graph", "figure"),
    [Input("global-year-range", "value")]
)
def update_global_trends(range_value):
    start_year, end_year = range_value
    df_filtered = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]
    global_avg = df_filtered.groupby("Year")["Internet Usage (%)"].mean().reset_index()

    fig = px.line(
        global_avg,
        x="Year",
        y="Internet Usage (%)",
        title="Global Average Internet Usage"
    )
    fig.update_layout(transition_duration=500)
    return fig


# ------------------------------------------------------------------------------
# 4.2 COUNTRY ANALYSIS
# ------------------------------------------------------------------------------
def country_analysis_page():
    countries_sorted = sorted(df["Country Name"].unique().tolist())
    layout = dbc.Container(
        [
            html.H2("Country Analysis", className="mb-4"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Select a Country:"),
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
                    dbc.Col(dcc.Graph(id="country-trend", style={"height": "450px"}), md=6),
                    dbc.Col(dcc.Graph(id="country-global-comparison", style={"height": "450px"}), md=6),
                ]
            )
        ],
        fluid=True
    )
    return layout


@app.callback(
    [Output("country-trend", "figure"),
     Output("country-global-comparison", "figure")],
    [Input("country-dropdown", "value")]
)
def update_country_analysis(selected_country):
    # Single-country usage over time
    country_data = df[df["Country Name"] == selected_country]
    fig1 = px.line(
        country_data,
        x="Year",
        y="Internet Usage (%)",
        title=f"{selected_country} - Internet Usage Over Time",
        markers=True
    )
    fig1.update_layout(transition_duration=500)

    # Compare selected country vs global avg
    global_avg = df.groupby("Year")["Internet Usage (%)"].mean().reset_index()
    fig2 = px.line(
        global_avg,
        x="Year",
        y="Internet Usage (%)",
        title="Comparison: Country vs Global Avg",
        markers=True
    )
    # Add the selected country
    fig2.add_trace(px.line(country_data, x="Year", y="Internet Usage (%)").data[0])
    # Rename lines
    fig2.data[0].name = "Global Avg"
    fig2.data[1].name = selected_country
    fig2.update_layout(transition_duration=500, hovermode="x unified")

    return fig1, fig2


# ------------------------------------------------------------------------------
# 4.3 COMPARE MULTIPLE COUNTRIES
# ------------------------------------------------------------------------------
def compare_countries_page():
    countries_sorted = sorted(df["Country Name"].unique().tolist())
    min_year = int(df["Year"].min())
    max_year = int(df["Year"].max())

    layout = dbc.Container(
        [
            html.H2("Compare Multiple Countries", className="mb-4"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Select Countries:"),
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
                            html.Label("Select Year Range:"),
                            dcc.RangeSlider(
                                id="compare-year-range",
                                min=min_year,
                                max=max_year,
                                step=1,
                                value=[2000, max_year],
                                marks={y: str(y) for y in range(min_year, max_year + 1, 3)},
                                allowCross=False,
                            )
                        ],
                        md=6
                    )
                ],
                className="mb-4"
            ),
            dcc.Graph(id="multi-country-comparison-graph", style={"height": "500px"})
        ],
        fluid=True
    )
    return layout


@app.callback(
    Output("multi-country-comparison-graph", "figure"),
    [Input("multi-country-dropdown", "value"),
     Input("compare-year-range", "value")]
)
def update_compare_countries(selected_countries, year_range):
    start_year, end_year = year_range
    dff = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]
    dff = dff[dff["Country Name"].isin(selected_countries)]

    fig = px.line(
        dff,
        x="Year",
        y="Internet Usage (%)",
        color="Country Name",
        markers=True,
        title="Internet Usage Comparison"
    )
    fig.update_layout(transition_duration=500)
    return fig


# ------------------------------------------------------------------------------
# 4.4 COUNTRY RANKING
# ------------------------------------------------------------------------------
def country_ranking_page():
    all_years = sorted(df["Year"].unique().tolist())
    layout = dbc.Container(
        [
            html.H2("Country Ranking", className="mb-4"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Select Year:"),
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
                    dbc.Col(dcc.Graph(id="top10-bar", style={"height": "450px"}), md=6),
                    dbc.Col(dcc.Graph(id="bottom10-bar", style={"height": "450px"}), md=6),
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
    dff = df[df["Year"] == selected_year].copy()
    df_sorted = dff.sort_values(by="Internet Usage (%)", ascending=False)

    top10 = df_sorted.head(10)
    bottom10 = df_sorted.tail(10).sort_values(by="Internet Usage (%)", ascending=True)

    fig_top = px.bar(
        top10,
        x="Internet Usage (%)",
        y="Country Name",
        orientation="h",
        color="Internet Usage (%)",
        title=f"Top 10 in {int(selected_year)}"
    )
    fig_top.update_layout(yaxis={"categoryorder": "total ascending"}, transition_duration=500, hovermode="x unified", template="ggplot2")

    fig_bottom = px.bar(
        bottom10,
        x="Internet Usage (%)",
        y="Country Name",
        orientation="h",
        color="Internet Usage (%)",
        title=f"Bottom 10 in {int(selected_year)}"
    )
    fig_bottom.update_layout(yaxis={"categoryorder": "total ascending"}, transition_duration=500, hovermode="x unified", template="ggplot2")

    return fig_top, fig_bottom


# ------------------------------------------------------------------------------
# 4.5 REGIONAL INSIGHTS
# ------------------------------------------------------------------------------
def regional_insights_page():
    """
    Displays:
      - an animated choropleth (no callback needed)
      - a bubble map controlled by a dropdown for color scale
    """
    # Animated choropleth
    dff_for_map = df.rename(columns={"Country Code": "iso_alpha"})
    animated_fig = px.choropleth(
        dff_for_map,
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
            html.H2("Regional Insights", className="mb-4"),
            html.P(
                "Below is an animated global map showing internet usage from 2000 to 2023. "
                "Press the play button to see usage evolve year by year.",
                className="mb-4"
            ),
            dcc.Graph(id="animated-choropleth", figure=animated_fig, style={"height": "600px"}),

            html.Hr(),

            html.P(
                "Below is a Bubble Map for the latest available year. You can adjust the color scale "
                "for better contrast. Circle size and color both reflect internet usage.",
                className="mt-4"
            ),
            dcc.Dropdown(
                id="bubble-color-scale",
                options=[{"label": scale, "value": scale} for scale in px.colors.named_colorscales()],
                value="Viridis",
                clearable=False,
                className="mb-3"
            ),
            dcc.Graph(id="bubble-map", style={"height": "550px"})
        ],
        fluid=True
    )
    return layout


@app.callback(
    Output("bubble-map", "figure"),
    [Input("bubble-color-scale", "value")]
)
def update_bubble_map(chosen_scale):
    latest_year = df["Year"].max()
    dff_latest = df[df["Year"] == latest_year].rename(columns={"Country Code": "iso_alpha"})

    fig = px.scatter_geo(
        dff_latest,
        locations="iso_alpha",
        size="Internet Usage (%)",
        color="Internet Usage (%)",
        hover_name="Country Name",
        color_continuous_scale=chosen_scale,
        projection="natural earth",
        title=f"Bubble Map of Internet Usage in {int(latest_year)}"
    )
    fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0}, transition_duration=500)
    return fig


# ------------------------------------------------------------------------------
# 5. FOOTER
# ------------------------------------------------------------------------------
footer = dbc.Container(
    [
        html.Hr(),
        dbc.Row(
            dbc.Col(
                html.P(
                    "© 2025 Global Internet Usage Dashboard",
                    className="text-center text-muted"
                ),
                md=12
            )
        )
    ],
    fluid=True
)

# ------------------------------------------------------------------------------
# 6. APP LAYOUT (MULTI-PAGE)
# ------------------------------------------------------------------------------
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        navbar,
        html.Div(id="page-content", className="mb-5"),
        footer
    ]
)


# ------------------------------------------------------------------------------
# 7. ROUTING CALLBACK
# ------------------------------------------------------------------------------
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
    else:
        # Default is Home
        return home_page()


# ------------------------------------------------------------------------------
# 8. MAIN BLOCK
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=False)