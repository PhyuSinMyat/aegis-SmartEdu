# Complete Beginner's Guide: Push Your Code to GitHub

This guide shows you **exactly** how to upload your SmartEdu project to GitHub, step-by-step.

---

## ⚠️ IMPORTANT: Read This First

**If your local code is VERY DIFFERENT from what's currently on GitHub**, you need to handle this carefully! 

This guide now includes **Part 9: Choose Your Strategy** which has 3 safe approaches:
- **Strategy 1: Merge** - Keep both old and new code history
- **Strategy 2: Force Push** - Replace old code completely (use with caution)
- **Strategy 3: Archive** - Save old code in a branch, start fresh on main (safest)

👉 **Follow steps 1-8 first, then Part 9 will help you choose the right approach based on your situation.**

---

## Prerequisites

You need:
1. **GitHub account** (create one at https://github.com if you don't have)
2. **GitHub repository URL** (you said you already have this)
3. **Git installed** on your computer (we'll check this first)

---

## Part 1: Check if Git is Installed

### Step 1.1: Open Command Prompt

**Windows:**
1. Press `Windows Key + R`
2. Type `cmd` and press Enter
3. A black window opens - this is Command Prompt

### Step 1.2: Check Git

Type this and press Enter:
```bash
git --version
```

**If you see:** `git version 2.x.x` - **You're good! Skip to Part 2**

**If you see:** `'git' is not recognized...` - **You need to install Git:**

1. Go to: https://git-scm.com/download/windows
2. Download and run the installer
3. Click "Next" on everything (default settings are fine)
4. After installation, **close and reopen Command Prompt**
5. Try `git --version` again

---

## Part 2: Navigate to Your Project Folder

```bash
# Navigate to your project
cd C:\Users\User\Downloads\version_24_AUTO_planning+replanning

# Confirm you're in the right place
dir
```

You should see files like: `app.py`, `requirements.txt`, `README.md`, etc.

---

## Part 3: Create .gitignore File (IMPORTANT!)

**What is .gitignore?** = A file that tells Git to ignore certain files (like passwords, temporary files, etc.)

### Step 3.1: Create the File

**Option A: Using Notepad**
1. Open Notepad
2. Copy and paste the content below
3. Save as: `C:\Users\User\Downloads\version_24_AUTO_planning+replanning\.gitignore`
   - **Important:** In "Save as type", select "All Files"
   - **Important:** Make sure filename is exactly `.gitignore` (starts with a dot)

**Option B: Using Command Prompt**
```bash
notepad .gitignore
```
- Click "Yes" when it asks to create a new file
- Paste the content below
- Save and close

### Step 3.2: .gitignore Content

**Copy and paste this:**

```gitignore
# Environment variables (NEVER commit this - contains passwords!)
.env
.env.local
.env.*.local

# Virtual environment
venv/
env/
ENV/
.venv

# Python cache
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Database (don't commit local database to GitHub)
*.db
*.sqlite
*.sqlite3
users.db

# Uploaded files (don't commit user uploads)
uploads/
frontend/static/profile_pics/*
!frontend/static/profile_pics/.gitkeep

# Logs
*.log
logs/
*.log.*

# IDE/Editor files
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Windows files
Thumbs.db
ehthumbs.db
Desktop.ini

# Testing
.pytest_cache/
.coverage
htmlcov/

# Temporary files
*.tmp
*.temp
.cache/

# Distribution / packaging
build/
dist/
*.egg-info/

# Don't commit AWS keys!
*.pem
*.ppk
credentials
credentials.json
```

**Why is this important?**
- Prevents you from accidentally uploading passwords (.env file)
- Prevents uploading large files (venv folder, database)
- Prevents uploading user data (uploads folder)
- Keeps your repo clean

---

## Part 4: Initialize Git Repository

```bash
# Initialize Git in this folder
git init
```

You should see: `Initialized empty Git repository...`

**What just happened?** = Git is now tracking this folder

---

## Part 5: Configure Git (First Time Only)

Tell Git who you are:

```bash
# Set your name (replace with your actual name)
git config --global user.name "Your Name"

# Set your email (use the same email as your GitHub account)
git config --global user.email "your.email@example.com"
```

**Example:**
```bash
git config --global user.name "John Doe"
git config --global user.email "john@example.com"
```

---

## Part 6: Add All Files to Git

```bash
# Add all files (except those in .gitignore)
git add .

# Check what files were added
git status
```

You should see a list of files in green. These will be uploaded to GitHub.

**If you see `.env` in the list** - STOP! That means .gitignore isn't working:
```bash
# Remove .env from staging
git rm --cached .env

# Try again
git status
```

---

## Part 7: Create Your First Commit

```bash
# Commit with a message
git commit -m "Initial commit: SmartEdu hackathon project"
```

You should see something like: `X files changed, Y insertions(+)`

**What is a commit?** = A snapshot of your code at this moment

---

## Part 8: Connect to GitHub Repository

### Step 8.1: Get Your GitHub Repo URL

1. Go to your GitHub repository in web browser
2. Click the green **"Code"** button
3. Copy the URL (it looks like one of these):
   - HTTPS: `https://github.com/username/smartedu.git`
   - SSH: `git@github.com:username/smartedu.git`

**Use HTTPS if you're unsure** (easier for beginners)

### Step 8.2: Add Remote

```bash
# Add GitHub repo as "origin"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Replace with your actual repo URL, for example:
# git remote add origin https://github.com/johndoe/smartedu.git

# Verify it was added
git remote -v
```

You should see:
```
origin  https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git (fetch)
origin  https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git (push)
```

### Step 8.3: **IMPORTANT - Check if Your Local Code is Different from GitHub**

Before pushing, check what's currently on your GitHub repository:

```bash
# Fetch information from GitHub (doesn't change your local files)
git fetch origin

# See what branches exist on GitHub
git branch -r
```

**If your local code is VERY DIFFERENT from GitHub's main branch**, you have several options:

---

## Part 9: Choose Your Strategy (IMPORTANT!)

### 🔍 First, Understand What You Have

**Check GitHub in your browser:**
1. Go to `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`
2. Look at the files in the `main` branch
3. Are they similar to your current local files, or completely different?

---

### 📊 Decision Tree - Which Strategy Should I Use?

```
START HERE:
│
├─ Is GitHub repo empty/only has README?
│  └─ YES → ✅ Safe! Skip to Part 10 (Regular Push)
│
├─ Is the old GitHub code important to keep?
│  ├─ YES → Do you need the old code in Git history?
│  │        ├─ YES → Use Strategy 1: Merge Approach
│  │        └─ NO → Use Strategy 3: Archive Old and Start Fresh
│  │
│  └─ NO → Is anyone else using this repository?
│           ├─ YES → Use Strategy 3: Archive Old and Start Fresh (safer)
│           └─ NO → Use Strategy 2A: Force Push (simplest)
```

**Quick Recommendations:**

#### **Scenario A: GitHub repo is empty or just has README**
→ **Action:** Skip to Part 10 (Regular Push) - simplest path

#### **Scenario B: GitHub has old code from months ago, completely different**
→ **Action:** Use **Strategy 2A: Force Push** (if you're sure old code isn't needed)
→ **Alternative:** Use **Strategy 3: Archive** (if you want to be extra safe)

#### **Scenario C: GitHub has slightly old code, same project**
→ **Action:** Use **Strategy 1: Merge Approach** (keeps history clean)

#### **Scenario D: Not sure what to do?**
→ **Action:** Use **Strategy 3: Archive** (safest - keeps everything)

---

### Strategy 1: Merge Approach (Keep History)

**When to use:** You want to preserve the old code in Git history, but your current code is the new version.

```bash
# Step 1: Fetch the GitHub code
git fetch origin

# Step 2: Check what branch exists on GitHub
git branch -r
# You'll see something like: origin/main or origin/master

# Step 3: Merge with allow-unrelated-histories
# Replace 'main' with 'master' if that's what you see
git pull origin main --allow-unrelated-histories

# Step 4: If there are merge conflicts, you'll see a message
# List files with conflicts:
git status
```

**If you get merge conflicts:**

```bash
# You'll see files marked as "both modified"
# For each conflicted file, choose YOUR version (current local code):

# Option A: Keep your version for specific files
git checkout --ours path/to/file.py
git add path/to/file.py

# Option B: Keep your version for ALL conflicts (recommended if your code is completely different)
git checkout --ours .
git add .

# Step 5: Complete the merge
git commit -m "Merge old GitHub code with new local version - using current version"

# Step 6: Now push (go to Part 11)
git push origin main
```

**What this does:**
- ✅ Preserves Git history from both branches
- ✅ Creates a merge commit
- ⚠️ May create conflicts (but we resolve them by keeping your version)

---

### Strategy 2: Fresh Start Approach (Replace Everything)

**When to use:** The GitHub code is completely outdated and you want to replace it entirely. This is simpler and cleaner.

#### **Option 2A: Force Push (Deletes Old History - Use with Caution)**

```bash
# Step 1: Make sure you're on main branch
git branch -M main

# Step 2: Force push (THIS DELETES OLD CODE ON GITHUB!)
git push -f origin main
```

**⚠️ WARNING:** This **permanently deletes** the old code from GitHub. Only use if:
- The old code on GitHub is not important
- No one else is using that repository
- You have a backup of old code if you need it

**✅ Use this if:** You're sure the old GitHub code is obsolete.

#### **Option 2B: Create a New Branch (Safer Alternative)**

```bash
# Step 1: Create a new branch for your new code
git checkout -b new-version

# Step 2: Push your new branch
git push -u origin new-version

# Step 3: On GitHub.com:
# - Go to your repository
# - Click "Settings" → "Branches"
# - Change default branch from "main" to "new-version"
# - Click "Update"

# Optional: Delete old main branch on GitHub
# Go to GitHub → Branches → Delete "main" branch
# Then rename new-version to main:
git branch -m new-version main
git push origin main
git push origin --delete new-version
```

**What this does:**
- ✅ Keeps old code safe in old branch
- ✅ Creates clean new branch
- ✅ You can switch default branch on GitHub
- ✅ Safest approach

---

### Strategy 3: Archive Old and Start Fresh (Most Professional)

**When to use:** You want to keep old code accessible but clearly show new version is current.

```bash
# Step 1: Fetch old code
git fetch origin

# Step 2: Create archive branch for old code
git checkout -b archive-old-version origin/main

# Step 3: Push archive branch
git push -u origin archive-old-version

# Step 4: Go back to your new code
git checkout main

# Step 5: Force push new code to main
git push -f origin main

# Step 6: Add a note in your README
echo "Note: Old version archived in 'archive-old-version' branch" >> README.md
git add README.md
git commit -m "Add note about archived old version"
git push
```

**What this does:**
- ✅ Old code preserved in `archive-old-version` branch
- ✅ Main branch has clean new code
- ✅ Anyone can see old version if needed
- ✅ Professional approach

---

## Part 10: Regular Push (If No Conflicts)

### Step 10.1: First Push (After Choosing Your Strategy)

**If you followed Strategy 1, 2, or 3 above, your code is already pushed!** Skip to Part 11 (Verify on GitHub).

**If GitHub was empty (Scenario A), push now:**

```bash
# Push to GitHub (main branch)
git push -u origin main
```

**If you get an error:** `src refspec main does not exist`

Try this instead:
```bash
# Check your branch name
git branch

# If it shows "master" instead of "main", use:
git push -u origin master
```

**Or rename your branch to main:**
```bash
git branch -M main
git push -u origin main
```

### Step 10.2: GitHub Login

**First time pushing, you'll need to authenticate:**

**Option A: Browser Login (Easiest)**
- A browser window will open
- Log into GitHub
- Click "Authorize"

**Option B: Personal Access Token**

If the browser doesn't open:

1. Go to GitHub: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: "SmartEdu Deploy"
4. Select scopes: Check **"repo"** (full control of private repos)
5. Click **"Generate token"**
6. **Copy the token** (you won't see it again!)
7. When Command Prompt asks for password, **paste the token** (not your GitHub password)

### Step 10.3: Success!

You should see:
```
Counting objects: 100% done.
Writing objects: 100% done.
To https://github.com/username/repo.git
 * [new branch]      main -> main
```

**Congratulations!** Your code is now on GitHub! 🎉

---

## Part 11: Verify on GitHub

1. Go to your GitHub repository in browser
2. Refresh the page
3. You should see all your files!

**Check these are NOT there** (they should be ignored):
- ❌ `.env` file
- ❌ `venv/` folder
- ❌ `users.db` file
- ❌ `__pycache__/` folders
- ❌ Any `.pem` or `.ppk` files

**If any of these ARE visible** - you need to remove them! See "Troubleshooting" below.

---

## Part 12: Create .env.example File

**Why?** = So others (and you on EC2) know what environment variables are needed

### Step 12.1: Create the File

```bash
notepad .env.example
```

### Step 12.2: Content

Paste this (notice: no actual passwords, just placeholders):

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here

# Environment
FLASK_ENV=production

# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL_ID=anthropic.claude-v2-1

# Bedrock Settings
BEDROCK_MAX_TOKENS=12000
BEDROCK_RETRY_MAX_TOKENS=18000
BEDROCK_TEXT_TEMPERATURE=0
BEDROCK_CONNECT_TIMEOUT=20
BEDROCK_READ_TIMEOUT=120
BEDROCK_MAX_ATTEMPTS=3
BEDROCK_API_RETRIES=2

# Debug Settings
USE_MOCK_LLM=0
DEBUG_LLM=1
```

Save and close.

### Step 12.3: Commit and Push

```bash
# Add the new file
git add .env.example

# Commit
git commit -m "Add .env.example for configuration reference"

# Push
git push
```

---

## Part 13: Update Your Deployment Guide

Now update the BEGINNER_DEPLOY_GUIDE.md to use GitHub:

In **Part 2** of the deployment guide, you can now tell people to use **Option B**:

```bash
# On your EC2 terminal
cd /home/ubuntu
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git smartedu
cd smartedu

# Copy .env.example to .env
cp .env.example .env

# Edit .env with your actual credentials
nano .env
```

This is **much easier** than uploading via SCP!

---

## Common Git Commands You'll Use

### After Making Changes:

```bash
# 1. Check what changed
git status

# 2. Add all changed files
git add .

# 3. Commit with a message
git commit -m "Description of what you changed"

# 4. Push to GitHub
git push
```

### View History:

```bash
# See all commits
git log

# See recent commits (short version)
git log --oneline -10
```

### Undo Changes:

```bash
# Discard changes to a file (before git add)
git checkout -- filename.py

# Unstage a file (after git add, before commit)
git reset HEAD filename.py

# Undo last commit (keep changes)
git reset --soft HEAD~1
```

---

## Troubleshooting

### Issue 1: "Permission denied (publickey)"

**Meaning:** Git is trying to use SSH but you don't have SSH keys set up

**Solution:** Use HTTPS instead:
```bash
# Remove SSH remote
git remote remove origin

# Add HTTPS remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Try pushing again
git push -u origin main
```

### Issue 2: ".env file is in the repository!"

**Meaning:** You accidentally committed .env file

**Solution:**
```bash
# Remove from Git (but keep local file)
git rm --cached .env

# Make sure .gitignore has .env in it
echo .env >> .gitignore

# Commit the removal
git commit -m "Remove .env from repository"

# Push
git push
```

**Then on GitHub:**
1. Go to your repo
2. Click ".env" file
3. Click trash icon to delete it
4. Commit the deletion

### Issue 3: "Repository already exists" or "Updates were rejected"

**Meaning:** Your GitHub repo already has files that conflict with your local code

**You should have already handled this in Part 9!** Go back to Part 9 and choose a strategy.

**Quick fix if you skipped Part 9:**
```bash
# See Part 9 above for detailed strategies
# Quick option - Archive old code and push new:
git fetch origin
git checkout -b archive-old-version origin/main
git push -u origin archive-old-version
git checkout main
git push -f origin main
```

### Issue 3B: "Divergent branches" error

**Meaning:** Git found differences and doesn't know how to merge them

**Solution - Choose your approach:**
```bash
# Option 1: Keep your version (discard GitHub's version)
git push -f origin main

# Option 2: Merge (see Strategy 1 in Part 9)
git pull origin main --allow-unrelated-histories
# Resolve conflicts, then:
git push origin main

# Option 3: Create new branch (see Strategy 2B in Part 9)
git checkout -b new-version
git push -u origin new-version
```

### Issue 4: "Large files detected"

**Meaning:** A file is too big (>100MB)

**Solution:**
```bash
# Find large files
find . -type f -size +10M

# Add to .gitignore
echo "path/to/large/file" >> .gitignore

# Remove from Git
git rm --cached path/to/large/file

# Commit
git commit -m "Remove large file"
```

### Issue 5: Can't remember GitHub password

**Solution:** Use Personal Access Token (see Part 9, Option B)

---

## Best Practices

### 1. Commit Often
```bash
# Good: Many small commits with clear messages
git commit -m "Add user registration feature"
git commit -m "Fix login bug"
git commit -m "Update README"

# Bad: One huge commit
git commit -m "Changed stuff"
```

### 2. Write Good Commit Messages
```bash
# Good messages:
"Add replanning agent for missed sessions"
"Fix database connection timeout issue"
"Update deployment guide with EC2 instructions"

# Bad messages:
"Fixed stuff"
"Changes"
"asdfgh"
```

### 3. Never Commit Sensitive Files

**NEVER commit:**
- `.env` files
- `.pem` keys
- Database files with real user data
- API keys
- Passwords

**Always check** before committing:
```bash
git status  # See what will be committed
```

### 4. Pull Before Push

If you're working with a team:
```bash
# Always pull latest changes first
git pull

# Then make your changes
# Then commit and push
git add .
git commit -m "Your message"
git push
```

---

## GitHub Desktop (Alternative - Easier for Beginners!)

If command line is confusing, try **GitHub Desktop**:

1. Download: https://desktop.github.com/
2. Install and login
3. Click **"Add"** → **"Add Existing Repository"**
4. Select your project folder
5. See all changes visually
6. Click **"Commit to main"**
7. Click **"Push origin"**

**Much easier with a visual interface!**

---

## Quick Reference Card

```bash
# First time setup
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/user/repo.git
git push -u origin main

# Daily workflow
git status                    # Check changes
git add .                     # Stage all changes
git commit -m "Message"       # Commit changes
git push                      # Upload to GitHub
git pull                      # Download from GitHub

# Check things
git log                       # View history
git remote -v                 # View GitHub URL
git branch                    # View branches

# Undo things
git checkout -- file.py       # Discard changes
git reset HEAD file.py        # Unstage file
git reset --soft HEAD~1       # Undo last commit
```

---

## After Pushing to GitHub

Now you can deploy easily! On your EC2:

```bash
# Clone from GitHub (one command!)
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git smartedu

# Navigate to project
cd smartedu

# Create .env from example
cp .env.example .env
nano .env
# Add your actual credentials

# Install dependencies
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Follow rest of deployment guide...
```

**Way easier than uploading via SCP!**

---

## Updating Code Later

When you make changes locally and want to update GitHub:

```bash
# 1. Make changes to your files
# 2. Check what changed
git status

# 3. Add changes
git add .

# 4. Commit with message
git commit -m "Describe what you changed"

# 5. Push to GitHub
git push

# 6. On EC2, pull the changes
ssh -i key.pem ubuntu@YOUR_EC2_IP
cd /home/ubuntu/smartedu
git pull
sudo systemctl restart smartedu
```

---

## Congratulations! 🎉

Your code is now on GitHub! This makes it:
- ✅ Easy to deploy to EC2 (just `git clone`)
- ✅ Safe (backed up on GitHub)
- ✅ Easy to share with team members
- ✅ Professional (judges can see your code)
- ✅ Version controlled (can go back to old versions)

**Your GitHub repo is now ready for your hackathon submission!** 🚀

You can share the repo link with judges: `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`
