-- Music Streaming Platform Schema
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users and Authentication
CREATE TABLE users(
    user_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    username varchar(50) UNIQUE NOT NULL,
    email varchar(255) UNIQUE NOT NULL,
    password_hash varchar(255) NOT NULL,
    display_name varchar(100),
    avatar_url text,
    country_code char(2),
    date_of_birth date,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    last_login timestamp,
    is_verified boolean DEFAULT FALSE,
    is_active boolean DEFAULT TRUE
);

-- Subscription Plans
CREATE TABLE subscription_plans(
    plan_id serial PRIMARY KEY,
    plan_name varchar(50) UNIQUE NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    currency char(3) DEFAULT 'USD',
    max_quality varchar(20),
    allows_offline boolean DEFAULT FALSE,
    allows_ads boolean DEFAULT TRUE,
    max_skip_count integer,
    description text
);

-- User Subscriptions
CREATE TABLE user_subscriptions(
    subscription_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    plan_id integer NOT NULL REFERENCES subscription_plans(plan_id),
    start_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_date timestamp,
    is_active boolean DEFAULT TRUE,
    auto_renew boolean DEFAULT TRUE,
    payment_method varchar(50)
);

-- Artists
CREATE TABLE artists(
    artist_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    artist_name varchar(255) NOT NULL,
    bio text,
    country varchar(100),
    profile_image_url text,
    verified boolean DEFAULT FALSE,
    monthly_listeners integer DEFAULT 0,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- Genres
CREATE TABLE genres(
    genre_id serial PRIMARY KEY,
    genre_name varchar(100) UNIQUE NOT NULL,
    description text,
    parent_genre_id integer REFERENCES genres(genre_id)
);

-- Albums
CREATE TABLE albums(
    album_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    album_title varchar(255) NOT NULL,
    artist_id uuid NOT NULL REFERENCES artists(artist_id) ON DELETE CASCADE,
    release_date date,
    album_type varchar(20) CHECK (album_type IN ('album', 'single', 'ep', 'compilation')),
    cover_art_url text,
    total_tracks integer,
    label varchar(255),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- Songs/Tracks
CREATE TABLE songs(
    song_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    song_title varchar(255) NOT NULL,
    album_id uuid REFERENCES albums(album_id) ON DELETE SET NULL,
    duration_seconds integer NOT NULL,
    track_number integer,
    disc_number integer DEFAULT 1,
    explicit boolean DEFAULT FALSE,
    isrc varchar(12) UNIQUE,
    audio_file_url text,
    preview_url text,
    play_count bigint DEFAULT 0,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- Song Artists (for collaborations)
CREATE TABLE song_artists(
    song_id uuid REFERENCES songs(song_id) ON DELETE CASCADE,
    artist_id uuid REFERENCES artists(artist_id) ON DELETE CASCADE,
    artist_role varchar(50) DEFAULT 'primary' CHECK (artist_role IN ('primary', 'featured', 'composer', 'producer')),
    PRIMARY KEY (song_id, artist_id, artist_role)
);

-- Song Genres (many-to-many)
CREATE TABLE song_genres(
    song_id uuid REFERENCES songs(song_id) ON DELETE CASCADE,
    genre_id integer REFERENCES genres(genre_id) ON DELETE CASCADE,
    PRIMARY KEY (song_id, genre_id)
);

-- Playlists
CREATE TABLE playlists(
    playlist_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    playlist_name varchar(255) NOT NULL,
    description text,
    is_public boolean DEFAULT TRUE,
    is_collaborative boolean DEFAULT FALSE,
    cover_image_url text,
    follower_count integer DEFAULT 0,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- Playlist Songs (with ordering)
CREATE TABLE playlist_songs(
    playlist_id uuid REFERENCES playlists(playlist_id) ON DELETE CASCADE,
    song_id uuid REFERENCES songs(song_id) ON DELETE CASCADE,
    position integer NOT NULL,
    added_at timestamp DEFAULT CURRENT_TIMESTAMP,
    added_by uuid REFERENCES users(user_id) ON DELETE SET NULL,
    PRIMARY KEY (playlist_id, song_id)
);

-- User Following Artists
CREATE TABLE user_artist_follows(
    user_id uuid REFERENCES users(user_id) ON DELETE CASCADE,
    artist_id uuid REFERENCES artists(artist_id) ON DELETE CASCADE,
    followed_at timestamp DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, artist_id)
);

-- User Following Users
CREATE TABLE user_follows(
    follower_id uuid REFERENCES users(user_id) ON DELETE CASCADE,
    following_id uuid REFERENCES users(user_id) ON DELETE CASCADE,
    followed_at timestamp DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, following_id),
    CHECK (follower_id != following_id)
);

-- User Playlist Follows
CREATE TABLE user_playlist_follows(
    user_id uuid REFERENCES users(user_id) ON DELETE CASCADE,
    playlist_id uuid REFERENCES playlists(playlist_id) ON DELETE CASCADE,
    followed_at timestamp DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, playlist_id)
);

-- Listening History
CREATE TABLE listening_history(
    history_id bigserial PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    song_id uuid NOT NULL REFERENCES songs(song_id) ON DELETE CASCADE,
    played_at timestamp DEFAULT CURRENT_TIMESTAMP,
    duration_played integer,
    completed boolean DEFAULT FALSE,
    device_type varchar(50),
    location_country char(2)
);

-- User Song Likes
CREATE TABLE user_song_likes(
    user_id uuid REFERENCES users(user_id) ON DELETE CASCADE,
    song_id uuid REFERENCES songs(song_id) ON DELETE CASCADE,
    liked_at timestamp DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, song_id)
);

