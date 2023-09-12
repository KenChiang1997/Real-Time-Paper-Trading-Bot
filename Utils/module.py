import numpy as np 
import pandas as pd 
import datetime as dt
import plotly.graph_objects as go
temp = dict(layout = go.Layout(font = dict(family="Franklin Gothic", size=12), width = 1500))


def transform_time(original_time):

    return dt.datetime.fromtimestamp(original_time / 1000).strftime("20%y-%m-%d %H:%M:%S")

def get_historical_price(client, symbol, interval, limit):

    candles = client.get_klines(symbol = symbol, interval = interval, limit = limit)
    df = pd.DataFrame(candles)
    df.columns = ['open_time','open','high','low','close','volume', 'close_time', 'quote asset volume', 'number of trade', 'take buy base asset volume', 'take buy quote asset volume', '']
    df['open_time'] = df.apply(lambda x: transform_time(x['open_time']), axis = 1)
    df['close_time'] = df.apply(lambda x: transform_time(x['close_time']), axis = 1)

    return df[['open_time','open','high','low','close','volume', 'close_time','number of trade']]

def generate_macd_variable(df, ema1, ema2):

    df["ema_12"] = df["close"].ewm(span = ema1).mean()
    df["ema_26"] = df["close"].ewm(span = ema2).mean()

    df["dif"] = df["ema_12"] - df["ema_26"]
    df["macd"] = df["dif"].ewm(span = 9).mean()
    df["barchart"] = df["dif"] - df["macd"]

    return df 

# Get P&L Result
def get_profit_and_lost(historical_trade_time, historical_trade_price):

    profit_and_loss_df = pd.DataFrame()
    trade_time_list  = []
    trade_profit_and_loss = []

    for i in range(0, len(historical_trade_time) -1, 2):

        buy_price = historical_trade_price[i]
        sell_price = historical_trade_price[i+1]
        profit_and_loss = (sell_price/buy_price) -1 

        trade_time_list.append(historical_trade_time[i+1])
        trade_profit_and_loss.append(profit_and_loss)

    profit_and_loss_df['Datetime'] = trade_time_list
    profit_and_loss_df['P&L'] = trade_profit_and_loss

    return profit_and_loss_df


def plot_macd_df(df, symbol):

    bgcolor = "#ECF2F6"  

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(x = df['open_time'], 
                y = df['close'], 
                name = symbol))

    fig.add_trace(
        go.Scatter(x = df['open_time'], 
                y = df['macd'], 
                name = 'macd',
                yaxis = "y2"))

    fig.add_trace(
        go.Scatter(x = df['open_time'], 
                y = df['dif'], 
                name = 'dif',
                yaxis = "y2"))

    fig.update_layout(template = temp,
                    title = dict(text = "\n Trading Asset: " + str(symbol), font = dict(size=20), y = 0.95),
                    hovermode = 'closest',
                    margin = dict(l = 75, r = 0, t = 20, b = 50),
                    height = 450, 
                    width = 700, 
                    showlegend = True,
                    xaxis = dict(tickfont = dict(size=20)),
                    yaxis = dict(side = "left", tickfont = dict(size=20)),
                    yaxis2 = dict(side = "right", overlaying = "y", tickfont = dict(size=20) ),
                    legend = dict(x = 0.01, y = 0.01, font = dict(size = 20), bgcolor = bgcolor, bordercolor = 'black', borderwidth = 1),

                    plot_bgcolor = bgcolor,
                    ) 
    return fig 

def plot_profit_and_loss(df):

    bgcolor = "#ECF2F6"  

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(x = df['Datetime'], 
                y = df['Cumulative P&L'], 
                name = "P&L"))

    fig.update_layout(template = temp,
                    title = dict(text = "Cumulative P&L", font = dict(size=20), y = 0.95),
                    hovermode = 'closest',
                    margin = dict(l = 75, r = 0, t = 20, b = 50),
                    height = 720, 
                    width = 1300, 
                    showlegend = True,
                    xaxis = dict(tickfont = dict(size=20)),
                    yaxis = dict(side = "left", tickfont = dict(size=20)),
                    yaxis2 = dict(side = "right", overlaying = "y", tickfont = dict(size=20) ),
                    legend = dict(x = 0.01, y = 0.01, font = dict(size = 20), bgcolor = bgcolor, bordercolor = 'black', borderwidth = 1),

                    plot_bgcolor = bgcolor)

    return fig 