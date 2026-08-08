# ✈️ TravelPilot

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Google ADK](https://img.shields.io/badge/Google_ADK-agent-4285F4?logo=google&logoColor=white)](https://google.github.io/adk-docs/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-8E75B2?logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

TravelPilot is an AI-powered travel planning assistant built with the Google Agent Development Kit (ADK) and Gemini. It answers travel questions from a Markdown knowledge base and generates personalized day-by-day itineraries.

The project is **local-first**: it runs out of the box with a free Gemini API key — no Google Cloud project or bucket required. Google Cloud Storage and Vertex AI are optional backends selected through environment variables.

---

## Features

- 🌍 Browse and read complete travel guides for 11 destinations
- 🔍 Keyword search across the knowledge base with line-level excerpts
- 🗺️ Personalized itineraries by destination, duration, interests and budget
- 💻 Local Markdown knowledge base — zero cloud setup (default)
- ☁️ Optional Google Cloud Storage knowledge base
- 🚀 Deployable as a container to any host, including Cloud Run

---

## Architecture

```text
User
  |
  v
TravelPilot (ADK Agent, Gemini)
  |
  +-- list_documents()
  +-- read_document(filename)
  +-- search_documents(keyword)
  +-- plan_trip(destination, days, interests, budget)
              |
              v
       KnowledgeProvider          (selected by KNOWLEDGE_SOURCE)
          /       \
         /         \
Local files    Cloud Storage
(knowledge/)   (KNOWLEDGE_BUCKET)
```

The agent depends only on the `KnowledgeProvider` interface (`app/knowledge.py`); storage backends are interchangeable. Google Cloud libraries are imported lazily, so local mode never touches Google Cloud.

---

## Quick Start

Requires Python 3.11+.

**1. Create and activate a virtual environment:**

```bash
python -m venv .venv

source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

**2. Install dependencies:**

```bash
pip install -r requirements.txt
```

**3. Copy the environment file:**

```bash
cp .env.example .env
```

**4. Add your API key.** You **must** edit `.env` and set a Gemini API key before running the application:

```bash
GOOGLE_API_KEY=your_google_ai_studio_api_key_here
```

Create a free key at [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey). This is the only credential needed in local mode.

**5. Start the application:**

```bash
adk web
```

Open http://localhost:8000 and select the `app` agent.

Optional checks:

```bash
python main.py                        # exercise the knowledge tools directly
python scripts/verify_local_setup.py  # verify setup without calling Gemini
python -m unittest discover tests     # run the test suite
```

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `MODEL` | `gemini-2.5-flash` | Gemini model used by the agent. |
| `GOOGLE_GENAI_USE_VERTEXAI` | `FALSE` | `FALSE`: Gemini API with `GOOGLE_API_KEY`. `TRUE`: Vertex AI (requires a Google Cloud project). |
| `GOOGLE_API_KEY` | — | Required when `GOOGLE_GENAI_USE_VERTEXAI=FALSE`. Free key from [AI Studio](https://aistudio.google.com/apikey). |
| `KNOWLEDGE_SOURCE` | `local` | `local`: Markdown files on disk. `cloud`: Google Cloud Storage bucket. |
| `LOCAL_KNOWLEDGE_DIRECTORY` | `knowledge` | Directory of Markdown guides (local mode). Relative paths resolve from the project root. |
| `GOOGLE_CLOUD_PROJECT` | — | Required when `GOOGLE_GENAI_USE_VERTEXAI=TRUE` or `KNOWLEDGE_SOURCE=cloud`. |
| `GOOGLE_CLOUD_LOCATION` | `global` | Vertex AI location. |
| `KNOWLEDGE_BUCKET` | — | Required when `KNOWLEDGE_SOURCE=cloud`. Bucket holding the Markdown guides. |

`.env.example` contains a documented template for both configurations.

---

## Google Cloud Storage Mode (Optional)

Serve the knowledge base from a Cloud Storage bucket instead of local files:

1. Authenticate and create a bucket:

   ```bash
   gcloud auth application-default login
   gcloud storage buckets create gs://YOUR_BUCKET --project YOUR_PROJECT
   ```

2. Upload the knowledge base:

   ```bash
   python scripts/upload_knowledge.py --dry-run   # preview
   python scripts/upload_knowledge.py --bucket YOUR_BUCKET
   ```

3. Configure `.env`:

   ```bash
   KNOWLEDGE_SOURCE=cloud
   GOOGLE_CLOUD_PROJECT=YOUR_PROJECT
   KNOWLEDGE_BUCKET=YOUR_BUCKET
   ```

Backends combine freely — e.g. a cloud knowledge base with the plain Gemini API, or Vertex AI (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`) with local files.

