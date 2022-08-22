import re
from threading import local
from flask import Blueprint, render_template, request, flash, redirect, session, url_for
from flask_login import login_required, current_user
from sqlalchemy import insert, select, subquery, update, delete, func
from sqlalchemy.orm import aliased
from webapp import db_session, engine
from webapp.models.User import User
from webapp.models.SongArtist import SongArtist
from webapp.models.Song import Song
from webapp.models.PlaylistSong import PlaylistSong
from webapp.models.Playlist import Playlist
from webapp.models.GenreSong import GenreSong
from webapp.models.Genre import Genre
from webapp.models.AlbumArtist import AlbumArtist
from webapp.models.Album import Album
from itertools import chain
import json

local_session = db_session()

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
#@login_required
def home():
        
        if session.get('userid'):
                return redirect("/home")
        
        return redirect("/login")


@views.route('/home', methods=['GET', 'POST'])
#@login_required
def home_authenticated():
        username="user not found"
        if session.get('username'):
                username =  session['username']
                #flash('Login effettuato con successo', category='success')

        stmt = select(Playlist).where(Playlist.id_user == session['userid'])
        playlist1 = local_session.execute(stmt).scalars()

        return render_template("home.html" , playlist1=playlist1, username=username)

@views.route('/create-playlist', methods=['GET', 'POST'])
@login_required
def create_playlist():

        if request.method == 'POST':
                nomePlaylist = request.form.get('nomePlaylist')
                stmt = (
                        insert(Playlist).
                        values(name=nomePlaylist).
                        values(id_user=session.get('userid'))
                        )
                local_session.execute(stmt)
                local_session.commit()

        stmt = select(Playlist).where(Playlist.id_user == session['userid'])
        playlists = local_session.execute(stmt).scalars()

        return render_template("playlists.html", playlists = playlists)

@views.route('/playlists', methods=['GET', 'POST'])
#@login_required
def playlists():
        userid = 0
        if session.get('userid'):
                userid =  session['userid'] 

        stmt = (
                select(Playlist.id, Playlist.name).
                where(Playlist.id_user == userid).
                where(Playlist.name != "Preferiti"))

        playlists = local_session.execute(stmt).all()

        return render_template("playlists.html", playlists = playlists)

@views.route('/playlists/delete/<int:id>', methods=['GET', 'POST'])
#@login_required
def delete_playlist(id):
        if request.method == 'POST':               
                delete_playlist = (
                        delete(Playlist).
                        where(Playlist.id == id)
                        )
                local_session.execute(delete_playlist)
                local_session.commit()
 

        stmt = select(Playlist).where(Playlist.id_user == session['userid'])
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

        stmt_song= (
                select(Song.id, Song.title, Song.id_album, Song.length, Album.name.label("name_album"), Album.id.label("id_album"), User.name.label("name_artist"), User.id.label("id_artist")).
                join(PlaylistSong, Song.id == PlaylistSong.id_song).
                join(Album, Song.id_album == Album.id).
                join(SongArtist, Song.id == SongArtist.id_song).
                join(User, User.id == SongArtist.id_artist).
                where(PlaylistSong.id_playlist == id_playlist_selected).
                order_by(PlaylistSong.date_created)
        )

        playlist_stmt = (
                select(Playlist.id, Playlist.name).
                join(User, User.id == Playlist.id_user).
                where(User.id == session['userid'])                
        )

        playlist_list = local_session.execute(playlist_stmt).all()

        playlist_name=None

        for playlist in playlist_list:
                if(id_playlist_selected == playlist.id):
                        playlist_name=playlist.name

        
        songs_list = local_session.execute(stmt_song).all()
        
        num_songs = 0
        tot_length = 0

        for song in songs_list:
                num_songs += 1
                tot_length += song.length

        return render_template("playlist-select.html", songs_list = songs_list, playlist_name = playlist_name, num_songs=num_songs, tot_length=tot_length, actual_playlist=id_playlist_selected,playlist_list=playlist_list)

