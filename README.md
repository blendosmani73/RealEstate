# Real Estate Data Engine

Platformë për analizën, procesimin e të dhënave dhe parashikimin e çmimeve të pasurive të paluajtshme.

Lënda: Sistemet e procesimit të të dhënave Dizajnuese.

Staku: Python, FastAPI, PostgreSQL, Streamlit, Pandas, Scikit-Learn, Docker.

## Struktura e projektit

```text
RealEstate_DataEngine/
├── backend/                 # API, ETL, ML, databaza (logjika)
│   ├── main.py              # FastAPI
│   ├── database.py, schemas.py, auth.py, admin_config.py
│   ├── etl_pipeline.py, ml_model.py
│   ├── schema.sql, data.csv
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # Streamlit dashboard (UI)
│   ├── app.py
│   ├── ui.py                # Stil premium & navigim
│   ├── .streamlit/config.toml
│   ├── requirements.txt
│   └── Dockerfile
├── docs/                    # Specifikim, arkitekturë, performancë
├── docker-compose.yml       # db + backend + frontend
├── .env.example
└── README.md
```

## Dokumentacioni i lëndës

| Dokument | Përmbajtja |
|----------|------------|
| [docs/SPECIFICATION.md](docs/SPECIFICATION.md) | Problemi, aktorët, kërkesat funksionale/jofunksionale |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Shtresat, rrjedha e të dhënave, arsyetimi teknik |
| [docs/DATA_SOURCE.md](docs/DATA_SOURCE.md) | Burimi dhe formati i `data.csv` |
| [docs/PERFORMANCE.md](docs/PERFORMANCE.md) | Indekse, matje, kufizime |
| [TEST_REPORT.md](TEST_REPORT.md) | Rastet e testimit dhe evidenca |

## Arkitektura

- `db` — PostgreSQL 16. `schema.sql` krijon tabelat `users` dhe `properties`, constraint-et `price > 0` dhe `area_sqm > 0`, dhe indekset B-Tree mbi `location`, `price`, `property_type`.
- `backend` — FastAPI. Në nisje pret databazën, siguron tabelat, ekzekuton ETL dhe trajnon Random Forest.
- `frontend` — Streamlit. Dashboard-i, parashikimi dhe lista e pronave thërrasin API-në.

`price_per_sqm` llogaritet gjatë ETL-së dhe përsëri kur shtohet një pronë nga API-ja. Klienti nuk e dërgon këtë fushë.

## Nisja me Docker

Duhet Docker Desktop. Nga **rrënja** e projektit (`RealEstate_DataEngine`):

```powershell
Copy-Item .env.example .env
docker compose up --build
```

- Dashboard: http://localhost:8501
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

Në logun e `backend` shfaqet raporti i ETL-së dhe i trajnimit (`rows`, `r2`, `training_mode`).

`schema.sql` ekzekutohet vetëm kur volume-i i PostgreSQL është bosh. ETL ngarkon `data.csv` vetëm kur tabela `properties` është bosh, që pronat e shtuara nga dashboard-i të mos fshihen në rinisje.

Për ta kthyer databazën në gjendjen e CSV-së:

```powershell
docker compose down -v
docker compose up --build
```

Ringarkim pa fshirë volume-in:

```powershell
docker compose exec backend python etl_pipeline.py --force
docker compose exec backend python ml_model.py
```

Pas një prone të re, modeli i hapur në memorie mbetet ai i nisjes. Rinisni backend-in që parashikimi të përfshijë rreshtat e rinj:

```powershell
docker compose restart backend
```

## Si ta provoni

1. Hapni http://localhost:8501 — **6 seksione:** Dashboard, Parashikim, Pronat, Raport & eksport, Krahaso, Rreth platformës.
2. Te "Parashikimi i çmimit" zgjidhni Prishtinë, Apartment, 2 dhoma, 1 banjo, 70 m².
3. Regjistrohuni nga menuja anësore, pastaj shtoni një pronë. Çmimi për m² llogaritet në server.
4. Te Swagger, `POST /api/auth/register`, pastaj `POST /api/auth/login`. Kopjoni `access_token`, shtypni Authorize dhe vendosni `Bearer <token>` për `POST /api/properties`.
5. **Administratori** i paracaktuar: emaili në `ADMIN_EMAIL` (`.env`) — **`blendosmani20@gmail.com`**. Ky email merr automatikisht rol **admin** kur regjistrohet; nëse ekziston si `user`, roli përditësohet në admin kur niset backend-i. Vetëm admin mund të **fshijë** prona.
6. Në Streamlit, seksioni **Pronat** ofron edhe **Ndrysho** dhe **Fshi (admin)**.

Shembull nga PowerShell:

```powershell
Invoke-RestMethod http://localhost:8000/api/properties

Invoke-RestMethod http://localhost:8000/api/predict -Method Post -ContentType "application/json" -Body '{"location":"Prishtinë","bedrooms":2,"bathrooms":1,"area_sqm":70,"property_type":"Apartment"}'
```

## Endpoint-et

| Metoda | Shtegu | Mbrojtja |
| --- | --- | --- |
| POST | `/api/auth/register` | publike |
| POST | `/api/auth/login` | publike, kthen JWT |
| GET | `/api/auth/me` | JWT |
| GET | `/api/properties` | publike, `page`, `page_size`, `location`, `min_price`, `max_price` |
| GET | `/api/properties/{id}` | publike |
| POST | `/api/properties` | JWT (`user` / `admin`) |
| PUT | `/api/properties/{id}` | JWT (`user` / `admin`) |
| DELETE | `/api/properties/{id}` | JWT, vetëm **`admin`** |
| POST | `/api/predict` | publike |

## Testim dhe performancë

```powershell
docker compose exec backend pytest tests/ -v
docker compose exec backend python benchmark_performance.py
```

## ETL

`etl_pipeline.py` lexon `data.csv` me Pandas dhe:

1. heq duplikatet;
2. pastron tekstin dhe kthen vlerat numerike e pavlefshme në missing;
3. heq rreshtat pa titull, lokacion, çmim, sipërfaqe ose lloj;
4. plotëson dhomat dhe banjot që mungojnë me medianë;
5. mban vetëm `price > 0` dhe `area_sqm > 0`;
6. llogarit `price_per_sqm = price / area_sqm`;
7. i ngarkon rreshtat në `properties`.

## Modeli

`ml_model.py` trajnon `RandomForestRegressor` me tipare: `bedrooms`, `bathrooms`, `area_sqm`, `location`, `property_type`.

`data.csv` ka 8 rreshta. Nën 10 rreshta modeli trajnohet mbi të gjithë kampionin dhe R² është in-sample. Me 10 ose më shumë prona, i njëjti kod bën train/test split 80/20.

## Nisje pa Docker

PostgreSQL duhet të jetë nisur lokalisht. Në `.env` (rrënjë) vendosni `POSTGRES_HOST=localhost`, krijoni databazën `realestate_db` dhe ekzekutoni `backend/schema.sql`.

**Backend:**

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python etl_pipeline.py
python ml_model.py
uvicorn main:app --reload
```

**Frontend** (terminal i ri):

```powershell
cd frontend
pip install -r requirements.txt
$env:API_URL="http://localhost:8000"
streamlit run app.py
```

## Shënim sigurie

`POSTGRES_PASSWORD` dhe `SECRET_KEY` në `.env.example` janë për punë lokale të lëndës. `.env` nuk kopjohet brenda imazhit të Docker-it; kontejnerët e marrin atë në nisje.
