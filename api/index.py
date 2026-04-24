#######
# First Milestone Project: Develop a Stock Ticker
# dashboard that either allows the user to enter
# a ticker symbol into an input box, or to select
# item(s) from a dropdown list, and uses pandas_datareader
# to look up and display stock data on a graph.
######

# EXPAND STOCK SYMBOL INPUT TO PERMIT MULTIPLE STOCK SELECTION
import dash
from dash import dcc
from dash import html
from dash import Input, Output, State
#import pandas_datareader.data as web # requires v0.6.0 or later
from plotly.figure_factory import create_ohlc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import pandas as pd
import yfinance as yf
from flask import Flask
from dash import Dash

server = Flask(__name__)

app = Dash(
    __name__,
    server=server,
    requests_pathname_prefix="/"
)

#app = dash.Dash()

nsdq = pd.read_csv("NASDAQcompanylist.csv")
nsdq.set_index('Symbol', inplace=True)
options = []
for tic in nsdq.index:
    options.append({'label':'{} {}'.format(tic,nsdq.loc[tic]['Name']), 'value':tic})

app.layout = html.Div([
    html.H1('NASDAQ Stock Ticker Dashboard',style={'paddingLeft':'600px', 'color': 'white'}),
    html.H2('Stock Closing Prices',style={'paddingLeft':'50px', 'color': 'white'}),
    html.Div([
        html.H3('Select stock symbols:', style={'paddingRight':'30px', 'color': 'white'}),
        dcc.Dropdown(
            id='my_ticker_symbol',
            options=options,
            value=['TSLA'],
            multi=True
        )
    ], style={'display':'inline-block', 'verticalAlign':'top', 'width':'30%'}),
    html.Div([
        html.H3('Select start and end dates:', style={'color': 'white'}),
        dcc.DatePickerRange(
            id='my_date_picker',
            min_date_allowed=datetime(2015, 1, 1),
            max_date_allowed=datetime.today(),
            start_date=datetime(2018, 1, 1),
            end_date=datetime.today()
        )
    ], style={'display':'inline-block'}),
    html.Div([
        html.Button(
            id='submit-button',
            n_clicks=0,
            children='Submit',
            style={'fontSize':24, 'marginLeft':'30px','background-color': '#007BFF', 'color': 'white'}
        ),
    ], style={'display':'inline-block'}),
    dcc.Graph(
        id='my_graph'
    ),

    html.H2('Open, High, Low, and Close Chart',style={'paddingLeft':'50px', 'color': 'white'}),
    html.Div([
        html.H3('Select stock symbols:', style={'paddingRight':'30px', 'color': 'white'}),
        dcc.Dropdown(
            id='my_ohlc_ticker_symbol',
            options=options,
            value=['TSLA'],
            multi=True
        )
    ], style={'display':'inline-block', 'verticalAlign':'top', 'width':'30%'}),
    html.Div([
        html.H3('Select start and end dates:', style={'color': 'white'}),
        dcc.DatePickerRange(
            id='my_ohlc_date_picker',
            min_date_allowed=datetime(2015, 1, 1),
            max_date_allowed=datetime.today(),
            start_date=datetime(2018, 1, 1),
            end_date=datetime.today()
        )
    ], style={'display':'inline-block'}),
    html.Div([
        html.Button(
            id='submit-ohlc-button',
            n_clicks=0,
            children='Submit',
            style={'fontSize':24, 'marginLeft':'30px','background-color': '#007BFF', 'color': 'white'}
        ),
    ], style={'display':'inline-block'}),
    dcc.Graph(
        id='my_ohlc_graph'
    )

], style={'backgroundColor': 'black'})



@app.callback(
    Output('my_graph', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_ticker_symbol', 'value'),
    State('my_date_picker', 'start_date'),
    State('my_date_picker', 'end_date')])
