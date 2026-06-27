---
title: CI/CD Platforms
description: Run AutonomyLoops agents in GitHub Actions, GitLab CI, Jenkins, and more
tags:
  - github-actions
  - gitlab-ci
  - jenkins
  - ci-cd
---

# CI/CD Platforms

AutonomyLoops agents run in any CI/CD environment. This guide provides templates for major platforms.

## GitHub Actions

```yaml
# .github/workflows/agent-review.yml
name: Agent Code Review

on:
  pull_request:
    branches: [main]

jobs:
  agent-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install AutonomyLoops
        run: pip install "autonomy-loops[anthropic]"

      - name: Run Review Agent
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          autonomy-loops run \
            --role reviewer \
            --mode review \
            --task "Review the changes in this PR. Focus on correctness, security, and performance." \
            > review-output.md

      - name: Post Review Comment
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('review-output.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: review
            });
```

## GitLab CI/CD

```yaml
# .gitlab-ci.yml
stages:
  - review
  - test

agent-review:
  stage: review
  image: python:3.12-slim
  variables:
    ANTHROPIC_API_KEY: $ANTHROPIC_API_KEY
  script:
    - pip install "autonomy-loops[anthropic]"
    - |
      autonomy-loops run \
        --role reviewer \
        --mode review \
        --task "Review the MR changes for correctness and security." \
        > review.md
    - cat review.md
  artifacts:
    paths:
      - review.md
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

agent-test-suggest:
  stage: review
  image: python:3.12-slim
  variables:
    ANTHROPIC_API_KEY: $ANTHROPIC_API_KEY
  script:
    - pip install "autonomy-loops[anthropic]"
    - |
      autonomy-loops run \
        --role tester \
        --mode test \
        --task "Suggest test cases for the changed files in this MR."
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

## Jenkins (Declarative Pipeline)

```groovy
// Jenkinsfile
pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
        }
    }
    
    environment {
        ANTHROPIC_API_KEY = credentials('anthropic-api-key')
    }
    
    stages {
        stage('Install') {
            steps {
                sh 'pip install "autonomy-loops[anthropic]"'
            }
        }
        
        stage('Agent Review') {
            when {
                changeRequest()
            }
            steps {
                sh '''
                    autonomy-loops run \
                      --role reviewer \
                      --mode review \
                      --task "Review the changes for quality and security."
                '''
            }
        }
        
        stage('Agent Pipeline') {
            steps {
                sh '''
                    autonomy-loops orchestrate \
                      --pipeline pipelines/ci-review.yaml
                '''
            }
        }
    }
}
```

## Azure DevOps

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include: [main]

pr:
  branches:
    include: [main]

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.12'

  - script: pip install "autonomy-loops[anthropic]"
    displayName: Install AutonomyLoops

  - script: |
      autonomy-loops run \
        --role reviewer \
        --mode review \
        --task "Review the PR changes."
    displayName: Agent Review
    env:
      ANTHROPIC_API_KEY: $(ANTHROPIC_API_KEY)
```

## Platform-Independent Pattern

For any CI system, the pattern is:

```bash
# 1. Install
pip install "autonomy-loops[all]"

# 2. Set provider key (from CI secrets)
export ANTHROPIC_API_KEY="$SECRET_KEY"

# 3. Run agent
autonomy-loops run --role <role> --mode <mode> --task "<task>"

# 4. Or run pipeline
autonomy-loops orchestrate --pipeline pipelines/<name>.yaml
```
