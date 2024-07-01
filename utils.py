from sqlalchemy import func

from models import Submission, FundHoldings, FundData
from bs4 import BeautifulSoup
from sec_edgar_downloader import Downloader
from dotenv import load_dotenv
import requests
from database import db
import shutil
from datetime import datetime
import os
import re
import logging.config

load_dotenv()

logging.config.fileConfig('logging.conf')

logger = logging.getLogger('sLogger')


# =======================================================

def download_and_store_all_companies_names_and_cik_from_edgar():
    logger.info('Starting downloading data from Edgar.')

    url = "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"

    headers = {"User-Agent": os.environ['EMAIL_FOR_AUTHORIZATION']}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        logger.info('Connected succesfully.')
        data_line = response.text.splitlines()
        all_lines_in_document = len(data_line)
        data = [(line.split(":")[0], line.split(":")[1].rstrip(':')) for line in data_line if ":" in line]

        # with app.app_context():
        for number_downloaded, (fund_name, fund_cik) in enumerate(data, start=1):
            fund_data = FundData(fund_name=fund_name, cik=fund_cik)
            db.session.add(fund_data)
            if number_downloaded % 1000 == 0:
                logging.info(f"Processed {number_downloaded} of {all_lines_in_document} lines.")
        db.session.commit()

        results = db.session.query(
            FundData.cik,
            func.group_concat(FundData.fund_name, ', ').label('fund_names')
        ).group_by(FundData.cik).having(func.count(FundData.cik) > 1).all()

        for number_dublicates, result in enumerate(results, start=1):
            fund_cik, fund_names = result

            fund_data = FundData.query.filter_by(cik=fund_cik).first()

            fund_data.fund_name = fund_names

            FundData.query.filter(FundData.cik == fund_cik, FundData.id != fund_data.id).delete()

            if number_dublicates % 1000 == 0:
                logging.info(f"Processed {number_dublicates} of {all_lines_in_document} updates.")

        db.session.commit()
    else:
        print(f"Error: {response.status_code}")


def edgar_downloader_from_sec(fund_cik):
    filing_types = ['NPORT-P', '13F-HR', 'N-Q']

    # Brookfield Investment Funds
    # filing_cik = '0001520738'

    # BERKSHIRE HATHAWAY INC
    # filing_type = '13F-HR'
    # filing_cik = '0001067983'

    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 6, 24)
    dir_path = 'sec-edgar-filings'

    for filing_type in filing_types:
        filings_path = os.path.join(dir_path, fund_cik, filing_type)
        if os.path.exists(filings_path):
            shutil.rmtree(filings_path)
        os.makedirs(filings_path)

        dl = Downloader(dir_path, os.environ['EMAIL_FOR_AUTHORIZATION'])
        dl.get(filing_type, fund_cik, after=start_date, before=end_date)

        if not os.listdir(filings_path):
            os.rmdir(filings_path)

        add_filing_to_db(fund_cik)


def checking_submission_type(path_to_file):
    with open(path_to_file, 'r') as file:
        data = file.read()

    conformed_sumbinion_type_line = re.compile(r'CONFORMED SUBMISSION TYPE:\s+(.+)')
    submission_type = conformed_sumbinion_type_line.search(data).group(
        1).strip() if conformed_sumbinion_type_line.search(
        data) else None
    return submission_type


def add_filing_to_db(fund_cik):
    directory_path = os.path.join('sec-edgar-filings', fund_cik)
    subdirectories = [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]
    for subdirectory in subdirectories:
        subdirectory_path = os.path.join(directory_path, subdirectory)
        sub_subdirectories = [d for d in os.listdir(subdirectory_path) if
                              os.path.isdir(os.path.join(subdirectory_path, d))]
        for sub_subdirectory in sub_subdirectories:
            sub_subdirectory_path = os.path.join(subdirectory_path, sub_subdirectory)
            files = os.listdir(sub_subdirectory_path)

            for file in files:
                file_path = os.path.join(sub_subdirectory_path, file)
                submission_type = checking_submission_type(file_path)
                # with app.app_context():
                if submission_type == 'NPORT-P':
                    extract_holdings_from_nport_p(file_path)
                elif submission_type == '13F-HR':
                    extract_holdings_from_13f_hr(file_path)
                else:
                    print(f"Unknown submission type: {submission_type}")


