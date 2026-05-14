<div align="center">

# AI Text Summarizer

**Production-grade abstractive text summarization powered by Google PEGASUS and FastAPI**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?style=flat-square&logo=huggingface&logoColor=black)](https://huggingface.co)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![AWS](https://img.shields.io/badge/AWS-ECR%20%2B%20ECS-FF9900?style=flat-square&logo=amazonaws&logoColor=white)](https://aws.amazon.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

*Summarize articles, research papers, dialogues, and documents instantly — with a custom-trained transformer model deployed on AWS.*

</div>

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Tech Stack](#tech-stack)
5. [Project Structure](#project-structure)
6. [ML Pipeline](#ml-pipeline)
7. [Prerequisites](#prerequisites)
8. [Local Development Setup](#local-development-setup)
9. [Configuration Reference](#configuration-reference)
10. [Running the Application](#running-the-application)
11. [API Endpoints](#api-endpoints)
12. [Docker Deployment](#docker-deployment)
13. [AWS ECR — Push Image](#aws-ecr--push-image)
14. [AWS ECS — Deploy Service](#aws-ecs--deploy-service)
15. [CI/CD Pipeline (GitHub Actions)](#cicd-pipeline-github-actions)
16. [GitHub Secrets Setup](#github-secrets-setup)
17. [Troubleshooting](#troubleshooting)

---

## Overview

AI Text Summarizer is an end-to-end ML application that fine-tunes **Google PEGASUS** (`pegasus-cnn_dailymail`) on the **SAMSum** dialogue dataset and serves predictions through a **FastAPI** backend with a modern glassmorphism UI.

The project implements a complete ML operations lifecycle:

```
Raw Data → Ingestion → Tokenization → Fine-tuning → ROUGE Evaluation → REST API → AWS
```

The trained model generates **abstractive** summaries — it writes new sentences rather than extracting existing ones, making summaries more natural and concise.

---

## Features

- **Abstractive summarization** using fine-tuned PEGASUS (seq2seq transformer)
- **Full training pipeline** — data ingestion, transformation, model training, and ROUGE evaluation
- **Modern glassmorphism UI** — dark theme, split-panel predict interface, live training dashboard with console logs
- **REST API** with FastAPI and async endpoints
- **Docker containerisation** with multi-stage build
- **AWS deployment** — ECR image registry + ECS Fargate orchestration
- **GitHub Actions CI/CD** — automated lint → security scan → test → build → deploy pipeline
- **Zero Docker Hub dependency** — authenticates directly to Amazon ECR

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                          User Browser                              │
└───────────────────────────────┬────────────────────────────────────┘
                                │ HTTP
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                    FastAPI Application (app.py)                    │
│                                                                    │
│   GET  /            →  Landing page  (index.html)                  │
│   GET  /predict     →  Summarize UI  (predict.html)                │
│   POST /predict     →  JSON API  →  PredictionPipeline             │
│   GET  /train       →  Training dashboard (train.html)             │
│   POST /train/start →  Async subprocess → main.py                  │
│   GET  /train/status→  Polling endpoint (JSON)                     │
│   POST /train/reset →  Reset training state                        │
└────────────────────────────────┬───────────────────────────────────┘
                                 │
               ┌─────────────────┴──────────────────┐
               │                                    │
               ▼                                    ▼
   ┌───────────────────────┐          ┌─────────────────────────┐
   │   PredictionPipeline  │          │      Training Pipeline   │
   │                       │          │                          │
   │  AutoTokenizer        │          │  1. DataIngestion        │
   │  AutoModelForSeq2Seq  │          │  2. DataTransformation   │
   │  model.generate()     │          │  3. ModelTrainer         │
   └───────────────────────┘          │  4. ModelEvaluation      │
               │                      └─────────────────────────┘
               ▼
   ┌───────────────────────┐
   │  artifacts/           │
   │  ├── model_trainer/   │
   │  │   ├── pegasus-     │
   │  │   │   samsum-model/│
   │  │   └── tokenizer/   │
   │  └── model_evaluation/│
   │      └── metrics.csv  │
   └───────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **Web Framework** | FastAPI + Uvicorn |
| **ML Framework** | HuggingFace Transformers 4.x |
| **Base Model** | `google/pegasus-cnn_dailymail` |
| **Dataset** | SAMSum (dialogue summarization) |
| **Evaluation** | ROUGE-1, ROUGE-2, ROUGE-L, ROUGE-Lsum |
| **Frontend** | Jinja2 Templates + Tailwind CSS |
| **Container** | Docker (multi-stage build) |
| **Registry** | Amazon ECR |
| **Orchestration** | Amazon ECS (Fargate) |
| **CI/CD** | GitHub Actions |
| **Config** | PyYAML + python-box |

---

## Project Structure

```
TextSummarizer/
│
├── app.py                          # FastAPI application & all routes
├── main.py                         # Full training pipeline runner
├── params.yaml                     # HuggingFace TrainingArguments
├── setup.py                        # Package setup
├── setup.cfg                       # flake8 / isort / pytest / coverage config
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Multi-stage production container
├── .dockerignore                   # Files excluded from Docker context
│
├── config/
│   └── config.yaml                 # Paths, URLs, and model checkpoints
│
├── src/textsummarizer/
│   ├── components/
│   │   ├── dataingestion.py        # Downloads & extracts SAMSum ZIP
│   │   ├── datatransformation.py  # Tokenises dataset with PEGASUS tokenizer
│   │   ├── modeltrainer.py        # Fine-tunes PEGASUS with HF Trainer
│   │   └── modelevaluation.py     # Computes ROUGE scores on test split
│   │
│   ├── pipeline/
│   │   ├── dataingestionpipeline.py
│   │   ├── datatransformationpipeline.py
│   │   ├── modeltrainerpipeline.py
│   │   ├── modelevaluationpipeline.py
│   │   └── predictionpipeline.py  # Inference: tokenize → generate → decode
│   │
│   ├── config/
│   │   └── configuration.py       # ConfigurationManager — reads config.yaml
│   ├── entity/
│   │   └── config_entity.py       # Typed dataclasses for each stage config
│   ├── constants/
│   │   └── __init__.py            # CONFIG_FILE_PATH, PARAMS_FILE_PATH
│   ├── utils/
│   │   └── main.py                # read_yaml, create_directories helpers
│   ├── logging/
│   │   └── __init__.py            # Structured logger → logs/running_logs.log
│   └── exception/
│       └── __init__.py            # TextSummarizerException with traceback
│
├── templates/
│   ├── index.html                  # Landing page (hero, features, CTA)
│   ├── predict.html               # Summarization UI (split panel)
│   └── train.html                 # Training dashboard (console, progress)
│
├── static/
│   ├── css/style.css              # Glassmorphism design system
│   └── js/app.js                  # Toast, scroll animations, shared utils
│
├── artifacts/                      # Generated at runtime — not committed
│   ├── data_ingestion/
│   ├── data_transformation/
│   ├── model_trainer/
│   │   ├── pegasus-samsum-model/  # Fine-tuned model weights
│   │   └── tokenizer/
│   └── model_evaluation/
│       └── metrics.csv
│
├── tests/
│   └── test_app.py                # 20 unit tests (ML components mocked)
│
├── research/
│   ├── 1. Data Ingestion.ipynb
│   ├── 2. Data Transformation.ipynb
│   ├── 3. Model Trainer.ipynb
│   └── 4. Model Evaluation.ipynb
│
└── .github/
    └── workflows/
        └── main.yml               # CI/CD: lint → security → test → ECR → ECS
```

---

## ML Pipeline

The training pipeline has four sequential stages, each encapsulated in its own component and orchestrated by `main.py`.

### Stage 1 — Data Ingestion

Downloads the SAMSum dataset as a ZIP archive from GitHub and extracts it to `artifacts/data_ingestion/`.

```
Source URL : https://github.com/krishnaik06/datasets/raw/refs/heads/main/summarizer-data.zip
Output     : artifacts/data_ingestion/samsum_dataset/
             ├── train/       (14,732 dialogues)
             ├── validation/  (818 dialogues)
             └── test/        (819 dialogues)
```

### Stage 2 — Data Transformation

Tokenises every dialogue and summary using the PEGASUS tokenizer. Inputs are truncated to 1024 tokens; targets to 128 tokens. The tokenised dataset is saved in Arrow format for fast loading.

```
Tokenizer  : google/pegasus-cnn_dailymail
Input col  : dialogue   (max_length=1024, truncation=True)
Target col : summary    (max_length=128,  truncation=True)
Output     : artifacts/data_transformation/samsum_dataset/
```

### Stage 3 — Model Training

Fine-tunes `google/pegasus-cnn_dailymail` on the tokenised SAMSum data using HuggingFace `Trainer`. Key hyperparameters (from `params.yaml`):

| Parameter | Value |
|---|---|
| `num_train_epochs` | 1 |
| `warmup_steps` | 500 |
| `per_device_train_batch_size` | 1 |
| `per_device_eval_batch_size` | 1 |
| `weight_decay` | 0.01 |
| `gradient_accumulation_steps` | 16 |
| `eval_steps` | 500 |

```
Base model : google/pegasus-cnn_dailymail
Output     : artifacts/model_trainer/
             ├── pegasus-samsum-model/   (model weights as .safetensors)
             └── tokenizer/
```

### Stage 4 — Model Evaluation

Runs the fine-tuned model on the first 10 test samples and computes ROUGE scores.

```
Metric file: artifacts/model_evaluation/metrics.csv

rouge1   | rouge2 | rougeL  | rougeLsum
---------|--------|---------|----------
0.0200   | 0.0000 | 0.0197  | 0.0197
```

> **Note:** Low ROUGE scores are expected with `num_train_epochs=1` on a single CPU/GPU pass. Increase `num_train_epochs` in `params.yaml` and run on a GPU instance for production-quality results.

---

## Prerequisites

Ensure the following are installed before starting:

| Tool | Version | Install |
|---|---|---|
| Python | 3.10 or 3.11 | [python.org](https://python.org) |
| pip | Latest | `python -m pip install --upgrade pip` |
| Git | Any | [git-scm.com](https://git-scm.com) |
| Docker | 24+ | [docker.com](https://docker.com) |
| AWS CLI | v2 | [AWS CLI install guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) |

For GPU-accelerated training (optional but strongly recommended):

- NVIDIA GPU with CUDA 11.8+
- [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)

---

## Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/navneetsxngh/TextSummarizer.git
cd TextSummarizer
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv TSenv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\TSenv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv TSenv
source TSenv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **PyTorch note:** `requirements.txt` installs the CPU version of PyTorch by default. For GPU support, first install the CUDA-specific wheel from [pytorch.org](https://pytorch.org/get-started/locally/), then run `pip install -r requirements.txt`.

### 4. Verify the installation

```bash
python -c "import transformers, fastapi, torch; print('All imports OK')"
```

### 5. (Optional) Run the training pipeline

Skip this step if you already have model artifacts in `artifacts/model_trainer/`.

```bash
python main.py
```

This runs all four pipeline stages sequentially and saves model weights to `artifacts/model_trainer/pegasus-samsum-model/`. Training on CPU takes several hours; use a GPU machine for practical results.

### 6. Start the development server

```bash
python app.py
```

Open [http://localhost:8080](http://localhost:8080) in your browser.

---

## Configuration Reference

### `config/config.yaml`

Controls all file paths and model checkpoints. Edit this to point to a different dataset URL or switch the base model.

```yaml
artifacts_root: artifacts

data_ingestion:
  root_dir: artifacts/data_ingestion
  source_URL: https://github.com/krishnaik06/datasets/raw/refs/heads/main/summarizer-data.zip
  local_data_file: artifacts/data_ingestion/data.zip
  unzip_dir: artifacts/data_ingestion

data_transformation:
  root_dir: artifacts/data_transformation
  data_path: artifacts/data_ingestion/samsum_dataset
  tokenizer_name: google/pegasus-cnn_dailymail   # ← change to switch base model

model_trainer:
  root_dir: artifacts/model_trainer
  data_path: artifacts/data_transformation/samsum_dataset
  model_ckpt: google/pegasus-cnn_dailymail        # ← change to switch base model

model_evaluation:
  root_dir: artifacts/model_evaluation
  data_path: artifacts/data_transformation/samsum_dataset
  model_path: artifacts/model_trainer/pegasus-samsum-model
  tokenizer_path: artifacts/model_trainer/tokenizer
  metric_file_name: artifacts/model_evaluation/metrics.csv
```

### `params.yaml`

HuggingFace `TrainingArguments`. Increase `num_train_epochs` for better quality.

```yaml
TrainingArguments:
  num_train_epochs: 1          # ← increase for production (e.g. 5–10)
  warmup_steps: 500
  per_device_train_batch_size: 1
  per_device_eval_batch_size: 1
  weight_decay: 0.01
  logging_steps: 10
  eval_strategy: steps
  eval_steps: 500
  save_steps: 1000
  gradient_accumulation_steps: 16
```

---

## Running the Application

### Development

```bash
python app.py
# Server starts on http://0.0.0.0:8080
```

### Production (Uvicorn directly)

```bash
uvicorn app:app --host 0.0.0.0 --port 8080 --workers 2 --log-level info
```

### Pages

| URL | Description |
|---|---|
| `http://localhost:8080/` | Landing page |
| `http://localhost:8080/predict` | Summarization interface |
| `http://localhost:8080/train` | Training dashboard |
| `http://localhost:8080/docs` | Interactive Swagger UI |
| `http://localhost:8080/redoc` | ReDoc API documentation |

---

## API Endpoints

### `GET /`
Returns the landing page HTML.

---

### `GET /predict`
Returns the summarization UI HTML.

---

### `POST /predict`
Runs the fine-tuned model on the provided text and returns a JSON summary.

**Request:**
```http
POST /predict
Content-Type: application/json

{
  "text": "Hannah: Hey, do you have Betty's number?\nAmanda: Lemme check..."
}
```

**Success response — 200:**
```json
{
  "summary": "Hannah asks Amanda for Betty's number. Amanda doesn't have it and suggests asking Larry."
}
```

**Error responses:**

| Status | Body | Cause |
|---|---|---|
| `400` | `{"error": "Text is required"}` | Empty or whitespace-only input |
| `500` | `{"error": "<exception message>"}` | Model not found or inference error |

---

### `GET /train`
Returns the training dashboard HTML.

---

### `POST /train/start`
Starts the full 4-stage training pipeline as a non-blocking background process.

**Success — 200:**
```json
{ "status": "started" }
```

**Already running — 409:**
```json
{ "message": "Training already in progress" }
```

---

### `GET /train/status`
Returns the current training state. Poll this every 2 seconds from the dashboard.

**Response:**
```json
{
  "running":   false,
  "completed": true,
  "error":     null,
  "logs": [
    "[INFO] Initializing training pipeline...",
    "[INFO] Data Ingestion Stage Started",
    "[SUCCESS] Training completed successfully!"
  ]
}
```

---

### `POST /train/reset`
Clears all training state (useful for retrying after an error).

**Response — 200:**
```json
{ "status": "reset" }
```

---

## Docker Deployment

### 1. Build the image

```bash
docker build -t textsummarizer:latest .
```

The Dockerfile uses a **multi-stage build**:
- **Stage 1 (builder):** Installs all Python packages including PyTorch.
- **Stage 2 (runtime):** Copies installed packages without the build toolchain. Runs as a non-root user.

> **Expected image size:** 3–6 GB due to PyTorch and Transformers. This is normal for ML workloads.

### 2. Run the container locally

```bash
docker run -d \
  --name textsummarizer \
  -p 8080:8080 \
  -v $(pwd)/artifacts:/app/artifacts \
  textsummarizer:latest
```

**Windows PowerShell:**
```powershell
docker run -d `
  --name textsummarizer `
  -p 8080:8080 `
  -v "${PWD}/artifacts:/app/artifacts" `
  textsummarizer:latest
```

> Mount `artifacts/` as a volume so the model weights are not baked into the image. In production, use Amazon EFS or S3 to provide model artifacts to the container.

### 3. Check the container

```bash
# View logs
docker logs -f textsummarizer

# Test the health endpoint
curl http://localhost:8080/

# Stop and remove
docker stop textsummarizer && docker rm textsummarizer
```

### 4. Docker Compose (local stack)

```yaml
# docker-compose.yml
version: "3.9"
services:
  api:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./artifacts:/app/artifacts
    environment:
      - TOKENIZERS_PARALLELISM=false
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
```

```bash
docker compose up -d
docker compose logs -f
```

---

## AWS ECR — Push Image

### Prerequisites

- AWS CLI v2 installed and configured
- An IAM user with ECR permissions (see [CI/CD GitHub Secrets Setup](#github-secrets-setup))

### Step 1 — Configure AWS CLI

```bash
aws configure
# AWS Access Key ID:     <your key>
# AWS Secret Access Key: <your secret>
# Default region name:   ap-south-1      ← change to your region
# Default output format: json
```

### Step 2 — Create the ECR repository

```bash
aws ecr create-repository \
  --repository-name textsummarizer \
  --region ap-south-1 \
  --image-scanning-configuration scanOnPush=true \
  --image-tag-mutability MUTABLE
```

Note the `repositoryUri` from the output. It looks like:
```
123456789012.dkr.ecr.ap-south-1.amazonaws.com/textsummarizer
```

### Step 3 — Authenticate Docker to ECR

```bash
aws ecr get-login-password --region ap-south-1 \
  | docker login \
      --username AWS \
      --password-stdin \
      123456789012.dkr.ecr.ap-south-1.amazonaws.com
```

> This uses a short-lived token — no Docker Hub credentials are involved.

### Step 4 — Build, tag, and push

```bash
# Set your variables
ECR_URI="123456789012.dkr.ecr.ap-south-1.amazonaws.com/textsummarizer"
GIT_SHA=$(git rev-parse --short HEAD)

# Build
docker build -t textsummarizer:latest .

# Tag with both latest and the commit SHA
docker tag textsummarizer:latest ${ECR_URI}:latest
docker tag textsummarizer:latest ${ECR_URI}:${GIT_SHA}

# Push both tags
docker push ${ECR_URI}:latest
docker push ${ECR_URI}:${GIT_SHA}
```

### Step 5 — Verify the push

```bash
aws ecr describe-images \
  --repository-name textsummarizer \
  --region ap-south-1 \
  --query 'imageDetails[*].{Tag:imageTags[0],Pushed:imagePushedAt,Size:imageSizeInBytes}' \
  --output table
```

---

## AWS ECS — Deploy Service

This section deploys the containerised application to **ECS Fargate** — a serverless container platform where AWS manages the underlying infrastructure.

### Step 1 — Create an ECS Cluster

```bash
aws ecs create-cluster \
  --cluster-name textsummarizer-cluster \
  --region ap-south-1
```

### Step 2 — Create the ECS Task Definition

Create a file `ecs-task-definition.json`:

```json
{
  "family": "textsummarizer-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "8192",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "textsummarizer",
      "image": "123456789012.dkr.ecr.ap-south-1.amazonaws.com/textsummarizer:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        { "name": "TOKENIZERS_PARALLELISM", "value": "false" },
        { "name": "PYTHONUNBUFFERED",       "value": "1" }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group":         "/ecs/textsummarizer",
          "awslogs-region":        "ap-south-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8080/ || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3,
        "startPeriod": 60
      },
      "essential": true
    }
  ]
}
```

Register it:

```bash
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json \
  --region ap-south-1
```

### Step 3 — Create a CloudWatch Log Group

```bash
aws logs create-log-group \
  --log-group-name /ecs/textsummarizer \
  --region ap-south-1
```

### Step 4 — Create an ECS Service

```bash
aws ecs create-service \
  --cluster       textsummarizer-cluster \
  --service-name  textsummarizer-service \
  --task-definition textsummarizer-task \
  --launch-type   FARGATE \
  --desired-count 1 \
  --network-configuration "awsvpcConfiguration={
    subnets=[subnet-xxxxxxxxxxxxxxxxx],
    securityGroups=[sg-xxxxxxxxxxxxxxxxx],
    assignPublicIp=ENABLED
  }" \
  --region ap-south-1
```

Replace `subnet-xxx` and `sg-xxx` with your VPC values from the AWS Console under **VPC → Subnets** and **VPC → Security Groups**.

### Step 5 — Verify the deployment

```bash
aws ecs describe-services \
  --cluster textsummarizer-cluster \
  --services textsummarizer-service \
  --region ap-south-1 \
  --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}' \
  --output table
```

Expected output:
```
-------------------------------------------
|          DescribeServices               |
+----------+------+---------+-------------+
|  Desired |  Running  |  Status  |
+----------+-----------+----------+
|    1     |     1     |  ACTIVE  |
+----------+-----------+----------+
```

### Step 6 — Manually update the service to a new image

```bash
aws ecs update-service \
  --cluster      textsummarizer-cluster \
  --service      textsummarizer-service \
  --force-new-deployment \
  --region       ap-south-1
```

ECS will pull the new `:latest` image and do a rolling replacement with zero downtime.

---

## CI/CD Pipeline (GitHub Actions)

The pipeline lives in `.github/workflows/main.yml` and runs automatically on every push.

### Pipeline flow

```
push / PR
   │
   ├──► 🔍 code-quality   (flake8 · black · isort)
   ├──► 🔒 security-scan  (bandit · safety)
   └──► 🧪 test           (pytest · coverage)
                │
                └── all pass?
                         │
                         ▼
              🐳 build-and-push
              (Docker build → ECR push → vulnerability scan)
                         │
                         └── main/master branch only?
                                      │
                                      ▼
                           🚀 deploy-ecs
                           (patch task def → register → rolling deploy)
                                      │
                                      ▼
                                📬 notify
```

### Trigger conditions

| Event | Jobs that run |
|---|---|
| Push to `main` / `master` | All 6 jobs including deploy |
| Push to `dev` | Jobs 1–5 (build+push but no deploy) |
| Pull request to `main` | Jobs 1–3 only (no Docker, no deploy) |
| `workflow_dispatch` | All jobs; optionally skip tests or force deploy |

---

## GitHub Secrets Setup

Go to your repository → **Settings → Secrets and variables → Actions → New repository secret** and add each of the following:

### Required — ECR & AWS auth

| Secret Name | Description | Example |
|---|---|---|
| `AWS_ACCESS_KEY_ID` | IAM access key ID | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | IAM secret access key | `wJalrXUtnFEMI/K7MDENGbPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | AWS region for ECR and ECS | `ap-south-1` |
| `AWS_ECR_REPOSITORY_URI` | Full ECR repository URI | `123456789012.dkr.ecr.ap-south-1.amazonaws.com/textsummarizer` |
| `AWS_ECR_REPOSITORY_NAME` | ECR repository name only | `textsummarizer` |

### Required — ECS deployment

| Secret Name | Description | Example |
|---|---|---|
| `ECS_CLUSTER` | ECS cluster name | `textsummarizer-cluster` |
| `ECS_SERVICE` | ECS service name | `textsummarizer-service` |
| `ECS_TASK_DEFINITION` | Task definition family name | `textsummarizer-task` |
| `ECS_CONTAINER_NAME` | Container name inside the task definition | `textsummarizer` |

### Optional

| Secret Name | Description |
|---|---|
| `CODECOV_TOKEN` | Codecov token for coverage reporting (required for private repos) |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook for pipeline notifications |

### IAM permissions required

The IAM user whose keys you add must have the following policy attached:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["ecr:GetAuthorizationToken"],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:BatchGetImage",
        "ecr:BatchCheckLayerAvailability",
        "ecr:CompleteLayerUpload",
        "ecr:DescribeImages",
        "ecr:DescribeRepositories",
        "ecr:GetDownloadUrlForLayer",
        "ecr:InitiateLayerUpload",
        "ecr:ListImages",
        "ecr:PutImage",
        "ecr:UploadLayerPart",
        "ecr:CreateRepository",
        "ecr:DescribeImageScanFindings"
      ],
      "Resource": "arn:aws:ecr:REGION:ACCOUNT_ID:repository/textsummarizer"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecs:DescribeServices",
        "ecs:DescribeTaskDefinition",
        "ecs:RegisterTaskDefinition",
        "ecs:UpdateService"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": ["iam:PassRole"],
      "Resource": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole"
    }
  ]
}
```

Replace `REGION` and `ACCOUNT_ID` with your actual values.

---

## Troubleshooting

### `TypeError: unhashable type: 'dict'` on startup

**Cause:** Starlette 0.36+ changed the `TemplateResponse` signature. The old form `TemplateResponse("template.html", {"request": request})` is broken.

**Fix** (already applied in `app.py`):
```python
# Old (broken)
templates.TemplateResponse("index.html", {"request": request})

# New (correct)
templates.TemplateResponse(request, "index.html")
```

---

### `Unknown task summarization` from the prediction endpoint

**Cause:** Transformers 4.52+ removed `"summarization"` from the pipeline task registry.

**Fix** (already applied in `predictionpipeline.py`): Use `AutoModelForSeq2SeqLM.generate()` directly instead of `pipeline("summarization", ...)`.

---

### Prediction endpoint returns `500 — Model not found`

**Cause:** The model artifacts in `artifacts/model_trainer/` do not exist yet.

**Fix:** Run the training pipeline first:
```bash
python main.py
```

Or trigger training from the `/train` dashboard in the UI. Wait for the "Training Completed" notification before using `/predict`.

---

### `ModuleNotFoundError: No module named 'src'`

**Cause:** The app is not being run from the project root directory.

**Fix:**
```bash
cd /path/to/TextSummarizer
python app.py           # always run from the root
```

Or set `PYTHONPATH`:
```bash
PYTHONPATH=/path/to/TextSummarizer python app.py
```

---

### Docker build fails with `pip install` errors

**Cause:** PyPI network timeout or a missing system library.

**Fix:**
```bash
docker build --no-cache --network host -t textsummarizer:latest .
```

---

### ECS tasks keep stopping with exit code 137

**Cause:** The container is running out of memory. PyTorch + PEGASUS require at least 6–8 GB RAM.

**Fix:** Increase memory in the task definition:
```json
"cpu": "2048",
"memory": "8192"
```

---

### Low ROUGE scores after training

**Cause:** `num_train_epochs: 1` in `params.yaml` is intentionally minimal to demonstrate the pipeline quickly.

**Fix:** Edit `params.yaml` and retrain:
```yaml
TrainingArguments:
  num_train_epochs: 5    # ← increase this
  warmup_steps: 500
  gradient_accumulation_steps: 16
```

Then retrain on a GPU instance (AWS `g4dn.xlarge` or `p3.2xlarge` recommended):
```bash
python main.py
```

---

<div align="center">

Built with FastAPI · HuggingFace Transformers · Amazon ECR/ECS · GitHub Actions

</div>
