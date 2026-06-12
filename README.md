# 🔍 Google Places Scraper

A full-stack web application for scraping business data from Google Places API. Extract leads, contact information, and business details worldwide.

## ✨ Features

- 🔎 **Multi-Keyword Search** — comma-separated queries searched in parallel
- 🌍 **Multi-Country** — Australia, United States, United Kingdom, Saudi Arabia
- 🏙️ **Multi-City** — up to 3 cities or "All Cities" per state
- 📊 **Smart Dedup** — domain-based unique identification
- 🏷️ **Google Maps Categories** — human-readable business categories
- 📧 **Email Extraction** — scrape contact emails from websites
- 📥 **CSV Export** — formatted with date/keyword/city in filename
- 📄 **Pagination** — 20 results per page with full navigation
- 🌐 **Website-Only Filter** — only returns businesses with websites
- 🚀 **One-Command Start** — `python start.py` or double-click `start.bat`
- 📱 **Responsive Design** — works on desktop and mobile

## 🛠️ Tech Stack

**Backend:** Flask (Python 3.11), Requests, Flask-CORS
**Frontend:** React 18, Axios, CSS3
**DevOps:** Docker, Nginx

## 🚀 Quick Start

```bash
# One command
python start.py

# Or manually
cd backend && pip install -r requirements.txt && python app.py   # Terminal 1
cd frontend && npm install && npm start                           # Terminal 2
```

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:5001`

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/search` | Search businesses (supports multi-keyword, multi-city) |
| POST | `/api/scrape-emails` | Extract emails from result websites |
| POST | `/api/jobs` | Create scraping job |
| GET | `/api/jobs/<id>` | Get job details |
| GET | `/api/export/<id>/csv` | Export results as CSV |
| GET | `/health` | Health check |

### Search Request

```json
{
  "query": "equipment hire, plumbing",
  "location": "Amsterdam, Auburn, Babylon NY",
  "limit": 800,
  "cities": ["Amsterdam", "Auburn", "Babylon"],
  "state": "NY"
}
```

## 📁 Project Structure

```
google_places/
├── backend/
│   ├── app.py                 # Flask routes
│   ├── scraper.py             # Google Places API + pagination + expansions
│   ├── address_parser.py      # International address parsing (AU/US/UK/SA)
│   ├── email_scraper.py       # Email extraction from websites
│   ├── utils.py               # URL cleaning, domain extraction
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.js             # Main component + state
│   │   ├── components/
│   │   │   ├── SearchForm.js  # Search form with country/state/city dropdowns
│   │   │   └── ResultsTable.js # Results table with pagination
│   │   └── data/
│   │       └── locations.js   # Countries, states, and cities
│   └── package.json
├── start.py / start.bat       # One-command launchers
├── stop.bat                   # Quick shutdown
├── docker-compose.yml
└── .env.example
```

## 🔧 Configuration

```bash
# .env
GOOGLE_PLACES_API_KEY=your_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| API key not valid | Enable Places API (New) in Google Cloud Console |
| Port in use | `taskkill /F /IM python.exe /IM node.exe` |
| CORS error | Backend has CORS enabled — check port is 5001 |
| No results | Try broader query or different city |

## 📄 License

MIT
