from pymongo import MongoClient
import json
from datetime import datetime

# === Připojení k MongoDB ===
client = MongoClient("mongodb://localhost:27017/")

# Vytvoření nebo připojení k databázi
db = client["articles_db"]
collection = db["articles"]

# === Načtení dat z NDJSON souboru ===

collection.delete_many({})

with open("data.ndjson", "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():  
            doc = json.loads(line)
            if "publish_date" in doc:
                try:
                    doc["publish_date"] = datetime.fromisoformat(doc["publish_date"].replace("Z", "+00:00"))
                except Exception:
                    pass
            collection.insert_one(doc)

print("Data successfully loaded into MongoDB.")



# 1 Jeden náhodný článek
random_article = list(collection.aggregate([{ "$sample": { "size": 1 } }]))[0]
print("\nRandom article:")
print("Title:", random_article["title"])
print("Category:", random_article["category"])
print("Publish date:", random_article["publish_date"])
print("URL:", random_article["url"])

# 2 Celkový počet článků 
total_articles = collection.count_documents({})
print("\nTotal number of articles:", total_articles)

# 3 Průměrný počet fotek na článek
avg_photos = list(collection.aggregate([
    { "$group": { "_id": None, "avg_photos": { "$avg": "$photos_count" } } }
]))
avg_value = avg_photos[0]["avg_photos"] if avg_photos else 0
print("Average number of photos per article:", round(avg_value, 2))

# 4 Počet článků s více než 100 komentáři
count_over_100 = collection.count_documents({ "comments_count": { "$gt": 100 } })
print("Number of articles with more than 100 comments:", count_over_100)

# 5 Počet článků z roku 2022 podle kategorií
articles_2022 = collection.aggregate([
    {
        "$match": {
            "publish_date": {
                "$gte": datetime(2022, 1, 1),
                "$lt": datetime(2023, 1, 1)
            }
        }
    },
    {
        "$group": {
            "_id": "$category",
            "count": { "$sum": 1 }
        }
    }
])

print("\nNumber of 2022 articles by category:")
for a in articles_2022:
    print(f" - {a['_id']}: {a['count']}")

print("\nAll queries executed successfully.")