@views.route('/playlists/<int:id_playlist_selected>/<int:idPlaylist_ToAddSong>/<int:id_song>', methods=['GET', 'POST'])
#@login_required
def playlist_add_song(id_playlist_selected,idPlaylist_ToAddSong, id_song):

        stmt = (
                insert(PlaylistSong).
                values(id_playlist=idPlaylist_ToAddSong).
                values(id_song=id_song)
        )

        local_session.execute(stmt)
        local_session.commit()
        flash('Canzone aggiunta con successo', category='success')

        return get_playlist_selected(id_playlist_selected)

@views.route('/playlists/<int:id_playlist_selected>/<int:id_song>', methods=['GET', 'POST'])
#@login_required
def playlist_remove_song(id_playlist_selected, id_song):

        delete_playlist = (
                        delete(PlaylistSong).
                        where(PlaylistSong.id_playlist==id_playlist_selected).
                        where(PlaylistSong.id_song==id_song)
                        )
        local_session.execute(delete_playlist)
        local_session.commit()

        flash('Canzone eliminata con successo', category='success')

        return get_playlist_selected(id_playlist_selected)

@views.route('/favourites', methods=['GET', 'POST'])
#@login_required
def get_favourite():        

        stmt_song= (
                select(Song.id, Song.title, Song.id_album, Song.length, Album.name.label("name_album"), Album.id.label("id_album"), User.name.label("name_artist"), User.id.label("id_artist")).
                join(PlaylistSong, Song.id == PlaylistSong.id_song).
                join(Album, Song.id_album == Album.id).
                join(SongArtist, Song.id == SongArtist.id_song).
                join(User, User.id == SongArtist.id_artist).
                where(PlaylistSong.id_playlist == session['id_fav_playlist']).
                order_by(PlaylistSong.date_created.desc())
        )

        playlist_stmt = (
                select(Playlist.id, Playlist.name).
                join(User, User.id == Playlist.id_user).
                where(User.id == session['userid'])                
        )

        playlist_list = local_session.execute(playlist_stmt).all()

        
        songs_list = local_session.execute(stmt_song).all()
        
        num_songs = 0
        tot_length = 0

        for song in songs_list:
                num_songs += 1
                tot_length += song.length

        return render_template("favourite-playlist.html", songs_list = songs_list, num_songs=num_songs, tot_length=tot_length,playlist_list=playlist_list)

@views.route('/favourites/<int:idPlaylist_ToAddSong>/<int:id_song>', methods=['GET', 'POST'])
#@login_required
def favourite_add_song(idPlaylist_ToAddSong,id_song):        

        stmt = (
                insert(PlaylistSong).
                values(id_playlist=idPlaylist_ToAddSong).
                values(id_song=id_song)
        )

        local_session.execute(stmt)
        local_session.commit()
        flash('Canzone aggiunta con successo', category='success')               

        return get_favourite()

@views.route('/favourites/<int:id_song>', methods=['GET', 'POST'])
#@login_required
def favourite_remove_song(id_song):

        delete_playlist = (
                        delete(PlaylistSong).
                        where(PlaylistSong.id_playlist==session['id_fav_playlist']).
                        where(PlaylistSong.id_song==id_song)
                        )
        local_session.execute(delete_playlist)
        local_session.commit()

        flash('Canzone eliminata con successo', category='success')

        return get_favourite()

@views.route('/albums', methods=['GET', 'POST'])
#@login_required
def albums():
        stmt = select(Album.name, Album.id)
        album_list = local_session.execute(stmt).all()
        return render_template("albums.html", album_list = album_list)

        

