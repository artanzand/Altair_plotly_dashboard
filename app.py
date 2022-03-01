import pandas as pd
import altair as alt
from dash import Dash, html, dcc, Input, Output

# Import and clean data
df = pd.read_csv("cleaned_salaries.csv")


def plot_altair(DS_identity=['Yes', 'No', 'Sort of (Explain more)'], df=df.copy()):
    # Clean data
    df = df.dropna()
    df = df.query("Salary_USD < 400_000")
    df = df[df["Tenure"] != "I don't write code to analyze data"]
    
    # Filter data
    if DS_identity == None:
        DS_identity = ['Yes', 'No', 'Sort of (Explain more)']
    if not isinstance(DS_identity, list):
        DS_identity = list(DS_identity)
    df = df[df['DataScienceIdentitySelect'].isin(DS_identity)]

    # Create Plot
    alt.themes.enable("dark")

    brush = alt.selection_interval()
    click = alt.selection_multi(fields=["Tenure"])

    points = (
        alt.Chart(df, title="Select a window for interactive coding experience count")
        .mark_circle()
        .encode(
            y=alt.Y("Country", title=None),
            x=alt.X("Salary_USD", title="Salary in USD"),
            color=alt.condition(
                brush,
                alt.Color("Tenure:N", legend=None),
                alt.value("lightgray"),
            ),
            opacity=alt.condition(click, alt.value(1.0), alt.value(0.1)),
            tooltip="EmployerIndustry",
        )
        .add_selection(brush)
    )

    bars = (
        alt.Chart(df, title="Click to filter the above plot!")
        .mark_bar()
        .encode(
            x="count()",
            y=alt.Y("Tenure", title="Coding Experience", sort=['More than 10 years', '6 to 10 years', '3 to 5 years', '1 to 2 years', 'Less than a year']),
            color="Tenure",
            opacity=alt.condition(click, alt.value(0.9), alt.value(0.2)),
        )
    ).transform_filter(brush)

    overall_plot = (points & bars).add_selection(click)
    
    return overall_plot.to_html()


# def plot_altair(year=["2020", "2021e"], df=df.copy()):
#     # Filter data
#     if year == None:
#         year = ["2020", "2021e"]
#     if not isinstance(year, list):
#         year = list(year)
#     df = df[df["work_year"].isin(year)]

#     # Create Plot
#     # alt.themes.enable("dark")

#     brush = alt.selection_interval()
#     click = alt.selection_multi(fields=["remote_ratio"])

#     points = (
#         alt.Chart(df, title="Select a window - Salary per Country")
#         .mark_circle()
#         .encode(
#             y=alt.Y("company_location", title="Country"),
#             x=alt.X("salary_in_usd", title="Salary in USD"),
#             color=alt.condition(
#                 brush,
#                 alt.Color("remote_ratio:N", legend=None),
#                 alt.value("lightgray"),
#             ),
#             opacity=alt.condition(click, alt.value(1.0), alt.value(0.1)),
#             tooltip="job_title",
#         )
#         .add_selection(brush)
#     )

#     bars = (
#         alt.Chart(df, title="Click on me!")
#         .mark_bar()
#         .encode(
#             x="count()",
#             y=alt.Y("remote_ratio", title="Remote Ratio", sort=["0%", "50%", "100%"]),
#             color="remote_ratio",
#             opacity=alt.condition(click, alt.value(0.9), alt.value(0.2)),
#         )
#     ).transform_filter(brush)

#     overall_plot = (points & bars).add_selection(click)

#     return overall_plot.to_html()


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
                "Are you a Data Scientist?",
                dcc.Dropdown(
                    id="data_scientist",
                    options=[
                        {"label": "Yes", "value": "Yes"},
                        {"label": "No", "value": "No"},
                        {"label": "Sort of", "value": 'Sort of (Explain more)'}
                    ],
                    value=['Yes', 'No', 'Sort of (Explain more)'],
                    multi=True,
                ),
            ]
        ),
        html.Iframe(
            id="scatter",
            srcDoc=plot_altair(DS_identity=['Yes', 'No', 'Sort of (Explain more)']),
            style={"border-width": "0", "width": "100%", "height": "1500px"},
        ),
    ]
)


@app.callback(Output("scatter", "srcDoc"), Input("data_scientist", "value"))
def update_output(DS_identity):
    return plot_altair(DS_identity)


if __name__ == "__main__":
    app.run_server(debug=True)
