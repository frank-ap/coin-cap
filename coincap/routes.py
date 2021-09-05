import os
from dotenv import load_dotenv
import pandas as pd
from flask import render_template, flash, redirect, url_for, request
from coincap.forms import RegistrationForm, LoginForm, AlertsForm
from coincap import app, create_plot, conn, bcrypt, db
from datetime import datetime
from coincap.models import User, Listings, Alerts
from flask_login import login_user, current_user, logout_user, login_required

load_dotenv()

@app.route('/')
def home():
    return render_template('home.html', title='Home')

@app.route('/last_ninety')
def last_ninety():
    conn = db.engine.connect().connection
    #df = pd.read_sql(str(Listings.query.all()), conn)
    df = pd.read_sql("SELECT * FROM listings", conn)
    group = df.groupby('name')
    y_axis='percent_change_90d'
    bar = create_plot(df, group, y_axis)
    conn.close()
    return render_template('index.html', plot=bar, title='Data')

@app.route('/price')
def price():
    conn = db.engine.connect().connection
    df = pd.read_sql("SELECT * FROM listings", conn)
    group = df.groupby('name')
    y_axis='price'
    bar = create_plot(df, group, y_axis)
    conn.close()
    return render_template('index.html', plot=bar, title='Data')

@app.route('/last_day')
def last_day():
    conn = db.engine.connect().connection
    df = pd.read_sql("SELECT * FROM listings", conn)
    group = df.groupby('name')
    y_axis='percent_change_24h'
    bar = create_plot(df, group, y_axis)
    conn.close()
    return render_template('index.html', plot=bar, title='Data')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Account created for {form.username.data}! You are now able to log in", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')

@app.route("/alerts", methods=['GET','POST'])
@login_required
def alerts():
    print(current_user.id)
    print([(listings.name, listings.name) for listings in Listings.query.with_entities(Listings.id, Listings.name).order_by(Listings.date.desc(), Listings.name.asc()).limit(100).all()])
    form = AlertsForm()
    form.crypto1.choices = [(listings.name, listings.name) for listings in Listings.query.with_entities(Listings.id, Listings.name).order_by(Listings.date.desc(), Listings.name.asc()).limit(100).all()]
    form.crypto2.choices = [(listings.name, listings.name) for listings in Listings.query.with_entities(Listings.id, Listings.name).order_by(Listings.date.desc(), Listings.name.asc()).limit(100).all()]
    form.crypto3.choices = [(listings.name, listings.name) for listings in Listings.query.with_entities(Listings.id, Listings.name).order_by(Listings.date.desc(), Listings.name.asc()).limit(100).all()]
    if form.validate_on_submit():
        alerts = Alerts(crypto1=form.crypto1.data, crypto2=form.crypto2.data, crypto3=form.crypto3.data, user_id=current_user.id)
        db.session.add(alerts)
        db.session.commit()
        flash(f'We will alert you when the price of {form.crypto1.data}, {form.crypto2.data} or {form.crypto3.data} drops!', 'success')
        return redirect(url_for('home'))
    return render_template('alerts.html', title='Alerts', form=form)

