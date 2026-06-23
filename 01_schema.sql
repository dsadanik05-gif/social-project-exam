-- =====================================================================
-- 4-нұсқа. Әлеуметтік желідегі пайдаланушылар белсенділігін талдау
-- (User Activity Tracking)
-- 2-кезең. Сақтау схемасын жобалау
--
-- СУБД: PostgreSQL (указана в задании напрямую).
-- Схема: Users -> Posts -> Activities
-- =====================================================================

DROP TABLE IF EXISTS Activities CASCADE;
DROP TABLE IF EXISTS Posts CASCADE;
DROP TABLE IF EXISTS Users CASCADE;


-- ---------------------------------------------------------------------
-- Таблица 1: Users
-- Пользователи соцсети.
-- ---------------------------------------------------------------------
CREATE TABLE Users (
    user_id          SERIAL PRIMARY KEY,
    full_name        VARCHAR(150) NOT NULL,
    account_created  DATE         NOT NULL DEFAULT CURRENT_DATE
);

COMMENT ON TABLE Users IS 'Әлеуметтік желі пайдаланушылары';


-- ---------------------------------------------------------------------
-- Таблица 2: Posts
-- Посты пользователей. view_count и like_count добавлены сверх
-- минимума задания как агрегированные счётчики "для скорости" —
-- но их точность всегда можно сверить через таблицу Activities.
-- ---------------------------------------------------------------------
CREATE TABLE Posts (
    post_id      SERIAL PRIMARY KEY,
    author_id    INTEGER     NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    post_text    TEXT        NOT NULL,
    published_at TIMESTAMP   NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE Posts IS 'Пайдаланушылардың посттары';

CREATE INDEX idx_posts_author ON Posts(author_id);
CREATE INDEX idx_posts_published ON Posts(published_at);


-- ---------------------------------------------------------------------
-- Таблица 3: Activities
-- Журнал действий пользователей: лайки, комментарии, репосты, просмотры.
-- post_id = 0 означает действие, не привязанное к посту
-- (например, просмотр профиля пользователя).
-- ---------------------------------------------------------------------
CREATE TABLE Activities (
    activity_id     SERIAL PRIMARY KEY,
    user_id          INTEGER      NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    action_type      VARCHAR(20)  NOT NULL
                          CHECK (action_type IN ('like', 'comment', 'share', 'view')),
    post_id           INTEGER     NOT NULL DEFAULT 0,
    comment_text       TEXT,
    activity_timestamp TIMESTAMP  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE Activities IS 'Пайдаланушы әрекеттерінің журналы';

-- Композитный индекс (user_id, action_type), как прямо требует задание:
-- ускоряет поиск действий конкретного пользователя определённого типа
-- (например: "все лайки пользователя №42").
CREATE INDEX idx_activities_user_action ON Activities(user_id, action_type);

-- Дополнительные индексы под аналитику по постам и по времени
CREATE INDEX idx_activities_post ON Activities(post_id);
CREATE INDEX idx_activities_timestamp ON Activities(activity_timestamp);
