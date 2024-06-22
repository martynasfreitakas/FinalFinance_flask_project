from models import CompanyData
from app import app


def show_edgar_cik_all_companies():
    with app.app_context():
        cik_all_list = CompanyData.query.all()
        for cik in cik_all_list:
            return cik.company_name, cik.cik


def show_edgar_cik_companies_with_text(text):
    with app.app_context():
        companies = CompanyData.query.filter(CompanyData.company_name.like(f'%{text}%')).all()
        return [(company.company_name, company.cik) for company in companies]


def show_edgar_cik_companies_with_text_by_cik(cik):
    with app.app_context():
        companies = CompanyData.query.filter(CompanyData.cik.like(f'%{cik}%')).all()
        return [(company.company_name, company.cik) for company in companies]


if __name__ == "__main__":
    print(show_edgar_cik_companies_with_text_by_cik('357476'))
