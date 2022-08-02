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

migrate = Migrate()
engine = create_engine(connection_string, echo=True)
Session = sessionmaker(bind=engine)


    

def create_app():

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'FakeNews'

    from .views import views
    from .auth import auth
    
    db = SQLAlchemy(app)
    db.init_app(app)
    migrate = Migrate(app, db)

    Base.metadata.create_all(engine, checkfirst=True)
    session = Session()

    from webapp.models.User import User
    from webapp.models.Playlist import Playlist
    from webapp.models.Song import Song


    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        stmt = select(User).where(User.id == id)
        user = session.execute(stmt).scalars().first()
        return user

    """   
    # Test it
    with Session(bind=engine) as session:

        
        user = User(
            name_surname="user02",
            email="user02@gmail.com",
            password="user"
            )
        session.add(user)

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

        session.commit()

        pl1 = Playlist(
            name="bella ciao",
            id_user=1
        )
        session.add(pl1)

        pl2 = Playlist(name="big one", id_user=1)
        session.add(pl2)

        session.commit()

        user.playlist = [pl1, pl2]

        # map songs to playlist
        pl1.songs = [song1, song2]
        pl2.songs = [song2]

        

        

        session.commit()
    """

    #with Session(bind=engine) as session:

        #print(session.query(User).where(User.id == 1).one().playlist)
        #print(session.query(Playlist).where(Playlist.id == 1).one().songs)
    

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app

