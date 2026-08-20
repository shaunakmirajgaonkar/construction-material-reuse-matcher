# GitHub Terminal Commands

Recommended repository: `construction-material-reuse-matcher`

Description: `Privacy-conscious, local-first construction material reuse matching platform with explainable quality, quantity, transport, readiness, and indicative carbon-saving analytics.`

## Existing repository

```bash
cd ~/Downloads/ConstructionMaterialReuseMatcher_Local
git init
git branch -M main
git add .
git commit -m "feat: add MaterialLoop construction material reuse matcher"
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/shaunakmirajgaonkar/construction-material-reuse-matcher.git
git push -u origin main
```

## Create repository with GitHub CLI

```bash
gh auth login
gh repo create construction-material-reuse-matcher --public --description "Privacy-conscious, local-first construction material reuse matching platform with explainable quality, quantity, transport, readiness, and indicative carbon-saving analytics."
git remote add origin https://github.com/shaunakmirajgaonkar/construction-material-reuse-matcher.git
git push -u origin main
```
