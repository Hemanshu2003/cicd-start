# 🚀 Deploy Node.js App to Google Cloud Run (CI/CD with GitHub Actions - Keyless OIDC)

### Full Repository Structure

```
Hemanshu2003/
│
├── .github/
│   └── workflows/
│       ├── deploying-container-apps-cicd        ← main CI/CD pipeline
│
└── 02-deploying-container-apps-on-gcp-cloud-run/          ← ALL CI/CD triggers on changes here
    ├── .dockerignore
    ├── .gitignore
    ├── app.js
    ├── Dockerfile
    ├── package.json
    ├── readme.md

```

---

This guide provides a **complete step-by-step setup** for deploying a Node.js app to **Google Cloud Run** using **GitHub Actions CI/CD** with **Workload Identity Federation (OIDC)** — **no service account keys required**.

It also includes **real-world errors + fixes** encountered during setup.

---

### What is CI/CD?

**CI/CD** automates the software delivery process:

- **CI (Continuous Integration)**: Automatically tests and validates new code changes by integrating them frequently into a shared repository.
- **CD (Continuous Deployment)**: Automatically deploys validated and tested code changes to production or staging environments.

Together, CI/CD significantly improves software development speed, code quality, and deployment reliability.

---

### GitHub Actions for CI/CD

**GitHub Actions** allows you to automate your workflows directly in your GitHub repository.  
You can define workflows in `.yml` files that are triggered by events such as pushes, pull requests, etc.

In this guide, we'll create a GitHub Actions workflow to:
- Build Docker image
- Push to Artifact Registry
- Deploy to Cloud Run
- Use **secure keyless authentication (OIDC)**

---

### 🔐 Keyless OIDC Authentication for GCP

This project uses GitHub Actions OIDC + GCP Workload Identity Federation to enable secure, keyless authentication. Instead of storing service account keys, GitHub issues short‑lived OIDC tokens that GCP validates and exchanges for temporary credentials — improving security, eliminating secret management, and simplifying CI/CD workflows.

---

### 🧱 Prerequisites

* Google Cloud Project
* Billing enabled
* GitHub repository
* Node.js app with:

  * `Dockerfile`
  * `app.js`
  * `package.json`

---



## ⚙️ STEP 1 — Enable Required APIs

Run **once** in Cloud Shell:

```bash
gcloud services enable \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  iamcredentials.googleapis.com \
  cloudbuild.googleapis.com
```

---

## ⚙️ STEP 2 — Create Artifact Registry

```bash
gcloud artifacts repositories create YOUR_REPO \
  --repository-format=docker \
  --location=us-central1
```

---

## ⚙️ STEP 3 — Create Service Account

```bash
gcloud iam service-accounts create cloudrun-deployer
```

---

## ⚙️ STEP 4 — Assign Roles

```bash
PROJECT_ID=$(gcloud config get-value project)

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:cloudrun-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:cloudrun-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:cloudrun-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

---

## ⚙️ STEP 5 — Setup Workload Identity Federation (OIDC) (one-time setup)

### 1. Create Workload Identity Pool

```bash
gcloud iam workload-identity-pools create github-pool \
  --location="global"
```

### 2. Create Provider

```bash
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='YOUR_USERNAME/YOUR_REPO'"
```

---

### 3. Allow GitHub repo to use SA

```bash
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud iam service-accounts add-iam-policy-binding \
  cloudrun-deployer@$PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME"
```

### 4. Get correct provider path

Run this in Cloud Shell:
```bash
gcloud iam workload-identity-pools providers describe github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --format="value(name)"
```

✅ Output will look like (note it down for GitHub Secrets ):
```bash
projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider
```

---

## 🔐 GitHub Secrets

Add in GitHub:

| Secret              | Value                                                                                                               |
| ------------------- | ------------------------------------------------------------------------------------------------------------------- |
| GCP_PROJECT_ID      | your-project-id                                                                                                     |
| GAR_REPOSITORY      | repo-name                                                                                                           |
| SERVICE_NAME        | service-name                                                                                                        |
| GCP_SERVICE_ACCOUNT | [cloudrun-deployer@PROJECT_ID.iam.gserviceaccount.com](mailto:cloudrun-deployer@PROJECT_ID.iam.gserviceaccount.com) |
| GCP_WIF_PROVIDER    | full provider path                                                                                                  |

---


### Workflow Explanation

- **Trigger**: Runs on `push` or `pull request` to the `main` branch.
- **Checkout Code**: Checks out your repository's latest code.
- **Authenticate with Google Cloud**: Authenticates using the Workload Identity Federation (OIDC).
- **Setup Cloud SDK**: Prepares `gcloud` CLI.
- **Dockerize and Push**: Builds a Docker image and pushes it to **Google Artifact Registry**.
- **Deploy to Cloud Run**: Deploys the new container image to **Google Cloud Run**.


***

## 🚨 Common Issues & Fixes

This section documents frequent errors encountered during GCP Workload Identity Federation + Cloud Run deployments, along with their fixes.

***

### ❗ Error: **Invalid audience**

This error appears when the audience (`aud`) configured in your Workload Identity Provider does not match what GitHub Actions sends.

### ✅ Fix: Verify the provider name

Run the following command to confirm your provider’s full resource name:

```bash
gcloud iam workload-identity-pools providers describe github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --format="value(name)"
```

Ensure your GitHub Actions workflow uses the exact `workload_identity_provider` value returned here.

***

## ⚙️ Fix Cloud Run Permission Issue

### ❗ Error:

    iam.serviceaccounts.actAs denied

This happens when your deploying service account does **not** have permission to act as the Cloud Run runtime service account.

### ✅ Fix: Grant `roles/iam.serviceAccountUser`

```bash
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud iam service-accounts add-iam-policy-binding \
  ${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
  --member="serviceAccount:cloudrun-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

***

### ⚙️ Make Cloud Run Service Public

### ❗ Error: **Forbidden**

This occurs when the service isn’t publicly invokable.

### ✅ Fix: Allow public (unauthenticated) access

```bash
gcloud run services add-iam-policy-binding SERVICE_NAME \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --region=us-central1
```

***

### License

© [2025] Hemanshu Waghmare.  
All rights reserved. please contact:
- Hemanshu Waghmare – [hemanshu.waghmare@gmail.com](hemanshu.waghmare@gmail.com)

---

## 🚀 Happy Deploying!







