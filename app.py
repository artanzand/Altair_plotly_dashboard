import pandas as pd
import altair as alt
from dash import Dash, html, dcc, Input, Output

# Import and clean data
df = pd.read_csv("Data Science Jobs Salaries.csv")
df["remote_ratio"] = df["remote_ratio"].apply(lambda x: str(x) + "%")


def plot_altair(year=["2020", "2021e"], df=df.copy()):
    # Filter data
    if year == None:
        year = ["2020", "2021e"]
    if not isinstance(year, list):
        year = list(year)
    df = df[df["work_year"].isin(year)]

    # Create Plot
    alt.themes.enable("dark")

    brush = alt.selection_interval()
    click = alt.selection_multi(fields=["remote_ratio"])

    points = (
        alt.Chart(df, title="Select a window - Salary per Country")
        .mark_circle()
        .encode(
            x=alt.X("company_location", title="Country"),
            y=alt.Y("salary_in_usd", title="Salary in USD"),
            color=alt.condition(
                brush,
                alt.Color("remote_ratio:N", legend=None),
                alt.value("lightgray"),
            ),
            opacity=alt.condition(click, alt.value(1.0), alt.value(0.1)),
            tooltip="job_title",
        )
        .add_selection(brush)
    )

    bars = (
        alt.Chart(df, title="Click on me!")
        .mark_bar()
        .encode(
            y="count()",
            x=alt.X("remote_ratio", title="Remote Ratio", sort=["0%", "50%", "100%"]),
            color="remote_ratio",
            opacity=alt.condition(click, alt.value(0.9), alt.value(0.2)),
        )
    ).transform_filter(brush)

    overall_plot = (points | bars).add_selection(click)

    return overall_plot.to_html()


# dash app
app = Dash(
    __name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]
)
# To run on server
server = app.server

app.layout = html.Div(
    [
        html.Br(),
        html.Div("Data Science Salaries", style={"color": "blue", "fontSize": 26}),
        html.P(
            "Altair Dashboard", id="my-para", style={"background-color": "lightgray"}
        ),
        html.Div(
            [
                "Year",
                dcc.Dropdown(
                    id="work_year",
                    options=[
                        {"label": "2020", "value": "2020"},
                        {"label": "2021", "value": "2021e"},
                    ],
                    value=["2020", "2021"],
                    multi=True,
                ),
            ]
        ),
        html.Iframe(
            id="scatter",
            srcDoc=plot_altair(year=["2020", "2021e"]),
            style={"border-width": "0", "width": "100%", "height": "600px"},
        ),
    ]
)


@app.callback(Output("scatter", "srcDoc"), Input("work_year", "value"))
def update_output(year):
    return plot_altair(year)


if __name__ == "__main__":
    app.run_server(debug=True)
