# ✈️ TravelPilot

TravelPilot is an AI-powered travel planning assistant built with the Google Agent Development Kit (ADK) and Gemini.

The assistant answers travel-related questions using a travel knowledge base and can generate personalized travel itineraries for supported destinations.

This project was developed as part of the Google Cloud & Agentic AI Summer School at POLITEHNICA Bucharest.

---

## Features

- 🌍 Browse available travel guides
- 📖 Read complete destination guides
- 🔍 Search destinations and attractions
- 🗺️ Generate personalized travel itineraries
- ☁️ Support for both Local Knowledge Base and Google Cloud Storage

---

## Architecture

```text
User
  |
  v
TravelPilot (ADK Agent)
  |
  +-- list_documents()
  |
  +-- read_document(filename)
  |
  +-- search_documents(keyword)
  |
  +-- plan_trip(destination, days, interests, budget)
              |
              v
       KnowledgeProvider
          /       \
         /         \
Local files    Cloud Storage
```

---

## Project Structure

```text
TravelPilot/
│
├── app/
│   ├── agent.py
│   ├── config.py
│   ├── knowledge.py
│   ├── prompts.py
│   ├── tools.py
│   └── utils.py
│
├── knowledge/
│   ├── rome.md
│   ├── paris.md
│   ├── tokyo.md
│   ├── london.md
│   ├── barcelona.md
│   ├── amsterdam.md
│   ├── athens.md
│   ├── dubai.md
│   ├── lisbon.md
│   ├── new_york.md
│   ├── seoul.md
│   ├── accommodation.md
│   ├── budgeting.md
│   ├── transportation.md
│   ├── packing.md
│   └── local_etiquette.md
│
├── scripts/
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

---

## Technologies

- Python 3.11
- Google Agent Development Kit (ADK)
- Gemini 2.5 Flash
- Vertex AI
- Google Cloud Storage
- Markdown Knowledge Base

---

## Local Setup

Create a virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy the environment file:

```bash
cp .env.example .env
```

Run the application:

```bash
adk web
```

---

## Example Prompts

- Tell me about Rome.
- What destinations are available?
- Search for museums.
- Plan a 4-day trip to Rome focused on history and food.
- Plan a budget trip to Paris.

---

## Current Status

- ✅ Local knowledge base
- ✅ Google Cloud Storage upload
- ✅ Travel itinerary planning
- ⏳ Docker containerization
- ⏳ Cloud Run deployment
- ⏳ Cloud Logging & Monitoring

---

## License

This project was developed for educational purposes during the Google Cloud & Agentic AI Summer School.
