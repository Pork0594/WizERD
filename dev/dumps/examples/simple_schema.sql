CREATE TABLE users(
    id uuid PRIMARY KEY,
    username text NOT NULL,
    email text NOT NULL,
    display_name text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE posts(
    id uuid PRIMARY KEY,
    user_id uuid,
    title text NOT NULL,
    body text,
    published_at timestamp with time zone
);

CREATE TABLE likes(
    id uuid PRIMARY KEY,
    user_id uuid,
    post_id uuid,
    published_at timestamp with time zone
);

ALTER TABLE ONLY posts
    ADD CONSTRAINT posts_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE ONLY likes
    ADD CONSTRAINT likes_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE ONLY likes
    ADD CONSTRAINT likes_post_id_fkey FOREIGN KEY (post_id) REFERENCES posts(id);

