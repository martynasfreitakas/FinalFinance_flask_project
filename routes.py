from datetime import datetime
from database import db
from flask import render_template, flash, redirect, url_for, session
from forms import SignUpForm, LoginForm
from models import User
from werkzeug.security import check_password_hash, generate_password_hash


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

    @app.route('/portfolio_tracker')
    def portfolio_tracker() -> str:
        return render_template('portfolio_tracker.html', year=datetime.now().year)

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

    @app.route('/fund_search')
    def fund_search():
        return render_template('portfolio_tracker.html', year=datetime.now().year)

