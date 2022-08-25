from webapp import Base
from flask import session
from webapp import db_session
from sqlalchemy import Column, Integer, Boolean, String, exc
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func,  insert, select, subquery, update, delete
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
    def get_songs_list():
        stmt = select(Song)
        songs = None
        try:
            songs = local_session.execute(stmt).all()
                
        except exc.SQLAlchemyError as e:
            return str(e.orig)

        return songs

    def get_songs_in_a_playlist_by_id(id_playlist):
        stmt = (select(Song.id, Song.title, Song.num_of_plays, Song.id_album, Song.length, Song.genre, PlaylistSong.date_created).
                join(PlaylistSong, Song.id == PlaylistSong.id_song).
                where(PlaylistSong.id_playlist == id_playlist))
        songs = None
        try:            
            songs = local_session.execute(stmt).all()
                
        except exc.SQLAlchemyError as e:
            return str(e.orig)

        return songs

    def get_user_playlist(withFav):
        playlists = None    
        if (withFav) :
            stmt = (
                select(Playlist.id, Playlist.name).
                join(UserPlaylist, Playlist.id == UserPlaylist.id_playlist).
                where(UserPlaylist.id_user == session['userid']))
            try:
                playlists = local_session.execute(stmt).all()
                    
            except exc.SQLAlchemyError as e:
                return str(e.orig)
        else :            
            stmt = (
                select(Playlist.id, Playlist.name).
                join(UserPlaylist, Playlist.id == UserPlaylist.id_playlist).
                where(UserPlaylist.id_user == session['userid']).
                where(Playlist.name != session['id_fav_playlist']))
            try:
                playlists = local_session.execute(stmt).all()
                    
            except exc.SQLAlchemyError as e:
                return str(e.orig)

        return playlists

    def get_albums_list():
        stmt = (
                select(Album.name, Album.id, Album.year).
                join(AlbumArtist, AlbumArtist.id_album==Album.id).
                where(AlbumArtist.id_artist==session['userid']).
                order_by(Album.year))
        albums = None
        try:
            albums = local_session.execute(stmt).all()            
                
        except exc.SQLAlchemyError as e:
            return str(e.orig)

        return albums

    def get_artists_list(noCurrentArtist):
        artists = None
        if(noCurrentArtist) :
            stmt = (
                    select(User.name).
                    where(User.isArtist==True).
                    where(User.name != session['username']))
            try:
                artists = local_session.execute(stmt).all()              
            except exc.SQLAlchemyError as e:
                return str(e.orig)

        else :
            stmt = (
                    select(User.name).
                    where(User.isArtist==True))
            try:
                artists = local_session.execute(stmt).all()     
            except exc.SQLAlchemyError as e:
                return str(e.orig)

        return artists   

    def get_genre_list():
        stmt = select(Genre.name)
        genres = None
        try:
            genres = local_session.execute(stmt).all()
            
                    
        except exc.SQLAlchemyError as e:
            return str(e.orig)

        return genres
      