def update_graph(n_clicks, stock_ticker, start_date, end_date):
    start = pd.to_datetime(start_date[:10],format='%Y-%m-%d').date()
    end = pd.to_datetime(end_date[:10],format='%Y-%m-%d').date()
    traces = []
    for tic in stock_ticker:
        df = yf.download(tic, start= start, end= end)['Adj Close']
        df = pd.DataFrame(df)
        df.columns = ['Close']
        #df = web.get_data_yahoo(tic, start=start_date, end=end_date)
        #df = web.DataReader(tic,'iex',start,end)
        #traces.append({'x':df.index, 'y': df.Close, 'name':tic})

        traces.append(go.Scatter(
        x=df.index,  # Assuming df contains your data
        y=df.Close,  # Assuming df contains the price data for each ticker
        mode='lines',  # Line mode
        fill='tozeroy',  # Fills the area below the line to the x-axis
        name=f'{tic} Closing Price'  # Name of the stock ticker
    ))

    """ fig = {
        'data': traces,
        'layout': {'title':', '.join(stock_ticker)+' Closing Prices',
        'xaxis': {'title': 'Date'},  # Adding title for the x-axis
        'yaxis': {'title': 'Price'},  # Adding title for the y-axis
        'plot_bgcolor':'black',
        'showlegend': True,  # Optionally display the legend
        'hovermode': 'closest',  # For better hover interaction
        'template':'plotly_dark'
        }
    } """

    fig = go.Figure(
    data=traces,
    layout=go.Layout(
        title=', '.join(stock_ticker) + ' Closing Prices',
        xaxis={'title': 'Date'},  # Adding title for the x-axis
        yaxis={'title': 'Price'},  # Adding title for the y-axis
        showlegend=True,  # Optionally display the legend
        hovermode='closest',  # For better hover interaction
        template='plotly_dark'  # Applying the 'plotly_dark' template
    )
    )

    

    return fig

@app.callback(
    Output('my_ohlc_graph', 'figure'),
    [Input('submit-ohlc-button', 'n_clicks')],
    [State('my_ohlc_ticker_symbol', 'value'),
    State('my_ohlc_date_picker', 'start_date'),
    State('my_ohlc_date_picker', 'end_date')])
def update_ohlc_graph(n_clicks, stock_ticker, start_date, end_date):
    start = pd.to_datetime(start_date[:10],format='%Y-%m-%d').date()
    end = pd.to_datetime(end_date[:10],format='%Y-%m-%d').date()
    traces = []
    """ for tic in stock_ticker:
        df = yf.download(tic, start= start, end= end)[['Open','High', 'Low','Close']]
        df = pd.DataFrame(df)
        #df.columns = ['Close']
        #df = web.get_data_yahoo(tic, start=start_date, end=end_date)
        #df = web.DataReader(tic,'iex',start,end)
        traces.append({'x':df.index, 'y': df.Close, 'name':tic})
    fig = create_ohlc(df.iloc[:,0], df.iloc[:,1], df.iloc[:,2], df.iloc[:,3], dates=df.index)
 """
    # Create a figure with subplots
    fig = make_subplots(specs=[[{"secondary_y": False}]])  # One subplot
    for tic in stock_ticker:
        df = yf.download(tic, start= start, end= end)[['Open','High', 'Low','Close']]
        df = pd.DataFrame(df)

        data = {
        'Date': df.index,
        'Open': df['Open'],
        'High': df['High'],
        'Low': df['Low'],
        'Close': df['Close']}

        df1 = pd.DataFrame(data)

        

        # Adding the first OHLC trace
        fig.add_trace(go.Ohlc(
            x=df1['Date'],
            open=df1['Open'],
            high=df1['High'],
            low=df1['Low'],
            close=df1['Close'],
            name="{}".format(tic),
            increasing_line_color='green', 
            decreasing_line_color='red'
        ))



    """ fig.update_traces(marker=dict(
        size=12,
        line=dict(width=2)
    )) """
    
    fig.update_layout(
        title = ', '.join(stock_ticker)+' OHLC',
        template='plotly_dark',
        #plot_bgcolor='black',
        xaxis_title='Date',
        yaxis_title='Price',
        hovermode= 'closest'  # For better hover interaction
    )
    return fig

app = server

#if __name__ == '__main__':
    #app.run_server()


