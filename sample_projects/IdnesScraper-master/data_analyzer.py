import json
from collections import Counter
from datetime import datetime

# count = 0
# urls = set()
# dups = 0
# bad_lines = 0
# empty_fields = 0
# valid_items = []

# # --- Read and analyze ---
# with open("data.json", "r", encoding="utf-8") as f:
#     for line in f:
#         line = line.strip()
#         if not line:
#             continue
#         try:
#             item = json.loads(line)
#         except json.JSONDecodeError:
#             bad_lines += 1
#             if bad_lines < 20:
#                 print("Invalid JSON line:", line[:200], "...")
#             continue

#         count += 1

#         if any(v in (None, "", [], {}) for v in item.values()):
#             empty_fields += 1

#         url = item.get("url")
#         if url in urls:
#             dups += 1
#         else:
#             urls.add(url)
#             valid_items.append(item)

#         if count % 100000 == 0:
#             print(f"Processed {count} news items, found {dups} duplicates, {empty_fields} items with empty fields")


# print("Total news items:", count)
# print("Total duplicates:", dups)
# print("Total items with empty fields:", empty_fields)
# if count > 0:
#     print("Duplicate percentage:", round(dups / count * 100, 2), "%")
#     print("Empty fields percentage:", round(empty_fields / count * 100, 2), "%")
# print("Invalid lines:", bad_lines)



# # --- Write cleaned file without duplicates or invalid lines ---
# with open("data.ndjson", "w", encoding="utf-8") as f:
#     for item in valid_items:
#         f.write(json.dumps(item, ensure_ascii=False) + "\n")

# # --- Stats after cleaning ---
# print("\n--- After cleaning ---")
# print("Total news items:", len(valid_items))
# print("Total duplicates removed:", dups)
# print("Invalid lines removed:", bad_lines)





# --- Load cleaned data ---
items = []
with open("data.ndjson", "r", encoding="utf-8") as f:
    for line in f:
        items.append(json.loads(line))

if not items:
    print("Soubor je prázdný!")
    exit()


# 1 --- Najít nejstarší datum ---
dates = []
oldest_item = None

for item in items:
    date_str = item.get("publish_date")
    if date_str:
        try:
            date_parsed = datetime.fromisoformat(date_str)
            dates.append(date_parsed)
            if oldest_item is None or date_parsed < datetime.fromisoformat(oldest_item["publish_date"]):
                oldest_item = item
        except ValueError:
            pass

if oldest_item:
    print("Nejstarší článek:")
    print("  Název:", oldest_item.get("title", "Bez názvu"))
    print("  Datum:", oldest_item["publish_date"])
    print("  URL:", oldest_item.get("url", "Bez URL"))
else:
    print("V datech nebyly nalezeny žádné platné publish_date.")


# 2 --- Článek s nejvíce komentáři ---
max_comments = -1
most_commented_item = None

for item in items:
    comments = item.get("comments_count", 0)
    try:
        comments = int(comments)
    except (ValueError, TypeError):
        comments = 0

    if comments > max_comments:
        max_comments = comments
        most_commented_item = item

if most_commented_item:
    print("Článek s nejvíce komentáři:")
    print("  Název:", most_commented_item.get("title", "Bez názvu"))
    print("  Komentáře:", max_comments)
    print("  URL:", most_commented_item.get("url", "Bez URL"))
else:
    print("V datech nebyly nalezeny žádné články s komentáři.")


# 3 --- Nejvyšší počet přidaných fotek u článku ---
max_photos = -1
max_photos_item = None

for item in items:
    photos = item.get("photos_count", 0)
    try:
        photos = int(photos)
    except (ValueError, TypeError):
        photos = 0

    if photos > max_photos:
        max_photos = photos
        max_photos_item = item

if max_photos_item:
    print("Článek s nejvyšším počtem fotek:")
    print("  Název:", max_photos_item.get("title", "Bez názvu"))
    print("  Počet fotek:", max_photos)
    print("  URL:", max_photos_item.get("url", "Bez URL"))
else:
    print("V datech nebyly nalezeny žádné fotky.")



from collections import Counter
from datetime import datetime

# --- 4. Počty článků podle roku publikace ---
year_counts = Counter()
for item in items:
    date_str = item.get("publish_date")
    if date_str:
        try:
            year = datetime.fromisoformat(date_str).year
            year_counts[year] += 1
        except ValueError:
            pass

