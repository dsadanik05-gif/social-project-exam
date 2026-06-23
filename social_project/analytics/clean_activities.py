import json
import re
import pandas as pd

INPUT_JSONL = r"C:\Users\Admin\Downloads\Telegram Desktop\social_project4\social_project\analytics\raw_activities.jsonl"
OUTPUT_CSV = r"C:\Users\Admin\Downloads\Telegram Desktop\social_project4\social_project\analytics\clean_activities.csv"

records = []
with open("raw_activities.jsonl", encoding="utf-8") as f:
    for line in f:
        records.append(json.loads(line))

df = pd.DataFrame(records)
print(f"Бастапқы жазбалар саны (исходных записей): {len(df)}")

# -----------------------------------------------------------------
# 1. Фильтрация некорректных типов действий
# -----------------------------------------------------------------
VALID_ACTIONS = ["like", "comment", "share", "view"]
before = len(df)
df = df[df["action_type"].isin(VALID_ACTIONS)]
print(f"Жарамсыз әрекет түрлері сүзілді (отфильтровано некорректных типов): {before - len(df)}")

# -----------------------------------------------------------------
# 2. Очистка comment_text от лишних спецсимволов и пробелов
# -----------------------------------------------------------------
def clean_comment(text):
    if pd.isna(text):
        return None
    # Убираем повторяющиеся спецсимволы типа *** //// и схожие, оставляем
    # буквы, цифры, базовую пунктуацию и эмодзи
    text = re.sub(r"[*/]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

df["comment_text"] = df["comment_text"].apply(clean_comment)

# -----------------------------------------------------------------
# 3. Заполнение пустого post_id значением 0
#    (действие не привязано к посту, например просмотр профиля)
# -----------------------------------------------------------------
missing_post = df["post_id"].isna().sum()
df["post_id"] = df["post_id"].fillna(0).astype(int)
print(f"'0' мәнімен толтырылған post_id саны (заполнено пустых post_id): {missing_post}")

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

OUTPUT_CSV = "clean_activities.csv"
print(f"\nТазаланған деректер сақталды (очищенные данные сохранены): {OUTPUT_CSV}")
print(f"Финал жазбалар саны (финальных записей): {len(df)}")
print("\nҮлгі (пример первых строк):")
print(df.head(5).to_string(index=False))
