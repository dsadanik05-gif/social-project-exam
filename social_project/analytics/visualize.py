import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import os

# 1. Автоматически определяем папку со скриптом
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Объединяем путь к папке с именем файла clean_acivities.csv
INPUT_CSV = os.path.join(BASE_DIR, "clean_activities.csv")

OUT_DIR = BASE_DIR

df = pd.read_csv(INPUT_CSV, parse_dates=["timestamp"])

# 1. Диаграмма

action_counts = df["action_type"].value_counts()

plt.figure(figsize=(8, 6))
colors = {"like": "#2E75B6", "comment": "#70AD47", "share": "#FFC000", "view": "#C0392B"}
bar_colors = [colors[a] for a in action_counts.index]
plt.bar(action_counts.index, action_counts.values, color=bar_colors)
plt.title("Әрекет түрлерінің таралуы (лайк/комментарий/репост/қаралым)")
plt.ylabel("Әрекеттер саны")
for i, v in enumerate(action_counts.values):
    plt.text(i, v + max(action_counts.values)*0.01, str(v), ha="center")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/chart_action_distribution.png", dpi=150)
plt.close()
print("Сохранён график: chart_action_distribution.png")

# -----------------------------------------------------------------
# 2. DAU — Daily Active Users (уникальные пользователи в день)
# -----------------------------------------------------------------
df["date"] = df["timestamp"].dt.date
dau = df.groupby("date")["user_id"].nunique()

plt.figure(figsize=(12, 5))
plt.plot(dau.index, dau.values, color="#2E75B6", linewidth=1.5)
plt.title("Күнделікті белсенді пайдаланушылар саны (DAU)")
plt.xlabel("Күн")
plt.ylabel("Бірегей пайдаланушылар саны")
plt.grid(alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/chart_dau.png", dpi=150)
plt.close()
print("Сохранён график: chart_dau.png")

# -----------------------------------------------------------------
# 3. Тепловая карта активности: дни недели x часы суток
# -----------------------------------------------------------------
df["day_name"] = df["timestamp"].dt.day_name()
df["hour"] = df["timestamp"].dt.hour

day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_labels = ["Дс", "Сс", "Ср", "Бс", "Жм", "Сб", "Жс"]

heatmap_data = df.groupby(["day_name", "hour"]).size().unstack(fill_value=0)
heatmap_data = heatmap_data.reindex(day_order)

plt.figure(figsize=(13, 5))
im = plt.imshow(heatmap_data.values, aspect="auto", cmap="YlOrRd")
plt.colorbar(im, label="Әрекеттер саны")
plt.yticks(range(len(day_labels)), day_labels)
plt.xticks(range(24), range(24))
plt.xlabel("Тәуліктің сағаты")
plt.ylabel("Апта күні")
plt.title("Апта күндері мен сағаттар бойынша белсенділік жылу картасы")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/chart_heatmap_activity.png", dpi=150)
plt.close()
print("Сохранён график: chart_heatmap_activity.png")
