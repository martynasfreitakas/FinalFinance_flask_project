from bs4 import BeautifulSoup
import requests
from database import db, my_db
from models import CompanyData
from flask import Flask
from dotenv import load_dotenv
import os
load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
my_db(app)

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