import numpy as np 
import pandas as pd

def Annual_Return(Daily_Returns):
    
    return np.mean(Daily_Returns) * 252

def Annual_Volatility(Daily_Returns):

    return np.std(Daily_Returns) * np.sqrt(252)

def Cumulative_Return(Daily_Returns):

    return np.cumsum(Daily_Returns)[-1]

def Sharpe_Ratio(Daily_Returns):

    u = np.mean(Daily_Returns) * 252
    sigma = np.std(Daily_Returns) * np.sqrt(252)

    sharpe_ratio = u/sigma

    return sharpe_ratio
        
def Maximum_drawdown(Daily_Returns):

    max_drawdown = max(pd.Series(np.cumsum(Daily_Returns)).cummax().values - np.cumsum(Daily_Returns))
    
    return max_drawdown

def Calmar_Ratio(Daily_Returns):

    u = np.mean(Daily_Returns) * 252
    max_drawdown = max(pd.Series(np.cumsum(Daily_Returns)).cummax().values - np.cumsum(Daily_Returns))

    Calmar_Ratio = u/max_drawdown

    return Calmar_Ratio



def BackTest_Summary_DF(Daily_Returns, Date_Index,labels):
    """
    
    """
    start_date = str(Date_Index[0])
    end_date = str(Date_Index[-1])

    Summary_DF = pd.DataFrame({

        "Start Date" : [start_date], 
        "End Date": [end_date], 
        "-" : ["-"],
        "Annual Return" : [Annual_Return(Daily_Returns)], 
        "Cumulative Return" : [Cumulative_Return(Daily_Returns)],
        "Annual Volatility" : [Annual_Volatility(Daily_Returns)], 
        "Sharpe_Ratio" : [Sharpe_Ratio(Daily_Returns)], 
        "Maximum_drawdown" : [Maximum_drawdown(Daily_Returns)], 
        "Calmar_Ratio" : [Calmar_Ratio(Daily_Returns)], 
    })

    Summary_DF.index = [labels]

    return Summary_DF.T