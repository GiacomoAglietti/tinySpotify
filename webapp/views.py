from calendar import month
from flask import Blueprint, render_template, request, flash, redirect, session, url_for
from flask_login import login_required, current_user
from sqlalchemy import select, update, delete, func, exc, desc, or_, and_, extract
from webapp import db_session
from functools import wraps
from webapp.models.User import User
from webapp.models.SongArtist import SongArtist
from webapp.models.Song import Song
from webapp.models.PlaylistSong import PlaylistSong
from webapp.models.Playlist import Playlist
from webapp.models.AlbumArtist import AlbumArtist
from webapp.models.Album import Album
from webapp.models.UserPlaylist import UserPlaylist
from webapp.models.MyFunctions import FunctionSession

local_session = db_session()

views = Blueprint('views', __name__)

def require_role(role_nedeed):
        """Function used to create a new decorator for user roles

        Parameters
        ----------
        role_nedeed : list
                The list of strings of roles nedeed to access in the specific endpoint

        Returns
        -------
        If the current user's role isn't in the list then page_not_found function is returned, otherwise it allows access to the endpoint to the user 
        """

        def wrapper(fn):
            @wraps(fn)
            def decorated_view(*args, **kwargs):

                if (current_user.role not in role_nedeed):
                    return page_not_found()      
                return fn(*args, **kwargs)

            return decorated_view
        return wrapper

@views.route('/', methods=['GET', 'POST'])
def home():
        """Function that redirect the user based on the session

        Returns
        -------
        if the userid is in the session then the user is redirected to the home, otherwise at login

        """
        
        if session.get('userid'):
                return redirect("/home")
        
        return redirect("/login")


@views.route('/home', methods=['GET', 'POST'])
@login_required
def home_authenticated():
        """Function used to load from the database informations about user's playlist and, only if the user is premium, all premium contents

        Returns
        -------
        Return the template "home.html"

        """   
           


        stmt_playlist =(
                select(Playlist.id, Playlist.name).
                join(UserPlaylist, Playlist.id == UserPlaylist.id_playlist).
                where(UserPlaylist.id_user == session['userid']).
                where(Playlist.isPremium == False).
                order_by(Playlist.name))

        playlist_list = None
        try:                     
                playlist_list = local_session.execute(stmt_playlist).all()
        except exc.SQLAlchemyError as e:
                return str(e.orig)

        for playlist in playlist_list:
                if(playlist.id == session['id_fav_playlist']):
                        playlist_list.remove(playlist)

        
        genre_playlists = None
        if(session['role']=="UserPremium" or session['role']=="ArtistPremium" or session['role']=="Admin" ):
         

                genre_playlists_stmt = (select(Playlist.id, Playlist.name).
                        join(UserPlaylist, Playlist.id == UserPlaylist.id_playlist).
                        where(UserPlaylist.id_user == session['userid']).
                        where(Playlist.isPremium == True))

                reccomended_stmt = (
                        select(Song.id, Song.title, Album.name.label('name_album'), Song.length, SongArtist.id_artist, Song.id_album, Song.num_of_plays).
                        join(Album, Album.id == Song.id_album).
                        join(SongArtist, SongArtist.id_song == Song.id).
                        where(extract('month',Song.date_created) == extract('month', func.current_date())).
                        order_by(desc(Song.num_of_plays)).limit(10)
                )              
        
        
                try:
                        genre_playlists = local_session.execute(genre_playlists_stmt).all() 
                        list_songs_reccomended = local_session.execute(reccomended_stmt).all()                      
                except exc.SQLAlchemyError as e:
                        return str(e.orig)

        return render_template("home.html" , genre_playlists=genre_playlists, playlist_list=playlist_list, list_songs_reccomended = list_songs_reccomended)

@views.route('/home/<int:idPlaylist_ToAddSong>/<int:id_song>', methods=['GET', 'POST'])
@login_required
def home_add_song(idPlaylist_ToAddSong,id_song):
        """Function used to add a song into the playlist from home page

        Decorators
        ----------
        @login_required

        Parameters
        ----------
        idPlaylist_ToAddSong : int
            The id of the playlist to which we want to add the song
        id_song : int
            The id of the song

        Returns
        -------
            Return the function home_authenticated()
        """       

        FunctionSession.insert_song_playlist(idPlaylist_ToAddSong, id_song)              

        return home_authenticated()

@views.route('/create-playlist', methods=['GET', 'POST'])
@login_required
def create_playlist():
        """Function used to create a playlist

        Decorators
        ----------
        @login_required

        Returns
        -------
            Return the function home_authenticated()
        """   

        if request.method == 'POST':
                if request.form["create_playlist"]=="create_playlist":
                        nomePlaylist = request.form.get('nomePlaylist')

                        newPlaylist = Playlist(name = nomePlaylist)
                        try:
                                local_session.add(newPlaylist)
                                local_session.commit()
                                local_session.flush()
                                local_session.refresh(newPlaylist)

                                user_playlist = UserPlaylist(id_playlist=newPlaylist.id, id_user=session['userid'])

                                local_session.add(user_playlist)                
                                local_session.commit()

                                flash('Playlist creata con successo', category='success')
                        except exc.SQLAlchemyError as e:
                                local_session.rollback()
                                return str(e.orig)
                        finally:
                                local_session.close()   

        return home_authenticated()