-- User Album Reviews
CREATE TABLE album_reviews(
    review_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    album_id uuid NOT NULL REFERENCES albums(album_id) ON DELETE CASCADE,
    rating integer CHECK (rating >= 1 AND rating <= 5),
    review_text text,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP,
    helpful_count integer DEFAULT 0,
    UNIQUE (user_id, album_id)
);

-- User Devices
CREATE TABLE user_devices(
    device_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    device_name varchar(100),
    device_type varchar(50),
    last_active timestamp DEFAULT CURRENT_TIMESTAMP,
    is_active boolean DEFAULT TRUE
);

-- Queue (Current playback queue)
CREATE TABLE user_queue(
    queue_id bigserial PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    song_id uuid NOT NULL REFERENCES songs(song_id) ON DELETE CASCADE,
    position integer NOT NULL,
    added_at timestamp DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, position)
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);

CREATE INDEX idx_users_username ON users(username);

CREATE INDEX idx_songs_album ON songs(album_id);

CREATE INDEX idx_albums_artist ON albums(artist_id);

CREATE INDEX idx_listening_history_user ON listening_history(user_id);

CREATE INDEX idx_listening_history_song ON listening_history(song_id);

CREATE INDEX idx_listening_history_played_at ON listening_history(played_at);

CREATE INDEX idx_playlist_songs_playlist ON playlist_songs(playlist_id);

CREATE INDEX idx_user_subscriptions_user ON user_subscriptions(user_id);

CREATE INDEX idx_song_artists_artist ON song_artists(artist_id);

-- Some useful views
CREATE VIEW popular_songs AS
SELECT
    s.song_id,
    s.song_title,
    a.artist_name,
    s.play_count,
    COUNT(DISTINCT usl.user_id) AS like_count
FROM
    songs s
    JOIN song_artists sa ON s.song_id = sa.song_id
    JOIN artists a ON sa.artist_id = a.artist_id
    LEFT JOIN user_song_likes usl ON s.song_id = usl.song_id
GROUP BY
    s.song_id,
    s.song_title,
    a.artist_name,
    s.play_count
ORDER BY
    s.play_count DESC;

CREATE VIEW user_listening_stats AS
SELECT
    u.user_id,
    u.username,
    COUNT(lh.history_id) AS total_plays,
    COUNT(DISTINCT lh.song_id) AS unique_songs,
    SUM(lh.duration_played) AS total_listen_time_seconds
FROM
    users u
    LEFT JOIN listening_history lh ON u.user_id = lh.user_id
GROUP BY
    u.user_id,
    u.username;

