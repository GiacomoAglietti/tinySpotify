from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from webapp import db_session
from webapp.models.User import User
from webapp.models.Playlist import Playlist
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import select

local_session = db_session()

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        stmt = (select(User).where(User.email == email))
        user = local_session.execute(stmt).scalars().first()

        if user:
            if check_password_hash(user.password, password):
                flash('Login effettuato con successo', category='success')
                login_user(user, remember=True)

                stmt = (
                    select(Playlist.id).
                    where(Playlist.id_user == user.id).
                    where(Playlist.name == "Preferiti"))

                id_fav_playlist= local_session.execute(stmt).scalar()

                print(id_fav_playlist)
                session['userid'] = user.id
                session['username'] = user.name
                session['id_fav_playlist'] = id_fav_playlist
                session['isArtist'] = user.isArtist
                return redirect("/home")
            else:                
                flash('Credenziali sbagliate, riprovare.', category='error')
        else:
            flash('Credenziali sbagliate, riprovare.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    session["username"] = None
    session["userid"] = None
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signUp', methods=['GET', 'POST'])
def signUp():

    if request.method == 'POST':
        email = request.form.get('email')
        nomeUtente = request.form.get('nomeUtente')
        password = request.form.get('password')
        passwordc = request.form.get('passwordc')
        selectResult = request.form['typeUser']

        if len(email) < 4:
            flash('Email deve essere di almeno 4 caratteri', category='error')
        elif len(nomeUtente) < 2:
            flash('Nome e Cognome deve essere di almeno 2 caratteri', category='error')
        elif len(password)<1:
            flash('Devi inserire una password', category='error')
        elif password != passwordc:
            flash('Le password non corrispondono', category='error')
        else:
            newUser = None
            
            if (selectResult == 'No'):
                newUser = User(
                    name=nomeUtente, 
                    email=email, 
                    password=generate_password_hash(password, method='sha256')
                    )
            if (selectResult == 'Si'):
                 newUser = User(
                    name=nomeUtente, 
                    email=email, 
                    password=generate_password_hash(password, method='sha256'),
                    isArtist = True
                    )
            

            local_session.add(newUser)
            local_session.commit()
            flash('Account creato!', category='success')
            return redirect(url_for('views.home'))

    return render_template("signUp.html")