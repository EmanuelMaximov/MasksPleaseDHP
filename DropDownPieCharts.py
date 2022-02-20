import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import GoogleAPI as ga
import webbrowser

# Spreadsheet Information
sheet_id = '1HjK2Qz95uCqtFoOmcRjbbRAfCgp6I6t9iwOmDFnnNt8'
df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv")
spreadsheet_tab_name = 'mask_please_metadata'
spreadsheet_tab_id = 263391688
spreadsheet_read_from_col = 'B'
spreadsheet_write_to_col = 'V'
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1HjK2Qz95uCqtFoOmcRjbbRAfCgp6I6t9iwOmDFnnNt8/edit#gid=' + str(
    spreadsheet_tab_id)

# Number of "Mask Please" signs in the database
num_of_signs = str(len(df))

# for counting cells instead of adding Amount Column
amount = [1 for i in range(len(df))]

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
    html.Div([
        # for opening new tab with the given URL
        dash.html.Div(id="open-link"),
    ]),
    html.Div([
        # dcc.Store stores the intermediate value to share mutual values
        dcc.Store(id='intermediate-value')
    ])

])


# ---------------------------------------------------------------

# CALLBACK for handling clicks on the graph
@app.callback(
    Output(component_id='open-link', component_property='children'),
    [Input(component_id='the_graph', component_property='clickData')],
    [Input(component_id='intermediate-value', component_property='data')]  # read from the store
)
def open_filtered_spreadsheet(clickData, data):
    if not clickData:
        raise dash.exceptions.PreventUpdate
    else:
        param = ((clickData['points'])[0])['label']
        col_name = data
        if param in {'female', 'male', 'none', 'both'} and col_name == 'Gender' \
                or param in {'plural', 'singular', 'none'} and col_name == 'Number' \
                or param in {'negative', 'positive'} and col_name == 'Position' \
                or param in {'imperative', 'not imperative'} and col_name == 'Tense':
            # filter the spreadsheet by GoogleApi
            column_number = 0
            if col_name == 'Gender':
                column_number = ord(spreadsheet_write_to_col) - ord('A')
            elif col_name == 'Number':
                column_number = ord(spreadsheet_write_to_col) - ord('A') + 1
            elif col_name == 'Tense':
                column_number = ord(spreadsheet_write_to_col) - ord('A') + 2
            elif col_name == 'Position':
                column_number = ord(spreadsheet_write_to_col) - ord('A') + 3
            ga.filter_spreadsheet(spreadsheet_tab_id, column_number, param)
            # open spreadsheet URL
            webbrowser.open_new(spreadsheet_url)


# ---------------------------------------------------------------
# CALLBACK for handling choosing values in the DropDown menu
@app.callback(
    Output(component_id='the_graph', component_property='figure'),
    Output(component_id='intermediate-value', component_property='data'),  # write into the store
    [Input(component_id='my_dropdown', component_property='value')]
)
def update_graph(my_dropdown):
    # copying the datafile
    dff = df
    # adjusting the title in Hebrew
    title = ""
    if my_dropdown == "Gender":
        title = 'מין הפנייה בשלטים'
    elif my_dropdown == "Number":
        title = 'ריבוי הפנייה בשלטים'
    elif my_dropdown == "Tense":
        title = 'פנייה בציווי או בבקשה בשלטים'
    elif my_dropdown == "Position":
        title = 'בקשה על דרך החיוב או השלילה בשלטים'

    # Making the Pie Chart
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

    # exporting html file for the chart in offline mode
    # pl.offline.plot(pie_chart, filename='file.html')
    return pie_chart, my_dropdown
