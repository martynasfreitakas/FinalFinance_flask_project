from models import CompanyData
from app import app
from bs4 import BeautifulSoup
import pandas as pd
from sec_edgar_downloader import Downloader
from datetime import datetime
import os
from dotenv import load_dotenv
import requests
from database import db, my_db
from flask import Flask

load_dotenv()


def show_edgar_cik_all_companies():
    with app.app_context():
        cik_all_list = CompanyData.query.all()
        for cik in cik_all_list:
            return cik.company_name, cik.cik


def extracting_company_info_from_submision_txt():
    path_to_file = 'sec-edgar-filings/0000089043/NPORT-P/0001752724-24-037604/full-submission.txt'

    with open(path_to_file, 'r') as file:
        data = file.read()

    soup = BeautifulSoup(data, 'lxml')

    invstorsec_tags = soup.find_all('invstorsec')

    data_list = []

    for tag in invstorsec_tags:
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


def parsing_submission_from_edgar():
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

    df.replace('\n', '', regex=True, inplace=True)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', None)

    print(df.to_string(index=False))


def edgar_downloader_from_sec():
    # Brookfield Investment Funds
    filing_type = 'NPORT-P'
    filing_cik = '0001520738'

    # BERKSHIRE HATHAWAY INC
    # filing_type = '13F-HR'
    # filing_cik = '0001067983'

    # time period
    start_date = datetime(2019, 1, 1)
    end_date = datetime(2024, 5, 5)

    dir_path = 'sec-edgar-filings'

    # path to the downloaded filings
    filings_path = os.path.join(dir_path, filing_cik, filing_type)

    if os.path.exists(filings_path):
        print(f"Directory exists: {filings_path}")
    else:
        os.makedirs(filings_path)
        print(f"Directory does not exist: {filings_path}. Created directory and downloading filings.")
        dl = Downloader(dir_path, os.environ['EMAIL_FOR_AUTHORIZATION'])

        # download the filings
        dl.get(filing_type, filing_cik, after=start_date, before=end_date)

    # Checking if the directory with the downloaded filings exists
    if os.path.exists(filings_path):
        filings = os.listdir(filings_path)
        filing_count = len(filings)
        print(f"Total number of filings downloaded: {filing_count}")
    else:
        print(f"The directory with the downloaded filings does not exist: {filings_path}")


def download_and_store_all_companies_names_and_cik_from_edgar():
    url = "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"

    headers = {"User-Agent": os.environ['EMAIL_FOR_AUTHORIZATION']}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        data = soup.prettify().splitlines()
        data = [(company_name, cik.rstrip(':')) for company_name, cik in
                (line.split(":", 1) for line in data if ":" in line)]
        with app.app_context():
            for company_name, cik in data:
                company_data = CompanyData(company_name=company_name, cik=cik)
                db.session.add(company_data)

            db.session.commit()
    else:
        print(f"Error: {response.status_code}")


if __name__ == "__main__":
    print('test')
    parsing_submission_from_edgar()
