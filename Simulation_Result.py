import time 
import numpy as np 
import pandas as pd 
import datetime as dt
from binance.client import Client
from Utils.module import get_historical_price, generate_macd_variable, get_profit_and_lost
from Utils.module import plot_macd_df, plot_profit_and_loss

import dash
import plotly.graph_objects as go
from dash import Dash, html, dash_table, dcc, Input, Output


# ----------- Binance API Setting ----------- 

api = pd.read_excel(r"./Trading Bot/Binance_API.xlsx")
api_key = api['api_key'].values[0]
api_secret = api['api_secret'].values[0]
client = Client(api_key = api_key, api_secret = api_secret)

# ----------- Hyper Trading Parameters ----------- 

ema1 = 3 
ema2 = 5
position = 0
limit = 100
trading_asset_list = ['BTCUSDT','ETHUSDT', 'BNBUSDT']
interval = Client.KLINE_INTERVAL_1MINUTE

historical_trade_time = []
historical_trade_type = []
historical_trade_asset = []
historical_trade_price = []
trade_detail_df = pd.DataFrame()
signal_df = pd.DataFrame()

# ---------------------------------------------------



app = Dash(__name__, external_stylesheets=['custom_styles.css'])


body_style = {
    'margin': '0'  # This removes the margin
}

app.layout = html.Div([

    html.Div([

        # Heder Setting
        html.Div([html.H1(children = "King's Hedge Fund Society Project - Trading Bot Simulation Result ", 
                          style={'textAlign': 'center', 'font-size': '30px', 'text-align': 'left', 'font-family': 'Roboto'}), 
                  
                  html.Div([html.H1(children = "By - Ken Chiang,  Please Select Trading Asset: ", 
                                    style={'textAlign': 'center', 'font-size': '20px', 'text-align': 'left'}), 
                            dcc.Dropdown(   trading_asset_list,
                                            id = 'coin_selection',
                                            value = 'BTCUSDT',
                                            style = {'width': '200px', 
                                                    'margin-left': '10px',
                                                    'margin-top': '5px'}),
                            ], style = {'display': 'flex', 'flexDirection': 'rows', 'gap': '10px'} ),

                  html.A(id = 'gh-link', 
                         children = ['View on GitHub'], 
                         href = "https://github.com/KenChiang1997/Real-Time-Paper-Trading-Bot", 
                         style = {'color': 'white', 
                                  'font-size': '15px', 
                                  'color': '#fff', 
                                  'border': 'solid 1px #fff',
                                  'border-radius': '2px', 
                                  'padding': '0px', 
                                  'padding-top': '0px', 
                                  'padding-left': '15px', 
                                  'padding-right': '15px', 
                                  'font-weight': '200', 
                                  'position': 'relative', 
                                  'top': '0px', 
                                  'float': 'right', 
                                  'margin-right': '40px', 
                                  'margin-left': '5px', 
                                  'transition-duration': '400ms',}), 

                  html.Div(className = "div-logo",
                           children = html.Img(className="logo", src=("https://opendatabim.io/wp-content/uploads/2021/12/GitHub-Mark-Light-64px-1.png"), 
                           style = {'height': '60px','padding': '30px', 'margin-top': '-50px'}), style={'display': 'inline-block', 'float': 'right'}),
                ], style = {"background": "#2c5c97", 
                            "color": "white", 
                            "padding-top": "30px", 
                            "padding-left": "48px", 
                            "padding-bottom": "50px", 
                            "padding-left": "24px",}),

        # Real Time Graph and Table Data
        html.Div(children = [html.P(children = "1.) Select asset and abstract real time data from Binance - API", id = 'output-data-upload', 
                                    style = {'font-size': '25 px', 
                                             'width': '50%', 
                                             'border-radius': '20px', 
                                             'text-align': 'left', 
                                             "padding-left": "20px", 
                                             'font-family' : 'Roboto', 
                                             "margin-left" : "20px", 
                                             "margin-up" : "-120px", 
                                             'background' : 'rgb(233 238 246)'}),

                            html.Div(children = [ dcc.Graph(id = "real_time_chart", animate=True),
                                                  dash_table.DataTable(id = 'table',
                                                                        style_cell = {'textAlign': 'right'},
                                                                        style_cell_conditional = [{'if': {'column_id': 'open_time'},'textAlign': 'left'}],
                                                                        style_header = {'backgroundColor': '#2c5c97', 'fontWeight': 'bold', 'color':'#D1D9DB', 'font-size': '20px', 'textAlign': 'center'},
                                                                        style_data = {'backgroundColor': 'White', "whiteSpace": 'auto', "height":"auto", 'textAlign': 'center', 'font-size': '15px'},
                                                                          style_table = {'height': '400px', 'width': '650px', 'overflowY': 'auto', 'margin-top': '20px'},
                                                                        page_size = 15,),
                                                  dcc.Interval(id = "interval" , interval = 4000),
                                                ], style = {'display': 'flex', 'flexDirection': 'row', 'gap': '35px'}, )
                 ]),
        
        html.Div(children = [html.P(children = "2.) Simulation Trading Result and P&L", 
                                    id = 'output-data-upload', 
                                    style = {'font-size': '25 px', 
                                             'width': '50%', 
                                             'border-radius': '20px', 
                                             'text-align': 'left', 
                                             "padding-left": "20px", 
                                             'font-family' : 'Roboto', 
                                             "margin-left" : "20px", 
                                             "margin-up" : "-120px", 
                                             'background' : 'rgb(233 238 246)'}),
                                
                            html.Div(children = [dash_table.DataTable(id = 'trade_detail', 
                                                                      style_cell = {'textAlign': 'right'},
                                                                      style_cell_conditional = [{'if': {'column_id': 'open_time'},'textAlign': 'left'}],
                                                                      style_header = {'backgroundColor': '#2c5c97', 'fontWeight': 'bold', 'color':'#D1D9DB', 'font-size': '25px', 'textAlign': 'center'},
                                                                      style_data = {'backgroundColor': 'White', "whiteSpace": 'auto', "height":"auto", 'textAlign': 'center', 'font-size': '20px'},
                                                                      style_table = {'height': '900px', 'width': '1300px', 'overflowY': 'auto', 'margin-top': '10px', 'margin-left' : '20px'},
                                                                      page_size = 20,),
                                                    
                            ], style = {'display': 'flex', 'flexDirection': 'columns', 'gap': '150px'})
                ])
            ])
    ]) 



