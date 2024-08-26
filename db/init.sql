
-- DROP TABLE IF EXISTS TRACKER;
-- DROP TABLE IF EXISTS GAMES;
DROP TABLE IF EXISTS REGIONS;

-- CREATE TABLE TRACKER (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     user_role VARCHAR(20),
--     user_name VARCHAR(50) UNIQUE,
--     nick_name VARCHAR(20),
--     last_activity_date DATETIME,
--     days_inactive INTEGER DEFAULT 0,
--     maps_participated_in INTEGER DEFAULT 0,
--     maps_led INTEGER DEFAULT 0,
--     maps_won INTEGER DEFAULT 0,
--     maps_lost INTEGER DEFAULT 0,
--     notes VARCHAR(100)
-- );
-- CREATE INDEX idx_user_name ON TRACKER (user_name);

-- CREATE TABLE GAMES (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     channel_id INTEGER,
--     region VARCHAR(50),
--     map VARCHAR(50),
--     speed VARCHAR(2),
--     leader VARCHAR(50),
--     ally1 VARCHAR(50),
--     ally2 VARCHAR(50),
--     ally3 VARCHAR(50),
--     ally4 VARCHAR(50)
-- );

CREATE TABLE REGIONS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_type VARCHAR(50),
    region VARCHAR(50),
    territory VARCHAR(50)
);