import os
import typing
from dotenv import load_dotenv
import fmpsdk
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt

def income_statement (apikey, symbols):
    df_income = []
    for symbol in symbols:
        df_income = df_income + fmpsdk.income_statement(apikey=apikey, symbol=symbol)

    df_income = pd.DataFrame(df_income)

    df_income['date']= pd.to_datetime(df_income['date'])
    df_income.set_index(['symbol','date'],inplace=True)
    df_income.sort_values(by=['symbol','date'],inplace=True)
    return df_income

def balance_sheet (apikey, symbols):
    df_balance = []
    for symbol in symbols:
        df_balance = df_balance + fmpsdk.balance_sheet_statement(apikey=apikey, symbol=symbol)

    df_balance = pd.DataFrame(df_balance)

    df_balance['date']= pd.to_datetime(df_balance['date'])
    df_balance.set_index(['symbol','date'],inplace=True)
    df_balance.sort_values(by=['symbol','date'],inplace=True)
    return df_balance

def cashflow_statement (apikey, symbols):
    df_cashflow = []
    for symbol in symbols:
        df_cashflow = df_cashflow + fmpsdk.cash_flow_statement(apikey=apikey, symbol=symbol)

    df_cashflow = pd.DataFrame(df_cashflow)

    df_cashflow['date']= pd.to_datetime(df_cashflow['date'])
    df_cashflow.set_index(['symbol','date'],inplace=True)
    df_cashflow.sort_values(by=['symbol','date'],inplace=True)

    return df_cashflow

def keymetrics (apikey, symbols):
    df_keymetrics = []
    for symbol in symbols:
        df_keymetrics = df_keymetrics + fmpsdk.key_metrics(apikey=apikey, symbol=symbol)

    df_keymetrics = pd.DataFrame(df_keymetrics)

    df_keymetrics['date']= pd.to_datetime(df_keymetrics['date'])
    df_keymetrics.set_index(['symbol','date'],inplace=True)
    df_keymetrics.sort_values(by=['symbol','date'],inplace=True)
    return df_keymetrics

def moat_per_share (df_balance, df_income, df_cashflow):
    moat_columns = ["EV+Div","Earnings","Sales","Cash"]
    df_moat_perShare = pd.DataFrame(index=df_balance.index,columns=moat_columns)
    df_moat_perShare["Sales"]=df_income['revenue']/df_income['weightedAverageShsOutDil']
    df_moat_perShare["Earnings"]=df_income['netIncome']/df_income['weightedAverageShsOutDil']
    df_moat_perShare["EV+Div"]=(df_balance['totalStockholdersEquity']
                                +df_cashflow['dividendsPaid'].fillna(0))/df_income['weightedAverageShsOutDil']
    df_moat_perShare["Cash"]=(df_cashflow['operatingCashFlow'])/df_income['weightedAverageShsOutDil']
    df_moat_perShare.sort_values(by=['symbol','date'],inplace=True)
    return df_moat_perShare

def growth_rates (df):
    symbols = df.reset_index()['symbol'].unique().tolist()
    time_periods = ['10 year', '5 year', '2 year']
    index=pd.MultiIndex.from_product([symbols,time_periods],names=['symbol','timeframe'])
    df_gr = pd.DataFrame(index=index, columns = df.columns)
    df_pct_chg = df.groupby('symbol').pct_change()
    for col in df.columns:
        for symbol in symbols:
            df_gr.loc[symbol,'2 year'][col] = df_pct_chg[col].loc[symbol].iloc[-2:-1].median()
            df_gr.loc[symbol,'5 year'][col] = df_pct_chg[col].loc[symbol].iloc[-5:-1].median()
            df_gr.loc[symbol,'10 year'][col] = df_pct_chg[col].loc[symbol].iloc[-10:-1].median()
    return df_gr