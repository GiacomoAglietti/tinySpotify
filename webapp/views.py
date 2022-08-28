from genericpath import exists
from unittest import result
from flask import Blueprint, render_template, request, flash, redirect, session, url_for
from flask_login import login_required, current_user
from sqlalchemy import insert, select, subquery, update, delete, func, exc, desc
from sqlalchemy.orm import aliased
from webapp import db_session, conn
from webapp.models.User import User
from webapp.models.SongArtist import SongArtist
from webapp.models.Song import Song
from webapp.models.PlaylistSong import PlaylistSong
from webapp.models.Playlist import Playlist
from webapp.models.Genre import Genre
from webapp.models.AlbumArtist import AlbumArtist
from webapp.models.Album import Album
from webapp.models.UserPlaylist import UserPlaylist
from webapp.models.MyFunctions import FunctionSession

local_session = db_session()

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
        
        if session.get('userid'):
                return redirect("/home")
        
        return redirect("/login")


@views.route('/home', methods=['GET', 'POST'])
@login_required
def home_authenticated():      


        stmt_playlist =(
                select(Playlist.id, Playlist.name).
                join(UserPlaylist, Playlist.id == UserPlaylist.id_playlist).
                where(UserPlaylist.id_user == session['userid']).
                where(Playlist.isPremium == False).
                order_by(Playlist.name)).limit

        playlist_list = None
        try:                     
                playlist_list = local_session.execute(stmt_playlist).all()
        except exc.SQLAlchemyError as e:
                return str(e.orig)

        for playlist in playlist_list:
                if(playlist.id == session['id_fav_playlist']):
                        playlist_list.remove(playlist)

        
        genre_playlists = None
        list_songs_raccomemded =None
        if(session['isPremium']):
         

                genre_playlists_stmt = (select(Playlist.id, Playlist.name).
                        join(UserPlaylist, Playlist.id == UserPlaylist.id_playlist).
                        where(UserPlaylist.id_user == session['userid']).
                        where(Playlist.isPremium == True))

                stmt_genre=(
                        select(Song.genre).
                        join(SongArtist, SongArtist.id_song == Song.id).
                        where(SongArtist.id_artist == session['userid']).
                        group_by(Song.genre).
                        order_by(desc(func.sum(Song.num_of_plays))).limit(1)
                )

                songs_already_added_stmt = (
                                select(PlaylistSong.id_song).
                                join(UserPlaylist, UserPlaylist.id_playlist == PlaylistSong.id_playlist).
                                where(UserPlaylist.id_user == session['userid'])
                )              
                

                if(session['isArtist']):                      
      
                        songs_created_stmt = (
                                select(SongArtist.id_song).
                                where(SongArtist.id_artist == session['userid'])
                        )
                        stmt_songs_raccomended=(
                                select(Song.id,  Song.title, Song.length, func.sum(Song.num_of_plays).label('tot_plays_genre'), Album.name.label("name_album"), Album.id.label("id_album"), User.name.label("name_artist"), User.id.label("id_artist")).
                                join(SongArtist, SongArtist.id_song == Song.id).
                                join(User, User.id == SongArtist.id_artist).
                                join(Album, Song.id_album == Album.id).
                                where(SongArtist.id_artist == session['userid']).
                                where(Song.genre.in_(stmt_genre)).
                                where(Song.id.notin_(songs_already_added_stmt)).
                                where(Song.id.notin_(songs_created_stmt)).
                                group_by(Song.id,  Song.title, Song.length, Album.name.label("name_album"), Album.id.label("id_album"), User.name.label("name_artist"), User.id.label("id_artist")).
                                order_by(desc(func.sum(Song.num_of_plays))).limit(5)
                        )
                else:
                        stmt_songs_raccomended=(
                                select(Song.id,  Song.title, Song.length, func.sum(Song.num_of_plays).label('tot_plays_genre'), Album.name.label("name_album"), Album.id.label("id_album"), User.name.label("name_artist"), User.id.label("id_artist")).
                                join(SongArtist, SongArtist.id_song == Song.id).
                                join(User, User.id == SongArtist.id_artist).
                                join(Album, Song.id_album == Album.id).
                                where(SongArtist.id_artist == session['userid']).
                                where(Song.genre.in_(stmt_genre)).
                                where(Song.id.notin_(songs_already_added_stmt)).
                                group_by(Song.id,  Song.title, Song.length, Album.name.label("name_album"), Album.id.label("id_album"), User.name.label("name_artist"), User.id.label("id_artist")).
                                order_by(desc(func.sum(Song.num_of_plays))).limit(5)
                        )
        
                try:
                        genre_playlists = local_session.execute(genre_playlists_stmt).all()
                        list_songs_raccomemded = local_session.execute(stmt_songs_raccomended).all()                        
                except exc.SQLAlchemyError as e:
                        return str(e.orig)        

        return render_template("home.html" , genre_playlists=genre_playlists, list_songs_raccomemded=list_songs_raccomemded,playlist_list=playlist_list)

