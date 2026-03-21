# CI/CD Deployment to Google Cloud Run using GitHub Actions

This guide explains how to set up **Continuous Integration (CI)** and **Continuous Deployment (CD)** for your project using **GitHub Actions**, and deploy it to **Google Cloud Run**.

---

## What is CI/CD?

**CI/CD** automates the software delivery process:

- **CI (Continuous Integration)**: Automatically tests and validates new code changes by integrating them frequently into a shared repository.
- **CD (Continuous Deployment)**: Automatically deploys validated and tested code changes to production or staging environments.

Together, CI/CD significantly improves software development speed, code quality, and deployment reliability.

---

## GitHub Actions for CI/CD

**GitHub Actions** allows you to automate your workflows directly in your GitHub repository.  
You can define workflows in `.yml` files that are triggered by events such as pushes, pull requests, etc.

In this guide, we'll create a GitHub Actions workflow to:
- Build a Docker image of the application.
- Push it to Google Artifact Registry.
- Deploy it to Google Cloud Run.

---

## Storing Sensitive Data Securely (GitHub Secrets)

To securely access Google Cloud resources during CI/CD, we store sensitive credentials as **GitHub Secrets**.

### Required Secrets

| Secret Name        | Purpose                                       |
|--------------------|-----------------------------------------------|
| `GCP_SA_KEY`        | Entire JSON key of your Google Service Account |
| `GCP_PROJECT_ID`    | Your Google Cloud Project ID                 |
| `DOCKER_IMAGE_NAME` | Your Docker image name (for tagging)          |

### How to Add Secrets

1. Go to your GitHub Repository.
2. Click on `Settings` → `Secrets and Variables` → `Actions`.
3. Under the `Secrets` tab, click **New repository secret**.
4. Add the above secrets with their corresponding values.

---

## Workflow Configuration

We will create a workflow file named `cicd.yml` and place it in:

```
.github/workflows/cicd.yml
```

Paste the following configuration into the file:

```yaml
name: Deploy to Cloud Run

env:
  SERVICE_NAME: next-app-project

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  dockerize-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Authenticate with Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: '${{ secrets.GCP_SA_KEY }}'
          project_id: ${{ secrets.GCP_PROJECT_ID }}

      - name: Set up Google Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker to use Google credentials
        run: |
          gcloud auth configure-docker

      - name: Build and Push Docker Image
        run: |
          docker build -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/${{ secrets.DOCKER_IMAGE_NAME }}:latest .
          docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/${{ secrets.DOCKER_IMAGE_NAME }}:latest

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy $SERVICE_NAME \
            --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/${{ secrets.DOCKER_IMAGE_NAME }}:latest \
            --platform managed \
            --region us-central1 \
            --allow-unauthenticated
```

---

## Workflow Explanation

- **Trigger**: Runs on `push` or `pull request` to the `main` branch.
- **Checkout Code**: Checks out your repository's latest code.
- **Authenticate with Google Cloud**: Authenticates using the Service Account key.
- **Setup Cloud SDK**: Prepares `gcloud` CLI.
- **Dockerize and Push**: Builds a Docker image and pushes it to **Google Artifact Registry**.
- **Deploy to Cloud Run**: Deploys the new container image to **Google Cloud Run**.

---

## Important Notes

- **First Deployment**:  
  On the **first deployment**, you should **not** pass the `--service-name` parameter.  
  Instead, deploy without specifying the service name to let Cloud Run create a default service.  
  After the first deployment, you can use the `SERVICE_NAME` environment variable as shown.
  
- **Service Account Permissions**:
  Ensure the GitHub Actions service account has the following IAM roles:
  - `Cloud Run Admin`
  - `Service Account User`
  - `Artifact Registry Writer`
  
  Example to assign roles:

  ```bash
  gcloud projects add-iam-policy-binding [PROJECT_ID] \
    --member="serviceAccount:[SERVICE_ACCOUNT_EMAIL]" \
    --role="roles/run.admin"
  
  gcloud projects add-iam-policy-binding [PROJECT_ID] \
    --member="serviceAccount:[SERVICE_ACCOUNT_EMAIL]" \
    --role="roles/artifactregistry.writer"
  
  gcloud projects add-iam-policy-binding [PROJECT_ID] \
    --member="serviceAccount:[SERVICE_ACCOUNT_EMAIL]" \
    --role="roles/iam.serviceAccountUser"
  ```

---

## License

© [2025] Hemanshu Waghmare.  
All rights reserved. please contact:
- Hemanshu Waghmare – [hemanshu.waghmare@gmail.com](hemanshu.waghmare@gmail.com)

---

# 🚀 Happy Deploying!

