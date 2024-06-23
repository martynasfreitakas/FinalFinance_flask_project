from bs4 import BeautifulSoup
import pandas as pd

path_to_file = 'sec-edgar-filings/0000089043/NPORT-P/0001752724-24-037604/full-submission.txt'

with open(path_to_file, 'r') as file:
    data = file.read()

soup = BeautifulSoup(data, 'lxml')

invstOrSec_tags = soup.find_all('invstorsec')

data_list = []

for tag in invstOrSec_tags:
    name = tag.find('name').text if tag.find('name') else None
    lei = tag.find('lei').text if tag.find('lei') else None
    title = tag.find('title').text if tag.find('title') else None
    cusip = tag.find('cusip').text if tag.find('cusip') else None
    isin = tag.find('isin').text if tag.find('isin') else None
    ticker = tag.find('ticker').text if tag.find('ticker') else None
    balance = tag.find('balance').text if tag.find('balance') else None
    units = tag.find('units').text if tag.find('units') else None
    curCd = tag.find('curcd').text if tag.find('curcd') else None
    valUSD = tag.find('valusd').text if tag.find('valusd') else None
    pctVal = tag.find('pctval').text if tag.find('pctval') else None
    payoffProfile = tag.find('payoffprofile').text if tag.find('payoffprofile') else None
    assetCat = tag.find('assetcat').text if tag.find('assetcat') else None
    issuerCat = tag.find('issuercat').text if tag.find('issuercat') else None
    invCountry = tag.find('invcountry').text if tag.find('invcountry') else None

    owner_cik = soup.find('regcik').text if soup.find('regcik') else None

    data_dict = {
        'Name': name,
        'LEI': lei,
        'Title': title,
        'CUSIP': cusip,
        'ISIN': isin,
        'Ticker': ticker,
        'Balance': balance,
        'Units': units,
        'Currency': curCd,
        'Value (USD)': valUSD,
        '% of Portfolio Value': pctVal,
        'Payoff Profile': payoffProfile,
        'Asset Category': assetCat,
        'Issuer Category': issuerCat,
        'Investment Country': invCountry,
        'Assets owner CIK': owner_cik
    }

    data_list.append(data_dict)

df = pd.DataFrame(data_list)

# pandas display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', None)

print(df)