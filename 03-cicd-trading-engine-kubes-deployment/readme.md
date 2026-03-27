# CI/CD Setup Guide — Trading Engine on AWS (Pluralsight Sandbox)

## Full Repository Structure

```
Hemanshu2003/
│
├── .github/
│   └── workflows/
│       ├── trading-engine-cicd.yml        ← main CI/CD pipeline
│       └── trading-engine-destroy.yml     ← manual sandbox teardown
│
└── cicd-trading-engine-kubes-deployment/                 ← ALL CI/CD triggers on changes here
    ├── .env.example
    ├── .gitignore
    ├── alembic.ini
    ├── docker-compose.yml
    ├── Dockerfile
    ├── pytest.ini
    ├── requirements.txt
    ├── requirements-dev.txt
    │
    ├── alembic/
    │   ├── env.py
    │   └── versions/
    │       └── 0001_initial.py
    │
    ├── app/
    │   ├── __init__.py
    │   ├── database.py
    │   ├── main.py
    │   ├── models.py
    │   ├── models_db.py
    │   └── worker/
    │       ├── __init__.py
    │       └── tasks.py
    │
    ├── k8s/
    │   ├── 00-namespace.yaml
    │   ├── 01-api-gateway-deployment.yaml
    │   ├── 02-worker-deployment.yaml
    │   └── 03-flower-deployment.yaml
    │
    ├── terraform/
    │   ├── backend.tf
    │   ├── main.tf
    │   ├── outputs.tf
    │   ├── terraform.tfvars
    │   └── modules/
    │       ├── vpc/  (main.tf, variables.tf, outputs.tf)
    │       ├── eks/  (main.tf, variables.tf, outputs.tf)
    │       ├── rds/  (main.tf, variables.tf, outputs.tf)
    │       └── redis/(main.tf, variables.tf, outputs.tf)
    │
    └── tests/
        ├── __init__.py
        ├── conftest.py
        ├── test_api.py
        └── test_signals.py
```

---

## Step 1 — Terraform Cloud Setup (one-time)

1. Create a free account at https://app.terraform.io
2. Create an **Organization** (e.g. `my-trading-org`)
3. Create a **Workspace**:
   - Name: `trading-engine-sandbox`
   - Type: **API-Driven workflow** ← important, not VCS-driven
4. In the workspace, go to **Variables** and add these as
   **Environment Variables** (mark sensitive ones as 🔒):

   | Key                    | Value                        | Sensitive |
   |------------------------|------------------------------|-----------|
   | `AWS_ACCESS_KEY_ID`    | from Pluralsight sandbox     | 🔒 Yes   |
   | `AWS_SECRET_ACCESS_KEY`| from Pluralsight sandbox     | 🔒 Yes   |
   | `AWS_DEFAULT_REGION`   | `us-east-1`                  | No        |
   | `TF_VAR_rds_username`  | e.g. `tradingadmin`          | 🔒 Yes   |
   | `TF_VAR_rds_password`  | strong password               | 🔒 Yes   |

5. Generate a **Team API Token** (Settings → Teams → API Token)

---

## Step 2 — GitHub Secrets Setup

In your GitHub repo: **Settings → Secrets and variables → Actions → New secret**

| Secret Name          | Value                                      |
|----------------------|--------------------------------------------|
| `TF_API_TOKEN`       | Terraform Cloud API token from Step 1      |
| `TFC_ORGANIZATION`   | Your TFC org name (e.g. `my-trading-org`)  |
| `TFC_WORKSPACE`      | `trading-engine-sandbox`                   |
| `AWS_ACCESS_KEY_ID`  | From Pluralsight sandbox credentials page  |
| `AWS_SECRET_ACCESS_KEY` | From Pluralsight sandbox               |
| `AWS_REGION`         | `us-east-1`                                |
| `EKS_CLUSTER_NAME`   | `trading-engine-sandbox` (matches tfvars)  |
| `SLACK_WEBHOOK_URL`  | Optional — Slack incoming webhook URL      |

---

## Step 3 — GitHub Environment Setup (for approval gate)

1. Go to **Settings → Environments → New environment**
2. Name it `production`
3. Enable **Required reviewers** — add yourself
4. This means every deploy to main needs a manual click to proceed

---

## Step 4 — Update the workflow to match your folder name

In `.github/workflows/trading-engine-cicd.yml`, line 20:

```yaml
env:
  APP_FOLDER: trading-engine      # ← change to your actual folder name
  TF_FOLDER: trading-engine/terraform
```

And in the `paths:` trigger (lines 11-13):

```yaml
    paths:
      - "trading-engine/**"       # ← change to match your folder
```

---

## Pipeline Flow Diagram