def extract_holdings_from_nport_p(path_to_file):
    if checking_submission_type(path_to_file) == 'NPORT-P':
        # with app.app_context():
        with open(path_to_file, 'r') as file:
            data = file.read()

        soup = BeautifulSoup(data, 'lxml')
        data_list = []
        tags = soup.find_all('invstorsec')

        cik_tag_line = re.compile(r'CENTRAL INDEX KEY:\s+(\d+)')
        owner_cik = cik_tag_line.search(data).group(1) if cik_tag_line.search(data) else None

        accession_number_line = re.compile(r'ACCESSION NUMBER:\s+(.+)')
        accession_number = accession_number_line.search(data).group(1).strip() if accession_number_line.search(
            data) else None

        fund_data = FundData.query.filter_by(cik=owner_cik).first()
        if not fund_data:
            print(f"No FundData found for CIK: {owner_cik}")
            return

        company_conformed_name_line = re.compile(r'COMPANY CONFORMED NAME:\s+(.+)')
        company_conformed_name = company_conformed_name_line.search(data).group(
            1).strip() if company_conformed_name_line.search(data) else None
        conformed_submission_type_line = re.compile(r'CONFORMED SUBMISSION TYPE:\s+(.+)')
        submission_type = conformed_submission_type_line.search(data).group(
            1).strip() if conformed_submission_type_line.search(data) else None
        filed_of_date_line = re.compile(r'FILED AS OF DATE:\s+(.+)')
        filed_of_date_format = filed_of_date_line.search(data).group(1).strip() if filed_of_date_line.search(
            data) else None
        filed_of_date = datetime.strptime(filed_of_date_format, '%Y%m%d') if filed_of_date_format else None

        existing_submission = Submission.query.filter_by(accession_number=accession_number).first()
        if existing_submission:
            existing_submission.cik = owner_cik
            existing_submission.company_name = company_conformed_name
            existing_submission.submission_type = submission_type
            existing_submission.filed_of_date = filed_of_date
            existing_submission.fund_data_id = fund_data.id
        else:
            submission = Submission(
                cik=owner_cik,
                company_name=company_conformed_name,
                submission_type=submission_type,
                filed_of_date=filed_of_date,
                accession_number=accession_number,
                fund_data_id=fund_data.id
            )
            db.session.add(submission)

        for tag in tags:
            nameofissuer = tag.find('name').text if tag.find('name') else None
            cusip = tag.find('cusip').text if tag.find('cusip') else None
            value = float(tag.find('valusd').text) if tag.find('valusd') else 0
            sshprnamt = float(tag.find('balance').text) if tag.find('balance') else 0

            data_dict = {
                'company_name': nameofissuer,
                'value_usd': value,
                'share_amount': sshprnamt,
                'cusip': cusip,
                'cik': owner_cik,
                'accession_number': accession_number,
            }
            data_list.append(data_dict)

        for data in data_list:
            existing_fund_holding = FundHoldings.query.filter_by(company_name=data['company_name'],
                                                                 accession_number=data['accession_number']).first()
            if existing_fund_holding:
                existing_fund_holding.value_usd = data['value_usd']
                existing_fund_holding.share_amount = data['share_amount']
                existing_fund_holding.cusip = data['cusip']
                existing_fund_holding.cik = data['cik']
                existing_fund_holding.fund_data_id = fund_data.id
            else:
                fund_holding = FundHoldings(
                    company_name=data['company_name'],
                    value_usd=data['value_usd'],
                    share_amount=data['share_amount'],
                    cusip=data['cusip'],
                    cik=data['cik'],
                    accession_number=data['accession_number'],
                    fund_data_id=fund_data.id
                )
                db.session.add(fund_holding)

        db.session.commit()


