import pandas as pd
import matplotlib.pyplot as plt
import re

# --- Load data ---
df = pd.read_json("data.ndjson", lines=True)

# --- Normalize date column ---
date_col = None
for candidate in ["publish_date", "date"]:
    if candidate in df.columns:
        date_col = candidate
        break

if not date_col:
    raise SystemExit("No valid date column found (publish_date/date)")

df[date_col] = pd.to_datetime(df[date_col], errors="coerce", utc=True)
df = df.dropna(subset=[date_col]).copy()
df["publish_date"] = pd.to_datetime(df[date_col], errors="coerce").dt.tz_localize(None)

# --- Numeric conversions ---
if "images" in df.columns:
    df["images_count"] = df["images"].apply(lambda x: len(x) if isinstance(x, list) else 0)
else:
    df["images_count"] = 0

if "comments_count" in df.columns:
    df["comments_count"] = pd.to_numeric(df["comments_count"], errors="coerce").fillna(0).astype(int)
else:
    df["comments_count"] = 0

# Word count
df["word_count"] = df["content"].fillna("").apply(lambda t: len(t.split()))

# --- 1. Line plot: articles over time ---
articles_over_time = df.set_index("publish_date").resample("ME").size()
plt.figure(figsize=(10, 4))
plt.plot(articles_over_time.index, articles_over_time.values, marker="o")
plt.title("Articles Over Time")
plt.xlabel("Date")
plt.ylabel("Number of Articles")
plt.grid(True)
plt.show()

# --- 2. Bar chart: articles per year ---
df["year"] = df["publish_date"].dt.year
year_counts = df["year"].value_counts().sort_index()
plt.figure(figsize=(8, 4))
plt.bar(year_counts.index.astype(str), year_counts.values)
plt.title("Articles per Year")
plt.xlabel("Year")
plt.ylabel("Number of Articles")
plt.show()

# --- 3. Scatter: length vs comments ---
plt.figure(figsize=(8, 6))
plt.scatter(df["word_count"], df["comments_count"], alpha=0.5)
plt.title("Relationship Between Article Length and Comments")
plt.xlabel("Word Count")
plt.ylabel("Number of Comments")
plt.grid(True)
plt.show()

# --- 4. Pie chart: categories (all, not just top 12) ---
if "category" in df.columns:
    cat_series = df["category"].dropna().astype(str)
    cat_series = cat_series[cat_series.str.strip() != ""]
    if len(cat_series) > 0:
        cat_counts = cat_series.value_counts()
        plt.figure(figsize=(8, 8))
        plt.pie(cat_counts.values, labels=cat_counts.index, autopct="%1.1f%%", startangle=90)
        plt.title("Article Distribution by Category")
        plt.show()

# --- 5. Histogram: word count ---
plt.figure(figsize=(8, 4))
plt.hist(df["word_count"].clip(upper=5000), bins=50, color="skyblue", edgecolor="black")
plt.title("Word Count Distribution")
plt.xlabel("Number of Words")
plt.ylabel("Number of Articles")
plt.show()

# --- 6. Histogram: word length (1–20 range) ---
all_text = " ".join(df["content"].dropna())
word_lengths = [len(w) for w in re.findall(r"\w+", all_text)]
word_lengths = [l for l in word_lengths if 1 <= l <= 20]

plt.figure(figsize=(8, 4))
plt.hist(word_lengths, bins=range(1, 22), color="lightgreen", edgecolor="black")
plt.title("Word Length Distribution (1–20 characters)")
plt.xlabel("Word Length")
plt.ylabel("Word Count")
plt.xticks(range(1, 21))
plt.show()

# --- 7. Timeline: 'koronavirus' vs 'vakcina' ---
df["title_clean"] = df["title"].fillna("").str.lower()
df["koronavirus_count"] = df["title_clean"].str.count("koronavirus")
df["vakcina_count"] = df["title_clean"].str.count("vakc")

timeline = (
    df.set_index("publish_date")[["koronavirus_count", "vakcina_count"]]
    .resample("M")
    .sum()
)

plt.figure(figsize=(10, 4))
plt.plot(timeline.index, timeline["koronavirus_count"], label="koronavirus", color="red")
plt.plot(timeline.index, timeline["vakcina_count"], label="vakcina", color="blue")
plt.title("Frequency of 'koronavirus' and 'vakcina' in Titles")
plt.xlabel("Date")
plt.ylabel("Count")
plt.legend()
plt.grid(True)
plt.show()

# --- 8. Articles by weekday ---
df["weekday"] = df["publish_date"].dt.day_name()
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weekday_counts = df["weekday"].value_counts().reindex(weekday_order)

plt.figure(figsize=(9, 4))
plt.bar(weekday_counts.index, weekday_counts.values, color="orange", edgecolor="black")
plt.title("Articles by Day of the Week")
plt.xlabel("Day of the Week")
plt.ylabel("Number of Articles")
plt.xticks(rotation=20)
plt.show()
