from bs4 import BeautifulSoup
import pandas as pd

path_to_file = 'sec-edgar-filings/0000089043/NPORT-P/0001752724-24-037604/full-submission.txt'

with open(path_to_file, 'r') as file:
    data = file.read()

soup = BeautifulSoup(data, 'lxml')

owner_cik = soup.find('regcik').text if soup.find('regcik') else None
class_contract_name = soup.find('regname').text if soup.find('regname') else None
class_contract_ticker_symbol = soup.find('class-contract-ticker-symbol').text if (
    soup.find('class-contract-ticker-symbol')) else None
submissiontype = soup.find('submissiontype').text if soup.find('submissiontype') else None
reppdend = soup.find('reppdend').text if soup.find('reppdend') else None

data = {
    'CIK': [owner_cik],
    'COMPANY NAME': [class_contract_name],
    'TICKER': [class_contract_ticker_symbol],
    'SUBMISSION TYPE': [submissiontype],
    'FILING END PERIOD': [reppdend],
}

df = pd.DataFrame(data)

df.replace('\n','', regex=True, inplace=True)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', None)

print(df.to_string(index=False))