```
git push to main (trading-engine/ changed)
            │
            ▼
    ┌───────────────┐
    │  1. Test       │  pytest + flake8
    └───────┬───────┘
            │ pass
     ┌──────┴───────┐
     │              │
     ▼              ▼
┌─────────┐   ┌──────────────┐
│ 2. Build│   │ 3. TF Plan   │  uploads config to TFC
│  & Push │   │  (TFC)       │  creates speculative run
│  to ECR │   └──────┬───────┘
└────┬────┘          │
     │          plan output
     │          shown in logs
     └────┬─────────┘
          │ both succeed
          ▼
  ┌───────────────┐
  │ 4. TF Apply   │  ← needs manual approval (GitHub Environment)
  │  (TFC)        │  applies infra changes
  └───────┬───────┘
          │
          ▼
  ┌───────────────┐
  │ 5. Deploy     │  kubectl apply  →  EKS rolling update
  │  to EKS       │  waits for rollout to complete
  └───────┬───────┘
          │
          ▼
  ┌───────────────┐
  │ 6. Notify     │  Slack message (optional)
  └───────────────┘


Pull Request flow (no apply, no deploy):
  push to feature branch → Test → TF Plan (speculative) → PR Comment with diff
```

---

## Step 5 —  Kubernetes Manifest Template (k8s/api-gateway-deployment.yaml)

The pipeline does `sed` substitution on `IMAGE_PLACEHOLDER`:

```yaml
spec:
  containers:
    - name: api-gateway
      image: IMAGE_PLACEHOLDER     # ← replaced by sed in deploy job
      ports:
        - containerPort: 8000
```

---


---

## Daily Sandbox Workflow

```bash
# Start of session — just push code, pipeline provisions everything
git add . && git commit -m "feat: your change" && git push origin main

# Local development
cd trading-engine
docker compose up --build
# API:    http://localhost:8000/docs
# Flower: http://localhost:5555

# Test locally
curl -X POST http://localhost:8000/api/v1/analyze/RELIANCE.NS
curl http://localhost:8000/api/v1/task/<task_id>

# Run tests 
# pytest tests/ -v

# END OF SESSION — destroy to save credits
# GitHub → Actions → "Trading Engine — Terraform Destroy" → Run workflow → type DESTROY
```

---

## API Reference

| Method | Endpoint                    | Description               |
|--------|-----------------------------|---------------------------|
| GET    | /health                     | Health check              |
| POST   | /api/v1/analyze/{ticker}    | Submit ticker for analysis|
| GET    | /api/v1/task/{task_id}      | Poll analysis result      |
| GET    | /api/v1/signals?limit=20    | List recent signals       |
| GET    | /docs                       | Swagger UI                |

---

## Signal Logic

| Signal      | RSI Condition | MACD Condition              |
|-------------|---------------|-----------------------------|
| STRONG_BUY  | RSI < 30      | MACD line > Signal line     |
| BUY         | RSI < 45      | MACD value > 0              |
| HOLD        | 45-55         | any                         |
| SELL        | RSI > 55      | MACD value < 0              |
| STRONG_SELL | RSI > 70      | MACD line < Signal line     |

---

## Sandbox Cost Estimate (us-east-1)

| Resource          | Type           | $/hr  |
|-------------------|----------------|-------|
| EKS Control Plane | Managed        | $0.10 |
| EC2 Node (1x)     | t3.medium      | $0.042|
| RDS PostgreSQL    | db.t3.micro    | $0.018|
| ElastiCache Redis | cache.t3.micro | $0.017|
| NAT Gateway       | Single         | $0.045|
| Total             |                | ~$0.22/hr |

> A full 8-hour dev session costs ~$1.76. Always destroy at end of day.

---

## Troubleshooting

| Problem                          | Fix                                                      |
|----------------------------------|----------------------------------------------------------|
| Pipeline doesn't trigger         | Check paths: filter matches your folder name exactly     |
| TFC plan fails: auth error       | Verify TF_API_TOKEN and workspace is API-driven          |
| EKS deploy fails: no context     | Terraform apply may still be running — check TFC         |
| Celery worker crashloops         | Check REDIS_URL secret in K8s namespace                  |
| DB connection refused            | RDS SG only allows traffic from EKS node SG              |
| IMAGE_PLACEHOLDER in pods        | sed substitution failed in deploy job — check CI logs    |



- CMD to run terraform plan in dev:
> terraform plan -out=tfplan-01 -var="rds_username=tradingadmin" -var="rds_password=password"

- Remove old tfstate file incase face conflict profile error
> rm -rf .terraform

>remove the state of the previous credential of AWS -> terraform state rm 'module.eks.aws_iam_openid_connect_provider.eks'



## Acknowledgments

- © All rights reserved by [@Hemanshu2003](https://github.com/Hemanshu2003).
- Sincere thanks to the open‑source community for the tools, libraries, and guidance that made this project possible.
- This application was developed with reference to the official documentation for **Terraform**, **Docker**, and **GitHub Actions**, and with assistance from **Claude.ai**.

## Contact

For questions, feedback, or support, please email **hemanshu.waghmare@gmail.com**.

> Feel free to modify this template to fit your project's specifics and branding. Don't use it for Commercial purpose.