@views.route('/home/<int:idPlaylist_ToAddSong>/<int:id_song>', methods=['GET', 'POST'])
@login_required
def home_add_song(idPlaylist_ToAddSong,id_song):      

        FunctionSession.insert_playlist_song(idPlaylist_ToAddSong, id_song)              

        return home_authenticated()

@views.route('/create-playlist', methods=['GET', 'POST'])
@login_required
def create_playlist():

        if request.method == 'POST':
                nomePlaylist = request.form.get('nomePlaylist')

                newPlaylist = Playlist(name = nomePlaylist)
                cur = conn.cursor()

                try:
                        local_session.add(newPlaylist)
                        local_session.commit()
                        local_session.flush()
                        local_session.refresh(newPlaylist)

                        cur.execute("CALL add_user_playlist(%s, %s);", [session['userid'], newPlaylist.id])    

                        conn.commit()
                except exc.SQLAlchemyError as e:
                        local_session.rollback()
                        return str(e.orig)
                finally:
                        cur.close()
                        local_session.close()   

                     

        playlists = FunctionSession.get_user_playlist(False)

        return render_template("playlists.html", playlists = playlists)

@views.route('/playlists', methods=['GET', 'POST'])
@login_required
def playlists():

        playlists = None

        stmt = (
                select(Playlist.id, Playlist.name).
                join(UserPlaylist, Playlist.id == UserPlaylist.id_playlist).
                where(UserPlaylist.id_user == session['userid']).
                where(Playlist.isPremium == False).
                where(UserPlaylist.id_playlist != session['id_fav_playlist']))
        try:
                playlists = local_session.execute(stmt).all()
                
        except exc.SQLAlchemyError as e:
                return str(e.orig)


        return render_template("playlists.html", playlists = playlists)

