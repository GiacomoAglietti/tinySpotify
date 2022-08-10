import imp
from flask import Flask
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, select
from sqlalchemy.orm import relationship, backref, sessionmaker
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

connection_string = 'postgresql://postgres:admin@localhost/SpotiFake'
#connection_string = 'postgres://eytjofnu:nSmD1KQOXfBDVNLkhHZl2P6oNyHtTX5y@hattie.db.elephantsql.com/eytjofnu'

Base = declarative_base()

engine = create_engine(connection_string, echo=True)
Session = sessionmaker(bind=engine)
migrate = Migrate()



def create_app():

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SECRET_KEY'] = 'FakeNews'
    db = SQLAlchemy(app)

    from webapp.models.User import User
    from webapp.models.Playlist import Playlist
    from webapp.models.Song import Song
    from webapp.models.Album import Album
    from webapp.models.AlbumArtist import AlbumArtist
    from webapp.models.Genre import Genre
    from webapp.models.GenreSong import GenreSong
    from webapp.models.PlaylistSong import PlaylistSong
    from webapp.models.SongArtist import SongArtist


    
    migrate.init_app(app, db)

    from .views import views
    from .auth import auth

    Base.metadata.create_all(engine, checkfirst=True)
    session = Session()



    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        stmt = select(User).where(User.id == id)
        user = session.execute(stmt).scalars().first()
        return user
   
   
    # Test it
    #with Session(bind=engine) as session:
 



        

    #with Session(bind=engine) as session:

        #print(session.query(User).where(User.id == 1).one().playlist)
        #print(session.query(Playlist).where(Playlist.id == 1).one().songs)
    

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app