@views.route('/albums/<int:id_album_selected>', methods=['GET', 'POST'])
#@login_required
def get_album_selected(id_album_selected):
        userid = 0
        if session.get('userid'):
                userid =  session['userid']


        stmt_album = (
                select(Album.name).
                where(Album.id == id_album_selected))

        """
        stmt_song=(
                select(Song.id, Song.title, Song.id_album, Song.length, Song.num_in_album, Album.name).
                join(Album, Song.id_album == Album.id).
                where(Album.id == id_album_selected).
                order_by(Song.num_in_album)) 
        """
        stmt_song= (
                select(Song.id, Song.title, Song.num_in_album, Song.length, User.name.label("name_artist"), User.id.label("id_artist")).
                join(SongArtist, Song.id == SongArtist.id_song).
                join(User, User.id == SongArtist.id_artist).
                where(Song.id_album==id_album_selected).
                order_by(Song.num_in_album)
        )

        

        album_name = local_session.execute(stmt_album).scalar()
        #if (album_name==None):
        #       TODO: aggiungere controllo sull'utente che visita la pagina

        songs_list = local_session.execute(stmt_song).all()

        playlist_stmt = (
                select(Playlist.id, Playlist.name).
                join(User, User.id == Playlist.id_user).
                where(User.id == session['userid'])                
        )

        playlist_list = local_session.execute(playlist_stmt).all()

        num_songs = 0
        tot_length = 0

        for song in songs_list:
                num_songs += 1
                tot_length += song.length

        subquery = (
                select(AlbumArtist.id_album).
                where(AlbumArtist.id_artist == session['userid']).
                where(AlbumArtist.id_album == id_album_selected)
        )

        stmt_album_artist = (
                select(Album.name).
                filter(Album.id.in_(subquery))
        )

        album_artist = local_session.execute(stmt_album_artist).scalar()

        list_art= (
                select(User.name).
                where(User.isArtist==True).
                where(User.name != session['username']))

        listArtist_db = local_session.execute(list_art).all()
        
        itemlist = [r[0] for r in listArtist_db]

        list_genre= (select(Genre.name))

        listGenre_db = local_session.execute(list_genre).all()
        
        itemGenrelist = [r[0] for r in listGenre_db]

        if (session['isArtist'] and album_artist):
                return render_template("album-select-artist.html", songs_list = songs_list, album_name = album_name, num_songs=num_songs, tot_length=tot_length, actual_album=id_album_selected, itemlist=itemlist, itemGenrelist=itemGenrelist)
        else:
                return render_template("album-select.html", songs_list = songs_list, album_name = album_name, num_songs=num_songs, tot_length=tot_length, actual_album=id_album_selected)


@views.route('/album_added/<id_album>', methods=['GET', 'POST'])
@login_required
def create_song(id_album):

        if request.method == 'POST':
        
                option = request.form['rad1']         
                titleSong = request.form.get('titleSong')
                yearSong = request.form.get('yearSong')
                minSong = request.form.get('minSong')
                secSong = request.form.get('secSong')

                tot_length = int(minSong) * 60 + int(secSong)

                songs = (
                        select (Song).
                        join(Album, Song.id_album == Album.id)
                )

                count_songs = local_session.execute(select(func.count(Song.id))).scalar_one()

                song = Song(title=titleSong, year=yearSong, length=tot_length, num_in_album = count_songs, id_album=id_album)
                local_session.add(song)
                local_session.commit()
                local_session.flush()
                local_session.refresh(song)

                if (option=="yes"):
                        list_art= (
                                select(User.id, User.name).
                                where(User.isArtist==True).
                                where(User.name != session['username']))

                        listArtist_db = local_session.execute(list_art).all()
                        
                        artist_name_list = [r[1] for r in listArtist_db]

                        artist_id_list = [r[0] for r in listArtist_db]

                        numArtist = request.form['numArtist']
                        count = 0
                        setArtist = set()
                        while(count<int(numArtist)):
                                nameArtist = request.form.get('nameArtist'+str(count))
                                count += 1
                                setArtist.add(nameArtist)                               

                        for artist in setArtist:
                                if(artist in artist_name_list):
                                        index = artist_name_list.index(artist)
                                        album_artist = AlbumArtist(id_album=id_album, id_artist=artist_id_list.__getitem__(index))
                                        local_session.add(album_artist)
                      
                local_session.commit()
        
        return get_album_selected(id_album)

@views.route('/albums/<int:id_album_selected>/<int:idPlaylist_ToAddSong>/<int:id_song>', methods=['GET', 'POST'])
#@login_required
def album_add_song(id_album_selected,idPlaylist_ToAddSong,id_song):
        
        stmt = (
                insert(PlaylistSong).
                values(id_playlist=idPlaylist_ToAddSong).
                values(id_song=id_song)
        )

        local_session.execute(stmt)
        local_session.commit()
        flash('Canzone aggiunta con successo', category='success') 

        return get_album_selected(id_album_selected)

