# qresult.py
import yfinance as yf
import pandas as pd

def info(symbol):
        yf_symbol = symbol + ".NS"
        tk = yf.Ticker(yf_symbol)
        return tk

def qresult(symbol):
    yfsymbol = symbol + ".NS"
    ticker = yf.Ticker(yfsymbol)
    df = ticker.quarterly_financials
    return df
    
def result(symbol):
    yfsymbol = symbol + ".NS"
    ticker = yf.Ticker(yfsymbol)
    df = ticker.financials
    return df
    
def balance(symbol):
    yfsymbol = symbol + ".NS"
    ticker = yf.Ticker(yfsymbol)
    df = ticker.balance_sheet
    return df
    
def cashflow(symbol):
    yfsymbol = symbol + ".NS"
    ticker = yf.Ticker(yfsymbol)
    df = ticker.cashflow
    return df
    
def dividend(symbol):        
    ticker = yf.Ticker(yfsymbol)
    df = ticker.dividends.to_frame('Dividend')
    return df