---

## Docker

The image bundles the `knowledge/` directory, so local mode works in a container out of the box:

```bash
docker build -t travelpilot .

docker run --rm -p 8080:8080 \
  -e GOOGLE_API_KEY=YOUR_API_KEY \
  travelpilot
```

For Cloud Storage mode, pass the cloud variables instead:

```bash
docker run --rm -p 8080:8080 \
  -e GOOGLE_API_KEY=YOUR_API_KEY \
  -e KNOWLEDGE_SOURCE=cloud \
  -e GOOGLE_CLOUD_PROJECT=YOUR_PROJECT \
  -e KNOWLEDGE_BUCKET=YOUR_BUCKET \
  -v ~/.config/gcloud:/home/appuser/.config/gcloud:ro \
  travelpilot
```

The volume mount provides Application Default Credentials to the container; on Cloud Run this is unnecessary. The app listens on `PORT` (default `8080`) at http://localhost:8080.

---

## Cloud Run Deployment

```bash
gcloud run deploy travelpilot \
  --source . \
  --project YOUR_PROJECT \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=YOUR_PROJECT,GOOGLE_CLOUD_LOCATION=global,KNOWLEDGE_SOURCE=cloud,KNOWLEDGE_BUCKET=YOUR_BUCKET"
```

Notes:

- Vertex AI mode is recommended on Cloud Run — the service account authenticates automatically, so no API key is needed. Grant it `roles/aiplatform.user` and `roles/storage.objectViewer` on the bucket.
- Local knowledge mode also works on Cloud Run (`KNOWLEDGE_SOURCE=local`) since the guides are baked into the image.

---

## Project Structure

```text
TravelPilot/
│
├── app/
│   ├── agent.py        # ADK agent definition
│   ├── config.py       # environment-driven configuration
│   ├── knowledge.py    # KnowledgeProvider: local + Cloud Storage
│   ├── prompts.py      # system prompt
│   └── tools.py        # agent tools
│
├── knowledge/          # Markdown travel guides (local knowledge base)
├── scripts/
│   ├── upload_knowledge.py     # upload knowledge base to Cloud Storage
│   └── verify_local_setup.py   # offline setup verification
├── tests/              # unit tests (no network access required)
├── docs/images/        # README screenshots
├── main.py             # CLI demo of the knowledge tools
├── server.py           # FastAPI entry point (Docker / Cloud Run)
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Example Prompts

- Tell me about Rome.
- What destinations are available?
- Search for museums.
- Plan a 4-day trip to Rome focused on history and food.
- Plan a budget trip to Paris.

---

## Acknowledgements

TravelPilot started as my project during the Google Cloud & Agentic AI Summer School at the National University of Science and Technology POLITEHNICA Bucharest, organized with support from Google Romania. That's where I built the first version of the agent and got my introduction to the Agent Development Kit.

After the summer school ended, I kept developing the project on my own. I redesigned the architecture around a pluggable knowledge provider, improved the documentation, added Docker support and Cloud Run deployment, and made Google Cloud an optional backend instead of a requirement, so everything now runs locally with a free Gemini API key.

This is a personal project, not affiliated with or endorsed by Google.

---

## License

Released under the [MIT License](LICENSE).
