from flask import Flask
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_session import Session
import os
import psycopg2

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

connection_string = 'postgresql://postgres:admin@localhost/SpotiFake'


engine = create_engine(connection_string, echo=True)
db_session = sessionmaker(bind=engine)

migrate = Migrate()

Base = declarative_base()

conn = psycopg2.connect("dbname=SpotiFake user=postgres password=admin")


def create_app():

    app = Flask(__name__, template_folder='templates')

    app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SECRET_KEY'] = 'FakeNews'
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app) 

    db = SQLAlchemy(app)

    from webapp.models.User import User
    from webapp.models.Playlist import Playlist
    from webapp.models.Song import Song
    from webapp.models.Album import Album
    from webapp.models.AlbumArtist import AlbumArtist
    from webapp.models.Genre import Genre
    from webapp.models.PlaylistSong import PlaylistSong
    from webapp.models.SongArtist import SongArtist
    from webapp.models.UserPlaylist import UserPlaylist
    from webapp.models.MyFunctions import FunctionSession
    from webapp.models.Role import Role
    
    migrate.init_app(app, db)

    from .views import views
    from .auth import auth

    Base.metadata.create_all(engine, checkfirst=True)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(id):
        stmt = select(User).where(User.id == id)
        user = db_session().execute(stmt).scalars().first()
        return user 
    
    

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app



