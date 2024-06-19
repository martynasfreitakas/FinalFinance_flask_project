from bs4 import BeautifulSoup
import pandas as pd

path_to_file = 'sec-edgar-filings/0001520738/NPORT-P/0001145549-24-012816/full-submission.txt'

with open(path_to_file, 'r') as file:
    data = file.read()

soup = BeautifulSoup(data, 'lxml')

# find all 'invstOrSec' tags
invstOrSec_tags = soup.find_all('invstorsec')

data_list = []

for tag in invstOrSec_tags:
    data_dict = {
        'name': tag.find('name').text if tag.find('name') else None,
        'lei': tag.find('lei').text if tag.find('lei') else None,
        'title': tag.find('title').text if tag.find('title') else None,
        'cusip': tag.find('cusip').text if tag.find('cusip') else None,
        'isin': tag.find('isin')['value'] if tag.find('isin') else None,
        'ticker': tag.find('ticker')['value'] if tag.find('ticker') else None,
        'balance': float(tag.find('balance').text) if tag.find('balance') else None,
        'units': tag.find('units').text if tag.find('units') else None,
        'curCd': tag.find('curcd').text if tag.find('curcd') else None,
        'valUSD': float(tag.find('valusd').text) if tag.find('valusd') else None,
        'pctVal': float(tag.find('pctval').text) if tag.find('pctval') else None,
        'payoffProfile': tag.find('payoffprofile').text if tag.find('payoffprofile') else None,
        'assetCat': tag.find('assetcat').text if tag.find('assetcat') else None,
        'issuerCat': tag.find('issuercat').text if tag.find('issuercat') else None,
        'invCountry': tag.find('invcountry').text if tag.find('invcountry') else None,
        'isRestrictedSec': tag.find('isrestrictedsec').text if tag.find('isrestrictedsec') else None
    }
    data_list.append(data_dict)

# convert list of dictionaries to a DataFrame
df = pd.DataFrame(data_list)

# pandas display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', None)

print(df)
