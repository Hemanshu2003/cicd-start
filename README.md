# 🚀 CI/CD Start
 
Welcome to **cicd-start**! This repository serves as a hands-on learning hub and practical codebase for implementing Continuous Integration and Continuous Deployment (CI/CD) pipelines.
 
It contains multiple projects focusing on Infrastructure as Code (IaC), containerization, cloud deployments, Kubernetes, and DevSecOps—all automated seamlessly using **GitHub Actions**.
 
---
 
## 📂 Repository Structure
 
The repository is divided into specific sub-projects, each demonstrating a unique CI/CD use case:
 
### 🏗️ [01-learn-terraform-github-actions](01-learn-terraform-github-actions/)
* **Focus:** Infrastructure as Code (IaC) Automation.
* **Overview:** Demonstrates how to automate Terraform workflows (`terraform init`, `plan`, and `apply`) via GitHub Actions and AWS free tier account. It ensures infrastructure changes are peer-reviewed and deployed predictably.
 
### ☁️ [02-deploying-container-apps-on-gcp-cloud-run](02-deploying-container-apps-on-gcp-cloud-run/)
* **Focus:** Serverless Deployments & Containerization.
* **Overview:** A complete CI/CD pipeline that builds a Docker container for NodeJS backend Application, pushes the image to Google Cloud (Artifact Registry/GCR), and automatically deploys the application to **GCP Cloud Run** and provide Public URL.
 
### ☸️ [03-cicd-trading-engine-kubes-deployment](03-cicd-trading-engine-kubes-deployment/)

* **Focus:** Kubernetes (K8s) Microservices.
* **Overview:** Covers the automation required to deploy a mock trading engine to a Kubernetes cluster. The workflow handles building the image, updating manifests, and executing rolling updates to the cluster._(Incomplete: Due to complexity of the project and time constraints image build and creating complete infrastructure using terraform and deploying it to AWS is DONE...testing and deploying build image to EKS is remaining.)_
 
---
 
## 🛡️ [DevSecOps: CodeQL Analysis](.github/workflows/codeql-analysis.yml)
 
## Enable CodeQL Analysis in Your GitHub Repository

**CodeQL** is GitHub’s semantic code analysis engine that treats **code as data** so you can query your codebase and automatically discover vulnerabilities before they reach production.<!-- [1](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/about-code-scanning-with-codeql)[2](https://codeql.github.com/docs/codeql-overview/about-codeql/) -->

### 🔍 What is CodeQL?

CodeQL builds a database representing your code (AST, control/data flow, etc.) and runs security queries against it. Findings appear as **code scanning alerts** right inside GitHub.<!-- [1](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/about-code-scanning-with-codeql) -->

- Works with both **compiled and interpreted** languages.<!-- [1](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/about-code-scanning-with-codeql) -->
- Supports variant analysis—find **all** instances of a vulnerability pattern across a codebase.<!-- [2](https://codeql.github.com/docs/codeql-overview/about-codeql/) -->


### 💡 Why use CodeQL?

- **Detect real vulnerabilities** (injection, insecure flows, and many CWEs) using a rich, community‑maintained query set.<!-- [3](https://codeql.github.com/docs/) -->
- **First‑class GitHub integration**: runs in GitHub Actions and annotates PRs and the Security tab.<!-- [1](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/about-code-scanning-with-codeql) -->
- **Faster PR scans** via incremental analysis for popular languages.<!-- [4](https://github.blog/changelog/2026-03-24-faster-incremental-analysis-with-codeql-in-pull-requests/) -->
- **Free for public repos** (part of GitHub’s security for open source).<!-- [5](https://github.com/pricing)[6](https://codeql.github.com/) -->


### 🗣️ Supported languages

C/C++, C#, Go, **Java/Kotlin**, **JavaScript/TypeScript**, **Python**, **Ruby**, **Rust**, **Swift**, and even **GitHub Actions workflows**.<!-- [1](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/about-code-scanning-with-codeql)[7](https://codeql.github.com/docs/codeql-overview/supported-languages-and-frameworks/) -->

> Tip: For the Java/Kotlin and JS/TS families, use `java-kotlin` and `javascript-typescript` in your workflow.<!-- [1](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/about-code-scanning-with-codeql) -->


### 🚀 Quick Start (Two Options)

### Option A — Default Setup (easiest)
1. In your repo, open **Security → Code scanning alerts → Set up code scanning**.  
2. Choose **CodeQL** and follow the prompts. GitHub will pick languages and triggers automatically (you can edit later).<!-- [1](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/about-code-scanning-with-codeql) -->

### Option B — Advanced Setup (custom workflow)
Create `.github/workflows/codeql-analysis.yml`

> Reference: [link](https://dev.to/nivicius/how-to-enable-codeql-analysis-in-your-github-repository-5ad3)

---
 
## 🛠️ Technologies & Tools Used
 
* **CI/CD & Automation:** GitHub Actions
* **Infrastructure as Code:** Terraform (HCL)
* **Cloud Provider:** Google Cloud Platform (GCP)
* **Containerization & Orchestration:** Docker, Kubernetes
* **Security Scanning:** GitHub CodeQL
* **Primary Languages:** Python, HCL, JavaScript, Dockerfile
 
---
 
## 🚀 Getting Started
 
If you want to use or explore these workflows locally or in your own GitHub environment:
 
1. **Clone the repository:**
```bash
   git clone [https://github.com/Hemanshu2003/cicd-start.git](https://github.com/Hemanshu2003/cicd-start.git)
   cd cicd-start
```
 
2.  **Explore the Workflows:**
    Navigate to the `.github/workflows/` directory to see the exact GitHub Actions YAML files powering the deployments and CodeQL analysis.
 
3.  **Configure Secrets:**
    If you are forking this repo to test the pipelines, ensure you add the required repository secrets in your GitHub settings (e.g., AWS Access Key, Terraform API tokens, or Kubeconfig files).
 
-----

### 🤝 Contributing
 
Issues and PRs are welcome. please contact:
- Hemanshu Waghmare – [hemanshu.waghmare@gmail.com](hemanshu.waghmare@gmail.com)

---

### 🚀 Happy Deploying!