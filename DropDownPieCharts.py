import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

# Spreadsheet URL
sheet_id = '1HjK2Qz95uCqtFoOmcRjbbRAfCgp6I6t9iwOmDFnnNt8'
df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv")

# Number of "Mask Please" signs in the database
num_of_signs = str(len(df))

# for counting cells instead of adding Amount Column
amount = [1 for i in range(len(df))]

# you need to include __name__ in your Dash constructor if
# you plan to use a custom CSS or JavaScript in your Dash apps
app = dash.Dash(__name__)

# ---------------------------------------------------------------
app.layout = html.Div([
    html.Div([
        html.Label(['Masks Please - Filters']),
        dcc.Dropdown(
            id='my_dropdown',
            options=[
                {'label': 'Gender', 'value': 'Gender'},
                {'label': 'Number', 'value': 'Number'},
                {'label': 'Tense', 'value': 'Tense'},
                {'label': 'Position', 'value': 'Position'}
            ],
            value='Gender',  # default
            multi=False,
            clearable=False,
            # style={"width": "50%"}
        ),
    ]),

    html.Div([
        dcc.Graph(id='the_graph')
    ]),

])


# ---------------------------------------------------------------


@app.callback(
    Output(component_id='the_graph', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')]
)
def update_graph(my_dropdown):
    # copying the datafile
    dff = df
    title = ""
    if my_dropdown == "Gender":
        title = 'מין הפנייה בשלטים'
    elif my_dropdown == "Number":
        title = 'ריבוי הפנייה בשלטים'
    elif my_dropdown == "Tense":
        title = 'פנייה בציווי או בבקשה בשלטים'
    elif my_dropdown == "Position":
        title = 'בקשה על דרך החיוב או השלילה בשלטים'
    pie_chart = px.pie(
        data_frame=dff,
        values=amount,
        names=my_dropdown,
        color=my_dropdown,
        # color_discrete_map={"male":"blue","female":"red","none":"yellow","both":"green"},
        # hover_data='plural' #adding extra data
        # labels={"gender": "Gender", "type": "Amount"},
        template='presentation',
        title=title
    )
    # Adding a label with the amount of masks signs in the database
    pie_chart.update_layout(dict(annotations=[{'x': 0.5, 'y': -0.2,
                                               'text': 'Total Amount of mask signs:  ' + num_of_signs,
                                               'font': {'color': 'rgb(0, 0, 0)', 'size': 15},
                                               'showarrow': False, 'xanchor': 'center'}]))

    return pie_chart

# if __name__ == '__main__':
#     app.run_server(debug=True)
