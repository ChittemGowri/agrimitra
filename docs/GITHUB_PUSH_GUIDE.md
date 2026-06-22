# Pushing AgriMitra to GitHub - Step by Step

This assumes you already have the agrimitra/ project folder on your
machine (from setup) and a GitHub account.

---

## 1. Create the repository on GitHub

1. Go to https://github.com/new
2. Repository name: agrimitra (or your choice)
3. Description: "Multi-agent AI farm advisory system - Google x Kaggle AI Agents Intensive capstone"
4. Choose Public (so judges can view it)
5. Do NOT check "Add a README" / "Add .gitignore" / "Add license"
   -- this project already has all three; checking these on GitHub
   causes a conflict when you push
6. Click Create repository

GitHub will show you a page with setup commands -- ignore it, use the
commands below instead (they're tailored to this project).

---

## 2. Initialize git locally and make your first commit

```bash
cd agrimitra
git init
git add .
git status   # sanity check: .env should NOT appear in this list
```

Important: confirm .env is NOT listed in git status output. If
it is, your .gitignore isn't being picked up -- check that
.gitignore exists in the project root and contains the line .env.

```bash
git commit -m "Initial commit: AgriMitra multi-agent farm advisory system"
```

---

## 3. Connect to your GitHub repository

Replace <your-username> with your actual GitHub username:

```bash
git branch -M main
git remote add origin https://github.com/<your-username>/agrimitra.git
git push -u origin main
```

If prompted for credentials and password auth fails (GitHub disabled
plain passwords), use a Personal Access Token instead:

1. GitHub -> Settings -> Developer settings -> Personal access tokens ->
   Tokens (classic) -> Generate new token -> check the "repo" scope
2. When git push asks for a password, paste the token instead

Or use SSH instead of HTTPS (recommended if you push often):

```bash
# Generate a key if you don't have one
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
# Paste this into GitHub -> Settings -> SSH and GPG keys -> New SSH key

# Then use the SSH remote instead:
git remote set-url origin git@github.com:<your-username>/agrimitra.git
git push -u origin main
```

---

## 4. Verify

Go to https://github.com/<your-username>/agrimitra -- you should see
all your files, with the README rendering on the repo homepage.

Double-check sensitive files were NOT pushed:

```bash
git ls-files | grep -E "^\.env$"
# should print nothing
```

---

## 5. Future updates

Whenever you make changes:

```bash
git add .
git commit -m "Describe what you changed"
git push
```

---

## 6. Optional: add topics and a nice repo description

On your GitHub repo page -> click the gear icon next to "About" -> add:
- Topics: ai-agents, gemini-api, streamlit, rag, multi-agent-systems, agriculture
- Website: (your deployed Streamlit Cloud URL, once deployed -- see docs/DEPLOYMENT.md)

This makes the repo easier for judges to find and understand at a glance.
