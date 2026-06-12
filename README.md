# 🔍 Google Places Scraper

A full-stack web application for scraping business data from Google Places API. Extract leads, contact information, and business details from Australian businesses with ease.

## ✨ Features

- 🔎 **Google Places Search** - Search businesses across multiple locations
- 📊 **Interactive Dashboard** - Modern React frontend with real-time results
- 📥 **CSV Export** - Download results in CSV format
- 🎯 **Advanced Parsing** - Automatic address parsing for Australian addresses
- 📧 **Email Extraction** - Extract contact emails from business websites (optional)
- 🚀 **Scalable Backend** - Flask API with job management
- 🐳 **Docker Support** - Easy deployment with Docker Compose
- 📱 **Responsive Design** - Works on desktop and mobile devices

## 🛠️ Tech Stack

**Backend:**
- Flask (Python 3.11)
- Flask-CORS for cross-origin requests
- Google Places API (New)
- Gunicorn for production serving

**Frontend:**
- React 18
- Axios for API calls
- Modern CSS3 with responsive design

**DevOps:**
- Docker & Docker Compose
- Nginx for frontend serving

## 📋 Prerequisites

- Python 3.8+ (for local development)
- Node.js 14+ (for local frontend development)
- Docker & Docker Compose (optional, for containerized deployment)
- Google Places API key ([Get one here](https://cloud.google.com/maps-platform))

## 🚀 Quick Start

### Option 1: Local Development

**Backend Setup:**
```bash
cd backend
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env and add your Google Places API key
python app.py
```

Backend will be available at `http://localhost:5000`

**Frontend Setup (in another terminal):**
```bash
cd frontend
npm install
npm start
```

Frontend will be available at `http://localhost:3000`

### Option 2: Docker Deployment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Google Places API key
nano .env  # or use your preferred editor

# Build and run
docker-compose up --build
```

Access the application at:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5000`

## 📡 API Documentation

### Search Businesses

**Endpoint:** `POST /api/search`

**Request:**
```json
{
  "query": "equipment hire",
  "location": "Sydney NSW",
  "limit": 50
}
```

**Response:**
```json
{
  "success": true,
  "count": 42,
  "query": "equipment hire in Sydney NSW",
  "location": "Sydney NSW",
  "results": [
    {
      "id": "place_12345",
      "name": "ABC Equipment Hire",
      "address": "123 Main St",
      "city": "Sydney",
      "state": "NSW",
      "postcode": "2000",
      "phone": "+61 2 1234 5678",
      "website": "https://abc-equipment.com.au",
      "domain": "abc-equipment.com.au"
    }
    // ... more results
  ]
}
```

### Create Job

**Endpoint:** `POST /api/jobs`

**Request:**
```json
{
  "query": "equipment hire",
  "locations": ["Sydney NSW", "Melbourne VIC"]
}
```

**Response:**
```json
{
  "id": 1,
  "query": "equipment hire",
  "locations": ["Sydney NSW", "Melbourne VIC"],
  "status": "pending",
  "created_at": "2024-06-05T10:30:00",
  "results": [],
  "progress": 0
}
```

### Get Job Details

**Endpoint:** `GET /api/jobs/<job_id>`

**Response:** Returns job object with current status and results

### Export Results as CSV

**Endpoint:** `GET /api/export/<job_id>/csv`

**Response:** CSV file download

### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-06-05T10:30:00"
}
```

## 🎨 Frontend Features

### Search Page
- Search query input
- Location selection
- Result limit adjustment
- Real-time result count

### Results Table
- Searchable/filterable results
- All business details displayed
- Website links (clickable)
- Phone numbers formatted
- State badges with color coding
- Domain extraction

### Data Export
- CSV export with all fields
- Formatted output ready for outreach
- Single-click download

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Google Places API
GOOGLE_PLACES_API_KEY=your_actual_key_here

# Backend
FLASK_ENV=development
FLASK_DEBUG=True

# Frontend
REACT_APP_API_URL=http://localhost:5000
```

## 📁 Project Structure

```
google_places/
├── backend/
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   └── .env                  # Environment variables
├── frontend/
│   ├── public/
│   │   └── index.html        # HTML entry point
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.css           # Application styles
│   │   ├── index.js          # React entry point
│   │   └── index.css         # Global styles
│   ├── package.json          # NPM dependencies
│   ├── .env                  # Frontend environment
│   └── .gitignore            # Git ignore file
├── docker-compose.yml        # Docker composition
├── Dockerfile.backend        # Backend container
├── Dockerfile.frontend       # Frontend container
├── .env.example             # Environment template
└── README.md                # This file
```

## 🐛 Troubleshooting

### API Key Issues
```
Error: "API key not configured"
```
- Ensure `GOOGLE_PLACES_API_KEY` is set in `.env`
- Verify the Places API (New) is enabled in Google Cloud Console
- Check that the API key has appropriate permissions and quota

### CORS Errors
```
Error: "Access to XMLHttpRequest blocked by CORS policy"
```
- Backend has CORS enabled by default
- Ensure `REACT_APP_API_URL` points to the correct backend URL
- Check that backend is running and accessible

### Port Already in Use
```
Error: "Address already in use"
```
- Change ports in `.env` or `docker-compose.yml`
- Or kill existing processes:
  ```bash
  # On macOS/Linux
  lsof -ti:5000,3000 | xargs kill -9
  
  # On Windows
  netstat -ano | findstr :5000
  taskkill /PID <PID> /F
  ```

### Frontend Can't Connect to Backend
- Verify backend is running: `curl http://localhost:5000/health`
- Check firewall settings
- Ensure CORS is enabled in Flask app

## 📊 Data Parsing

### Address Parsing
The application automatically parses Australian addresses in the format:
```
Street Address, Suburb STATE POSTCODE, Australia
```

Returns:
- **address_line**: Street address
- **city**: Suburb/locality
- **state**: Australian state code (VIC, NSW, QLD, SA, WA, TAS, NT, ACT)
- **postcode**: 4-digit postcode

### Business Name Cleaning
Removes common suffixes from business names:
- Regional qualifiers (e.g., "- Victoria", "- NSW")
- Duplicate state references

## 🔐 Security Notes

- Never commit `.env` file - use `.env.example` as template
- Change `SECRET_KEY` in production
- Use HTTPS in production
- Implement rate limiting for API endpoints
- Sanitize user inputs
- Use environment-specific CORS policies

## 🚀 Deployment

### AWS
```bash
# Using Elastic Beanstalk
eb init
eb create google-places-env
eb deploy
```

### Heroku
```bash
heroku create google-places-scraper
heroku config:set GOOGLE_PLACES_API_KEY=your_key
git push heroku main
```

### DigitalOcean
- Connect GitHub repository
- Set environment variables
- Configure build and run commands

## 📝 Rate Limiting

- Google Places API: Subject to quota limits (check Google Cloud Console)
- Default email scraping delay: 1.5 seconds per website
- Adjust delays in `.env` if needed

## 📧 Support

For issues, questions, or feature requests:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [API Documentation](#-api-documentation)
3. Check backend logs: `docker logs google-places-backend`
4. Check frontend console in browser DevTools

## 📄 License

MIT License - Feel free to use and modify for your needs

## 🙏 Acknowledgments

- Built with Flask and React
- Powered by Google Places API
- Designed for Australian business lead generation

---

**Created:** 2024  
**Version:** 1.0.0  
**Status:** Production Ready ✅