@app.callback(
    Output("real_time_chart", "figure"),
    Input("interval", "n_intervals"),
    Input("coin_selection", "value"),
)
def update_figure(n_intervals, symbol):

    global signal_df
    global asset_price_df
    global ema1
    global ema2

    asset_price_df = get_historical_price(client, symbol, interval, limit)
    signal_df = generate_macd_variable(asset_price_df, ema1 = ema1, ema2 = ema2)
    asset_price_figure = plot_macd_df(signal_df, symbol)


    return asset_price_figure 

@app.callback(
        dash.dependencies.Output('table', 'data'),
        [dash.dependencies.Input('interval', 'n_intervals')])
def update_signal_dataframe(n_intervals):

    global signal_df

    signal_df[['close', 'volume', 'dif', 'macd']] = signal_df[['close', 'volume', 'dif', 'macd']].astype(float).round(decimals = 2)
    signal_df = signal_df[['open_time', 'close', 'volume', 'dif', 'macd']]
    signal_df.columns = ['Datetime', 'PX_LAST', 'Volume', 'DIFF', 'MACD']

    return signal_df.tail(30).iloc[::-1].to_dict('records')



@app.callback(
        dash.dependencies.Output('trade_detail', 'data'),
        [dash.dependencies.Input('interval', 'n_intervals'),
         dash.dependencies.Input("coin_selection", "value")])
def update_trade(n_intervals, symbol):

    global position
    global signal_df
    global trade_detail_df
    
    global historical_trade_time
    global historical_trade_type
    global historical_trade_asset
    global historical_trade_price
    
    row_data = signal_df.iloc[-1]
    trade_time = row_data['Datetime']
    px_last = float(row_data['PX_LAST'])
    macd = row_data['MACD']
    dif = row_data['DIFF']


    # print(trade_time, px_last, macd, dif, position)

    if (dif > macd) and (position == 0):
        trade_type = 'Buy'
        position = 1

        historical_trade_type.append(trade_type)
        historical_trade_asset.append(symbol)
        historical_trade_time.append(trade_time)
        historical_trade_price.append(px_last)

        print("Buy Now!!!!!")

    elif (dif < macd) and (position == 1):
        trade_type = 'Sell'
        position = 0

        historical_trade_type.append(trade_type)
        historical_trade_asset.append(symbol)
        historical_trade_time.append(trade_time)
        historical_trade_price.append(px_last)

        print("Sell Now!!!!!")

    
    trade_detail_df = pd.DataFrame()
    trade_detail_df['Datetime'] = historical_trade_time
    trade_detail_df['Asset'] = historical_trade_asset
    trade_detail_df['Type'] = historical_trade_type
    trade_detail_df['PX_LAST'] = historical_trade_price


    profit_and_loss_df = get_profit_and_lost(historical_trade_time, historical_trade_price)
    trade_detail_df = pd.merge(trade_detail_df, profit_and_loss_df, right_on = "Datetime", left_on = "Datetime", how = 'left')
    trade_detail_df['Cumulative P&L'] = trade_detail_df['P&L'].fillna(value = 0).cumsum()

    trade_detail_df[['P&L', 'Cumulative P&L']] = trade_detail_df[['P&L', 'Cumulative P&L']] * 100
    trade_detail_df[['P&L', 'Cumulative P&L']] = trade_detail_df[['P&L', 'Cumulative P&L']].round(decimals = 4)


    return trade_detail_df.to_dict('records')


@app.callback(
    Output("coin_selection", "children"),  # Use the dropdown itself as the output
    Input("coin_selection", "value")
)
def reset_trade_detail(value):

    global historical_trade_time
    global historical_trade_type
    global historical_trade_asset
    global historical_trade_price

    global trade_detail_df
    global position

    historical_trade_time = []
    historical_trade_type = []
    historical_trade_asset = []
    historical_trade_price = []

    position = 0
    trade_detail_df = pd.DataFrame()
    trade_detail_df['Datetime'] = historical_trade_time
    trade_detail_df['Asset'] = historical_trade_asset
    trade_detail_df['Type'] = historical_trade_type
    trade_detail_df['PX_LAST'] = historical_trade_price

    print("--------- Reset All Feature ----------")
    print("Reset Position: ", position)
    print(trade_detail_df)
    print("--------------------------------------")


    return value 



if __name__ == '__main__':
    app.run_server(debug=True)