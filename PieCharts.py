import plotly
import plotly.express as px
import pandas as pd


def main():
    sheet_id = '1HjK2Qz95uCqtFoOmcRjbbRAfCgp6I6t9iwOmDFnnNt8'
    df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv")
    num_of_signs = str(len(df))
    pie_chart = px.pie(
        data_frame=df,
        values='type',
        names='gender',
        color='gender',
        # color_discrete_map={"male":"blue","female":"red","none":"yellow","both":"green"},
        # hover_data='plural' #adding extra data
        labels={"gender": "Gender", "type": "Amount"},
        template='presentation',
        title='מין הפנייה'

    )
    pie_chart.update_layout(dict(annotations=[{'x': 0.5, 'y': 1.1,
                                               'text': 'Total Amount of mask signs: ' + num_of_signs,
                                               'font': {'color': 'rgb(0, 0, 0)', 'size': 14},
                                               'showarrow': False, 'xanchor': 'center'}]))
    plotly.offline.plot(pie_chart, filename='file.html')


if __name__ == '__main__':
    main()
