from threading import local
from flask import Blueprint, render_template, request, flash, redirect, session, url_for
from flask_login import login_required, current_user
from sqlalchemy import insert, select, subquery, update, delete
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
@views.route('/home')
#@login_required
def home2():
        stmt = select(Playlist)#.where(Playlist.id_user == id)
        playlist1 = local_session.execute(stmt).scalars()
        return render_template("home.html" , playlist1=playlist1)

@views.route('/playlists')
#@login_required
def playlists():
        stmt = select(Playlist).where(Playlist.id_user == 1)
        playlists = local_session.execute(stmt).scalars()
        return render_template("playlists.html", playlists = playlists)


@views.route('/playlists/<int:id_playlist_selected>')
#@login_required
def get_playlist_selected(id_playlist_selected):
        if request.method == 'POST':
                nomePlaylist = request.form.get('nomePlaylist')
                stmt = (
                        update(Playlist).
                        where(Playlist.id == id_playlist_selected).
                        values(name=nomePlaylist)
                        )
                local_session.execute(stmt)
                local_session.commit()
        
        stmt_playlist = (
                select(Playlist.name).
                where(Playlist.id == id_playlist_selected))

        stmt_song=(
                select(Song.id, Song.title, Song.id_album, Song.length, PlaylistSong.num_order, Album.name).
                join(PlaylistSong, Song.id == PlaylistSong.id_song).
                join(Album, Song.id_album == Album.id).
                where(PlaylistSong.id_playlist == id_playlist_selected).
                order_by(PlaylistSong.num_order))      


        playlist_name = local_session.execute(stmt_playlist).scalar()
        if (playlist_name==None):
                playlist_name="Playlist not found"

        songs_list = local_session.execute(stmt_song).all()

        num_songs = 0
        tot_length = 0

        for song in songs_list:
                num_songs += 1
                tot_length += song.length

        return render_template("playlist-select.html", songs_list = songs_list, playlist_name = playlist_name, num_songs=num_songs, tot_length=tot_length)

@views.route('/albums')
#@login_required
def albums():
        stmt = select(Album)#.where(Playlist.id_user == id)
        album_list = local_session.execute(stmt).scalars()
        return render_template("albums.html", album_list = album_list)

@views.route('/artists')
#@login_required
def artists():
        stmt = select(Artist)#.where(Playlist.id_user == id)
        artist_list = local_session.execute(stmt).scalars()
        return render_template("artists.html", artist_list = artist_list)


@views.route('/album/<album_selected>')
#@login_required
def get_album_selected(id, album_selected):
        stmt = (select(Song.title).
                join(PlaylistSong, Song.id == PlaylistSong.id_song).
                join(Playlist, Playlist.id == PlaylistSong.id_playlist).
                where(Playlist.id_user == id and Playlist.name == album_selected).
                order_by(PlaylistSong.num_order))

        songs_list = local_session.execute(stmt).scalars().all()
        return render_template("album.html", songs_list = songs_list)


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

#da sistemare
@views.route('/addAlbum', methods=['GET', 'POST'])
def addAlbum():

    if request.method == 'POST':
        email = request.form.get('email')
        firstSecondName = request.form.get('firstSecondName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
            flash('Email deve essere di almeno 4 caratteri', category='error')
        elif len(firstSecondName) < 2:
            flash('Nome e Cognome deve essere di almeno 2 caratteri', category='error')
        elif len(password1)<1:
            flash('Devi inserire una password', category='error')
        elif password1 != password2:
            flash('Le password non corrispondono', category='error')
        else:
            newUser = User(
                name_surname=firstSecondName, 
                email=email, 
                password="")
                

            local_session.add(newUser)
            local_session.commit()
            flash('Account creato!', category='success')
            return redirect(url_for('views.home'))

    return render_template("signUp.html")

