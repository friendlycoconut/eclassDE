# -*- coding: utf-8 -*-

# 1.0 Imports
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from tabulate import tabulate
import json
import dash_bootstrap_components as dbc


def parse_json_data(node):
    # Initialize lists to store extracted data
    names = []
    levels = []
    ids = []
    counts = []
    sumGrossAmountValues = []
    sumNetAmountValues = []
    sumTotalPriceValues = []

    # Extract data from the current node
    names.append(node.get("name"))
    levels.append(node.get("level"))
    ids.append(node.get("id"))
    counts.append(node.get("count"))
    sumGrossAmountValues.append(node.get("sumGrossAmountValue"))
    sumNetAmountValues.append(node.get("sumNetAmountValue"))
    sumTotalPriceValues.append(node.get("sumTotalPriceValue"))

    # Recursively process children nodes
    if "children" in node:
        for child in node["children"]:
            (
                child_names,
                child_levels,
                child_ids,
                child_counts,
                child_sumGrossAmountValues,
                child_sumNetAmountValues,
                child_sumTotalPriceValues,
            ) = parse_json_data(child)

            names.extend(child_names)
            levels.extend(child_levels)
            ids.extend(child_ids)
            counts.extend(child_counts)
            sumGrossAmountValues.extend(child_sumGrossAmountValues)
            sumNetAmountValues.extend(child_sumNetAmountValues)
            sumTotalPriceValues.extend(child_sumTotalPriceValues)

    return (
        names,
        levels,
        ids,
        counts,
        sumGrossAmountValues,
        sumNetAmountValues,
        sumTotalPriceValues,
    )

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# 1.1 Read in data
with open("data.json") as data_file:
    data = json.load(data_file)

# 1.2 create normalization - TODO make pretify and refactor
df_1 = pd.json_normalize(data, record_path=["children"], errors="ignore")

df_2 = pd.json_normalize(data, record_path=["children", "children"], errors="ignore")

df_3 = pd.json_normalize(
    data, record_path=["children", "children", "children"], errors="ignore"
)

df_4 = pd.json_normalize(
    data, record_path=["children", "children", "children", "children"], errors="ignore"
)

# 1.3 Merging the df - TODO make optimization
df_1 = df_1.merge(df_2, on=["classHierarchy.eclass_1"])
df_2 = df_2.merge(df_3, on=["classHierarchy.eclass_2"])
df_3 = df_3.merge(df_4, on=["classHierarchy.eclass_3"])

pdList = [df_1, df_2, df_3, df_4]
concat_df = pd.concat(pdList)

# 1.4 make figure
fig = px.treemap(
    df_1,
    template="plotly_dark",
    path=[
        px.Constant("all"),
        "classHierarchy.eclass_1_name_x",
        "classHierarchy.eclass_2_name_y",
        "classHierarchy.eclass_3_name_y",
        "classHierarchy.eclass_4_name_y",
    ],
    values="sumTotalPriceValue_x",
    hover_data=["sumTotalPriceValue_y"],
    color="name_x",
)

fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))

# 2.1 - Making layout
app.layout = [
    html.H1(
        children="__Test nested JSON parser with Plotly treemap__",
        style={"textAlign": "center"},
    ),
    dcc.Graph(id="graph-content", figure=fig),
]

if __name__ == "__main__":
    app.run(debug=True)
