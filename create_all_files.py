#!/usr/bin/env python3
from pathlib import Path

BASE_DIR = Path(__file__).parent

files = {
    "backend/app.py": """from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
from urllib.parse import urlparse

load_dotenv()
app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/api/search", methods=["POST"])
def search():
    data = request.json
    return jsonify({"success": True, "results": []})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
""",
    "backend/requirements.txt": "Flask==2.3.2\nFlask-CORS==4.0.0\npython-dotenv==1.0.0\nrequests==2.31.0\n",
    "backend/.env": "FLASK_ENV=development\nGOOGLE_PLACES_API_KEY=your_key_here\n",
    "frontend/package.json": """{"name": "scraper", "version": "1.0.0", "private": true, "dependencies": {"react": "^18.2.0", "react-dom": "^18.2.0", "axios": "^1.4.0"}, "scripts": {"start": "react-scripts start", "build": "react-scripts build"}, "devDependencies": {"react-scripts": "5.0.1"}}""",
    "frontend/public/index.html": "<!DOCTYPE html><html><head><meta charset='utf-8' /><title>Scraper</title></head><body><div id='root'></div></body></html>",
    "frontend/src/index.js": "import React from 'react';\nimport ReactDOM from 'react-dom/client';\nimport App from './App';\nconst root = ReactDOM.createRoot(document.getElementById('root'));\nroot.render(<App />);",
    "frontend/src/App.js": "import React, { useState } from 'react';\nimport axios from 'axios';\nfunction App() { return <div><h1>Google Places Scraper</h1></div>; }\nexport default App;",
    "frontend/.env": "REACT_APP_API_URL=http://localhost:5000\n",
    "docker-compose.yml": "version: '3.8'\nservices:\n  backend:\n    build:\n      dockerfile: Dockerfile.backend\n    ports:\n      - '5000:5000'\n",
    ".env.example": "GOOGLE_PLACES_API_KEY=your_key_here\n",
}

for path, content in files.items():
    p = BASE_DIR / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    print(f"✅ {path}")

print(f"\n✨ Created {len(files)} files!")