@views.route('/artists')
#@login_required
def artists():
        stmt = select(User.name, User.id).where(User.isArtist == True)
        artist_list = local_session.execute(stmt).all()
        return render_template("artists.html", artist_list = artist_list)

@views.route('/artists/<int:id_artist_selected>', methods=['GET', 'POST'])
#@login_required
def get_artist_selected(id_artist_selected):
        stmt_album = (
                select(Album.id, Album.name, Album.year).
                join(AlbumArtist, Album.id == AlbumArtist.id_album).
                where(AlbumArtist.id_artist == id_artist_selected).
                order_by(Album.year))

        """
        stmt_song=(
                select(Song.id, Song.title, Song.length).
                join(SongArtist, SongArtist.id_song == Song.id).
                where(SongArtist.id_artist == id_artist_selected).
                order_by(Song.num_in_album)).limit(5)                   #TODO da sistemare -> ordinare in base al numero di ascolti
        """

        stmt_song= (
                select(Song.id, Song.title, Song.id_album, Song.length, Album.name.label("name_album"), Album.id.label("id_album")).
                join(PlaylistSong, Song.id == PlaylistSong.id_song).
                join(Album, Song.id_album == Album.id).
                join(SongArtist, Song.id == SongArtist.id_song).
                join(User, User.id == SongArtist.id_artist).
                where(SongArtist.id_artist == id_artist_selected).
                order_by(PlaylistSong.date_created)).limit(5) 


        stmt_artist = (
                select(User.name).
                where(User.id == id_artist_selected).
                where(User.isArtist == True)) 

        artist_name = local_session.execute(stmt_artist).scalar()

        playlist_stmt = (
                select(Playlist.id, Playlist.name).
                join(User, User.id == Playlist.id_user).
                where(User.id == session['userid'])                
        )

        playlist_list = local_session.execute(playlist_stmt).all()

        album_list = local_session.execute(stmt_album).all()
        songs_list = local_session.execute(stmt_song).all()

        tot_length = 0

        for song in songs_list:
                tot_length += song.length

        return render_template("artist-select.html", songs_list = songs_list, album_list = album_list,actual_artist=id_artist_selected, tot_length=tot_length, artist_name=artist_name,playlist_list=playlist_list)

@views.route('/artists/<int:id_artist_selected>/<int:idPlaylist_ToAddSong>/<int:id_song>', methods=['GET', 'POST'])
#@login_required
def artist_add_song(id_artist_selected,idPlaylist_ToAddSong,id_song):
        
        stmt = (
                insert(PlaylistSong).
                values(id_playlist=idPlaylist_ToAddSong).
                values(id_song=id_song)
        )

        local_session.execute(stmt)
        local_session.commit()
        flash('Canzone aggiunta con successo', category='success')

        return get_artist_selected(id_artist_selected)




@views.route('/search', methods=['GET', 'POST'])
#login_required
def search():

        album_found = None
        artist_found = None
        song_found = None
        song_result = None
        album_result = None
        user_result = None
        playlist_list = None

        lookingFor = None

        if request.method == 'POST':
                lookingFor = "Avicii"


        list_art= (
                select(User.name).
                where(User.isArtist==True))

        list_alb= (select(Album.name))

        list_song= (select(Song.title))

        stmt_list = list_art.union(list_alb,list_song)

        dblist = local_session.execute(stmt_list).all()
        
        itemlist = [r[0] for r in dblist]

        return render_template("search.html", list_item=itemlist, song_result=song_result, album_result=album_result,user_result=user_result, playlist_list=playlist_list, lookingFor=lookingFor)

