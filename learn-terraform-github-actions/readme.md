# 🚀 Automating Terraform with GitHub Actions

This repository demonstrates how to automate Terraform workflows using **GitHub Actions** integrated with **HCP Terraform (Terraform Cloud)**. The configuration provisions a publicly accessible EC2 web server on AWS using Terraform, and the CI/CD pipeline runs inside GitHub Actions.

## 📘 Overview

GitHub Actions enables continuous integration and automation for Terraform workflows, helping enforce best practices, improve collaboration, and ensure consistent infrastructure deployments. HashiCorp provides official GitHub Actions that integrate directly with the **HCP Terraform API**. These allow custom CI/CD workflows to plan and apply Terraform changes automatically.

This tutorial-based workflow will:

*   Generate a Terraform **plan** on every pull request.
*   Perform a Terraform **apply** when changes are merged into the `main` branch.
*   Deploy a publicly accessible web server in AWS via an HCP Terraform workspace.

***

# 🏗️ Infrastructure Overview

This Terraform configuration builds:

*   An EC2 instance running Ubuntu
*   Apache web server configured on port **8080**
*   A security group allowing inbound port 8080
*   Outputs exposing the public DNS of the EC2 instance

***

# 🧩 Prerequisites

Before using this workflow, you need:

*   A **GitHub account**
*   An **HCP Terraform account** and organization
*   An **AWS account** (Free‑tier eligible recommended)
*   A **team token** created inside your HCP Terraform organization for GitHub Actions authentication
*   A workspace created in HCP Terraform named `gh-actions-demo` configured for API‑driven runs

***

# 🔐 Configuring HCP Terraform Access

1.  In HCP Terraform → Organization Settings → Teams
    *   Create a new team named **GitHub Actions**
2.  Generate a **Team Token** (expires in 30 days by default)
3.  Save this token and add it to your GitHub repo as a secret (e.g., `TF_API_TOKEN`)

***

# 📁 File Used

    .
    ├── readme.md
    ├── learn-terraform-github-actions
    |   └── main.tf
    └── .github/
        └── workflows/
            └── terraform-apply.yml
            └── terraform-plan.yml

***

# ⚙️ GitHub Actions Workflow Daigram

![workflow daigram](https://github.com/Hemanshu2003/cicd-start/blob/main/learn-terraform-github-actions/1.avif)


The workflow will:

- Generate a plan for every commit to a pull request branch, which you can review in HCP Terraform.

- Apply the configuration when you update the main branch.


# 🌐 Accessing the Web Server

After apply finishes successfully:

Open the URL:

    http://<public-dns>:8080

Example:

    http://ec2-54-163-44-76.compute-1.amazonaws.com:8080

This will load your Apache “Hello World” page.


***

# 📚 References

*   HashiCorp Official Tutorial — *Automate Terraform with GitHub Actions*
- This Code and Step are taken/ Followed from the official website, Kindly Refer it.

[https://developer.hashicorp.com/terraform/tutorials/automation/github-actions](https://developer.hashicorp.com/terraform/tutorials/automation/github-actions)

***
