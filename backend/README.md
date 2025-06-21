# FanFollow Backend

A FastAPI-based backend service for analyzing Twitter followers using AI.

## Features

- Twitter follower scraping using RapidAPI
- AI-powered user analysis using Google's Gemini API
- Local JSON file storage for data persistence
- Batch processing with progress tracking
- Asynchronous processing

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following variables:
```env
RAPID_API_KEY=your_rapidapi_key
GEMINI_API_KEY=your_gemini_api_key
```

## Running the Server

To run the development server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## Data Storage

The application stores data in JSON files in the `data` directory:
- `followers.json`: Contains analyzed Twitter follower data
- `jobs.json`: Contains job tracking information
- `job_customers.json`: Contains customer-specific job information

## API Documentation

Once the server is running, you can access:
- Swagger UI documentation at `http://localhost:8000/docs`
- ReDoc documentation at `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── webscrape.py      # API endpoints
│   ├── core/
│   │   ├── config.py         # Configuration settings
│   │   └── constants.py      # Constants and settings
│   ├── models/
│   │   └── schemas.py        # Pydantic models
│   ├── services/
│   │   ├── json_storage.py   # JSON file storage service
│   │   ├── twitter.py        # Twitter API integration
│   │   └── gemini.py         # Gemini API integration
│   └── utils/
│       └── helpers.py        # Utility functions
├── data/                     # JSON file storage directory
├── requirements.txt          # Python dependencies
├── main.py                  # FastAPI application
└── README.md               # This file
``` 