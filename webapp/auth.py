from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from webapp import db_session
from webapp.models.User import User
from webapp.models.Playlist import Playlist
from webapp.models.UserPlaylist import UserPlaylist
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import select, exc

local_session = db_session()

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Function used to login a user. If the credentials inserted by the user are correct then id, name, id_fav_playlist and role are saved in the session

        Returns
        -------
        Return to endpoint /home if users'credentials are correct, otherwise return the template of "login.html"
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        stmt = (select(User).where(User.email == email))
        user = None
        try:
            user = local_session.execute(stmt).scalars().first()                
        except exc.SQLAlchemyError as e:
            return str(e.orig)

        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)

                stmt = (
                    select(Playlist.id).
                    join(UserPlaylist, Playlist.id == UserPlaylist.id_playlist).
                    where(UserPlaylist.id_user == user.id).
                    where(Playlist.name == "Preferiti"))

                id_fav_playlist = None
                try:
                    id_fav_playlist= local_session.execute(stmt).scalar()            
                except exc.SQLAlchemyError as e:
                    return str(e.orig)

                session['userid'] = user.id
                session['username'] = user.name
                session['id_fav_playlist'] = id_fav_playlist
                session['role'] = user.role
                
                flash('Login effettuato con successo', category='success')
                return redirect("/home")
            else:                
                flash('Credenziali sbagliate, riprovare.', category='error')
        else:
            flash('Credenziali sbagliate, riprovare.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    """Function used to logout the authenticated user and set all session's variables to None

        Decorators
        ----------
        @login_required

        Returns
        -------
        Return to auth.login
    """

    session['userid'] = None
    session['username'] = None
    session['id_fav_playlist'] = None
    session['role'] = None
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signUp', methods=['GET', 'POST'])
def signUp():
    """Function used to sign up a user. 
       Sign up is successful only if
       the name or the email entered are not already in the database and
       the password entered and the confirm password are the same and
       the email has to have at least 4 chars and
       the name has to have at least 2 chars and
       the password has to have at least 1 char.

       If any of the above conditions are not respected then a flash message will appear.
       
       If, instead, all the conditions have been met, then the user is signed up and assigned a role.
       In particular, if a user is an artist the role given to him is "ArtistFree", otherwise "UserFree".


        Returns
        -------
        Return the template of "login.html" if the signed up is successful, otherwise return the template of "signUp.html"
    """

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

            exists_name = local_session.execute(select(User.name).where(User.name == nomeUtente)).scalar()

            exists_email = local_session.execute(select(User.email).where(User.email == email)).scalar()

            if(exists_name is not None):
                flash('Il nome utente esiste già', category='error')
                return render_template("signUp.html")
            if (exists_email is not None):
                flash('L\'email esiste già', category='error')
                return render_template("signUp.html")

            
            newUser = None
            if (selectResult == 'No'):
                newUser = User(
                    name=nomeUtente, 
                    email=email, 
                    password=generate_password_hash(password, method='sha256'),
                    role="UserFree"
                    )
            if (selectResult == 'Si'):
                newUser = User(
                    name=nomeUtente, 
                    email=email, 
                    password=generate_password_hash(password, method='sha256'),
                    role="ArtistFree"
                    )   
        
            playlistPreferiti = Playlist(name='Preferiti') 


            try:
                local_session.add(newUser)
                local_session.add(playlistPreferiti)                
                local_session.commit()
                local_session.flush()
                local_session.refresh(newUser)
                local_session.refresh(playlistPreferiti) 

                user_playlist = UserPlaylist(id_playlist=playlistPreferiti.id, id_user=newUser.id)

                local_session.add(user_playlist)                
                local_session.commit() 

                flash('Account creato!', category='success')
                return redirect(url_for('auth.login'))
            except exc.SQLAlchemyError as e:
                local_session.rollback()
                return str(e.orig)
                
            finally:                                 
                local_session.close()            
    
    return render_template("signUp.html")

        