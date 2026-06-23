-- =====================================================================
-- 3-кезең. Аналитикалық өңдеу және агрегация
-- 5 күрделі SQL-скрипт.
-- =====================================================================


-- ---------------------------------------------------------------------
-- СКРИПТ 1: коэффициент вовлечённости (Engagement Rate) для каждого поста
-- Engagement Rate = (лайки + комментарии + репосты) / просмотры
-- ---------------------------------------------------------------------
SELECT
    p.post_id,
    p.post_text,
    COUNT(*) FILTER (WHERE a.action_type = 'view')    AS views_count,
    COUNT(*) FILTER (WHERE a.action_type = 'like')    AS likes_count,
    COUNT(*) FILTER (WHERE a.action_type = 'comment') AS comments_count,
    COUNT(*) FILTER (WHERE a.action_type = 'share')   AS shares_count,
    ROUND(
        (
            COUNT(*) FILTER (WHERE a.action_type IN ('like', 'comment', 'share'))::NUMERIC
        ) / NULLIF(COUNT(*) FILTER (WHERE a.action_type = 'view'), 0),
        3
    ) AS engagement_rate
FROM Posts p
LEFT JOIN Activities a ON a.post_id = p.post_id
GROUP BY p.post_id, p.post_text
ORDER BY engagement_rate DESC NULLS LAST;


-- ---------------------------------------------------------------------
-- СКРИПТ 2: топ-5 самых активных пользователей по числу совершённых действий
-- ---------------------------------------------------------------------
SELECT
    u.user_id,
    u.full_name,
    COUNT(*) AS total_actions
FROM Activities a
JOIN Users u ON u.user_id = a.user_id
GROUP BY u.user_id, u.full_name
ORDER BY total_actions DESC
LIMIT 5;


-- ---------------------------------------------------------------------
-- СКРИПТ 3: среднее количество комментариев, оставляемых
-- пользователями в день
-- ---------------------------------------------------------------------
WITH comments_per_user_day AS (
    SELECT
        user_id,
        DATE(activity_timestamp) AS activity_day,
        COUNT(*) AS comments_count
    FROM Activities
    WHERE action_type = 'comment'
    GROUP BY user_id, DATE(activity_timestamp)
)
SELECT
    ROUND(AVG(comments_count), 3) AS avg_comments_per_user_per_day
FROM comments_per_user_day;


-- ---------------------------------------------------------------------
-- СКРИПТ 4: поиск "заброшенных" постов — старше недели,
-- у которых 0 просмотров и 0 лайков
-- ---------------------------------------------------------------------
SELECT
    p.post_id,
    p.post_text,
    p.published_at,
    NOW() - p.published_at AS post_age
FROM Posts p
WHERE p.published_at < NOW() - INTERVAL '7 days'
  AND NOT EXISTS (
      SELECT 1 FROM Activities a
      WHERE a.post_id = p.post_id
        AND a.action_type IN ('view', 'like')
  )
ORDER BY p.published_at ASC;


-- ---------------------------------------------------------------------
-- СКРИПТ 5: оконная функция — первая и последняя дата активности
-- для каждого пользователя
-- ---------------------------------------------------------------------
SELECT DISTINCT
    user_id,
    MIN(activity_timestamp) OVER (PARTITION BY user_id) AS first_activity,
    MAX(activity_timestamp) OVER (PARTITION BY user_id) AS last_activity,
    MAX(activity_timestamp) OVER (PARTITION BY user_id)
        - MIN(activity_timestamp) OVER (PARTITION BY user_id) AS active_period
FROM Activities
ORDER BY user_id;