print("Počet článků podle roku publikace:")
for year, count in sorted(year_counts.items()):
    print(f"{year}: {count}")


# --- 5. Počet unikátních kategorií a počet článků v každé kategorii ---
category_counts = Counter()
for item in items:
    cat = item.get("category")
    if cat:
        category_counts[cat] += 1

print("\nPočet unikátních kategorií:", len(category_counts))
print("Počet článků v každé kategorii:")
for cat, count in category_counts.items():
    print(f"{cat}: {count}")


# --- 6. 5 nejčastějších slov v názvu článků z roku 2021 ---
titles_2021 = [item.get("title", "") for item in items 
               if item.get("publish_date") 
               and datetime.fromisoformat(item.get("publish_date")).year == 2021]

words_2021 = Counter()
for title in titles_2021:
    for word in title.lower().split():
        word = word.strip(".,!?:;\"()[]{}")  # odstranění interpunkce
        if word:
            words_2021[word] += 1

print("\n5 nejčastějších slov v názvech článků z roku 2021:")
for word, count in words_2021.most_common(5):
    print(f"{word} - {count}")


# --- 7. Celkový počet komentářů ---
total_comments = 0
for item in items:
    comments = item.get("comments_count", 0)
    try:
        total_comments += int(comments)
    except (ValueError, TypeError):
        pass

print("\nCelkový počet komentářů:", total_comments)


# --- 8. Celkový počet slov ve všech článcích ---
total_words = 0
for item in items:
    content = item.get("content", "")
    total_words += len(content.split())

print("Celkový počet slov ve všech článcích:", total_words)



# --- 1. 8 nejčastějších slov v článcích, délka >= 6 písmen ---
word_counts = Counter()
total_word_length = 0
total_words = 0
articles_word_counts = []  # uloží počet slov na článek

for item in items:
    content = item.get("content", "")
    words = content.split()
    articles_word_counts.append((item, len(words)))

    for word in words:
        clean_word = word.lower().strip(".,!?:;\"()[]{}")
        total_word_length += len(clean_word)
        total_words += 1
        if len(clean_word) >= 6:
            word_counts[clean_word] += 1

print("8 nejčastějších slov v článcích (≥6 písmen):")
for word, count in word_counts.most_common(8):
    print(f"{word} - {count}")


# --- 2. 3 články s nejvyšším počtem výskytů slova 'covid-19' ---
covid_counts = []
for item in items:
    content = item.get("content", "").lower()
    count = content.count("covid-19")
    covid_counts.append((item, count))

top_covid_articles = sorted(covid_counts, key=lambda x: x[1], reverse=True)[:3]
print("\n3 články s nejvyšším počtem výskytů slova 'Covid-19':")
for art, count in top_covid_articles:
    print(f"  Název: {art.get('title', 'Bez názvu')}, Počet: {count}, URL: {art.get('url', 'Bez URL')}")


# --- 3. Články s nejvyšším a nejnižším počtem slov ---
articles_word_counts_sorted = sorted(articles_word_counts, key=lambda x: x[1])
min_article, min_words = articles_word_counts_sorted[0]
max_article, max_words = articles_word_counts_sorted[-1]

print("\nČlánek s nejmenším počtem slov:")
print(f"  Název: {min_article.get('title', 'Bez názvu')}, Počet slov: {min_words}, URL: {min_article.get('url', 'Bez URL')}")

print("\nČlánek s největším počtem slov:")
print(f"  Název: {max_article.get('title', 'Bez názvu')}, Počet slov: {max_words}, URL: {max_article.get('url', 'Bez URL')}")


# --- 4. Průměrná délka slova přes všechny články ---
avg_word_length = total_word_length / total_words if total_words > 0 else 0
print(f"\nPrůměrná délka slova přes všechny články: {avg_word_length:.2f} písmen")


# --- 5. Měsíce s nejvíce a nejméně publikovanými články ---
month_counts = Counter()
for item in items:
    date_str = item.get("publish_date")
    if date_str:
        try:
            dt = datetime.fromisoformat(date_str)
            month_counts[dt.month] += 1
        except ValueError:
            pass

most_month = month_counts.most_common(1)[0]
least_month = min(month_counts.items(), key=lambda x: x[1])

print(f"\nMěsíc s nejvíce publikovanými články: {most_month[0]} ({most_month[1]} článků)")
print(f"Měsíc s nejméně publikovanými články: {least_month[0]} ({least_month[1]} článků)")