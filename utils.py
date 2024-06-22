from models import CompanyData
from app import app


def show_edgar_cik_all_companies():
    with app.app_context():
        cik_all_list = CompanyData.query.all()
        for cik in cik_all_list:
            return cik.company_name, cik.cik



if __name__ == "__main__":
    print('test')
