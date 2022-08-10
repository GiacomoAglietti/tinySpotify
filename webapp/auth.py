from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from webapp import Session
from webapp.models.User import User
from webapp.models.Playlist import Playlist
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import select

local_session = Session()

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        stmt = select(User).where(User.email == email)
        user = local_session.execute(stmt).scalars().first()
        if user:
            if check_password_hash(user.password, password):
                flash('Login effettuato con successo', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Credenziali sbagliate, riprovare.', category='error')
        else:
            flash('Credenziali sbagliate, riprovare.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signUp', methods=['GET', 'POST'])
def signUp():

    if request.method == 'POST':
        email = request.form.get('email')
        firstSecondName = request.form.get('nomeCognome')
        password = request.form.get('password')
        passwordc = request.form.get('passwordc')
        selectResult = request.form.get('typeUser')
        alias = request.form.get('alias')

        if len(email) < 4:
            flash('Email deve essere di almeno 4 caratteri', category='error')
        elif len(firstSecondName) < 2:
            flash('Nome e Cognome deve essere di almeno 2 caratteri', category='error')
        elif len(password)<1:
            flash('Devi inserire una password', category='error')
        elif password != passwordc:
            flash('Le password non corrispondono', category='error')
        else:
            newUser = User(
                    name=firstSecondName, 
                    email=email, 
                    password=generate_password_hash(password, method='sha256')
                    )
            """
            if (selectResult == 'No'):
                newUser = User(
                    name_surname=firstSecondName, 
                    email=email, 
                    password=generate_password_hash(password, method='sha256')
                    )
            if (selectResult == 'Si'):
                newUser = Artist(
                    alias = alias,
                    name_surname=firstSecondName, 
                    email=email, 
                    password=generate_password_hash(password, method='sha256'))
            """

            local_session.add(newUser)
            local_session.commit()
            flash('Account creato!', category='success')
            return redirect(url_for('views.home'))

    return render_template("signUp.html")