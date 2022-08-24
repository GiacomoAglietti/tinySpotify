"""empty message

Revision ID: 5a2b8c132f81
Revises: aaa058cec565
Create Date: 2022-08-23 17:30:19.550540

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5a2b8c132f81'
down_revision = 'aaa058cec565'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('playlist_song')
    op.drop_table('album_artist')
    op.drop_table('song_artist')
    op.drop_table('playlist')
    op.drop_table('songs')
    op.drop_table('album')
    op.drop_table('genres')
    op.drop_table('users')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('users_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('password', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('isArtist', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('isPremium', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='users_pkey'),
    sa.UniqueConstraint('email', name='users_email_key'),
    sa.UniqueConstraint('name', name='users_name_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('song_artist',
    sa.Column('id_artist', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('id_song', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['id_artist'], ['users.id'], name='song_artist_id_artist_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_song'], ['songs.id'], name='song_artist_id_song_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id_artist', 'id_song', name='song_artist_pkey')
    )
    op.create_table('genres',
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('num_of_plays', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('name', name='genres_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('album_artist',
    sa.Column('id_artist', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('id_album', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['id_album'], ['album.id'], name='album_artist_id_album_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_artist'], ['users.id'], name='album_artist_id_artist_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id_artist', 'id_album', name='album_artist_pkey')
    )
    op.create_table('album',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('album_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('year', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('image', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.CheckConstraint('(year > 1900) AND (year <= 2022)', name='album_year_check'),
    sa.PrimaryKeyConstraint('id', name='album_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('songs',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('songs_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('title', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('year', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('length', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('date_created', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('id_album', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('genre', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.CheckConstraint('(length > 0) AND (length < 3600)', name='songs_length_check'),
    sa.CheckConstraint('(year > 1900) AND (year <= 2022)', name='songs_year_check'),
    sa.ForeignKeyConstraint(['genre'], ['genres.name'], name='songs_genre_fkey'),
    sa.ForeignKeyConstraint(['id_album'], ['album.id'], name='songs_id_album_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='songs_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('playlist_song',
    sa.Column('id_playlist', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('id_song', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('date_created', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['id_playlist'], ['playlist.id'], name='playlist_song_id_playlist_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_song'], ['songs.id'], name='playlist_song_id_song_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id_playlist', 'id_song', name='playlist_song_pkey')
    )
    op.create_table('playlist',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('isPremium', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('id_user', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('name_genre', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['id_user'], ['users.id'], name='playlist_id_user_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['name_genre'], ['genres.name'], name='playlist_name_genre_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='playlist_pkey')
    )
    # ### end Alembic commands ###
