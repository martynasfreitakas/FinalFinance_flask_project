from database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    favorite_funds = db.relationship('AddFundToFavorites', back_populates='user',  cascade="all, delete-orphan")


class FundData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fund_name = db.Column(db.String(80), nullable=False)
    cik = db.Column(db.String(10), nullable=False)
    submissions = db.relationship('Submission', back_populates='fund_data', cascade="all, delete-orphan")
    fund_holdings = db.relationship('FundHoldings', back_populates='fund_data', cascade="all, delete-orphan")
    favorites = db.relationship('AddFundToFavorites', back_populates='fund', cascade="all, delete-orphan")


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cik = db.Column(db.String(10), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    submission_type = db.Column(db.String(10), nullable=False)
    filed_of_date = db.Column(db.Date, nullable=False)
    accession_number = db.Column(db.String(20), nullable=False)
    fund_data_id = db.Column(db.Integer, db.ForeignKey('fund_data.id'))
    fund_data = db.relationship('FundData', back_populates='submissions')


class FundHoldings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    value_usd = db.Column(db.Float, nullable=False)
    share_amount = db.Column(db.Float, nullable=False)
    cusip = db.Column(db.String(9), nullable=False)
    cik = db.Column(db.String(10), nullable=False)
    accession_number = db.Column(db.String(20), nullable=False)
    fund_data_id = db.Column(db.Integer, db.ForeignKey('fund_data.id'))
    fund_data = db.relationship('FundData', back_populates='fund_holdings')


# models.py

class AddFundToFavorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fund_id = db.Column(db.Integer, db.ForeignKey('fund_data.id'), nullable=False)
    fund = db.relationship('FundData', back_populates='favorites')
    user = db.relationship('User', back_populates='favorite_funds')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'fund_id', name='unique_favorite'),
    )