@views.route('/search/', methods=['GET', 'POST'])
@views.route('/search/<result>', methods=['GET', 'POST'])
#login_required
def search_result(result=None):

        album_found = None
        artist_found = None
        song_found = None     

        lookingFor = result  

        if request.method == 'POST':
                lookingFor = request.form['search']


        list_art= (
                select(User.name).
                where(User.isArtist==True))

        list_alb= (select(Album.name))

        list_song= (select(Song.title))

        stmt_list = list_art.union(list_alb,list_song)

        dblist = local_session.execute(stmt_list).all()
        
        itemlist = [r[0] for r in dblist]

        playlist_stmt = (
                select(Playlist.id, Playlist.name).
                join(User, User.id == Playlist.id_user).
                where(User.id == session['userid'])                
        )

        playlist_list = local_session.execute(playlist_stmt).all()

        searchInSong= (
                select(Song.id, Song.title, Song.id_album, Song.length, Album.name.label("name_album"), Album.id.label("id_album"), User.name.label("name_artist"), User.id.label("id_artist")).
                join(Album, Song.id_album == Album.id).
                join(SongArtist, Song.id == SongArtist.id_song).
                join(User, User.id == SongArtist.id_artist).
                where((Song.title).like('%' + lookingFor + '%')).
                order_by(Song.title, Song.year, Song.length)
        )

        searchInAlbum= (
                select(Album.name, Album.year, Album.id).
                where((Album.name).like('%' + lookingFor + '%')).
                order_by(Album.name,Album.year)
        )

        searchInUser= (
                select(User.name, User.id).
                where(User.isArtist == True).
                where((User.name).like('%' + lookingFor + '%')).
                order_by(User.name)
        )

        song_result = local_session.execute(searchInSong).all()
        album_result = local_session.execute(searchInAlbum).all()
        user_result = local_session.execute(searchInUser).all()

        return render_template("search.html", list_item=itemlist, song_result=song_result, album_result=album_result,user_result=user_result, playlist_list=playlist_list,lookingFor=lookingFor)

@views.route('/search/<result>/<int:playlistId>/<int:songId>', methods=['GET', 'POST'])
#login_required
def search_add_song(result, playlistId, songId):

        stmt = (
                insert(PlaylistSong).
                values(id_playlist=playlistId).
                values(id_song=songId)
                )
        local_session.execute(stmt)
        local_session.commit()
        flash('Canzone aggiunta con successo', category='success')

        return search_result(result)

@views.route('/profile')
def profile():
        userid = 0
        if session.get('userid'):
                userid =  session['userid']

        list_art= (
                select(User.name).
                where(User.isArtist==True).
                where(User.name != session['username']))

        stmt_playlist = (
                select(Playlist).
                where(Playlist.id_user == userid))

        stmt_song=(
                select(Song.id, Song.title, Song.length).
                order_by(Song.num_in_album)).limit(5)

        playlists = local_session.execute(stmt_playlist).scalars()
        songs_list = local_session.execute(stmt_song).all()

        listArtist_db = local_session.execute(list_art).all()
        
        itemlist = [r[0] for r in listArtist_db]


        if (session['isArtist']):
                return render_template("artist-profile.html", playlists = playlists, songs_list = songs_list, name = session['username'], itemlist = itemlist)
        else:
                return render_template("user-profile.html", playlists = playlists, songs_list = songs_list, name = session['username'])

@views.route('/album_added', methods=['GET', 'POST'])
@login_required
def create_album():

        if request.method == 'POST':
        
                option = request.form['rad1']         
                nameAlbum = request.form.get('nameAlbum')
                yearAlbum = request.form.get('yearAlbum')

                album = Album(name=nameAlbum, year=yearAlbum)
                local_session.add(album)
                local_session.commit()
                local_session.flush()
                local_session.refresh(album)

                album_artist = AlbumArtist(id_album=album.id, id_artist=session['userid'])
                local_session.add(album_artist)

                if (option=="yes"):
                        list_art= (
                                select(User.id, User.name).
                                where(User.isArtist==True).
                                where(User.name != session['username']))

                        listArtist_db = local_session.execute(list_art).all()
                        
                        artist_name_list = [r[1] for r in listArtist_db]

                        artist_id_list = [r[0] for r in listArtist_db]

                        numArtist = request.form['numArtist']
                        count = 0
                        setArtist = set()
                        while(count<int(numArtist)):
                                nameArtist = request.form.get('nameArtist'+str(count))
                                count += 1
                                setArtist.add(nameArtist)                               

                        for artist in setArtist:
                                if(artist in artist_name_list):
                                        index = artist_name_list.index(artist)
                                        album_artist = AlbumArtist(id_album=album.id, id_artist=artist_id_list.__getitem__(index))
                                        local_session.add(album_artist)
                      
                local_session.commit()
        
        return get_album_selected(album.id)

