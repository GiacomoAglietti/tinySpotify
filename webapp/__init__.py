from flask import Flask
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from .views import views
from .auth import auth
from webapp.models.User import User
from webapp.models.Playlist import Playlist
from webapp.models.PlaylistSong import PlaylistSong
from webapp.models.Song import Song
from webapp.models.Genre import Genre
from webapp.models.Album import Album
from webapp.models.GenreSong import GenreSong
from webapp.models.SongArtist import SongArtist
from webapp.models.Artist import Artist
from webapp.models.AlbumArtist import AlbumArtist
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

connection_string = "sqlite:///"+os.path.join(BASE_DIR,"tinySpotify.db")

Base = declarative_base()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'FakeNews'

    engine = create_engine(connection_string, echo=True)
    Base.metadata.create_all(engine, checkfirst=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    """
    # Test it
    with Session(bind=engine) as session:

        user = User(
            name_surname="gianni",
            email="gas@gmail.com",
            )
        session.add(user)

        # add users
        usr1 = Song(
            title="prova1",
            year=2000,
            )
        session.add(usr1)

        usr2 = Song(
            title="prova2",
            year=2001,
            )
        session.add(usr2)

        session.commit()

        # add projects
        prj1 = Playlist(
            name="bella ciao",
            id_user=1
        )
        session.add(prj1)

        prj2 = Playlist(name="big one", id_user=1)
        session.add(prj2)

        session.commit()

        user.playlist = [prj1, prj2]

        # map users to projects
        prj1.songs = [usr1, usr2]
        prj2.songs = [usr2]

        

        session.commit()

    with Session(bind=engine) as session:

        print(session.query(User).where(User.id == 1).one().playlist)
        print(session.query(Playlist).where(Playlist.id == 1).one().songs)
    """

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app  