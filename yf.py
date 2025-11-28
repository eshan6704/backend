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
    