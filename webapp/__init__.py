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

connection_string = 'postgresql://postgres:admin@localhost/tinySpotify'

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
    from webapp.models.Artist import Artist
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
    with Session(bind=engine) as session:
        """
        artist1 = Artist(
            alias="Linkin Park", 
            name_surname="Chester Bennington", 
            email="linkinpark@gmail.com", 
            password="linkinpark")

        session.add(artist1)
        session.commit()

        album= Album(name="Minutes To Midnight", year=2007, image="")
        session.add(album)
        session.commit()
        
        song1= Song(title="Wake", year="2007", length=100, num_order=1, id_album=2)
        song2= Song(title="Given Up", year="2008", length=189, num_order=2, id_album=2)
        song3= Song(title="Leave Out All the Rest", year="2008", length=209, num_order=3, id_album=2)
        song4= Song(title="Bleed It Out", year="2007", length=164, num_order=4, id_album=2)
        song5= Song(title="Shadow of the Day", year="2007", length=289, num_order=5, id_album=2)
        song6= Song(title="What I've Done", year="2007", length=205, num_order=6, id_album=2)
        song7= Song(title="Hands Held High", year="2007", length=233, num_order=7, id_album=2)
        song8= Song(title="No More Sorrow", year="2007", length=221, num_order=8, id_album=2)
        song9= Song(title="Valentine's Day", year="2007", length=196, num_order=9, id_album=2)
        song10= Song(title="In Between", year="2007", length=196, num_order=10, id_album=2)
        song11= Song(title="In Pieces", year="2007", length=218, num_order=11, id_album=2)
        song12= Song(title="The Little Things Give You Away", year="2007", length=383, num_order=12, id_album=2)

        session.add_all([song1, song2,song3,song4,song5,song6,song7,song8,song9,song10,song11,song12])
        session.commit()
        al_ar=AlbumArtist(id_album=2, id_artist=2)
        session.add(al_ar)
        session.commit()

        counter = 11
        while counter < 23:
            gs1=GenreSong(id_genre=14, id_song=counter)
            session.add(gs1)
            counter+=1

        counter = 11
        while counter < 23:
            sa=SongArtist(id_artist=2, id_song=counter)
            session.add(sa)
            counter+=1

        session.commit()
        
       
        song1 = Song(
            title="song1",
            year=2000
            )
        session.add(song1)

        song2 = Song(
            title="song2",
            year=2001
            )
        session.add(song2)
        """
        pl1 = Playlist(
            name="playlist01",
            id_user=1
        )
        #session.add(pl1)

        #session.commit()

    
    

        

        
    

    #with Session(bind=engine) as session:

        #print(session.query(User).where(User.id == 1).one().playlist)
        #print(session.query(Playlist).where(Playlist.id == 1).one().songs)
    

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app

