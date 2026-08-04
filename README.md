# Summer School Cloud AI Assistant

A cloud-native AI assistant developed during the Google Cloud and Agentic AI Summer School at POLITEHNICA Bucharest.

During Day 4, the application uses a local Markdown knowledge base and Google Agent Development Kit tools.

Later, the same application will use:

- Gemini through Vertex AI;
- Google Cloud Storage;
- Cloud Run;
- Docker;
- Google Cloud Logging and Monitoring.

## Application architecture

```text
User
  |
  v
ADK Agent
  |
  +-- list_documents()
  |
  +-- read_document(filename)
  |
  +-- search_documents(keyword)
             |
             v
       KnowledgeProvider
          /       \
         /         \
Local files      Cloud Storage
```

The application initially uses `LocalKnowledgeProvider`.

When the assigned Google Cloud project becomes available, the configuration can switch to `CloudKnowledgeProvider` without changing the agent or its tools.

## Repository structure

```text
summer-school-agent/
|
|-- app/
|   |-- __init__.py
|   |-- agent.py
|   |-- config.py
|   |-- knowledge.py
|   |-- prompts.py
|   `-- tools.py
|
|-- knowledge/
|   |-- bigtable.md
|   |-- cloud_sql.md
|   |-- cloud_storage.md
|   |-- compute_engine.md
|   |-- day1.md
|   |-- day2.md
|   |-- day3.md
|   |-- docker.md
|   |-- faq.md
|   |-- gke.md
|   `-- kubernetes.md
|
|-- scripts/
|   |-- generate_dependency_files.py
|   |-- upload_knowledge.py
|   `-- verify_local_setup.py
|
|-- tests/
|   |-- __init__.py
|   |-- test_agent.py
|   |-- test_knowledge.py
|   `-- test_tools.py
|
|-- .env.example
|-- .gitignore
|-- main.py
|-- requirements.txt
|-- requirements-lock.txt
`-- README.md
```

## Prerequisites

Install the following before Day 4:

- Python 3.11;
- Git;
- Google Cloud CLI;
- Visual Studio Code or another Python editor;
- Docker Desktop or Docker Engine, recommended for Day 5.

Verify the local tools:

```bash
python3.11 --version
git --version
gcloud --version
docker --version
```

## Local setup

### 1. Open the repository

```bash
cd summer-school-agent
```

### 2. Create a Python 3.11 virtual environment

macOS or Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Verify the active Python interpreter

```bash
python --version
```

Expected:

```text
Python 3.11.x
```

On macOS or Linux, also check:

```bash
which python
```

The path should point inside:

```text
summer-school-agent/.venv/
```

### 4. Install the dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Local configuration

Create the local environment file.

macOS or Linux:

```bash
cp .env.example .env
```

Windows Command Prompt:

```cmd
copy .env.example .env
```

Use this configuration before receiving the Google Cloud project:

```text
MODEL=gemini-2.5-flash

KNOWLEDGE_SOURCE=local
LOCAL_KNOWLEDGE_DIRECTORY=knowledge

GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_PROJECT=
GOOGLE_CLOUD_LOCATION=global

KNOWLEDGE_BUCKET=
```

The empty cloud fields are valid while:

```text
KNOWLEDGE_SOURCE=local
```

## Run the local demonstration

```bash
python main.py
```

This command:

1. loads the local knowledge provider;
2. lists the available Markdown files;
3. reads one document;
4. searches the knowledge base;
5. displays matching excerpts.

It does not call Gemini and does not connect to Google Cloud.

## Verify the complete local setup

```bash
python scripts/verify_local_setup.py
```

Expected final result:

```text
All local checks passed.
No Google Cloud request or Gemini request was made.
```

## Run the automated tests

```bash
python -m unittest discover -s tests -v
```

The tests cover:

- local document discovery;
- local document reading;
- missing-document handling;
- keyword search;
- structured tool responses;
- mocked Cloud Storage behaviour;
- ADK agent construction.

The Cloud Storage tests use a mocked client and make no network requests.

## Preview the future Cloud Storage upload

```bash
python scripts/upload_knowledge.py --dry-run
```

This displays the files that will eventually be uploaded.

It does not contact Google Cloud.

## ADK agent

The agent is defined in:

```text
app/agent.py
```

The package exposes:

```python
root_agent
```

The agent currently has three tools:

```text
list_documents
read_document
search_documents
```

The tools use the local knowledge provider until cloud mode is enabled.

## Cloud setup

Complete this section only after receiving an assigned Google Cloud project.

Authenticate:

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default login
```

Update `.env`:

```text
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
KNOWLEDGE_BUCKET=YOUR_UNIQUE_BUCKET_NAME
```

The initial Gemini test may still use:

```text
KNOWLEDGE_SOURCE=local
```

This allows the ADK agent to use Gemini through Vertex AI while retrieving knowledge from the local Markdown files.

Later, after creating the bucket and uploading the files, switch to:

```text
KNOWLEDGE_SOURCE=cloud
```

## Upload the knowledge base

After the bucket exists:

```bash
python scripts/upload_knowledge.py
```

Verify the upload plan first:

```bash
python scripts/upload_knowledge.py --dry-run
```

## Run the ADK development interface

After Google Cloud authentication is configured:

```bash
adk web
```

Alternatively, use the terminal interface:

```bash
adk run app
```

Do not run these commands before the Vertex AI configuration and authentication steps are complete.

## Useful test prompts

Once the ADK agent is connected to Gemini:

```text
What workshop documents are available?
```

```text
Which documents discuss Docker?
```

```text
Read the Day 2 document and summarize the differences between Cloud Storage, Cloud SQL, and Bigtable.
```

```text
Does the workshop material explain Kubernetes Services?
```

```text
Which lab introduced GKE?
```

## Day 5 extension

During Day 5, this application will be extended with:

- a student-selected domain;
- one custom domain-specific tool;
- a Docker image;
- deployment to Cloud Run;
- logging and monitoring;
- a public demonstration.

Students will reuse the same agent and tool architecture rather than starting a new project.