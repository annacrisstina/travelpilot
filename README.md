  # ✈️ TravelPilot

  > **An AI-powered travel planning assistant built with the Google Agent Development Kit and Gemini.** Grounded answers and personalized day-by-day itineraries from a curated knowledge base — local-first by design, with Google Cloud as an optional deployment target.

  [![CI](https://github.com/annacrisstina/travelpilot/actions/workflows/ci.yml/badge.svg)](https://github.com/annacrisstina/travelpilot/actions/workflows/ci.yml)
  [![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
  [![Google ADK](https://img.shields.io/badge/Google_ADK-2.6-4285F4?logo=google&logoColor=white)](https://google.github.io/adk-docs/)
  [![Gemini](https://img.shields.io/badge/Gemini-Flash-8E75B2?logo=googlegemini&logoColor=white)](https://ai.google.dev/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

  *Started as a prototype at the **Google Cloud & Agentic AI Summer School** (POLITEHNICA Bucharest, supported by Google Romania) — independently redesigned and extended since.*

  ---

  ## Overview

  TravelPilot is a tool-using AI agent that answers travel questions and generates personalized itineraries. It grounds every answer in a curated knowledge base of 19 Markdown travel guides — 11 destinations plus cross-cutting topics such as budgeting and transportation — and is instructed never to answer beyond them.

  The application is **local-first**: it runs end to end with a free Gemini API key — no Google Cloud project, no bucket, no service account. Google Cloud Storage and Vertex AI are optional backends selected through environment variables, so the same codebase runs unchanged on a laptop and on Cloud Run.

  The current architecture is my own independent work — see [What I Built Independently](#what-i-built-independently).

  ---

  ## Key Engineering Highlights

  - **Local-first by design** — the full application runs with a free Gemini API key; Google Cloud is an optional deployment backend, never a requirement.
  - **Pluggable knowledge architecture** — a two-method `KnowledgeProvider` `Protocol` with interchangeable local-filesystem and Cloud Storage implementations.
  - **Lazy cloud imports** — the Google Cloud SDK loads only when cloud mode is selected; local mode never touches it, even at import time.
  - **Fail-fast configuration** — environment variables are validated once into a frozen dataclass; misconfiguration fails at startup, naming the missing variable.
  - **Grounded itinerary generation** — `plan_trip` validates input and constrains the model to a retrieved destination guide instead of free generation.
  - **One image, every environment** — the same non-root Docker container runs locally and on Cloud Run; Vertex AI keeps production free of stored API keys.
  - **Offline test suite** — providers, tools and agent wiring are tested without network access, in CI on Python 3.11 and 3.12.

  ---

  ## Features

  - **Grounded travel answers** — the agent reads complete guides for 11 destinations and never invents information that is not in the knowledge base.
  - **Keyword search with line-level excerpts** — `search_documents` returns matching filenames with up to three excerpts each, including line numbers, so answers stay traceable to a source.
  - **AI-generated itineraries** — `plan_trip` takes a destination, duration, interests and budget, validates them, and hands the model a structured brief built from the destination guide.
  - **Two interchangeable knowledge backends** — local Markdown files by default, a Google Cloud Storage bucket when configured; the agent code is identical in both cases.
  - **Fail-fast configuration** — a missing bucket or project is reported at startup, not mid-conversation.
  - **Container and Cloud Run ready** — a FastAPI entry point serves the agent from a non-root image with the knowledge base baked in.

  ---

  ## Architecture

  ```text
                        User
                          │
                          ▼
          ┌───────────────────────────────┐
          │   TravelPilot ADK Agent       │
          │   (Gemini Flash)              │
          └───────────────┬───────────────┘
                          │  tool calls
          ┌───────────────┴───────────────┐
          │  list_documents               │
          │  read_document(filename)      │
          │  search_documents(keyword)    │
          │  plan_trip(dest, days, ...)   │
          └───────────────┬───────────────┘
                          ▼
          ┌───────────────────────────────┐
          │      KnowledgeProvider        │   ← selected by KNOWLEDGE_SOURCE
          │        (Protocol)             │
          └───────┬───────────────┬───────┘
                  │               │
      LocalKnowledgeProvider   CloudKnowledgeProvider
          ./knowledge/*.md      gs://KNOWLEDGE_BUCKET
  ```

  A request flows top to bottom: the model decides which tool to call, the tools resolve every document access through the `KnowledgeProvider` interface, and the concrete provider — local filesystem or Cloud Storage — is selected once at startup from the `KNOWLEDGE_SOURCE` environment variable. Nothing above the provider line knows which backend is active, which is what keeps the laptop, Docker and Cloud Run deployments on a single code path.

  ---

  ## Technologies

  | Area | Technologies |
  |---|---|
  | **AI** | Google Agent Development Kit (ADK) 2.6, Gemini Flash |
  | **Backend** | Python 3.11+, FastAPI |
  | **Cloud** | Google Cloud Storage, Vertex AI, Cloud Run |
  | **DevOps** | Docker, GitHub Actions |
  | **Knowledge base** | Markdown |

  ---

  ## Engineering Decisions

  **A `Protocol`, not a base class.** `KnowledgeProvider` (`app/knowledge.py`) is a two-method structural interface both backends satisfy without inheritance or registration. The tools never learn where documents live, so swapping local files for a Cloud Storage bucket is a one-variable change, not a code change.

  **Lazy cloud imports.** The Cloud Storage SDK is imported at its point of use, so local mode never initializes a client or looks for credentials — not even at import time.

  **Grounding over free generation.** `plan_trip` validates the request (1–30 days, budget tier, a guide that exists) and returns the destination guide with a structured planning brief. Invalid input yields a structured error, not a plausible-sounding hallucinated trip.

  **Configuration as a boundary.** `load_config()` reads the environment once into a frozen dataclass. Inconsistent combinations — Vertex AI without a project, cloud knowledge without a bucket — fail at startup, naming the missing variable.

  **One entry point, every environment.** `server.py` serves the agent through FastAPI and binds to `PORT`, so the same image runs under Docker locally and on Cloud Run without modification.

  ---

  ## What I Built Independently

  TravelPilot began as a small prototype. The engineering below is my independent work:

  - **Redesigned the application local-first** — cut the barrier to entry from a full Google Cloud setup to a free API key and three commands.
  - **Designed the `KnowledgeProvider` abstraction** — a structural interface that lets local files and Cloud Storage share one code path, so storage concerns never leak into the agent logic.
  - **Built the configuration system** — environment-driven, validated once, fail-fast; each deployment mode demands only the variables it actually uses.
  - **Made Google Cloud fully optional** — lazy SDK imports guarantee local mode never touches Google Cloud, even at import time.
  - **Implemented AI-powered itinerary generation** — the `plan_trip` tool, with input validation and prompt rules that constrain every plan to the retrieved guide.
  - **Restructured the codebase into clean modules** — configuration, knowledge access, tools and agent wiring each with a single responsibility.
  - **Containerized and prepared for Cloud Run** — a slim non-root Docker image with the knowledge base baked in, plus a Vertex AI production path where the service account replaces stored API keys.
  - **Hardened quality and developer experience** — offline unit tests in CI on Python 3.11/3.12, a setup verification script, a knowledge upload tool and a documented `.env.example`.

  ---

  ## Quick Start

  Requires Python 3.11+ and a free Google AI Studio API key — the only credential needed in local mode. To create one, sign in at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) and click **Create API key**.

  ```bash
  python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
  pip install -r requirements.txt
  cp .env.example .env                                # then set GOOGLE_API_KEY
  python scripts/verify_local_setup.py                # checks setup + model availability
  adk web
  ```

  Open <http://localhost:8000> and select the `app` agent. Try *"Plan a 4-day trip to Rome focused on history and food."*

  ```bash
  python -m unittest discover tests      # run the test suite (offline)
  ```

  ### Configuration

  | Variable | Default | Description |
  |---|---|---|
  | `MODEL` | `gemini-flash-latest` | Gemini model used by the agent. The default is a rolling alias that always resolves to the current stable Flash model, so it works for newly created API keys; set a dated name to pin a version. |
  | `GOOGLE_GENAI_USE_VERTEXAI` | `FALSE` | `FALSE`: Gemini API with `GOOGLE_API_KEY`. `TRUE`: Vertex AI (requires a Google Cloud project). |
  | `GOOGLE_API_KEY` | — | Required when `GOOGLE_GENAI_USE_VERTEXAI=FALSE`. |
  | `KNOWLEDGE_SOURCE` | `local` | `local`: Markdown files on disk. `cloud`: Google Cloud Storage bucket. |
  | `LOCAL_KNOWLEDGE_DIRECTORY` | `knowledge` | Directory of Markdown guides. Relative paths resolve from the project root. |
  | `GOOGLE_CLOUD_PROJECT` | — | Required when `GOOGLE_GENAI_USE_VERTEXAI=TRUE` or `KNOWLEDGE_SOURCE=cloud`. |
  | `GOOGLE_CLOUD_LOCATION` | `global` | Vertex AI location. |
  | `KNOWLEDGE_BUCKET` | — | Required when `KNOWLEDGE_SOURCE=cloud`. |

  The two backends are independent: a Cloud Storage knowledge base can be paired with the plain Gemini API, and Vertex AI with local files.

  <details>
  <summary><b>Troubleshooting: model errors (404 NOT_FOUND)</b></summary>

  `404 NOT_FOUND — this model is no longer available to new users` means the configured `MODEL` has been retired for your API key; Google occasionally closes dated model names to newly created keys. Set `MODEL=gemini-flash-latest` in `.env` (the default), or run `python scripts/verify_local_setup.py` — it checks the configured model against your key and lists the Flash models you can use.

  </details>

  <details>
  <summary><b>Google Cloud Storage knowledge base</b></summary>

  ```bash
  gcloud auth application-default login
  gcloud storage buckets create gs://YOUR_BUCKET --project YOUR_PROJECT

  python scripts/upload_knowledge.py --dry-run          # preview
  python scripts/upload_knowledge.py --bucket YOUR_BUCKET
  ```

  Then set `KNOWLEDGE_SOURCE=cloud`, `GOOGLE_CLOUD_PROJECT` and `KNOWLEDGE_BUCKET` in `.env`.

  </details>

  <details>
  <summary><b>Docker</b></summary>

  The image bundles `knowledge/`, so local mode works in a container with no extra setup. The app listens on `PORT` (default `8080`).

  ```bash
  docker build -t travelpilot .
  docker run --rm -p 8080:8080 -e GOOGLE_API_KEY=YOUR_API_KEY travelpilot
  ```

  For Cloud Storage mode, add the cloud variables and mount Application Default Credentials:

  ```bash
  docker run --rm -p 8080:8080 \
    -e GOOGLE_API_KEY=YOUR_API_KEY \
    -e KNOWLEDGE_SOURCE=cloud \
    -e GOOGLE_CLOUD_PROJECT=YOUR_PROJECT \
    -e KNOWLEDGE_BUCKET=YOUR_BUCKET \
    -v ~/.config/gcloud:/home/appuser/.config/gcloud:ro \
    travelpilot
  ```

  </details>

  <details>
  <summary><b>Cloud Run deployment</b></summary>

  ```bash
  gcloud run deploy travelpilot \
    --source . \
    --project YOUR_PROJECT \
    --region europe-west1 \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=YOUR_PROJECT,GOOGLE_CLOUD_LOCATION=global,KNOWLEDGE_SOURCE=cloud,KNOWLEDGE_BUCKET=YOUR_BUCKET"
  ```

  Vertex AI is the intended production mode: the Cloud Run service account authenticates automatically, so no API key is stored. Grant it `roles/aiplatform.user` and `roles/storage.objectViewer` on the bucket.

  </details>

  ---

  ## Listing Available Models

  If you're unsure which Gemini model is available for your API key, run:

  ```bash
  python scripts/list_available_models.py
  ```

  This utility lists the supported Gemini chat models available for your API key.

  ---

  ## Project Structure

  ```text
  TravelPilot/
  ├── app/
  │   ├── agent.py        # ADK agent definition and provider selection
  │   ├── config.py       # environment-driven configuration, validated once
  │   ├── knowledge.py    # KnowledgeProvider protocol + local/Cloud Storage backends
  │   ├── prompts.py      # system prompt and tool-routing rules
  │   └── tools.py        # the four agent tools
  ├── knowledge/          # 19 Markdown travel guides (local knowledge base)
  ├── scripts/            # knowledge upload, offline setup verification
  ├── tests/              # unit tests, no network access required
  ├── server.py           # FastAPI entry point (Docker / Cloud Run)
  ├── main.py             # CLI demo of the knowledge tools
  └── Dockerfile
  ```

  ---

  ## Acknowledgements

  TravelPilot started during the **Google Cloud & Agentic AI Summer School** at the National University of Science and Technology POLITEHNICA Bucharest, organized with support from Google Romania, where I was introduced to the Agent Development Kit and wrote the first prototype of the agent.

  Everything since — the architecture, the local-first redesign, the `KnowledgeProvider` abstraction, the configuration system, itinerary generation, Docker support, the Cloud Run deployment path, the tests and the documentation — is my own independent work.
