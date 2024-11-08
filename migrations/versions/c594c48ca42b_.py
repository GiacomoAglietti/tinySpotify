"""empty message

Revision ID: c594c48ca42b
Revises: bee95eda13ec
Create Date: 2022-09-04 18:36:58.101098

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c594c48ca42b'
down_revision = 'bee95eda13ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('playlist_song')
    op.drop_index('ix_album_id', table_name='album')
    op.drop_table('album')
    op.drop_index('ix_songs_id', table_name='songs')
    op.drop_table('songs')
    op.drop_index('ix_playlist_id', table_name='playlist')
    op.drop_table('playlist')
    op.drop_table('roles')
    op.drop_table('user_playlist')
    op.drop_table('song_artist')
    op.drop_table('genres')
    op.drop_table('album_artist')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('users_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('password', sa.VARCHAR(length=150), autoincrement=False, nullable=False),
    sa.Column('role', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['role'], ['roles.name'], name='users_role_fkey', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='users_pkey'),
    sa.UniqueConstraint('email', name='users_email_key'),
    sa.UniqueConstraint('name', name='users_name_key'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_table('album_artist',
    sa.Column('id_artist', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('id_album', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['id_album'], ['album.id'], name='album_artist_id_album_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_artist'], ['users.id'], name='album_artist_id_artist_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id_artist', 'id_album', name='album_artist_pkey')
    )
    op.create_table('genres',
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('name', name='genres_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('song_artist',
    sa.Column('id_artist', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('id_song', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['id_artist'], ['users.id'], name='song_artist_id_artist_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_song'], ['songs.id'], name='song_artist_id_song_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id_artist', 'id_song', name='song_artist_pkey')
    )
    op.create_table('user_playlist',
    sa.Column('id_playlist', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('id_user', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('date_created', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['id_playlist'], ['playlist.id'], name='user_playlist_id_playlist_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_user'], ['users.id'], name='user_playlist_id_user_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id_playlist', 'id_user', name='user_playlist_pkey')
    )
    op.create_table('roles',
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('name', name='roles_pkey')
    )
    op.create_table('playlist',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('playlist_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('isPremium', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='playlist_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_playlist_id', 'playlist', ['id'], unique=False)
    op.create_table('songs',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('songs_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('title', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('year', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('length', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('num_of_plays', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('date_created', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('id_album', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('genre', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.CheckConstraint('(length > 0) AND (length < 3600)', name='songs_length_check'),
    sa.CheckConstraint('(year > 1900) AND (year <= 2022)', name='songs_year_check'),
    sa.ForeignKeyConstraint(['genre'], ['genres.name'], name='songs_genre_fkey', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_album'], ['album.id'], name='songs_id_album_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='songs_pkey'),
    sa.UniqueConstraint('title', 'id_album', name='title_id_album'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_songs_id', 'songs', ['id'], unique=False)
    op.create_table('album',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('album_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('year', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.CheckConstraint('(year > 1900) AND (year <= 2022)', name='album_year_check'),
    sa.PrimaryKeyConstraint('id', name='album_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_album_id', 'album', ['id'], unique=False)
    op.create_table('playlist_song',
    sa.Column('id_playlist', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('id_song', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('date_created', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['id_playlist'], ['playlist.id'], name='playlist_song_id_playlist_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_song'], ['songs.id'], name='playlist_song_id_song_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id_playlist', 'id_song', name='playlist_song_pkey')
    )
    # ### end Alembic commands ###
