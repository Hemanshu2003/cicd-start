
gcloud iam service-accounts create my-sa-key   --display-name "deploy-container-app@project-1e48a7cb-1772-4775-8f1.iam.gserviceaccount.com"
    2  ls
    3  gcloud iam service-accounts keys create my-sa-key   --iam-account=deploy-container-app@project-1e48a7cb-1772-4775-8f1.iam.gserviceaccount.com
    4  lear
    5  cls
    6  clear
    7  PROJECT_ID=$(gcloud config get-value project)
    8  SA_NAME=cloudrun-deployer
    9  SA_EMAIL=$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com
   10  gcloud iam service-accounts create $SA_NAME   --display-name="Cloud Run Deployer SA"
   11  gcloud projects add-iam-policy-binding $PROJECT_ID   --member="serviceAccount:$SA_EMAIL"   --role="roles/artifactregistry.writer"
   12  gcloud iam service-accounts create $SA_NAME   --display-name="Cloud Run Deployer SA"
   13  gcloud projects add-iam-policy-binding $PROJECT_ID   --member="serviceAccount:$SA_EMAIL"   --role="roles/artifactregistry.writer"
   14  gcloud projects add-iam-policy-binding $PROJECT_ID   --member="serviceAccount:$SA_EMAIL"   --role="roles/run.admin"
   15  gcloud projects add-iam-policy-binding $PROJECT_ID   --member="serviceAccount:$SA_EMAIL"   --role="roles/run.admin"
   16  gcloud projects add-iam-policy-binding $PROJECT_ID   --member="serviceAccount:$SA_EMAIL"   --role="roles/viewer"
   17  gcloud iam service-accounts keys create key.json   --iam-account=$SA_EMAIL
   18  cat key.json 
   19  ls
   20  cat my-sa-key 
   21  cat key.json 
   22  gcloud org-policies describe constraints/iam.disableServiceAccountKeyCreation
   23  gcloud org-policies disable-enforce constraints/iam.disableServiceAccountKeyCreation
   24  gcloud resource-manager org-policies disable-enforce   constraints/iam.disableServiceAccountKeyCreation   --project=$PROJECT_ID
   25  clear
   26  gcloud iam workload-identity-pools create github-pool   --location="global"   --display-name="GitHub Pool"
   27  gcloud iam workload-identity-pools providers create-oidc github-provider   --location="global"   --workload-identity-pool="github-pool"   --display-name="GitHub Provider"   --issuer-uri="https://token.actions.githubusercontent.com"   --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository"
   28  gcloud iam workload-identity-pools providers create-oidc github-provider   --location="global"   --workload-identity-pool="github-pool"   --display-name="GitHub Provider"   --issuer-uri="https://token.actions.githubusercontent.com"   --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository"
   29  gcloud iam workload-identity-pools providers create-oidc github-provider   --location="global"   --workload-identity-pool="github-pool"   --display-name="GitHub Provider"   --issuer-uri="https://token.actions.githubusercontent.com"   --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository"   --attribute-condition="assertion.repository=='Hemanshu2003/cicd-start'"
   30  PROJECT_ID=$(gcloud config get-value project)
   31  PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
   32  gcloud iam service-accounts add-iam-policy-binding   cloudrun-deployer@$PROJECT_ID.iam.gserviceaccount.com   --role="roles/iam.workloadIdentityUser"   --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME"
   33  clear
   34  PROJECT_ID=$(gcloud config get-value project)
   35  PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
   36  gcloud iam service-accounts add-iam-policy-binding   cloudrun-deployer@$PROJECT_ID.iam.gserviceaccount.com   --role="roles/iam.workloadIdentityUser"   --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/Hemanshu2003/cicd-start"
   37  principalSet://iam.googleapis.com/projects/489927143253/locations/global/workloadIdentityPools/github-pool/attribute.repository/Hemanshu2003/cicd
   38  clear
   39  gcloud iam workload-identity-pools providers describe github-provider   --location=global   --workload-identity-pool=github-pool   --format="value(name)"
   40  gcloud services enable iamcredentials.googleapis.com   --project=$(gcloud config get-value project)
   41  gcloud services enable   artifactregistry.googleapis.com   run.googleapis.com   iamcredentials.googleapis.com   cloudbuild.googleapis.com
   42  gcloud artifacts repositories create node-repo   --repository-format=docker   --location=us-central1
   43  PROJECT_ID=$(gcloud config get-value project)
   44  gcloud iam service-accounts add-iam-policy-binding   $PROJECT_ID-compute@developer.gserviceaccount.com   --member="serviceAccount:cloudrun-deployer@$PROJECT_ID.iam.gserviceaccount.com"   --role="roles/iam.serviceAccountUser"
   45  PROJECT_ID=$(gcloud config get-value project)
   46  PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
   47  gcloud iam service-accounts add-iam-policy-binding   ${PROJECT_NUMBER}-compute@developer.gserviceaccount.com   --member="serviceAccount:cloudrun-deployer@${PROJECT_ID}.iam.gserviceaccount.com"   --role="roles/iam.serviceAccountUser"
   48  gcloud iam service-accounts get-iam-policy   ${PROJECT_NUMBER}-compute@developer.gserviceaccount.com
   49  curl https://cloudrun-deployer-489927143253.us-central1.run.app
   50  gcloud run services add-iam-policy-binding cloudrun-deployer   --member="allUsers"   --role="roles/run.invoker"   --region=us-central1
   51  his
   52  history


   README DOCS 02

   # 🚀 Deploy Node.js App to Google Cloud Run (CI/CD with GitHub Actions - Keyless OIDC)