@views.route('/playlists/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_playlist(id):
        if request.method == 'POST':               
                delete_playlist = (
                        delete(Playlist).
                        where(Playlist.id == id))

                try:
                        local_session.execute(delete_playlist)
                        local_session.commit()

                except exc.SQLAlchemyError as e:
                        local_session.rollback()
                        return str(e.orig)
                finally:                        
                        local_session.close() 
               
        playlists = FunctionSession.get_user_playlist(False)

        return render_template("playlists.html", playlists = playlists)

@views.route('/playlists/<int:id_playlist_selected>', methods=['GET', 'POST'])
@login_required
def get_playlist_selected(id_playlist_selected):
        if request.method == 'POST':                            
                if 'change-name-playlist' in request.form:
                        nomePlaylist = request.form.get('nomePlaylist')
                        update_playlist = (
                                update(Playlist).
                                where(Playlist.id == id_playlist_selected).
                                values(name=nomePlaylist)
                                )

                        try:
                                local_session.execute(update_playlist)
                                local_session.commit()

                        except exc.SQLAlchemyError as e:
                                local_session.rollback()
                                return str(e.orig)
                        finally:                        
                                local_session.close()

        songs_list = (
                select(Song.id).
                join(PlaylistSong, Song.id == PlaylistSong.id_song).
                where(PlaylistSong.id_playlist == id_playlist_selected))

        stmt_song= (
                select(Song.id, Song.title, Song.id_album, Song.length, Album.name.label("name_album"), Album.id.label("id_album"), User.name.label("name_artist"), User.id.label("id_artist")).
                join(Album, Song.id_album == Album.id).
                join(SongArtist, Song.id == SongArtist.id_song).
                join(User, User.id == SongArtist.id_artist).
                filter(Song.id.in_(songs_list)).
                order_by(Song.date_created)
        )

        

        stmt_playlist =(
                select(Playlist.id, Playlist.name).
                join(UserPlaylist, Playlist.id == UserPlaylist.id_playlist).
                where(UserPlaylist.id_user == session['userid']).
                where(Playlist.isPremium == False).
                order_by(Playlist.name))

        songsPlaylist = None
        playlist_list = None

        try:            
            songsPlaylist = local_session.execute(stmt_song).all()
            playlist_list = local_session.execute(stmt_playlist).all()
                
        except exc.SQLAlchemyError as e:
            return str(e.orig)

        playlist_name=None

        for playlist in playlist_list:
                if(id_playlist_selected == playlist.id):
                        playlist_name=playlist.name

        num_songs = 0
        tot_length = 0

        for song in songsPlaylist:
                num_songs += 1
                tot_length += song.length

        return render_template("playlist-select.html", songs_list = songsPlaylist, playlist_name = playlist_name, num_songs=num_songs, tot_length=tot_length, actual_playlist=id_playlist_selected,playlist_list=playlist_list, isPlPremium=False)

@views.route('/playlists/<string:name_playlist_selected>', methods=['GET', 'POST'])
@login_required
def get_premium_playlist_selected(name_playlist_selected):


        stmt_song= (
                select(Song.id, Song.title, Song.genre, Song.length, func.sum(Song.num_of_plays).label('tot_plays_genre'),  Album.name.label("name_album"), Album.id.label("id_album"), User.name.label("name_artist"), User.id.label("id_artist")).
                join(Album, Song.id_album == Album.id).
                join(SongArtist, Song.id == SongArtist.id_song).
                join(User, User.id == SongArtist.id_artist).
                where(Song.genre == name_playlist_selected).
                group_by(Song.genre, Song.id, Song.title, Song.length, Album.name.label("name_album"), Album.id.label("id_album"), User.name.label("name_artist"), User.id.label("id_artist")).
                order_by(desc(func.sum(Song.num_of_plays))).limit(10)
        )

        stmt_playlist =(
                select(Playlist.id, Playlist.name, Playlist.isPremium).
                join(UserPlaylist, Playlist.id == UserPlaylist.id_playlist).
                where(UserPlaylist.id_user == session['userid']).
                order_by(Playlist.name))

        songsPlaylist = None
        all_playlist_list = None

        try:            
            songsPlaylist = local_session.execute(stmt_song).all()
            all_playlist_list = local_session.execute(stmt_playlist).all()
                
        except exc.SQLAlchemyError as e:
            return str(e.orig)

        id_playlist_selected=None
        isPlPremium = False
        playlist_list = []

        for playlist in all_playlist_list:
                if(playlist.isPremium):
                        if(name_playlist_selected == playlist.name):
                                id_playlist_selected=playlist.id
                                isPlPremium = True
                else:
                        playlist_list.append(playlist)          
        
        num_songs = 0
        tot_length = 0

        for song in songsPlaylist:
                num_songs += 1
                tot_length += song.length

        return render_template("playlist-select.html", songs_list = songsPlaylist, playlist_name = name_playlist_selected, num_songs=num_songs, tot_length=tot_length, actual_playlist=id_playlist_selected,playlist_list=playlist_list, isPlPremium=isPlPremium)


@views.route('/playlists/<int:id_playlist_selected>/<int:idPlaylist_ToAddSong>/<int:id_song>', methods=['GET', 'POST'])
@login_required
def playlist_add_song(id_playlist_selected,idPlaylist_ToAddSong, id_song):

        FunctionSession.insert_playlist_song(idPlaylist_ToAddSong, id_song)

        return get_playlist_selected(id_playlist_selected)

@views.route('/playlists/<int:id_playlist_selected>/<int:id_song>', methods=['GET', 'POST'])
@login_required
def playlist_remove_song(id_playlist_selected, id_song):

        delete_playlist = (
                        delete(PlaylistSong).
                        where(PlaylistSong.id_playlist==id_playlist_selected).
                        where(PlaylistSong.id_song==id_song)
                        )

                
        try:
                local_session.execute(delete_playlist)
                local_session.commit()

        except exc.SQLAlchemyError as e:
                local_session.rollback()
                return str(e.orig)
        finally:                        
                local_session.close()

        flash('Canzone eliminata con successo', category='success')

        return get_playlist_selected(id_playlist_selected)

@views.route('/favourites', methods=['GET', 'POST'])
@login_required
def get_favourite():


        songs_list = (
                select(Song.id).
                join(PlaylistSong, Song.id == PlaylistSong.id_song).
                where(PlaylistSong.id_playlist == session['id_fav_playlist']))

        stmt_song= (
                select(Song.id, Song.title, Song.length, Album.name.label("name_album"), Album.id.label("id_album"), User.name.label("name_artist"), User.id.label("id_artist")).
                join(Album, Song.id_album == Album.id).
                join(SongArtist, Song.id == SongArtist.id_song).
                join(User, User.id == SongArtist.id_artist).
                filter(Song.id.in_(songs_list)).
                order_by(Song.date_created.desc())
        )

        playlist_list = None
        songsPlaylist = None

        stmt = (
        select(Playlist.id, Playlist.name).
                join(UserPlaylist, Playlist.id == UserPlaylist.id_playlist).
                where(UserPlaylist.id_user == session['userid']).
                where(Playlist.id != session['id_fav_playlist']))
        
        try:            
                playlist_list = local_session.execute(stmt).all()
                songsPlaylist = local_session.execute(stmt_song).all()                
        except exc.SQLAlchemyError as e:
                return str(e.orig)
        
        num_songs = 0
        tot_length = 0

        for song in songsPlaylist:
                num_songs += 1
                tot_length += song.length

        return render_template("favourite-playlist.html", songs_list = songsPlaylist, num_songs=num_songs, tot_length=tot_length,playlist_list=playlist_list)

@views.route('/favourites/<int:idPlaylist_ToAddSong>/<int:id_song>', methods=['GET', 'POST'])
@login_required
def favourite_add_song(idPlaylist_ToAddSong,id_song):      

        FunctionSession.insert_playlist_song(idPlaylist_ToAddSong, id_song)              

        return get_favourite()

@views.route('/favourites/<int:id_song>', methods=['GET', 'POST'])
@login_required
def favourite_remove_song(id_song):

        deletePlaylistSong = (
                        delete(PlaylistSong).
                        where(PlaylistSong.id_playlist==session['id_fav_playlist']).
                        where(PlaylistSong.id_song==id_song)
                        )
        
        
        try:
                local_session.execute(deletePlaylistSong)
                local_session.commit()

        except exc.SQLAlchemyError as e:
                local_session.rollback()
                return str(e.orig)
        finally:                        
                local_session.close()

        flash('Canzone eliminata con successo', category='success')

        return get_favourite()

@views.route('/albums', methods=['GET', 'POST'])
@login_required
def albums():

        album_list = FunctionSession.get_albums_list()

        return render_template("albums.html", album_list = album_list)
        
@views.route('/albums/<int:id_album_selected>', methods=['GET', 'POST'])
@login_required
def get_album_selected(id_album_selected):

        itemArtistlist = None
        itemGenrelist = None

        stmt_album = (
                select(Album.name).
                where(Album.id == id_album_selected))
        
        stmt_song= (
                select(Song.id, Song.title, Song.length, Song.num_of_plays, User.name.label("name_artist"), User.id.label("id_artist")).
                join(SongArtist, Song.id == SongArtist.id_song).
                join(User, User.id == SongArtist.id_artist).
                where(Song.id_album==id_album_selected).
                order_by(Song.date_created)
        )

        album_name = None    
        songs_list = None

        try:
                album_name = local_session.execute(stmt_album).scalar() 
                #if (album_name==None):
                #       TODO: aggiungere controllo sull'utente che visita la pagina
                songs_list = local_session.execute(stmt_song).all()       
                
        except exc.SQLAlchemyError as e:
                return str(e.orig)

        num_songs = 0
        tot_length = 0

        for song in songs_list:
                num_songs += 1
                tot_length += song.length

        playlist_list = FunctionSession.get_user_playlist(True)

        if(session['isArtist']):

                amIowner = (
                        select(AlbumArtist.id_artist).
                        where(AlbumArtist.id_artist == session['userid']).
                        where(AlbumArtist.id_album == id_album_selected)
                )

                #stmt_album_artist = (
                #        select(Album.name).
                #        filter(Album.id.in_(subquery))
                #)        
         
                #album_artist = None        
                result = None        

                try:
                        result = local_session.execute(amIowner).scalar()    
                        
                except exc.SQLAlchemyError as e:
                        return str(e.orig)     

                listArtist_db = FunctionSession.get_artists_list(True)      
                list_genre= FunctionSession.get_genre_list()

                itemArtistlist = [r[0] for r in listArtist_db]
                itemGenrelist = [r[0] for r in list_genre]             

                return render_template("album-select.html", songs_list = songs_list, album_name = album_name, num_songs=num_songs, tot_length=tot_length, actual_album=id_album_selected, playlist_list=playlist_list, itemArtistlist=itemArtistlist, itemGenrelist=itemGenrelist, owner = result)

        return render_template("album-select.html", songs_list = songs_list, album_name = album_name, num_songs=num_songs, tot_length=tot_length, actual_album=id_album_selected,playlist_list=playlist_list, itemArtistlist=[], itemGenrelist=[], owner = False)


@views.route('/album_added/<id_album>', methods=['GET', 'POST'])
@login_required
def create_song(id_album):

        if request.method == 'POST':
        
                option = request.form['rad1']         
                titleSong = request.form.get('titleSong')
                yearSong = request.form.get('yearSong')

                minSong= request.form.get('minSong')
                secSong= request.form.get('secSong')
                genreSong = request.form.get('selectGenre')


                tot_length = int(minSong) * 60 + int(secSong)


                song = Song(title=titleSong, year=yearSong, length=tot_length,id_album=id_album, genre=genreSong)

                try:
                        local_session.add(song)
                        local_session.commit()
                        local_session.flush()
                        local_session.refresh(song)


                except exc.SQLAlchemyError as e:
                        local_session.rollback()
                        return str(e.orig)
                finally:                        
                        local_session.close()



                song_artist = SongArtist(id_song=song.id, id_artist=session['userid'])
                local_session.add(song_artist)


                if (option=="yes"):
                        listArtist_db = FunctionSession.get_artists_list(True)
                        
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
                                        song_artist = SongArtist(id_song=song.id, id_artist=artist_id_list.__getitem__(index))
                                        local_session.add(song_artist)
 
                try:
                        local_session.commit()
                except exc.SQLAlchemyError as e:
                        local_session.rollback()
                        return str(e.orig)
                finally:                        
                        local_session.close()
        
        return get_album_selected(id_album)

@views.route('/albums/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_album(id):
        if request.method == 'POST':               
                delete_playlist = (
                        delete(Album).
                        where(Album.id == id))

                try:
                        local_session.execute(delete_playlist)
                        local_session.commit()

                except exc.SQLAlchemyError as e:
                        local_session.rollback()
                        return str(e.orig)
                finally:                        
                        local_session.close() 
               
                album_list = FunctionSession.get_albums_list()


                return render_template("albums.html", album_list = album_list)
        #else:
                #return error_page


@views.route('/albums/<int:id_album_selected>/<int:idPlaylist_ToAddSong>/<int:id_song>', methods=['GET', 'POST'])
@login_required
def album_add_song(id_album_selected,idPlaylist_ToAddSong,id_song):

        FunctionSession.insert_playlist_song(idPlaylist_ToAddSong, id_song)

        return get_album_selected(id_album_selected)

"""
@views.route('/artists')   #da togliere?
@login_required
def artists():
        stmt = select(User.name, User.id).where(User.isArtist == True)
        artist_list = local_session.execute(stmt).all()
        return render_template("artists.html", artist_list = artist_list)
"""

@views.route('/artists/<int:id_artist_selected>', methods=['GET', 'POST'])
@login_required
def get_artist_selected(id_artist_selected):


        album_list = FunctionSession.get_albums_list()

        stmt_song= (
                select(Song.id, Song.title, Song.length, Album.name.label("name_album"), Album.id.label("id_album")).
                join(Album, Song.id_album == Album.id).
                join(SongArtist, Song.id == SongArtist.id_song).
                where(SongArtist.id_artist == id_artist_selected).
                order_by(Song.num_of_plays)).limit(5) 


        stmt_artist = (
                select(User.name).
                where(User.id == id_artist_selected).
                where(User.isArtist == True)) 

        artist_name = None
        songs_list = None

        try:
                artist_name = local_session.execute(stmt_artist).scalar()
                songs_list = local_session.execute(stmt_song).all()
              
        except exc.SQLAlchemyError as e:
                return str(e.orig)

        
        playlist_list = FunctionSession.get_user_playlist(True)

        tot_length = 0

        for song in songs_list:
                tot_length += song.length

        return render_template("artist-select.html", songs_list = songs_list, album_list = album_list,actual_artist=id_artist_selected, tot_length=tot_length, artist_name=artist_name,playlist_list=playlist_list)

@views.route('/artists/<int:id_artist_selected>/<int:idPlaylist_ToAddSong>/<int:id_song>', methods=['GET', 'POST'])
@login_required
def artist_add_song(id_artist_selected,idPlaylist_ToAddSong,id_song):

        FunctionSession.insert_playlist_song(idPlaylist_ToAddSong, id_song)

        return get_artist_selected(id_artist_selected)




@views.route('/search', methods=['GET', 'POST'])
@login_required
def search():

        song_result = None
        album_result = None
        user_result = None
        playlist_list = None

        lookingFor = None

        if request.method == 'POST':
                #lookingFor = "Avicii"
                lookingFor = request.form['search']


        list_art= ( select(User.name).
                    where(User.isArtist==True))


        list_alb= (select(Album.name))
        list_song= (select(Song.title))
        stmt_list = list_art.union(list_alb,list_song)
        dblist = None

        try:                       
                dblist = local_session.execute(stmt_list).all()
                
        except exc.SQLAlchemyError as e:
                return str(e.orig)

        itemlist = [r[0] for r in dblist]

        return render_template("search.html", list_item=itemlist, song_result=song_result, album_result=album_result,user_result=user_result, playlist_list=playlist_list, lookingFor=lookingFor)

@views.route('/search/', methods=['GET', 'POST'])
@views.route('/search/<result>', methods=['GET', 'POST'])
@login_required
def search_result(result=None):
  

        lookingFor = result  

        if request.method == 'POST':
                lookingFor = request.form['search']


        list_art= ( select(User.name).
                    where(User.isArtist==True))

        list_alb= (select(Album.name))

        list_song= (select(Song.title))

        stmt_list = list_art.union(list_alb,list_song)

        dblist = None

        try:                       
                dblist = local_session.execute(stmt_list).all()
        except exc.SQLAlchemyError as e:
                return str(e.orig)

        
        itemlist = [r[0] for r in dblist]

        playlist_list = FunctionSession.get_user_playlist(True)

        searchInSong= (
                select(Song.id, Song.title, Song.length, Album.name.label("name_album"), Album.id.label("id_album"), User.name.label("name_artist"), User.id.label("id_artist")).
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

        song_result = None
        album_result = None
        user_result = None

        try:                       
                song_result = local_session.execute(searchInSong).all()
                album_result = local_session.execute(searchInAlbum).all()
                user_result = local_session.execute(searchInUser).all()

        except exc.SQLAlchemyError as e:
                return str(e.orig)

        return render_template("search.html", list_item=itemlist, song_result=song_result, album_result=album_result,user_result=user_result, playlist_list=playlist_list,lookingFor=lookingFor)

@views.route('/search/<result>/<int:playlistId>/<int:songId>', methods=['GET', 'POST'])
@login_required
def search_add_song(result, playlistId, songId):

        FunctionSession.insert_playlist_song(playlistId, songId)
        

        return search_result(result)

@views.route('/profile')
@login_required
def profile():

        if (session['isArtist']):

                listArtist_db = FunctionSession.get_artists_list(False)    


                playlist_list = FunctionSession.get_user_playlist(True)

                stmt_count_song=(
                        select(func.count(Song.id)).
                        join(SongArtist, Song.id == SongArtist.id_song).
                        where(SongArtist.id_artist == session['userid'])
                )

                stmt_count_album=(
                        select(func.count(Album.id)).
                        join(AlbumArtist, AlbumArtist.id_album == Album.id).
                        where(AlbumArtist.id_artist == session['userid'])
                )

                stmt_genre=(
                        select(Song.genre, func.sum(Song.num_of_plays).label('tot_plays_genre')).
                        join(SongArtist, SongArtist.id_song == Song.id).
                        where(SongArtist.id_artist == session['userid']).
                        group_by(Song.genre).
                        order_by(desc(func.sum(Song.num_of_plays))).limit(1)
                )

                stmt_song=(
                        select(Song.id, Song.title, Song.length, Song.num_of_plays).
                        join(SongArtist, SongArtist.id_song == Song.id).
                        where(SongArtist.id_artist == session['userid']).
                        order_by(desc(Song.num_of_plays))).limit(5)

                stmt_album=(
                        select(Album.id, Album.name, func.sum(Song.num_of_plays).label('tot_plays')).
                        join(Song, Song.id_album == Album.id).
                        join(AlbumArtist, AlbumArtist.id_album == Album.id).
                        where(AlbumArtist.id_artist == session['userid']).
                        group_by(Album.id)).limit(5)

                album_list = None
                songs_list = None

                count_song = None
                count_album = None
                top_genre = None

                try:
                        album_list = local_session.execute(stmt_album).all()
                        songs_list = local_session.execute(stmt_song).all()
                        top_genre = local_session.execute(stmt_genre).all()
                        count_song = local_session.execute(stmt_count_song).scalar()
                        count_album = local_session.execute(stmt_count_album).scalar()
                        
                except exc.SQLAlchemyError as e:
                        return str(e.orig)
                
                itemlist = [r[0] for r in listArtist_db]


                return render_template("artist-profile.html", playlists = playlist_list, album_list = album_list, songs_list = songs_list,  itemlist = itemlist, count_song = count_song, count_album = count_album, top_genre = top_genre)
        else:
                return render_template("user-profile.html")

@views.route('/profile/premium-subscription', methods=['GET', 'POST'])
@login_required
def premium_subscription():

        if request.method == 'POST':
                update_user = (
                        update(User).
                        where(User.id == session['userid']).
                        values(isPremium=True)
                        )

                stmt_playlist_premium = (
                        select(Playlist.id).
                        where(Playlist.isPremium == True)
                        ) 


                try:
                        local_session.execute(update_user)
                        id_playlist_premium = local_session.execute(stmt_playlist_premium).all()
                        for playlist in id_playlist_premium:
                                userplaylist = UserPlaylist(id_playlist=playlist.id , id_user=session['userid'])
                                local_session.add(userplaylist)

                        local_session.commit()

                except exc.SQLAlchemyError as e:
                        local_session.rollback()
                        return str(e.orig)
                finally:                        
                        local_session.close()
                
        return redirect(url_for('auth.logout'))

@views.route('/album_added', methods=['GET', 'POST'])
@login_required
def create_album():

        if request.method == 'POST':
        
                option = request.form['rad1']         
                nameAlbum = request.form.get('nameAlbum')
                yearAlbum = request.form.get('yearAlbum')

                album = Album(name=nameAlbum, year=yearAlbum)

                try:
                        local_session.add(album)
                        local_session.commit()
                        local_session.flush()
                        local_session.refresh(album)

                except exc.SQLAlchemyError as e:
                        local_session.rollback()
                        return str(e.orig)
                finally:                        
                        local_session.close()

                

                album_artist = AlbumArtist(id_album=album.id, id_artist=session['userid'])
                local_session.add(album_artist)

                if (option=="yes"):
                        listArtist_db = FunctionSession.get_artists_list(True)
                        
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
                      
                      
                try:
                        local_session.commit()
                except exc.SQLAlchemyError as e:
                        local_session.rollback()
                        return str(e.orig)
                finally:                        
                        local_session.close()
        
        return get_album_selected(album.id)