@views.route('/playlists/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_playlist(id):
        """Function to delete a playlist

        Decorators
        ----------
        @login_required

        Parameters
        ----------
        id : int
            The id of the playlist to delete

        Returns
        -------
            Return the function home_authenticated()
        """ 
        if request.method == 'POST':               
                delete_playlist = (
                        delete(Playlist).
                        where(Playlist.id == id))

                try:
                        local_session.execute(delete_playlist)
                        local_session.commit()

                        flash('Playlist eliminata con successo', category='success')
                except exc.SQLAlchemyError as e:
                        local_session.rollback()
                        return str(e.orig)
                finally:                        
                        local_session.close() 

        return home_authenticated()

@views.route('/playlists/<int:id_playlist_selected>', methods=['GET', 'POST'])
@login_required
def get_playlist_selected(id_playlist_selected):
        """Function to load all songs of a playlist and all user's playlist in case he wants to add a song to one of his playlists. 
        Songs are sorted in descending order according to their date of inclusion in the playlist
        It handle also the possibilty of change the playlist's name throught a post request

        Decorators
        ----------
        @login_required

        Parameters
        ----------
        id_playlist_selected : int
            The id of the playlist that the user has selected

        Returns
        -------
            Return the template "playlist-select.html"
        """ 

        if request.method == 'POST':  
                if request.form["change-name-playlist"]=="change-name-playlist":                          
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


        stmt_song= (
                select(Song.id, Song.title, Song.id_album, Song.length, Album.name.label("name_album"), Album.id.label("id_album"), User.name.label("name_artist"), User.id.label("id_artist")).
                join(PlaylistSong, Song.id == PlaylistSong.id_song).
                join(Album, Song.id_album == Album.id).
                join(SongArtist, Song.id == SongArtist.id_song).
                join(User, User.id == SongArtist.id_artist).
                where(PlaylistSong.id_playlist == id_playlist_selected).
                order_by(PlaylistSong.date_created, Song.id)
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

        if(playlist_name is None):
                return page_not_found()


        i = 0 
        while i < len(songsPlaylist)-1:
                if(songsPlaylist[i].id == songsPlaylist[i+1].id):
                        x=i
                        dict_artist={}
                        dict_artist["id"] = songsPlaylist[x].id
                        dict_artist["title"] = songsPlaylist[x].title
                        dict_artist["length"] = songsPlaylist[x].length
                        dict_artist["name_album"] = songsPlaylist[x].name_album
                        dict_artist["id_album"] = songsPlaylist[x].id_album
                        dict_artist["artists_data"] = {}
                        dict_artist["artists_data"]['artist'+str(x)] = []
                        dict_artist["artists_data"]['artist'+str(x)].append(songsPlaylist[x].id_artist)
                        dict_artist["artists_data"]['artist'+str(x)].append(songsPlaylist[x].name_artist)
                        j=i+1
                        y=j
                        while (j < len(songsPlaylist)) and (songsPlaylist[i].id == songsPlaylist[j].id) :
                                dict_artist["artists_data"]['artist'+str(y)] = []
                                dict_artist["artists_data"]['artist'+str(y)].append(songsPlaylist[j].id_artist)
                                dict_artist["artists_data"]['artist'+str(y)].append(songsPlaylist[j].name_artist)
                                songsPlaylist.pop(j)
                                y=y+1

                        songsPlaylist.pop(i)
                        songsPlaylist.insert(i,dict_artist)
                i=i+1

                
        
        num_songs = len(songsPlaylist)

        return render_template("playlist-select.html", songs_list = songsPlaylist, playlist_name = playlist_name, num_songs=num_songs, actual_playlist=id_playlist_selected,playlist_list=playlist_list, isPlPremium=False)

@views.route('/playlists/<string:name_playlist_selected>', methods=['GET', 'POST'])
@login_required
@require_role(role_nedeed=['Admin','ArtistPremium','UserPremium'])
def get_premium_playlist_selected(name_playlist_selected):
        """Function to load the top 10 songs of a premium playlist and all user's playlist in case he wants to add a song to one of his playlists. 
        Songs are sorted in descending order according to their number of plays and their id.
        This endpoint is only accessible to users with the following roles: 'Admin','ArtistPremium','UserPremium'.

        Decorators
        ----------
        @login_required
        @require_role

        Parameters
        ----------
        id_playlist_selected : int
            The id of the playlist that the user has selected

        Returns
        -------
            Return the template "playlist-select.html"
        """ 

        stmt_song_subquery= (
                select(Song.id).
                where(Song.genre == name_playlist_selected).
                group_by(Song.id).
                order_by(desc(func.sum(Song.num_of_plays))).limit(10)
        )

        stmt_song= (
                select(Song.id, Song.title, Song.length, func.sum(Song.num_of_plays).label('tot_plays_genre'),
                  Album.name.label("name_album"), Album.id.label("id_album"), User.name.label("name_artist"), 
                  User.id.label("id_artist")).
                join(Album, Song.id_album == Album.id).
                join(SongArtist, Song.id == SongArtist.id_song).
                join(User, User.id == SongArtist.id_artist).
                where(Song.id.in_(stmt_song_subquery)).
                group_by(Song.genre, Song.id, Song.title, Song.length, Album.name.label("name_album"),
                 Album.id.label("id_album"), User.name.label("name_artist"), User.id.label("id_artist")).
                order_by(desc(func.sum(Song.num_of_plays)), Song.id)
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
        
        i = 0 
        while i < len(songsPlaylist)-1:
                if(songsPlaylist[i].id == songsPlaylist[i+1].id):
                        x=i
                        dict_artist={}
                        dict_artist["id"] = songsPlaylist[x].id
                        dict_artist["title"] = songsPlaylist[x].title
                        dict_artist["length"] = songsPlaylist[x].length
                        dict_artist["tot_plays_genre"] = songsPlaylist[x].tot_plays_genre
                        dict_artist["name_album"] = songsPlaylist[x].name_album
                        dict_artist["id_album"] = songsPlaylist[x].id_album
                        dict_artist["artists_data"] = {}
                        dict_artist["artists_data"]['artist'+str(x)] = []
                        dict_artist["artists_data"]['artist'+str(x)].append(songsPlaylist[x].id_artist)
                        dict_artist["artists_data"]['artist'+str(x)].append(songsPlaylist[x].name_artist)
                        j=i+1
                        y=j
                        while (j < len(songsPlaylist)) and (songsPlaylist[i].id == songsPlaylist[j].id) :
                                dict_artist["artists_data"]['artist'+str(y)] = []
                                dict_artist["artists_data"]['artist'+str(y)].append(songsPlaylist[j].id_artist)
                                dict_artist["artists_data"]['artist'+str(y)].append(songsPlaylist[j].name_artist)
                                songsPlaylist.pop(j)
                                y=y+1

                        songsPlaylist.pop(i)
                        songsPlaylist.insert(i,dict_artist)
                i=i+1
        
        num_songs = len(songsPlaylist)

        songsPlaylist = reversed(sorted(songsPlaylist, key=lambda song: next(v for k,v in song.items() if(k=='tot_plays_genre')) if (type(song)==dict) else song.tot_plays_genre))

        return render_template("playlist-select.html", songs_list = songsPlaylist, playlist_name = name_playlist_selected, num_songs=num_songs, actual_playlist=id_playlist_selected,playlist_list=playlist_list, isPlPremium=isPlPremium)


@views.route('/playlists/<int:id_playlist_selected>/<int:idPlaylist_ToAddSong>/<int:id_song>', methods=['GET', 'POST'])
@login_required
def playlist_add_song(id_playlist_selected,idPlaylist_ToAddSong, id_song):
        """Function used to add a song into the playlist from a playlist page

        Decorators
        ----------
        @login_required

        Parameters
        ----------
         id_album_selected : int
            The id of the playlist selected
        idPlaylist_ToAddSong : int
            The id of the playlist to which we want to add the song
        id_song : int
            The id of the song

        Returns
        -------
            Return the function get_playlist_selected with id_playlist_selected as parameter
        """

        FunctionSession.insert_song_playlist(idPlaylist_ToAddSong, id_song)

        return get_playlist_selected(id_playlist_selected)

@views.route('/playlists/<name_playlist_selected>/<int:idPlaylist_ToAddSong>/<int:id_song>', methods=['GET', 'POST'])
@login_required
def playlist_premium_add_song(name_playlist_selected,idPlaylist_ToAddSong, id_song):
        """Function used to add a song into the playlist from a premium playlist page

        Decorators
        ----------
        @login_required

        Parameters
        ----------
         id_album_selected : int
            The id of the playlist selected
        idPlaylist_ToAddSong : int
            The id of the playlist to which we want to add the song
        id_song : int
            The id of the song

        Returns
        -------
            Return the function get_playlist_selected with id_playlist_selected as parameter
        """

        FunctionSession.insert_song_playlist(idPlaylist_ToAddSong, id_song)

        return get_premium_playlist_selected(name_playlist_selected)

@views.route('/playlists/<int:id_playlist_selected>/<int:id_song>', methods=['GET', 'POST'])
@login_required
def playlist_remove_song(id_playlist_selected, id_song):
        """Function to delete a song in a playlist

        Decorators
        ----------
        @login_required

        Parameters
        ----------
        id_playlist_selected : int
            The id of the playlist that the user has selected
        id_playlist_selected : int
            The id of the song to delete

        Returns
        -------
            Return the template "playlist-select.html"
        """ 

        delete_playlist = (
                        delete(PlaylistSong).
                        where(PlaylistSong.id_playlist==id_playlist_selected).
                        where(PlaylistSong.id_song==id_song)
                        )

                
        try:
                local_session.execute(delete_playlist)
                local_session.commit()

                flash('Canzone eliminata con successo', category='success')
        except exc.SQLAlchemyError as e:
                local_session.rollback()
                return str(e.orig)
        finally:                        
                local_session.close()


        return get_playlist_selected(id_playlist_selected)

@views.route('/favourites', methods=['GET', 'POST'])
@login_required
def get_favourite():
        """Function to load all songs of personal "Preferiti" playlist and all user's playlist in case he wants to add a song to one of his playlists. 
        Songs are sorted in ascending order according to their date of inclusion in the playlist

        Decorators
        ----------
        @login_required

        Returns
        -------
            Return the template favourite-playlist.html
        """ 

        stmt_song= (
                select(Song.id, Song.title, Song.length, Album.name.label("name_album"), Album.id.label("id_album"), User.name.label("name_artist"), User.id.label("id_artist")).
                join(PlaylistSong, Song.id == PlaylistSong.id_song).
                join(Album, Song.id_album == Album.id).
                join(SongArtist, Song.id == SongArtist.id_song).
                join(User, User.id == SongArtist.id_artist).
                where(PlaylistSong.id_playlist == session['id_fav_playlist']).
                order_by(desc(PlaylistSong.date_created),Song.id)
        )

        playlist_list = None
        songsPlaylist = None

        stmt = (
        select(Playlist.id, Playlist.name).
                join(UserPlaylist, Playlist.id == UserPlaylist.id_playlist).
                where(and_(UserPlaylist.id_user == session['userid'], Playlist.id != session['id_fav_playlist'], Playlist.isPremium == False))
        )
        
        try:            
                playlist_list = local_session.execute(stmt).all()
                songsPlaylist = local_session.execute(stmt_song).all()                
        except exc.SQLAlchemyError as e:
                return str(e.orig)
        
                
        i = 0 
        while i < len(songsPlaylist)-1:
                if(songsPlaylist[i].id == songsPlaylist[i+1].id):
                        x=i
                        dict_artist={}
                        dict_artist["id"] = songsPlaylist[x].id
                        dict_artist["title"] = songsPlaylist[x].title
                        dict_artist["length"] = songsPlaylist[x].length
                        dict_artist["name_album"] = songsPlaylist[x].name_album
                        dict_artist["id_album"] = songsPlaylist[x].id_album
                        dict_artist["artists_data"] = {}
                        dict_artist["artists_data"]['artist'+str(x)] = []
                        dict_artist["artists_data"]['artist'+str(x)].append(songsPlaylist[x].id_artist)
                        dict_artist["artists_data"]['artist'+str(x)].append(songsPlaylist[x].name_artist)
                        j=i+1
                        y=j
                        while (j < len(songsPlaylist)) and (songsPlaylist[i].id == songsPlaylist[j].id) :
                                dict_artist["artists_data"]['artist'+str(y)] = []
                                dict_artist["artists_data"]['artist'+str(y)].append(songsPlaylist[j].id_artist)
                                dict_artist["artists_data"]['artist'+str(y)].append(songsPlaylist[j].name_artist)
                                songsPlaylist.pop(j)
                                y=y+1

                        songsPlaylist.pop(i)
                        songsPlaylist.insert(i,dict_artist)
                i=i+1
        
        num_songs = len(songsPlaylist)
        

        return render_template("favourite-playlist.html", songs_list = songsPlaylist, num_songs=num_songs, playlist_list=playlist_list)

@views.route('/favourites/<int:idPlaylist_ToAddSong>/<int:id_song>', methods=['GET', 'POST'])
@login_required
def favourite_add_song(idPlaylist_ToAddSong,id_song):
        """Function used to add a song in favourite playlist

        Decorators
        ----------
        @login_required 

        Parameters
        ----------
        idPlaylist_ToAddSong : int
            The id of the playlist to which we want to add the song
        id_song : int
            The id of the song

        Returns
        -------
            Return the function get_favourite()
        """      

        FunctionSession.insert_song_playlist(idPlaylist_ToAddSong, id_song)              

        return get_favourite()

@views.route('/favourites/<int:id_song>', methods=['GET', 'POST'])
@login_required
def favourite_remove_song(id_song):
        """Function used to remove a song from favourite playlist

        Decorators
        ----------
        @login_required 

        Parameters
        ----------
        id_song : int
            The id of the song to remove

        Returns
        -------
            Return the function get_favourite()
        """

        deletePlaylistSong = (
                        delete(PlaylistSong).
                        where(PlaylistSong.id_playlist==session['id_fav_playlist']).
                        where(PlaylistSong.id_song==id_song)
                        )
        
        
        try:
                local_session.execute(deletePlaylistSong)
                local_session.commit()

                flash('Canzone eliminata con successo', category='success')
        except exc.SQLAlchemyError as e:
                local_session.rollback()
                return str(e.orig)
        finally:                        
                local_session.close()

        return get_favourite()

@views.route('/albums', methods=['GET', 'POST'])
@login_required
@require_role(role_nedeed=['Admin','ArtistFree','ArtistPremium'])
def albums():
        """Function used to load all albums of authenticated artist

        Decorators
        ----------
        @login_required
        @require_role   

        Returns
        -------
            Return the template of "albums.html"
        """
        
        album_list_stmt = FunctionSession.get_albums_list_stmt(session['userid'])

        album_list = None
        try:
            album_list = local_session.execute(album_list_stmt).all()            
                
        except exc.SQLAlchemyError as e:
            return str(e.orig)        

        return render_template("albums.html", album_list = album_list)
        
@views.route('/albums/<int:id_album_selected>', methods=['GET', 'POST'])
@login_required
def get_album_selected(id_album_selected):
        """Function used to load the album selected from the database

        Decorators
        ----------
        @login_required
        @require_role   

        Parameters
        ----------
        id_album_selected : int
            The id of the album selected

        Returns
        -------
            Return the template of "album-select.html"
        """

        itemArtistlist = None
        itemGenrelist = None

        stmt_album_name = (
                select(Album.name).
                where(Album.id == id_album_selected))

        stmt_album_artists = (
                select(User.id,User.name).
                join(AlbumArtist, AlbumArtist.id_artist == User.id).
                where(AlbumArtist.id_album == id_album_selected))
        
        stmt_song= (
                select(Song.id, Song.title, Song.length, Song.num_of_plays, User.name.label("name_artist"), User.id.label("id_artist")).
                join(SongArtist, Song.id == SongArtist.id_song).
                join(User, User.id == SongArtist.id_artist).
                where(Song.id_album==id_album_selected).
                order_by(Song.date_created, Song.id)
        )

        album_name = None    
        songs_list = None
        album_artists = None
        try:
                album_name = local_session.execute(stmt_album_name).scalar_one() 
                album_artists = local_session.execute(stmt_album_artists).all()
                if(album_name is None or album_artists is None):
                        return page_not_found()
                songs_list = local_session.execute(stmt_song).all()       
                
        except exc.SQLAlchemyError as e:
                return str(e.orig)


        i = 0 
        while i < len(songs_list)-1:
                if(songs_list[i].id == songs_list[i+1].id):
                        x=i
                        dict_artist={}
                        dict_artist["id"] = songs_list[x].id
                        dict_artist["title"] = songs_list[x].title
                        dict_artist["length"] = songs_list[x].length
                        dict_artist["num_of_plays"] = songs_list[x].num_of_plays
                        dict_artist["artists_data"] = {}
                        dict_artist["artists_data"]['artist'+str(x)] = []
                        dict_artist["artists_data"]['artist'+str(x)].append(songs_list[x].id_artist)
                        dict_artist["artists_data"]['artist'+str(x)].append(songs_list[x].name_artist)
                        j=i+1
                        y=j
                        while (j < len(songs_list)) and (songs_list[i].id == songs_list[j].id) :
                                dict_artist["artists_data"]['artist'+str(y)] = []
                                dict_artist["artists_data"]['artist'+str(y)].append(songs_list[j].id_artist)
                                dict_artist["artists_data"]['artist'+str(y)].append(songs_list[j].name_artist)
                                songs_list.pop(j)
                                y=y+1

                        songs_list.pop(i)
                        songs_list.insert(i,dict_artist)
                i=i+1
        
        num_songs = len(songs_list)           
        
                
        playlist_list = FunctionSession.get_user_playlist(True)
        


        if(session['role']=="ArtistFree" or session['role']=="ArtistPremium" or session['role']=="Admin"):

                amIowner = (
                        select(AlbumArtist.id_artist).
                        where(AlbumArtist.id_artist == session['userid']).
                        where(AlbumArtist.id_album == id_album_selected)
                )  
                result = None        

                try:
                        result = local_session.execute(amIowner).scalar()    
                        
                except exc.SQLAlchemyError as e:
                        return str(e.orig)     

                listArtist_db = FunctionSession.get_artists_list(True)      
                list_genre= FunctionSession.get_genre_list()

                itemArtistlist = [r[0] for r in listArtist_db]
                itemGenrelist = [r[0] for r in list_genre]             

                return render_template("album-select.html", songs_list = songs_list, album_name = album_name, album_artists = album_artists,num_songs=num_songs, actual_album=id_album_selected, playlist_list=playlist_list, itemArtistlist=itemArtistlist, itemGenrelist=itemGenrelist, owner = result)

        return render_template("album-select.html", songs_list = songs_list, album_name = album_name, album_artists = album_artists, num_songs=num_songs, actual_album=id_album_selected,playlist_list=playlist_list, itemArtistlist=[], itemGenrelist=[], owner = False)


@views.route('/song_added/<id_album>', methods=['GET', 'POST'])
@login_required
@require_role(role_nedeed=['Admin','ArtistFree','ArtistPremium'])
def create_song(id_album):
        """Function used to insert a song in the database

        Decorators
        ----------
        @login_required
        @require_role   

        Parameters
        ----------
        id_album : int
            The id of the album 

        Returns
        -------
            Return the function get_album_selected with parameter album.id
        """

        if request.method == 'POST':
        
                option = request.form['rad1']         
                titleSong = request.form.get('titleSong')
                yearSong = request.form.get('yearSong')

                minSong= request.form.get('minSong')
                secSong= request.form.get('secSong')
                genreSong = request.form.get('selectGenre')


                tot_length = int(minSong) * 60 + int(secSong)

                exists_Song = local_session.execute(
                        select(Song).
                        join(SongArtist, SongArtist.id_song == Song.id).
                        where(Song.title==titleSong).
                        where(SongArtist.id_artist==session['userid'])).scalar()

                if(exists_Song is not None):
                        flash('La canzone è già presente in questo o in un altro album', category='error')
                        return get_album_selected(id_album)


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
                        
                        artist_name_list = [r[0] for r in listArtist_db]

                        artist_id_list = [r[1] for r in listArtist_db]

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
                        flash('Nuova canzone inserita con successo', category='success')
                except exc.SQLAlchemyError as e:
                        local_session.rollback()
                        return str(e.orig)
                finally:                        
                        local_session.close()
        
        return get_album_selected(id_album)

@views.route('/album_added', methods=['GET', 'POST'])
@login_required
@require_role(role_nedeed=['Admin','ArtistFree','ArtistPremium'])
def create_album():
        """Function used to insert an album in the database

        Decorators
        ----------
        @login_required
        @require_role   

        Returns
        -------
            Return the function get_album_selected with parameter album.id
        """

        if request.method == 'POST':
        
                option = request.form['rad1']         
                nameAlbum = request.form.get('nameAlbum')
                yearAlbum = request.form.get('yearAlbum')

                exists_Album = local_session.execute(
                        select(Album).
                        join(AlbumArtist, AlbumArtist.id_album == Album.id).
                        where(Album.name==nameAlbum).
                        where(AlbumArtist.id_artist==session['userid'])).scalar()

                if(exists_Album is not None):
                        flash('Hai già creato un album con questo nome', category='error')
                        return profile()

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


                        artist_name_list = [r[0] for r in listArtist_db]
                        artist_id_list = [r[1] for r in listArtist_db]


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
                        flash('Album creato con successo', category='success')
                except exc.SQLAlchemyError as e:
                        local_session.rollback()
                        return str(e.orig)
                finally:                        
                        local_session.close()
        
        return get_album_selected(album.id)

@views.route('/album_added/<id_album_selected>/<int:id_song>', methods=['GET', 'POST'])
@login_required
@require_role(role_nedeed=['Admin','ArtistFree','ArtistPremium'])
def album_remove_song(id_album_selected, id_song):
        """Function used to delete a song from the database

        Decorators
        ----------
        @login_required
        @require_role

        Parameters
        ----------
        id_album_selected : int
            The id of the album selected
        id_song : int
            The id of the song to remove       

        Returns
        -------
            Return the template of "albums.html"   
        """

        delete_song = (
                delete(Song).
                where(Song.id==id_song))

        try:
                local_session.execute(delete_song)
                local_session.commit()

                flash('Canzone eliminata con successo', category='success')
        except exc.SQLAlchemyError as e:
                local_session.rollback()
                return str(e.orig)
        finally:                        
                local_session.close()


        return get_album_selected(id_album_selected)

@views.route('/albums/delete/<int:id>', methods=['GET', 'POST'])
@login_required
@require_role(role_nedeed=['Admin','ArtistFree','ArtistPremium'])
def delete_album(id):
        """Function used to delete an album from the database

        Decorators
        ----------
        @login_required
        @require_role

        Parameters
        ----------
        id : int
            The id of the album to remove    

        Returns
        -------
            Return the template of "albums.html"   
        """

        if request.method == 'POST':               
                delete_album = (
                        delete(Album).
                        where(Album.id == id))

                try:
                        local_session.execute(delete_album)
                        local_session.commit()

                        flash('Album eliminato con successo', category='success')
                except exc.SQLAlchemyError as e:
                        local_session.rollback()
                        return str(e.orig)
                finally:                        
                        local_session.close() 
               
        album_list_stmt = FunctionSession.get_albums_list_stmt(session['userid'])

        album_list = None
        try:
            album_list = local_session.execute(album_list_stmt).all()            
                
        except exc.SQLAlchemyError as e:
            return str(e.orig)

        return render_template("albums.html", album_list = album_list)


@views.route('/albums/<int:id_album_selected>/<int:idPlaylist_ToAddSong>/<int:id_song>', methods=['GET', 'POST'])
@login_required
def album_add_song(id_album_selected,idPlaylist_ToAddSong,id_song):
        """Function used to add a song into the playlist from album page

        Decorators
        ----------
        @login_required

        Parameters
        ----------
        id_album_selected : int
            The id of the album selected
        idPlaylist_ToAddSong : int
            The id of the playlist to which we want to add the song
        id_song : int
            The id of the song

        Returns
        -------
            Return the function get_album_selected with parameter id_album_selected    
        """

        FunctionSession.insert_song_playlist(idPlaylist_ToAddSong, id_song)

        return get_album_selected(id_album_selected)


@views.route('/artists/<int:id_artist_selected>', methods=['GET', 'POST'])
@login_required
def get_artist_selected(id_artist_selected):
        """Function used to load albums and songs of an artist

        Decorators
        ----------
        @login_required

        Parameters
        ----------
        id_artist_selected : ind
            The id of the artist selected

        Returns
        -------
            Return the template of "artist-select.html"    
        """

        album_artist_list_stmt = (
                select(Album.id).
                join(AlbumArtist, AlbumArtist.id_album==Album.id).
                join(User, User.id==AlbumArtist.id_artist).
                where(AlbumArtist.id_artist==id_artist_selected).
                order_by(Album.name, Album.year, Album.id))

        album_list_stmt = (
                select(Album.name, Album.id, Album.year, User.name.label('name_artist'), User.id.label("id_artist")).
                join(AlbumArtist, AlbumArtist.id_album==Album.id).
                join(User, User.id==AlbumArtist.id_artist).
                where(Album.id.in_(album_artist_list_stmt)).
                order_by(Album.id, Album.name, Album.year))


        stmt_song_id= (
                select(Song.id).
                join(Album, Song.id_album == Album.id).
                join(SongArtist, Song.id == SongArtist.id_song).
                where(SongArtist.id_artist == id_artist_selected).
                order_by(desc(Song.num_of_plays))).limit(5) 

        stmt_song = (
                select(Song.id, Song.title, Song.num_of_plays, Song.length, Album.name.label("name_album"), Album.id.label("id_album"), User.name.label("name_artist"), User.id.label("id_artist")).
                join(Album, Song.id_album == Album.id).
                join(SongArtist, Song.id == SongArtist.id_song).
                join(User, User.id == SongArtist.id_artist).
                where(Song.id.in_(stmt_song_id)).
                order_by(Song.id, Song.title))


        stmt_artist = (
                select(User.name).
                where(User.id == id_artist_selected).
                where(or_(User.role == "ArtistFree", User.role == "ArtistPremium")))


        artist_name = None
        songs_list = None
        album_list = None


        try:
                album_list = local_session.execute(album_list_stmt).all()            
                artist_name = local_session.execute(stmt_artist).scalar()
                songs_list = local_session.execute(stmt_song).all()
              
        except exc.SQLAlchemyError as e:
                return str(e.orig)


        i = 0 
        while i < len(album_list)-1:
                if(album_list[i].id == album_list[i+1].id):
                        x=i
                        dict_artist={}
                        dict_artist["id"] = album_list[x].id
                        dict_artist["name"] = album_list[x].name
                        dict_artist["year"] = album_list[x].year
                        dict_artist["artists_data"] = {}
                        dict_artist["artists_data"]['artist'+str(x)] = []
                        dict_artist["artists_data"]['artist'+str(x)].append(album_list[x].id_artist)
                        dict_artist["artists_data"]['artist'+str(x)].append(album_list[x].name_artist)
                        j=i+1
                        y=j
                        while (j < len(album_list)) and (album_list[i].id == album_list[j].id) :
                                dict_artist["artists_data"]['artist'+str(y)] = []
                                dict_artist["artists_data"]['artist'+str(y)].append(album_list[j].id_artist)
                                dict_artist["artists_data"]['artist'+str(y)].append(album_list[j].name_artist)
                                album_list.pop(j)
                                y=y+1

                        album_list.pop(i)
                        album_list.insert(i,dict_artist)
                i=i+1
        
        playlist_list = FunctionSession.get_user_playlist(True)


        i = 0 
        while i < len(songs_list)-1:
                if(songs_list[i].id == songs_list[i+1].id):
                        x=i
                        dict_artist={}
                        dict_artist["id"] = songs_list[x].id
                        dict_artist["title"] = songs_list[x].title
                        dict_artist["length"] = songs_list[x].length
                        dict_artist["num_of_plays"] = songs_list[x].num_of_plays
                        dict_artist["name_album"] = songs_list[x].name_album
                        dict_artist["id_album"] = songs_list[x].id_album
                        dict_artist["artists_data"] = {}
                        dict_artist["artists_data"]['artist'+str(x)] = []
                        dict_artist["artists_data"]['artist'+str(x)].append(songs_list[x].id_artist)
                        dict_artist["artists_data"]['artist'+str(x)].append(songs_list[x].name_artist)
                        j=i+1
                        y=j
                        while (j < len(songs_list)) and (songs_list[i].id == songs_list[j].id) :
                                dict_artist["artists_data"]['artist'+str(y)] = []
                                dict_artist["artists_data"]['artist'+str(y)].append(songs_list[j].id_artist)
                                dict_artist["artists_data"]['artist'+str(y)].append(songs_list[j].name_artist)
                                songs_list.pop(j)
                                y=y+1

                        songs_list.pop(i)
                        songs_list.insert(i,dict_artist)
                i=i+1

        songs_list = reversed(sorted(songs_list, key=lambda song: next(v for k,v in song.items() if(k=='num_of_plays')) if (type(song)==dict) else song.num_of_plays))

        return render_template("artist-select.html", songs_list = songs_list, album_list = album_list,actual_artist=id_artist_selected, artist_name=artist_name,playlist_list=playlist_list)

@views.route('/artists/<int:id_artist_selected>/<int:idPlaylist_ToAddSong>/<int:id_song>', methods=['GET', 'POST'])
@login_required
def artist_add_song(id_artist_selected,idPlaylist_ToAddSong,id_song):
        """Function used to add a song into the playlist from artist page

        Decorators
        ----------
        @login_required

        Parameters
        ----------
        id_artist_selected : int
            The id of the artist selected
        idPlaylist_ToAddSong : int
            The id of the playlist to which we want to add the song
        id_song : int
            The id of the song

        Returns
        -------
            Return the function get_artist_selected with parameter id_artist_selected    
        """

        FunctionSession.insert_song_playlist(idPlaylist_ToAddSong, id_song)

        return get_artist_selected(id_artist_selected)




@views.route('/search', methods=['GET', 'POST'])
@login_required
def search():
        """Function used to query the database to get albums, artists and songs

        Decorators
        ----------
        @login_required

        Returns
        -------
            Return the template of "search.html"    
        """
        

        song_result = None
        album_result = None
        user_result = None
        playlist_list = None

        lookingFor = None

        if request.method == 'POST':
                lookingFor = request.form['search']


        list_art= ( select(User.name).
                    where(or_(User.role == "ArtistFree", User.role == "ArtistPremium")))


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
        """Function used to give the result of albums, artists and songs into the database

        Decorators
        ----------
        @login_required

        Parameters
        ----------
        result : str
            The value entered by the user. If no value is entered, result is None

        Returns
        -------
            Return the template of "search.html"    
        """

        lookingFor = result  

        if request.method == 'POST':
                lookingFor = request.form['search']


        list_art= ( select(User.name).
                    where(or_(User.role == 'ArtistPremium', User.role =='ArtistFree' )))

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
                order_by(Song.id, Song.title, Song.year)
        )

        searchInAlbum= (
                select(Album.name, Album.year, Album.id, User.name.label('name_artist'), User.id.label("id_artist")).
                join(AlbumArtist, Album.id==AlbumArtist.id_album).
                join(User, User.id==AlbumArtist.id_artist).
                where((Album.name).like('%' + lookingFor + '%')).
                order_by(Album.id,Album.name)
        )

        searchInUser= (
                select(User.name, User.id).
                where(or_(User.role == "ArtistFree", User.role == "ArtistPremium")).
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

        i = 0 
        while i < len(song_result)-1:
                if(song_result[i].id == song_result[i+1].id):
                        x=i
                        dict_artist={}
                        dict_artist["id"] = song_result[x].id
                        dict_artist["title"] = song_result[x].title
                        dict_artist["length"] = song_result[x].length
                        dict_artist["name_album"] = song_result[x].name_album
                        dict_artist["id_album"] = song_result[x].id_album
                        dict_artist["artists_data"] = {}
                        dict_artist["artists_data"]['artist'+str(x)] = []
                        dict_artist["artists_data"]['artist'+str(x)].append(song_result[x].id_artist)
                        dict_artist["artists_data"]['artist'+str(x)].append(song_result[x].name_artist)
                        j=i+1
                        y=j
                        while (j < len(song_result)) and (song_result[i].id == song_result[j].id) :
                                dict_artist["artists_data"]['artist'+str(y)] = []
                                dict_artist["artists_data"]['artist'+str(y)].append(song_result[j].id_artist)
                                dict_artist["artists_data"]['artist'+str(y)].append(song_result[j].name_artist)
                                song_result.pop(j)
                                y=y+1

                        song_result.pop(i)
                        song_result.insert(i,dict_artist)
                i=i+1

        i = 0 
        while i < len(album_result)-1:
                if(album_result[i].id == album_result[i+1].id):
                        x=i
                        dict_artist={}
                        dict_artist["id"] = album_result[x].id
                        dict_artist["name"] = album_result[x].name
                        dict_artist["year"] = album_result[x].year
                        dict_artist["artists_data"] = {}
                        dict_artist["artists_data"]['artist'+str(x)] = []
                        dict_artist["artists_data"]['artist'+str(x)].append(album_result[x].id_artist)
                        dict_artist["artists_data"]['artist'+str(x)].append(album_result[x].name_artist)
                        j=i+1
                        y=j
                        while (j < len(album_result)) and (album_result[i].id == album_result[j].id) :
                                dict_artist["artists_data"]['artist'+str(y)] = []
                                dict_artist["artists_data"]['artist'+str(y)].append(album_result[j].id_artist)
                                dict_artist["artists_data"]['artist'+str(y)].append(album_result[j].name_artist)
                                album_result.pop(j)
                                y=y+1

                        album_result.pop(i)
                        album_result.insert(i,dict_artist)
                i=i+1

        return render_template("search.html", list_item=itemlist, song_result=song_result, album_result=album_result,user_result=user_result, playlist_list=playlist_list,lookingFor=lookingFor)

@views.route('/search/<result>/<int:playlistId>/<int:songId>', methods=['GET', 'POST'])
@login_required
def search_add_song(result, playlistId, songId):
        """Function used to add a song into a playlist from search

        Decorators
        ----------
        @login_required

        Parameters
        ----------
        result : str
            The value entered from the user
        playlistId : int
            The id of the playlist
        songId : int
            The id of the song    

        Returns
        -------
        list
            Return the function search_result with param result.
        """

        FunctionSession.insert_song_playlist(playlistId, songId)
        

        return search_result(result)

@views.route('/profile')
@login_required
def profile():
        """Function used to show statistics to the user, getting most listened albums and songs

        Decorators
        ----------
        @login_required

        Returns
        -------
        list
            if user has one of this roles "ArtistFree", "ArtistPremium" or "Admin"
            Return the template of "artist-profile.html"
            Otherwise
            Return the template of "user-profile.html"         
        """

        if (session['role']=="ArtistFree" or session['role']=="ArtistPremium" or session['role']=="Admin"):

                listArtist_db = FunctionSession.get_artists_list(True)    


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

                stmt_user=(
                        select(User.name, User.email).
                        where(User.id == session['userid'])
                )

                album_list = None
                songs_list = None
                user_in = None
                count_song = None
                count_album = None
                top_genre = None

                try:
                        album_list = local_session.execute(stmt_album).all()
                        songs_list = local_session.execute(stmt_song).all()
                        top_genre = local_session.execute(stmt_genre).all()
                        count_song = local_session.execute(stmt_count_song).scalar()
                        count_album = local_session.execute(stmt_count_album).scalar()
                        user_in = local_session.execute(stmt_user).all()
                        
                except exc.SQLAlchemyError as e:
                        return str(e.orig)
                
                itemlist = [r[0] for r in listArtist_db]


                return render_template("artist-profile.html", playlists = playlist_list, album_list = album_list, songs_list = songs_list,  itemlist = itemlist, count_song = count_song, count_album = count_album, top_genre = top_genre, user_in = user_in)
        else:

                stmt_user=(
                        select(User.name, User.email).
                        where(User.id == session['userid'])
                )

                user_in = None

                try:
                        user_in = local_session.execute(stmt_user).all()

                except exc.SQLAlchemyError as e:
                        return str(e.orig)

                return render_template("user-profile.html", user_in = user_in)

@views.route('/profile/premium-subscription', methods=['GET', 'POST'])
@login_required
def premium_subscription():
        """Function used to give the user access to the premium account

        Decorators
        ----------
        @login_required

        """

        if request.method == 'POST':
                if (session['role']=="UserFree"):
                        update_user = (
                                update(User).
                                where(User.id == session['userid']).
                                values(role='UserPremium')
                                )
                elif (session['role']=="ArtistFree"):
                        update_user = (
                                update(User).
                                where(User.id == session['userid']).
                                values(role='ArtistPremium')
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


@views.route('/page-not-found')
@login_required
def page_not_found():
        """Function that warns the user that the page is not available

        Decorators
        ----------
        @login_required

        """

        return render_template("page-not-found.html")

@views.route('/addPlays', methods=['GET', 'POST'])
@login_required
def addPlays():
        """Function used to add plays to the num_of_plays attribute of a song

        Decorators
        ----------
        @login_required

        """
        if(request.headers.get('Content-type') == 'addPlays'):
                idSong=int(request.data.decode("utf-8"))
                update_plays = (
                        update(Song).
                        where(Song.id == idSong).
                        values(num_of_plays = Song.num_of_plays + 1)
                )
                local_session.execute(update_plays)
                local_session.commit()
        
        return redirect('/')