This guide provides a **complete step-by-step setup** for deploying a Node.js app to **Google Cloud Run** using **GitHub Actions CI/CD** with **Workload Identity Federation (OIDC)** — **no service account keys required**.

It also includes **real-world errors + fixes** encountered during setup.

---

# 📌 Overview

### ✅ What this setup does

* Build Docker image
* Push to Artifact Registry
* Deploy to Cloud Run
* Use **secure keyless authentication (OIDC)**

---

# 🧱 Prerequisites

* Google Cloud Project
* Billing enabled
* GitHub repository
* Node.js app with:

  * `Dockerfile`
  * `app.js`
  * `package.json`

---

# ⚙️ STEP 1 — Enable Required APIs

Run **once** in Cloud Shell:

```bash
gcloud services enable \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  iamcredentials.googleapis.com \
  cloudbuild.googleapis.com
```

---

# ⚙️ STEP 2 — Create Artifact Registry

```bash
gcloud artifacts repositories create YOUR_REPO \
  --repository-format=docker \
  --location=us-central1
```

---

# ⚙️ STEP 3 — Create Service Account

```bash
gcloud iam service-accounts create cloudrun-deployer
```

---

# ⚙️ STEP 4 — Assign Roles

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

# ⚙️ STEP 5 — Setup Workload Identity Federation (OIDC)

## 1. Create Pool

```bash
gcloud iam workload-identity-pools create github-pool \
  --location="global"
```

## 2. Create Provider

```bash
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='YOUR_USERNAME/YOUR_REPO'"
```

---

## ❗ Error: INVALID_ARGUMENT (attribute-condition missing)

**Fix:**
Add:

```bash
--attribute-condition="assertion.repository=='USERNAME/REPO'"
```

---

## 3. Bind GitHub to Service Account

```bash
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud iam service-accounts add-iam-policy-binding \
  cloudrun-deployer@$PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/YOUR_USERNAME/YOUR_REPO"
```

---

# 🔐 GitHub Secrets

Add in GitHub:

| Secret              | Value                                                                                                               |
| ------------------- | ------------------------------------------------------------------------------------------------------------------- |
| GCP_PROJECT_ID      | your-project-id                                                                                                     |
| GAR_REPOSITORY      | repo-name                                                                                                           |
| SERVICE_NAME        | service-name                                                                                                        |
| GCP_SERVICE_ACCOUNT | [cloudrun-deployer@PROJECT_ID.iam.gserviceaccount.com](mailto:cloudrun-deployer@PROJECT_ID.iam.gserviceaccount.com) |
| GCP_WIF_PROVIDER    | full provider path                                                                                                  |

---

## ❗ Error: Invalid audience

**Fix:**
Use:

```bash
gcloud iam workload-identity-pools providers describe github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --format="value(name)"
```

---

# ⚙️ STEP 6 — CI/CD YAML (Fixed)

### 🔥 Key Fix

* Use `image_uri` (lowercase)

---

## ❗ Error: IMAGE_URI empty

**Fix:**

```bash
echo "image_uri=..." >> $GITHUB_OUTPUT
```

and use:

```yaml
${{ steps.meta.outputs.image_uri }}
```

---

## ❗ Error: docker build path not found

**Fix:**

```yaml
docker build ... ./02-deploying-container-apps-on-gcp-cloud-run
```

---

## ❗ Error: Dockerfile not found

**Fix:**
Ensure correct folder path or move Dockerfile to root.

---

## ❗ Error: docker pull ""

**Fix:**

* Wrong output variable
* Remove docker pull step (recommended)

---

# ⚙️ STEP 7 — Cloud Run Permission Fix

## ❗ Error:

```
iam.serviceaccounts.actAs denied
```

### Fix:

```bash
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud iam service-accounts add-iam-policy-binding \
  ${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
  --member="serviceAccount:cloudrun-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

---

# ⚙️ STEP 8 — Make Service Public

## ❗ Error: Forbidden

```bash
gcloud run services add-iam-policy-binding SERVICE_NAME \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --region=us-central1
```

---

# ⚙️ STEP 9 — Fix Node.js App

## ❗ Error: 403 / Forbidden

Add route:

```js
app.get("/", (req, res) => {
  res.send("Cloud Run working!");
});
```

---

## ❗ Error: App not responding

Ensure:

```js
const port = process.env.PORT || 8080;
```

---

# 🧠 Key Learnings

| Issue                        | Fix                    |
| ---------------------------- | ---------------------- |
| Service account keys blocked | Use OIDC               |
| Wrong provider path          | Use PROJECT NUMBER     |
| IMAGE_URI empty              | Case-sensitive outputs |
| Docker build failed          | Fix path               |
| actAs denied                 | Add IAM binding        |
| Forbidden                    | Allow unauthenticated  |
| Repo missing                 | Create manually        |

---

# 🎉 Final Result

```text
✅ Keyless authentication (OIDC)
✅ Secure CI/CD pipeline
✅ Docker build + push
✅ Cloud Run deployment
🚀 Production-ready setup
```

---

# 💡 Bonus Tips

* Never use service account keys
* Keep infra setup manual, CI/CD for deploy only
* Use least privilege roles

---

# 🚀 You're Done!

Your pipeline is now:

* Secure 🔐
* Scalable ⚡
* Production-ready 🚀

---
