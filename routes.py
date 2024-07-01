from datetime import datetime
from database import db
from flask import render_template, flash, redirect, url_for, session, request
from forms import SignUpForm, LoginForm
from models import User, FundData, Submission, AddFundToFavorites
from werkzeug.security import check_password_hash, generate_password_hash

from utils import edgar_downloader_from_sec


def my_routes(app):
    @app.route('/')
    def home() -> str:
        return render_template('home.html', year=datetime.now().year)

    @app.route('/about')
    def about() -> str:
        return render_template('about.html', year=datetime.now().year)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            user = User.query.filter_by(username=username).first()
            print(f"User: {user}")
            if user:
                print(f"Stored password hash: {user.password}")
                print(f"Entered password: {password}")
                print(f"Password check result: {check_password_hash(user.password, password)}")
                if check_password_hash(user.password, password):
                    session['username'] = user.username
                    print('User logged in')
                    flash('Logged in successfully.')
                    return redirect(url_for('home'))
            flash('Invalid username or password.')
            print('Invalid username or password')
        return render_template('login.html', year=datetime.now().year, form=form)

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        form = SignUpForm()
        if form.validate_on_submit():
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash('The username already exists. Try Diffrent one.')
                return redirect(url_for('signup'))
            hashed_password = generate_password_hash(form.password.data)
            user = User(name=form.name.data, surname=form.surname.data, username=form.username.data,
                        email=form.email.data, phone_number=form.phone_number.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
        return render_template('signup.html', year=datetime.now().year, form=form)

    @app.route('/logout')
    def logout():
        session.pop('username', None)
        flash('You have been logged out.')
        return redirect(url_for('home'))

    @app.route('/fund_search', methods=['GET'])
    def fund_search():
        query = request.args.get('query', default='', type=str)

        if not query:
            flash('Please enter a company name or CIK.')
            return render_template('fund_search.html', year=datetime.now().year)

        funds = FundData.query.filter(
            FundData.cik.like(f'%{query}%') if query.isdigit() else
            FundData.fund_name.like(f'%{query}%')
        ).all()

        return render_template('fund_search.html', funds=funds, year=datetime.now().year)

    @app.route('/fund_details/<cik>')
    def fund_details(cik):
        if 'username' not in session:
            flash('This is only for registered users. Please sign in or log in.')
            return redirect(url_for('login'))
        fund = Submission.query.filter_by(cik=cik).first()
        if not fund:
            edgar_downloader_from_sec(cik)
            fund = Submission.query.filter_by(cik=cik).first()
            if not fund:
                flash('No fund found with the given CIK.')
                return redirect(url_for('fund_search'))
        all_submissions = Submission.query.filter_by(cik=cik).all()
        return render_template('fund_details.html', fund=fund, submissions=all_submissions, year=datetime.now().year)

    @app.route('/portfolio_monitor')
    def portfolio_tracker() -> str:
        return render_template('portfolio_monitor.html', year=datetime.now().year)

    @app.route('/fund_favorites')
    def fund_favorites():
        if 'username' not in session:
            flash('You need to be logged in to view favorites.')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=session['username']).first()
        if not user:
            flash('User not found.')
            return redirect(url_for('login'))

        favorite_funds = user.favorite_funds

        return render_template('fund_favorites.html', favorite_funds=favorite_funds, year=datetime.now().year)

    @app.route('/add_to_favorites/<int:fund_id>', methods=['POST'])
    def add_to_favorites(fund_id):
        if 'username' not in session:
            flash('You need to be logged in to add favorites.')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=session['username']).first()
        if not user:
            flash('User not found.')
            return redirect(url_for('login'))

        favorite = AddFundToFavorites.query.filter_by(user_id=user.id, fund_id=fund_id).first()
        if favorite:
            flash('Fund is already in favorites.')
        else:
            favorite = AddFundToFavorites(user_id=user.id, fund_id=fund_id)
            db.session.add(favorite)
            db.session.commit()
            flash('Fund added to favorites.')

        return redirect(url_for('fund_search'))

    @app.route('/remove_from_favorites/<int:fund_id>', methods=['POST'])
    def remove_from_favorites(fund_id):
        if 'username' not in session:
            flash('Please log in to manage your favorites.', 'error')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=session['username']).first()
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('login'))

        favorite_entry = AddFundToFavorites.query.filter_by(user_id=user.id, fund_id=fund_id).first()
        if favorite_entry:
            db.session.delete(favorite_entry)
            db.session.commit()
            flash('Fund removed from favorites successfully!', 'success')
        else:
            flash('Fund not found in favorites.', 'error')

        return redirect(url_for('fund_favorites'))