def extract_holdings_from_13f_hr(path_to_file):
    if checking_submission_type(path_to_file) == '13F-HR':
        # with app.app_context():
        with open(path_to_file, 'r') as file:
            data = file.read()

        soup = BeautifulSoup(data, 'lxml')
        data_dict = {}
        tags = soup.find_all('infotable')

        cik_tag_line = re.compile(r'CENTRAL INDEX KEY:\s+(\d+)')
        owner_cik = cik_tag_line.search(data).group(1) if cik_tag_line.search(data) else None

        accession_number_line = re.compile(r'ACCESSION NUMBER:\s+(.+)')
        accession_number = accession_number_line.search(data).group(1).strip() if accession_number_line.search(
            data) else None

        fund_data = FundData.query.filter_by(cik=owner_cik).first()
        if not fund_data:
            print(f"No FundData found for CIK: {owner_cik}")
            return

        company_conformed_name_line = re.compile(r'COMPANY CONFORMED NAME:\s+(.+)')
        company_conformed_name = company_conformed_name_line.search(data).group(
            1).strip() if company_conformed_name_line.search(data) else None
        conformed_submission_type_line = re.compile(r'CONFORMED SUBMISSION TYPE:\s+(.+)')
        submission_type = conformed_submission_type_line.search(data).group(
            1).strip() if conformed_submission_type_line.search(data) else None
        filed_of_date_line = re.compile(r'FILED AS OF DATE:\s+(.+)')
        filed_of_date_format = filed_of_date_line.search(data).group(1).strip() if filed_of_date_line.search(
            data) else None
        filed_of_date = datetime.strptime(filed_of_date_format, '%Y%m%d') if filed_of_date_format else None

        existing_submission = Submission.query.filter_by(accession_number=accession_number).first()
        if existing_submission:
            existing_submission.cik = owner_cik
            existing_submission.company_name = company_conformed_name
            existing_submission.submission_type = submission_type
            existing_submission.filed_of_date = filed_of_date
            existing_submission.fund_data_id = fund_data.id
        else:
            submission = Submission(
                cik=owner_cik,
                company_name=company_conformed_name,
                submission_type=submission_type,
                filed_of_date=filed_of_date,
                accession_number=accession_number,
                fund_data_id=fund_data.id
            )
            db.session.add(submission)

        for tag in tags:
            nameofissuer = tag.find('nameofissuer').text if tag.find('nameofissuer') else None
            cusip = tag.find('cusip').text if tag.find('cusip') else None
            value = int(tag.find('value').text) if tag.find('value') else 0
            sshprnamt = int(tag.find('sshprnamt').text) if tag.find('sshprnamt') else 0

            data_dict[nameofissuer] = {
                'value_usd': value,
                'share_amount': sshprnamt,
                'cusip': cusip,
                'cik': owner_cik,
                'accession_number': accession_number,
            }

        data_list = [{'company_name': name_of_company_key, **company_details_values} for
                     name_of_company_key, company_details_values in data_dict.items()]

        for data in data_list:
            existing_fund_holding = FundHoldings.query.filter_by(company_name=data['company_name'],
                                                                 accession_number=data['accession_number']).first()
            if existing_fund_holding:
                existing_fund_holding.value_usd = data['value_usd']
                existing_fund_holding.share_amount = data['share_amount']
                existing_fund_holding.cusip = data['cusip']
                existing_fund_holding.cik = data['cik']
                existing_fund_holding.fund_data_id = fund_data.id
            else:
                fund_holding = FundHoldings(
                    company_name=data['company_name'],
                    value_usd=data['value_usd'],
                    share_amount=data['share_amount'],
                    cusip=data['cusip'],
                    cik=data['cik'],
                    accession_number=data['accession_number'],
                    fund_data_id=fund_data.id
                )
                db.session.add(fund_holding)

        db.session.commit()


if __name__ == "__main__":
    print('test')
    # BERKSHIRE    HATHAWAY
    # 0001067983
    edgar_downloader_from_sec('0001067983')
    # edgar_downloader_from_sec('0000089043')
    # my_fil_cao('0001067983')
    print('completed.')
