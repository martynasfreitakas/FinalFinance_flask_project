from sec_edgar_downloader import Downloader
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


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