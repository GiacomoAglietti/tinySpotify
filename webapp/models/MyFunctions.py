from webapp import Base
from flask import session
from sqlalchemy import Column, Integer, Boolean, String
from sqlalchemy.orm import relationship, self
from datetime import datetime
from sqlalchemy.sql import func,  insert, select, subquery, update, delete
from sqlalchemy_utils import create_view
from . import User, Song, PlaylistSong, Genre, Album, SongArtist, Playlist, UserPlaylist, AlbumArtist

class FunctionSession:
    def __init__(session):
        self.session = session

    def get_songs_in_a_playlist_by_id(id_playlist):
        songList = FunctionSession.get_songs_list()

        return self.session.execute(
            select(songList.id, songList.title, songList.num_of_plays, songList.id_album, songList.length, songList.genre).
            join(PlaylistSong, songList.id == PlaylistSong.id_song).
            where(PlaylistSong.id_playlist == id_playlist)
        ).all()

    def get_user_playlist(withFav):    
        if (withFav) :
            return self.session.execute(
                select(Playlist).
                join(UserPlaylist, Playlist.id == UserPlaylist.id_playlist).
                where(UserPlaylist.id_user == session['userid'])
            ).all()
        else :
            return self.session.execute(
                select(Playlist).
                join(UserPlaylist, Playlist.id == UserPlaylist.id_playlist).
                where(UserPlaylist.id_user == session['userid']).
                where(Playlist.name != session['id_fav_playlist'])
            ).all()

    def get_albums_list():
        return self.session.execute(
            select(Album.name, Album.id).
            join(AlbumArtist, AlbumArtist.id_album==Album.id).
            where(AlbumArtist.id_artist==session['userid'])
        ).all()

    def get_artists_list(onlyMine):
        if(onlyMine) :
            return self.session.execute(
                select(User.name).
                where(User.isArtist==True).
                where(User.name != session['username'])
            ).all()
        else :
            return self.session.execute(
                select(User.name).
                where(User.isArtist==True)                
            ).all()

    def get_songs_list():
            return self.session.execute(
                select(Song)          
            ).all()

    def get_genre_list():
            return self.session.execute(
                select(Genre.name)          
            ).all()
      
