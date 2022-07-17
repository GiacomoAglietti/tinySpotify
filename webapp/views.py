from threading import local
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import select
from webapp import Session
from webapp.models.User import User
from webapp.models.SongArtist import SongArtist
from webapp.models.Song import Song
from webapp.models.PlaylistSong import PlaylistSong
from webapp.models.Playlist import Playlist
from webapp.models.GenreSong import GenreSong
from webapp.models.Genre import Genre
from webapp.models.Artist import Artist
from webapp.models.AlbumArtist import AlbumArtist
from webapp.models.Album import Album

local_session = Session()

views = Blueprint('views', __name__)

@views.route('/')
#@login_required
def home():
    return render_template("home.html")

#url_for('get-playlist', id='A')
@views.route('/')
#@login_required
def playlist():
        #stmt = select(Playlist).order_by(Playlist.date_created)
        playlist1 = local_session.query(Playlist).first().name
        #local_session.execute(stmt).scalars().first()

        

        """
        stmt = (select(Playlist).
                where(Playlist.id_user == id).
                order_by(Playlist.date_created))
        playlist_list = local_session.execute(stmt).scalars().all()
        
        playlist1 = Playlist(
                id_user = 1, 
                name = "Rap")
        playlist2 = Playlist(
                id_user = 2, 
                name = "Rock")
        playlist3 = Playlist(
                id_user = 3, 
                name = "Pop")

        playlist_list=[playlist1, playlist2, playlist3]
        local_session.add(playlist1)
        local_session.commit()
        """
        return render_template("home.html" , playlist1=playlist1)

@views.route('/playlist/<playlist_selected>')
#@login_required
def get_playlist_selected(id, playlist_selected):
        stmt = (select(Song.title).
                join(PlaylistSong, Song.id == PlaylistSong.id_song).
                join(Playlist, Playlist.id == PlaylistSong.id_playlist).
                where(Playlist.id_user == id and Playlist.name == playlist_selected).
                order_by(PlaylistSong.num_order))

        songs_list = local_session.execute(stmt).scalars().all()
        return songs_list


@views.route('/create-new-playlist')
#@login_required
def create_new_playlist(id, name):
        newPlaylist = Playlist(
                id_user = id, 
                name = name)
        local_session.add(newPlaylist)
        local_session.commit()
        flash('Playlist creata!', category='success')
        return redirect(url_for('views.home'))

