from threading import local
from flask import Blueprint, render_template, request, flash, redirect, session, url_for
from flask_login import login_required, current_user
from sqlalchemy import insert, select, subquery, update, delete, func
from webapp import Session
from webapp.models.User import User
from webapp.models.SongArtist import SongArtist
from webapp.models.Song import Song
from webapp.models.PlaylistSong import PlaylistSong
from webapp.models.Playlist import Playlist
from webapp.models.GenreSong import GenreSong
from webapp.models.Genre import Genre
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


@views.route('/playlists/<int:id_playlist_selected>', methods=['GET', 'POST'])
#@login_required
def get_playlist_selected(id_playlist_selected):
        if request.method == 'POST':

                if(request.headers.get('Content-Type')=='addToFav'):
                        idSong=int(request.data.decode("utf-8"))
                        ps1= PlaylistSong(id_playlist=1, id_song=idSong)
                        local_session.add(ps1)
                        update_song = (
                                update(Song).
                                where(Song.id == idSong).
                                values(favourite=True)
                                )
                        local_session.execute(update_song)
                        local_session.commit()
                if(request.headers.get('Content-Type')=='removeFromFav'):
                        idSong=int(request.data.decode("utf-8"))
                        delete_song= (
                                delete(PlaylistSong).
                                where(PlaylistSong.id_playlist==1).
                                where(PlaylistSong.id_song==idSong)
                                )
                        local_session.execute(delete_song)
                        update_song = (
                                update(Song).
                                where(Song.id == idSong).
                                values(favourite=False)
                                )
                        local_session.execute(update_song)
                        local_session.commit()                    

                elif 'change-name-playlist' in request.form:
                        nomePlaylist = request.form.get('nomePlaylist')
                        stmt = (
                                update(Playlist).
                                where(Playlist.id == id_playlist_selected).
                                values(name=nomePlaylist)
                                )
                        local_session.execute(stmt)
                        local_session.commit()
                        #local_session.flush()
        
        
        
        stmt_playlist = (
                select(Playlist.name).
                where(Playlist.id == id_playlist_selected))


        stmt_song=(
                select(Song.id, Song.title, Song.id_album, Song.length, PlaylistSong.num_in_playlist, Album.name).
                join(PlaylistSong, Song.id == PlaylistSong.id_song).
                join(Album, Song.id_album == Album.id).
                where(PlaylistSong.id_playlist == id_playlist_selected).
                order_by(PlaylistSong.num_in_playlist)) 

        """select_favourite= (
                select((func.count(PlaylistSong.id_song)).label('isFav')).
                where(PlaylistSong.id_song == stmt_song.id).
                where(PlaylistSong.id_playlist == 1))
        """

    

        """
        Select*, (select count (*) 
                  from playlistsong ps 
                  where ps.idcanzone = s.idcanzone And ps.idplaylist = id_playlist_selected)
        From Song as s
        """

        playlist_name = local_session.execute(stmt_playlist).scalar()
        if (playlist_name==None):
                playlist_name="Playlist not found"
        
        songs_list = local_session.execute(stmt_song).all()
        
        num_songs = 0
        tot_length = 0

        for song in songs_list:
                num_songs += 1
                tot_length += song.length

        return render_template("playlist-select.html", songs_list = songs_list, playlist_name = playlist_name, num_songs=num_songs, tot_length=tot_length, actual_playlist=id_playlist_selected)

@views.route('/albums')
#@login_required
def albums():
        stmt = select(Album)#.where(Playlist.id_user == id)
        album_list = local_session.execute(stmt).scalars()
        return render_template("albums.html", album_list = album_list)

@views.route('/artists')
#@login_required
def artists():
        stmt = select(User)#.where(Playlist.id_user == id)
        artist_list = local_session.execute(stmt).scalars()
        return render_template("artists.html", artist_list = artist_list)


@views.route('/albums/<int:id_album_selected>')
#@login_required
def get_album_selected(id_album_selected):
        stmt_album = (
                select(Album.name).
                where(Album.id == id_album_selected))

        stmt_song=(
                select(Song.id, Song.title, Song.id_album, Song.length, Song.num_in_album, Album.name).
                join(Album, Song.id_album == Album.id).
                where(Album.id == id_album_selected).
                order_by(Song.num_in_album)) 

        album_name = local_session.execute(stmt_album).scalar()
        if (album_name==None):
                album_name="Album not found"

        songs_list = local_session.execute(stmt_song).all()

        num_songs = 0
        tot_length = 0

        for song in songs_list:
                num_songs += 1
                tot_length += song.length

        return render_template("album-select.html", songs_list = songs_list, album_name = album_name, num_songs=num_songs, tot_length=tot_length, actual_playlist=id_album_selected)

@views.route('/search')
#login_required
def search():
    return render_template("search.html")


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

