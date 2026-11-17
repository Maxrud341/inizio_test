# Google SERP Scraper — Vstupní test pro INIZIO

Webová aplikace pro získání a export první stránky **pouze přirozených (organických) výsledků vyhledávání Google** bez reklam a sponzorovaných odkazů.

- **Autor:** Maksym Rudniev
- **GitHub:** [https://github.com/Maxrud341/inizio_test](https://github.com/Maxrud341/inizio_test)

---

## 🚀 Funkce aplikace
1. **Jednoduché rozhraní:** Webová stránka s jedním vyhledávacím polem (Bootstrap 5).
2. **Čistá organika:** Získání výsledků z 1. stránky Google s odfiltrováním reklam, Google Ads a sponzorovaného obsahu.
3. **Strukturovaný export:** Možnost okamžitého stažení výsledků do strojově čitelného formátu:
   - **JSON**
   - **CSV** (s kódováním UTF-8 BOM pro bezproblémové otevření v Microsoft Excelu).
4. **Unit testy:** Pokrytí 18 unit testy ověřujícími správnost výstupu, formát dat a nepřítomnost reklam (pokrytí modulu scraperu 87 %).
5. **Docker Compose:** Plně konfigurované prostředí pro lokální vývoj (`compose.yaml`).
6. **CI/CD:** Automatické testy na GitHub Actions při každém pushi.

---

## 🛠️ Použité technologie
- **Backend:** Python 3.11+, Flask (Application Factory vzor), Gunicorn
- **Získávání SERP dat:** SerpApi (zaručuje 100% stabilitu v produkci bez rizika CAPTCHA a blokace IP)
- **Frontend:** HTML5, Bootstrap 5, JavaScript (Fetch API)
- **Testování:** `pytest`, `pytest-cov`
- **Kontejnerizace & Nasazení:** Docker, Docker Compose, Railway

---

## 💻 Lokální spuštění

### Možnost A: Přes Docker Compose (Doporučeno)
```bash
# 1. Zkopírujte vzorový soubor proměnných
cp .env.example .env

# 2. Vložte váš SERPAPI_KEY do souboru .env

# 3. Spusťte aplikaci
docker compose up --build
```
Aplikace bude dostupná na: `http://localhost:8080`

---

### Možnost B: Lokální spuštění v Pythonu
```bash
# 1. Vytvoření a aktivace virtuálního prostředí
python -m venv .venv
source .venv/bin/activate    # Linux / macOS
# nebo na Windows:
.\.venv\Scripts\activate

# 2. Instalace závislostí
pip install -r requirements.txt

# 3. Nastavení .env souboru (přidejte SERPAPI_KEY)
cp .env.example .env

# 4. Spuštění serveru
python run.py
```
Aplikace běží na: `http://127.0.0.1:5000`

---

## 🧪 Spuštění Unit Testů
Testy běží kompletně offline na připraveném mock fixture bez nutnosti internetového připojení či API klíče:

```bash
pytest -v --cov=app/scraper --cov-report=term-missing
```

---

## 📁 Struktura projektu
```text
├── app/
│   ├── __init__.py          # create_app() továrna aplikace
│   ├── config.py            # Konfigurace prostředí
│   ├── routes/
│   │   └── main.py          # Endpointy: GET /, POST /api/search, POST /api/export
│   ├── scraper/
│   │   ├── google_serp.py   # Logika filtrování a parsování organiky
│   │   └── models.py        # Datový model SerpItem
│   └── templates/
│       └── index.html       # Frontend (Bootstrap 5)
├── tests/
│   ├── fixtures/
│   │   └── sample_serp.json # Mock SERP odpověď pro offline testy
│   └── unit/
│       └── test_parser.py   # 18 unit testů
├── Dockerfile               # Produkční Dockerfile
├── compose.yaml             # Docker Compose pro vývoj
├── requirements.txt         # Závislosti projektu
├── run.py                   # Vstupní bod aplikace
└── README.md
```
