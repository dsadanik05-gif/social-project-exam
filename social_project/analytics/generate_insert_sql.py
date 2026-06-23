import json
import pandas as pd
import random

random.seed(9)

with open("posts_meta.json", encoding="utf-8") as f:
    posts_meta = json.load(f)

df = pd.read_csv("clean_activities.csv", parse_dates=["timestamp"])

# Для удобства демонстрации на защите ограничим объём логов
if len(df) > 3000:
    df = df.sample(n=3000, random_state=42).sort_values("timestamp").reset_index(drop=True)

user_ids = sorted(set(df["user_id"]) | {p["author_id"] for p in posts_meta})

NAMES = ["Айгерим", "Нурлан", "Бакыт", "Гульнара", "Асан", "Дана", "Бекзат",
         "Жанна", "Серик", "Алия", "Ержан", "Madina", "Тимур", "Сауле"]

lines = []
lines.append("-- =====================================================================")
lines.append("-- Тестовые данные: загрузка пользователей, постов и активностей")
lines.append("-- Сгенерировано автоматически из posts_meta.json и clean_activities.csv")
lines.append("-- =====================================================================\n")

# -----------------------------------------------------------------
# Users
# -----------------------------------------------------------------
lines.append("INSERT INTO Users (user_id, full_name, account_created) VALUES")
user_rows = []
for uid in user_ids:
    name = f"{random.choice(NAMES)} №{uid}"
    days_before = random.randint(60, 900)
    created = (pd.Timestamp("2026-05-01") - pd.Timedelta(days=days_before)).strftime("%Y-%m-%d")
    user_rows.append(f"({uid}, '{name}', '{created}')")
lines.append(",\n".join(user_rows) + ";\n")
lines.append("SELECT setval('users_user_id_seq', (SELECT MAX(user_id) FROM Users));\n")

# -----------------------------------------------------------------
# Posts
# -----------------------------------------------------------------
lines.append("INSERT INTO Posts (post_id, author_id, post_text, published_at) VALUES")
post_rows = []
for p in posts_meta:
    pub_date = (pd.Timestamp("2026-05-01") + pd.Timedelta(days=p["created_offset"])).strftime("%Y-%m-%d %H:%M:%S")
    post_text = f"Пост №{p['post_id']} мазмұны"
    post_rows.append(f"({p['post_id']}, {p['author_id']}, '{post_text}', '{pub_date}')")
lines.append(",\n".join(post_rows) + ";\n")
lines.append("SELECT setval('posts_post_id_seq', (SELECT MAX(post_id) FROM Posts));\n")

# -----------------------------------------------------------------
# Activities (батчами по 500 строк)
# -----------------------------------------------------------------
lines.append(f"-- Загрузка {len(df)} записей активности (батчами по 500 строк)")
batch_size = 500
for start in range(0, len(df), batch_size):
    batch = df.iloc[start:start + batch_size]
    lines.append("INSERT INTO Activities (user_id, action_type, post_id, comment_text, activity_timestamp) VALUES")
    row_strs = []
    for _, row in batch.iterrows():
        ts = row["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        comment = row["comment_text"]
        if pd.isna(comment):
            comment_sql = "NULL"
        else:
            comment_sql = "'" + str(comment).replace("'", "''") + "'"
        row_strs.append(f"({int(row['user_id'])}, '{row['action_type']}', {int(row['post_id'])}, {comment_sql}, '{ts}')")
    lines.append(",\n".join(row_strs) + ";\n")

with open("02_seed_data.sql", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Сгенерирован SQL-файл: {len(user_ids)} пользователей, {len(posts_meta)} постов, {len(df)} активностей -> 02_seed_data.sql")
