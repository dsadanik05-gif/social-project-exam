import json
import random
from datetime import datetime, timedelta

random.seed(33)

VALID_ACTIONS = ["like", "comment", "share", "view"]
NOISY_ACTIONS = ["klik", "vote", "ping"]  # "мусорные" типы действий

N_USERS = 120
N_POSTS = 80
start_date = datetime(2026, 5, 1)

posts = []
for post_id in range(1, N_POSTS + 1):
    author_id = random.randint(1, N_USERS)
    created_offset = random.randint(0, 50)
    posts.append({"post_id": post_id, "author_id": author_id, "created_offset": created_offset})

events = []
event_id = 1

for _ in range(8000):
    user_id = random.randint(1, N_USERS)

    # 3% действий — "мусорный" тип (опечатка/баг клиента)
    if random.random() < 0.03:
        action_type = random.choice(NOISY_ACTIONS)
    else:
        action_type = random.choices(VALID_ACTIONS, weights=[40, 20, 10, 30])[0]

    # Действие может относиться к посту, либо быть "просмотром профиля" (без post_id)
    if random.random() < 0.05:
        post_id = None  # действие не привязано к посту
    else:
        post = random.choice(posts)
        post_id = post["post_id"]

    day_offset = random.randint(0, 55)
    hour_weights = [1]*6 + [2,3,4,4,3,3] + [3,3,4,4,3] + [4,5,6,6,5,4] + [3]
    hour = random.choices(range(24), weights=hour_weights)[0]
    minute = random.randint(0, 59)
    ts = (start_date + timedelta(days=day_offset)).replace(hour=hour, minute=minute, second=random.randint(0,59))

    comment_text = None
    if action_type == "comment":
        raw_comments = [
            "  Тамаша пост!!! 😍😍😍  ",
            "wow***...керемет екен",
            "Қызық   жазылған  ",
            "////осы дұрыс емес сияқты////",
            "Рахмет, пайдалы ақпарат)))",
        ]
        comment_text = random.choice(raw_comments)

    events.append({
        "event_id": event_id,
        "user_id": user_id,
        "action_type": action_type,
        "post_id": post_id,
        "comment_text": comment_text,
        "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
    })
    event_id += 1

with open("raw_activities.jsonl", "w", encoding="utf-8") as f:
    for ev in events:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")

# Сохраним также список постов и их авторов/дат создания — понадобится
# для таблицы Posts и поиска "заброшенных" постов
with open("posts_meta.json", "w", encoding="utf-8") as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)

print(f"Сгенерировано {len(events)} событий активности -> raw_activities.jsonl")
print(f"Постов: {len(posts)}, пользователей: {N_USERS}")
