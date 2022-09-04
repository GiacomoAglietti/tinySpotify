from flask import session, flash
from webapp import db_session
from sqlalchemy import exc
from sqlalchemy.sql import select, or_
from webapp.models.User import User
from webapp.models.SongArtist import SongArtist
from webapp.models.Song import Song
from webapp.models.PlaylistSong import PlaylistSong
from webapp.models.Playlist import Playlist
from webapp.models.Genre import Genre
from webapp.models.AlbumArtist import AlbumArtist
from webapp.models.Album import Album
from webapp.models.UserPlaylist import UserPlaylist

local_session = db_session()

class FunctionSession:
    """
    A class used to contain functions

    """

    def get_songs_list() -> list:
        """Function used to get all songs from database

        Returns
        -------
        list
            a list of Row which contains all columns of Song
        """
        stmt = select(Song)
        songs = None
        try:
            songs = local_session.execute(stmt).all()
                
        except exc.SQLAlchemyError as e:
            return str(e.orig)

        return songs

    def get_songs_in_a_playlist_by_id(id_playlist):
        """Function used to get all songs of a playlist from database

        Parameters
        ----------
        id_playlist : int
            The id of the playlist

        Returns
        -------
        ScalarResult
            a Scalar object which contains the following columns: Song.id, Song.title, Song.num_of_plays, Song.id_album, Song.length, Song.genre, PlaylistSong.date_created
        """

        stmt = (select(Song.id, Song.title, Song.num_of_plays, Song.id_album, Song.length, Song.genre, PlaylistSong.date_created).
                join(PlaylistSong, Song.id == PlaylistSong.id_song).
                where(PlaylistSong.id_playlist == id_playlist))
        songs = None
        try:            
            songs = local_session.execute(stmt).scalars()
                
        except exc.SQLAlchemyError as e:
            return str(e.orig)

        return songs

    
    def get_user_playlist(withFav) -> list:
        """Function used to get all playlist not premium of the current user from database, ordered by Playlist.name 

        Parameters
        ----------
        withFav : bool
            True if you also want the "Preferiti" playlist, False otherwise 

        Returns
        -------
        list
            a list of Row which contains the following columns: Playlist.id, Playlist.name
        """

        playlists = None    
        if (withFav) :
            stmt = (
                select(Playlist.id, Playlist.name).
                join(UserPlaylist, Playlist.id == UserPlaylist.id_playlist).
                where(UserPlaylist.id_user == session['userid']).
                where(Playlist.isPremium == False).
                order_by(Playlist.name))
            try:
                playlists = local_session.execute(stmt).all()
                    
            except exc.SQLAlchemyError as e:
                return str(e.orig)
        else :            
            stmt = (
                select(Playlist.id, Playlist.name).
                join(UserPlaylist, Playlist.id == UserPlaylist.id_playlist).
                where(UserPlaylist.id_user == session['userid']).
                where(Playlist.id != session['id_fav_playlist']).
                where(Playlist.isPremium == False).
                order_by(Playlist.name))
            try:
                playlists = local_session.execute(stmt).all()
                    
            except exc.SQLAlchemyError as e:
                return str(e.orig)

        return playlists
    
    def get_albums_list_stmt(id_artist):
        """Function used to get all albums of an artist from database, ordered by Album.name, Album.year, Album.id

        Parameters
        ----------
        id_artist : int
            The id of the artist

        Returns
        -------
        list
            a list of Row which contains the following columns: Album.name, Album.id, Album.year, User.name.label('name_artist'), User.id.label("id_artist")
        """
        stmt = (
                select(Album.name, Album.id, Album.year, User.name.label('name_artist'), User.id.label("id_artist")).
                join(AlbumArtist, AlbumArtist.id_album==Album.id).
                join(User, User.id==AlbumArtist.id_artist).
                where(AlbumArtist.id_artist==id_artist).
                order_by(Album.name, Album.year, Album.id))
        

        return stmt

    def get_artists_list(noCurrentArtist) -> list:
        """Function used to get all artists from database

        Parameters
        ----------
        noCurrentArtist : bool
            True if you also want the current user(only if it's an artist) in the list, False otherwise

        Returns
        -------
        list
            a list of Row which contains the following columns: User.name, User.id
        """
        artists = None
        if(noCurrentArtist) :
            stmt = (
                    select(User.name, User.id).
                    where(or_(User.role == 'ArtistPremium', User.role =='ArtistFree' )).
                    where(User.name != session['username']))
            try:
                artists = local_session.execute(stmt).all()              
            except exc.SQLAlchemyError as e:
                return str(e.orig)

        else :
            stmt = (
                    select(User.name, User.id).
                    where(or_(User.role == 'ArtistPremium', User.role =='ArtistFree' )))
            try:
                artists = local_session.execute(stmt).all()     
            except exc.SQLAlchemyError as e:
                return str(e.orig)

        return artists   

    def get_genre_list() -> list:
        """Function used to get all genres from database

        Returns
        -------
        list
            a list of Row which contains the following columns: User.name, User.id
        """
        stmt = select(Genre.name)
        genres = None
        try:
            genres = local_session.execute(stmt).all()
            
                    
        except exc.SQLAlchemyError as e:
            return str(e.orig)

        return genres

    def insert_song_playlist(playlistId, songId):
        """Function used to insert a song in a playlist. If the song is already in the playlist it returns a flash message

        Parameters
        ----------
        playlistId : int
            The id of the playlist

        songId : int
            The id of the song

        """

        exists_PlaylistSong = local_session.execute(
            select(PlaylistSong).
            where(PlaylistSong.id_playlist==playlistId).
            where(PlaylistSong.id_song==songId)).scalar()

        if(exists_PlaylistSong is not None):
            flash('La canzone è già presente nella playlist', category='error')
        else:
            insertPlaylistSong = PlaylistSong(id_playlist=playlistId, id_song=songId)
            try:
                    local_session.add(insertPlaylistSong)
                    local_session.commit()

                    flash('Canzone aggiunta con successo', category='success')                                       
            except exc.SQLAlchemyError as e:
                    local_session.rollback()
                    return str(e.orig)
            finally:
                    local_session.close()

    def add_dict_artist_to_list_song(listSong) -> list:
        return []
      
