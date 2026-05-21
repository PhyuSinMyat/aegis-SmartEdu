# Complete Beginner's Guide to Deploy SmartEdu on AWS EC2

This guide assumes you know **nothing** about cloud deployment. I'll explain every single step!

---

## 🚀 **QUICK START FOR HACKATHON DEMO?**

**If you just need a working demo ASAP (30 minutes), use this instead:**

👉 **[QUICK_DEPLOY_GUIDE.md](QUICK_DEPLOY_GUIDE.md)** - Simplified, hackathon-focused version!

**This full guide** is comprehensive with explanations, troubleshooting, security, and cost management. Great for learning or production deployment.

---

## Deployment Strategy Overview

We're using the **GitHub Upload Method** for deployment:

```
📁 Your Laptop (Local Code)
    ↓
    1. Verify .env is in .gitignore
    ↓
    2. Push code to GitHub (WITHOUT .env)
    ↓
☁️  GitHub Repository
    ↓
    3. Clone repo to EC2
    ↓
🖥️  EC2 Server
    ↓
    4. Manually create .env on EC2
    ↓
    5. Install dependencies & run
```

**Why this approach?**
- ✅ Secure: Secret keys stay off GitHub
- ✅ Version control: Track all changes
- ✅ Easy updates: Just `git pull` to update
- ✅ Professional: Industry standard

---

## Complete Deployment Checklist

**Here's the bird's-eye view of what we'll do:**

### Phase 1: AWS Setup (Part 0-1)
- [ ] Verify `.gitignore` excludes `.env`
- [ ] Create EC2 instance (Ubuntu, t2.micro)
- [ ] Download `.pem` key file (save it safely!)
- [ ] Configure Security Group (SSH, HTTP, HTTPS)
- [ ] Note down Public IP address

### Phase 2: Connect & Upload (Part 2-3)
- [ ] Connect to EC2 via SSH/PuTTY
- [ ] Push code to GitHub (without `.env`)
- [ ] Clone repository to EC2

### Phase 3: Server Setup (Part 4-7)
- [ ] Update Ubuntu & install Python 3.11
- [ ] Install Nginx, Git
- [ ] Create virtual environment
- [ ] Install Python dependencies
- [ ] Create AWS IAM user for Bedrock
- [ ] Enable Bedrock model access (Claude)
- [ ] Create `.env` file on EC2 (with AWS keys)
- [ ] Initialize database

### Phase 4: Production Setup (Part 8-11)
- [ ] Test app locally on EC2
- [ ] Configure Nginx
- [ ] Set up Gunicorn service
- [ ] Verify firewall rules

### Phase 5: Testing & Go Live (Part 12-14)
- [ ] Test website from browser
- [ ] Test all features (register, login, upload, plan generation)
- [ ] Update browser extension & desktop app with EC2 IP
- [ ] Demo and celebrate! 🎉

**Estimated time:** 2-4 hours (first time)

---

## Architecture Overview

**Here's what you're building:**

```
┌─────────────────────────────────────────────────────────────┐
│                         INTERNET                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP Request (port 80)
                     ▼
┌────────────────────────────────────────────────────────────┐
│              AWS EC2 Instance (Ubuntu)                      │
│                                                             │
│  ┌──────────────┐     ┌────────────────┐                  │
│  │    Nginx     │────▶│   Gunicorn     │                  │
│  │  (Port 80)   │     │  (Port 8000)   │                  │
│  │  Web Server  │     │  App Server    │                  │
│  └──────────────┘     └────────┬───────┘                  │
│                                │                            │
│                                ▼                            │
│                      ┌──────────────────┐                  │
│                      │   Flask App      │                  │
│                      │   (app.py)       │                  │
│                      └────┬────────┬────┘                  │
│                           │        │                        │
│                           │        └─────────┐              │
│                           ▼                  ▼              │
│                    ┌─────────────┐   ┌──────────────┐     │
│                    │  SQLite DB  │   │   Uploads    │     │
│                    │ (users.db)  │   │  (Files)     │     │
│                    └─────────────┘   └──────────────┘     │
│                                                             │
└────────────────────────┬───────────────────────────────────┘
                         │
                         │ API Calls
                         ▼
                ┌─────────────────────┐
                │   AWS Bedrock       │
                │   (Claude AI)       │
                │   - Study Plans     │
                │   - AI Features     │
                └─────────────────────┘
```

**Components:**
- **Nginx**: Web server that receives requests from internet
- **Gunicorn**: Production Python server that runs Flask
- **Flask App**: Your SmartEdu application code
- **SQLite DB**: Database with user data and sessions
- **AWS Bedrock**: Claude AI for generating study plans

---

## What You Need Before Starting

You'll need:
1. **AWS Account** (with permission to create EC2 instances)
2. **Credit/Debit card** (for AWS - they offer free tier)
3. **Your laptop** with internet connection

We'll create everything else together in this guide!

---

## Part 0: Before You Start - Verify .gitignore (IMPORTANT!)

**This ensures your secret keys DON'T get uploaded to GitHub!**

On your local computer, check if `.gitignore` file exists:

```bash
cd C:\Users\User\Downloads\version_24_AUTO_planning+replanning
cat .gitignore
```

**Make sure it includes:**
```
.env
*.pyc
__pycache__/
venv/
*.db
*.log
uploads/
frontend/static/profile_pics/
```

**If `.gitignore` doesn't exist, create it:**

```bash
# Create .gitignore file with these contents
notepad .gitignore
```

Then paste the above contents, save, and close.

**Test it:**
```bash
# This should NOT show .env in the list
git status
```

If you see `.env` in the list, run:
```bash
git rm --cached .env
```

✅ Now you're safe to push to GitHub!

### What Files Should NEVER Go to GitHub?

**Never upload these to GitHub:**
- ❌ `.env` - Contains secret keys (AWS credentials, etc.)
- ❌ `*.pem` - SSH key files
- ❌ `users.db` - Contains user data
- ❌ `uploads/` - User uploaded files
- ❌ `frontend/static/profile_pics/` - User profile pictures
- ❌ `__pycache__/` - Python compiled files
- ❌ `venv/` - Virtual environment (too large)

**What SHOULD go to GitHub:**
- ✅ All `.py` files (your code)
- ✅ `requirements.txt` (dependencies list)
- ✅ `templates/` and `frontend/` (HTML, CSS, JS)
- ✅ `.gitignore` (tells git what to ignore)
- ✅ `README.md` (documentation)

**Security Tip:** If you accidentally pushed `.env` to GitHub:
```bash
# Remove it from git history (on your local machine)
git rm --cached .env
git commit -m "Remove .env from git"
git push

# IMPORTANT: Change ALL passwords and keys in that .env file!
# The old ones are now exposed on GitHub!
```

---

## Part 1: Create Your AWS EC2 Instance

### Step 1.1: Sign Up / Log In to AWS

1. **Go to AWS Console**: https://console.aws.amazon.com/
2. **Sign in** with your AWS account
   - If you don't have an account, click "Create a new AWS account"
   - You'll need: email, password, credit card (for verification)
   - **AWS Free Tier**: First 12 months are mostly free! Perfect for hackathons.

### Step 1.2: Navigate to EC2

1. After logging in, you'll see the **AWS Console Dashboard**
2. In the search bar at the top, type: **EC2**
3. Click on **EC2** (it says "Virtual Servers in the Cloud")
4. You should now see the **EC2 Dashboard**

### Step 1.3: Launch a New Instance

1. Click the orange **"Launch Instance"** button (top right)
2. You'll see a form with several sections. Let's fill them out:

#### Name and Tags
```
Name: smartedu-server
```
(You can name it anything, but this is descriptive)

#### Application and OS Images (Amazon Machine Image - AMI)

1. **Quick Start** tab should be selected
2. Select **Ubuntu**
3. Choose: **Ubuntu Server 24.04 LTS** (or latest LTS version)
4. Architecture: **64-bit (x86)**
5. Make sure it says **"Free tier eligible"** (if you want free tier)

**What is an AMI?** = The operating system that will run on your server

#### Instance Type

1. Select: **t2.micro** (should be default)
   - This gives you: 1 vCPU, 1 GB RAM
   - **Free tier eligible** ✓
   - Good enough for your hackathon demo!

2. If you need more power (after free tier or for production):
   - **t2.small** (1 vCPU, 2 GB RAM) - ~$17/month
   - **t2.medium** (2 vCPU, 4 GB RAM) - ~$34/month

**For now, stick with t2.micro!**

#### Key Pair (login) - IMPORTANT!

This is how you'll connect to your server!

1. Click **"Create new key pair"**
2. Fill in:
   ```
   Key pair name: smartedu-key
   Key pair type: RSA
   Private key file format: .pem (for Mac/Linux) or .ppk (for PuTTY on Windows)
   ```
   
   **For Windows users:**
   - If you'll use **PuTTY**: Choose **.ppk**
   - If you'll use **PowerShell/Git Bash**: Choose **.pem**
   - Not sure? Choose **.pem** (you can convert later)

3. Click **"Create key pair"**
4. **IMPORTANT**: The file will download automatically
   - **Save it somewhere safe!** Like: `C:\Users\User\smartedu-key.pem`
   - **You can NEVER download it again!**
   - **Don't lose it or you can't access your server!**

#### Network Settings

Click **"Edit"** button on the right, then configure:

1. **Auto-assign public IP**: **Enable** ✓

2. **Firewall (security groups)**:
   - Select: **Create security group**
   - Security group name: `smartedu-security-group`
   - Description: `Security group for SmartEdu web app`

3. **Inbound security group rules** - Add these 3 rules:

   **Rule 1: SSH (for you to connect)**
   - Type: SSH
   - Protocol: TCP
   - Port: 22
   - Source type: My IP (recommended) or Anywhere (less secure)
   - Description: SSH access

   **Rule 2: HTTP (for website)**
   - Click "Add security group rule"
   - Type: HTTP
   - Protocol: TCP
   - Port: 80
   - Source type: Anywhere (0.0.0.0/0)
   - Description: Web traffic

   **Rule 3: HTTPS (for secure website)**
   - Click "Add security group rule"
   - Type: HTTPS
   - Protocol: TCP
   - Port: 443
   - Source type: Anywhere (0.0.0.0/0)
   - Description: Secure web traffic

**What are security groups?** = Firewall rules that control who can access your server

#### Configure Storage

1. **Size**: 8 GB is default (should be enough)
   - You can increase to **20-30 GB** for free tier (up to 30 GB free)
   - Recommended: **20 GB** (gives you room for logs, uploads, etc.)

2. **Volume type**: gp3 (General Purpose SSD) - default is fine

3. **Delete on termination**: ✓ (checked) - so you don't pay for storage after deleting server

#### Advanced Details (Optional - can skip for basic setup)

You can leave everything as default, but if you want:

**User data** (optional - for automatic setup):
You can skip this for now, we'll install everything manually.

### Step 1.4: Review and Launch

1. On the right side, you'll see a **Summary** panel
2. Review:
   - Name: smartedu-server
   - Instance type: t2.micro
   - Storage: 20 GB
   - Security group: 3 rules (SSH, HTTP, HTTPS)

3. Click the orange **"Launch instance"** button

4. You'll see: "Successfully initiated launch of instance"

5. Click **"View all instances"**

### Step 1.5: Wait for Instance to Start

1. You'll see your instance in the list
2. **Instance State** will say: "Pending" (yellow circle)
3. Wait 1-2 minutes...
4. It will change to: **"Running"** (green circle) ✓

### Step 1.6: Get Your Connection Details

1. **Click on your instance** (the checkbox on the left)
2. Look at the **Details** tab below
3. Find and note down:

   **Public IPv4 address**: `54.123.45.67` (example - yours will be different)
   - This is your server's address on the internet!
   
   **Public IPv4 DNS**: `ec2-54-123-45-67.compute-1.amazonaws.com`
   - Another way to access your server

4. **Username for Ubuntu**: `ubuntu` (this is standard for Ubuntu AMIs)

**Save these somewhere:**
```
EC2 Public IP: ___________________
Key file location: C:\Users\User\smartedu-key.pem
Username: ubuntu
```

### Step 1.7: Important AWS Free Tier Notes

**Free Tier Limits (first 12 months):**
- ✅ 750 hours/month of t2.micro (that's 24/7 for one instance!)
- ✅ 30 GB of storage
- ✅ 15 GB of bandwidth out

**After free tier or if you exceed limits:**
- t2.micro: ~$8-10/month if running 24/7
- Data transfer: First 100 GB/month is free, then ~$0.09/GB

**Cost-saving tips:**
- **Stop** (not terminate) your instance when not using it
  - Right-click instance → Instance state → Stop
  - This keeps your data but stops charges
  - Start it again when needed
- **Terminate** when you're completely done
  - This deletes everything (can't recover!)

**Monitor your costs:**
- Go to: https://console.aws.amazon.com/billing/
- Set up billing alerts (recommended!)

---

## Part 2: Connecting to Your EC2 Instance

### Step 2.1: Prepare Your Key File (Windows)

1. **Find your `.pem` or `.ppk` file** (you downloaded this in Part 1, Step 1.3)
2. It should be in your **Downloads** folder
3. **Move it somewhere safe**, like: `C:\Users\User\smartedu-key.pem`

**Important for Windows users**: You need to convert the `.pem` file to work with PuTTY (a program to connect to servers).

**Option A: Use PuTTY (Recommended for Windows)**

Download and install:
1. **PuTTY**: https://www.putty.org/
2. **PuTTYgen**: (comes with PuTTY installer)

**Convert .pem to .ppk:**
1. Open **PuTTYgen**
2. Click **Load**
3. Select your `.pem` file (change file type to "All Files" if you don't see it)
4. Click **Save private key**
5. Save as `my-key.ppk`

**Connect with PuTTY:**
1. Open **PuTTY**
2. In "Host Name", type: `ubuntu@YOUR_EC2_IP` 
   - Replace YOUR_EC2_IP with the IP from Part 1, Step 1.6
   - Example: `ubuntu@54.123.45.67`
3. On the left menu, go to: **Connection → SSH → Auth → Credentials**
4. Click **Browse** and select your `.ppk` file
5. (Optional) Go back to "Session", give it a name under "Saved Sessions", click Save
6. Click **Open**
7. If you see a security alert about the server's host key, click **Accept** or **Yes**
8. You're now connected! You should see a terminal with `ubuntu@ip-xxx:~$`

**Option B: Use Windows PowerShell/Git Bash**

If you have Git Bash or Windows 10+:

```powershell
# Open PowerShell or Git Bash
# Navigate to where your .pem file is
cd C:\Users\User\

# Set permissions (only needed once)
icacls smartedu-key.pem /inheritance:r
icacls smartedu-key.pem /grant:r "%username%":"(R)"

# Connect to EC2
ssh -i smartedu-key.pem ubuntu@YOUR_EC2_IP
# Replace YOUR_EC2_IP with the IP from Part 1, Step 1.6
# Example: ssh -i smartedu-key.pem ubuntu@54.123.45.67
```

When you see a message like "Are you sure you want to continue?", type `yes` and press Enter.

---

### Step 2.2: You're Connected!

If successful, you should see something like:
```
ubuntu@ip-172-31-12-34:~$
```

This is the **terminal** of your server. Every command you type here runs on the EC2 server, not your computer!

**Test it:**
```bash
# Type this and press Enter
whoami
```

You should see: `ubuntu` (or whatever username you're using)

---

## Part 3: Upload Your Project to EC2

**We'll use GitHub to deploy your code** (safer and recommended approach):

### Step 3.1: Push Code to GitHub (On Your Local Computer)

**Important:** Before pushing, make sure your `.env` file is NOT included (it should already be in `.gitignore`)

```bash
# Check if .env is ignored
cat .gitignore
# You should see ".env" listed there

# If you haven't initialized git yet:
cd C:\Users\User\Downloads\version_24_AUTO_planning+replanning
git init
git add .
git commit -m "Initial commit for SmartEdu deployment"

# Create a new repository on GitHub:
# 1. Go to https://github.com
# 2. Click "+" icon (top right) → "New repository"
# 3. Name it "smartedu" (or whatever you like)
# 4. Don't initialize with README
# 5. Click "Create repository"

# Link your local code to GitHub (replace with YOUR username)
git remote add origin https://github.com/YOUR_USERNAME/smartedu.git
git branch -M main
git push -u origin main
```

**What is .gitignore?** = A file that tells git which files NOT to upload (like `.env` with your secret keys)

### Step 3.2: Clone from GitHub to EC2

**On your EC2 terminal (PuTTY window):**

```bash
# Navigate to home directory
cd /home/ubuntu

# Clone your repository (replace with YOUR GitHub username)
git clone https://github.com/YOUR_USERNAME/smartedu.git

# Navigate into the project
cd smartedu

# Check if files are there (but .env should NOT be here)
ls
# You should see: app.py, requirements.txt, backend/, frontend/, etc.
# You should NOT see: .env (we'll create this manually next)
```

**Why this approach?**
✓ Safer: Your `.env` file (with secret keys) stays on your computer
✓ Easier updates: Just `git pull` to update code later
✓ Professional: Industry standard deployment method
✓ Version control: Track all your changes

---

## Part 4: Install Everything Your App Needs

**Run these commands in your EC2 terminal (PuTTY window):**

### Step 4.1: Update Ubuntu

```bash
# Update package list (like refreshing available software)
sudo apt update

# Upgrade installed packages (this might take 5-10 minutes)
sudo apt upgrade -y
```

**What is `sudo`?** = "Super User DO" - it gives you admin permissions

### Step 4.2: Install Python 3.11

```bash
# Install Python 3.11 and pip
sudo apt install -y python3.11 python3.11-venv python3-pip

# Check if installed correctly
python3.11 --version
# Should show: Python 3.11.x
```

### Step 4.3: Install Other Required Software

```bash
# Install Nginx (web server)
sudo apt install -y nginx

# Install Git (if you need it)
sudo apt install -y git
```

---

## Part 5: Set Up Your Application

### Step 5.1: Navigate to Your Project

```bash
# Go to your project folder (already created in Part 2)
cd /home/ubuntu/smartedu

# Verify files are there
ls
# You should see: app.py, requirements.txt, backend/, frontend/, etc.
# You should NOT see .env (we'll create it in Part 5)
```

### Step 5.2: Create Python Virtual Environment

**What is a virtual environment?** = A separate space for your project's Python packages, so they don't conflict with system packages.

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate it (you'll need to do this every time you work on the project)
source venv/bin/activate

# Your prompt should now start with (venv)
# Like: (venv) ubuntu@ip-172-31-12-34:~/smartedu$
```

### Step 5.3: Install Python Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements (this takes 5-10 minutes)
pip install -r requirements.txt

# Install Gunicorn (production web server)
pip install gunicorn
```

**What is Gunicorn?** = A production-ready server that runs your Flask app (better than `python app.py` for real deployment)

---

## Part 6: Configure Environment Variables

**IMPORTANT:** Since we didn't upload `.env` to GitHub (for security), we need to create it manually on EC2.

### Step 6.1: Create .env File on EC2

```bash
# Make sure you're in the project directory
cd /home/ubuntu/smartedu

# Create .env file with your configuration
nano .env
```

**What is nano?** = A text editor in the terminal (like Notepad but in command line)

**Copy and paste this** (use right-click to paste in PuTTY):

```env
SECRET_KEY=your-super-secret-key-change-this-12345
FLASK_ENV=production

# AWS Bedrock credentials (get these from your advisor or AWS console)
AWS_ACCESS_KEY_ID=your-access-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL_ID=anthropic.claude-v2-1

# Bedrock settings
BEDROCK_MAX_TOKENS=12000
BEDROCK_RETRY_MAX_TOKENS=18000
BEDROCK_TEXT_TEMPERATURE=0
BEDROCK_CONNECT_TIMEOUT=20
BEDROCK_READ_TIMEOUT=120
BEDROCK_MAX_ATTEMPTS=3
BEDROCK_API_RETRIES=2

# Debug settings
USE_MOCK_LLM=0
DEBUG_LLM=1
```

**Save and exit:**
1. Press `Ctrl + O` (that's letter O, not zero) to save
2. Press `Enter` to confirm
3. Press `Ctrl + X` to exit

**Important:** Replace `your-access-key-here` with your actual AWS keys!

**Where to get AWS keys?**

### Step 6.2: Create AWS Access Keys for Bedrock

Your app uses AWS Bedrock (Claude AI) for generating study plans. Here's how to get the keys:

1. **Go to IAM Console**: https://console.aws.amazon.com/iam/
2. Click on **Users** in the left menu
3. Click **Create user**
4. Username: `smartedu-bedrock-user`
5. Click **Next**
6. Select **Attach policies directly**
7. Search for and select: **AmazonBedrockFullAccess**
8. Click **Next**, then **Create user**

**Now create access keys for this user:**

1. Click on the user you just created (`smartedu-bedrock-user`)
2. Go to **Security credentials** tab
3. Scroll to **Access keys**
4. Click **Create access key**
5. Select use case: **Application running outside AWS**
6. Click **Next**
7. Description: `SmartEdu EC2 deployment`
8. Click **Create access key**

**IMPORTANT: Save these immediately!**
```
Access key ID: AKIA.....................
Secret access key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

You'll paste these into your `.env` file!

**Click "Download .csv file"** for backup, then click **Done**

### Step 6.3: Enable Bedrock Model Access

**Your app needs access to Claude AI models:**

1. Go to Bedrock Console: https://console.aws.amazon.com/bedrock/
2. On the left menu, click **Model access** (under "Bedrock configurations")
3. Click **Manage model access** (orange button, top right)
4. Find and enable:
   - ✓ **Anthropic - Claude 3.5 Sonnet v2**
   - ✓ **Anthropic - Claude 3.5 Sonnet** (original)
   - ✓ **Anthropic - Claude 3 Haiku**
   - ✓ **Anthropic - Claude Instant** (if available)
5. Scroll down and click **Request model access**
6. Wait 1-2 minutes for approval (usually instant)
7. Refresh page - Status should show **Access granted** (green)

**Important:** If you don't enable model access, your app will get errors when generating study plans!

### Step 6.4: Update .env with Your Keys

Now go back to your EC2 terminal and update the `.env` file:

```bash
# If you already created .env, edit it:
nano .env
```

Update these lines with your actual keys:
```env
AWS_ACCESS_KEY_ID=AKIA..................  # From Step 6.2
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxx... # From Step 6.2
AWS_REGION=us-east-1                      # Use the region where you enabled Bedrock
AWS_BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

**What region to use?**
- Check which region you enabled Bedrock in (top right of AWS console)
- Common regions: `us-east-1`, `us-west-2`, `eu-west-1`

Save and exit (`Ctrl + O`, `Enter`, `Ctrl + X`)

---

## Part 7: Initialize Database

```bash
# Make sure you're in project folder with venv activated
cd /home/ubuntu/smartedu
source venv/bin/activate

# Initialize the database
python3 -c "from database import DatabaseHelper; DatabaseHelper()"

# Check if database was created
ls users.db
# Should show: users.db
```

**What just happened?** = Created an empty SQLite database with all the tables your app needs.

---

## Part 8: Test Your App Locally

Before making it public, let's test if it works:

```bash
# Run the app in debug mode
python3 app.py
```

You should see output like:
```
[AppInit] Starting schedulers in main Flask process
[AppInit] OK Summary scheduler successfully initialized
[AppInit] OK Planning scheduler successfully initialized
 * Running on http://127.0.0.1:5000
```

**Test it:**
Open a **new terminal/PowerShell** on your local computer and run:
```bash
ssh -i smartedu-key.pem -L 5000:localhost:5000 ubuntu@YOUR_EC2_IP
# Replace YOUR_EC2_IP with your actual IP
```

Then open your browser and go to: `http://localhost:5000`

If you see the SmartEdu website, it works! 🎉

**Stop the app:**
Go back to the EC2 terminal and press `Ctrl + C`

---

## Part 9: Set Up Nginx (Web Server)

**Why Nginx?** = It makes your app accessible from the internet and handles requests better than Flask alone.

### Step 9.1: Configure Nginx

```bash
# Create Nginx configuration file
sudo nano /etc/nginx/sites-available/smartedu
```

**Paste this configuration:**

```nginx
server {
    listen 80;
    server_name _;
    
    client_max_body_size 20M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /static {
        alias /home/ubuntu/smartedu/frontend/static;
        expires 30d;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

Save and exit (`Ctrl + O`, `Enter`, `Ctrl + X`)

### Step 9.2: Enable the Configuration

```bash
# Create symbolic link (enables the site)
sudo ln -s /etc/nginx/sites-available/smartedu /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t
# Should say: "syntax is ok" and "test is successful"

# Restart Nginx
sudo systemctl restart nginx

# Check if Nginx is running
sudo systemctl status nginx
# Should show: "active (running)" in green
```

**Press `q` to exit the status view**

---

## Part 10: Set Up Gunicorn as a Service

**Why a service?** = So your app keeps running even if you close the terminal, and restarts automatically if it crashes.

### Step 10.1: Create Service File

```bash
sudo nano /etc/systemd/system/smartedu.service
```

**Paste this:**

```ini
[Unit]
Description=SmartEdu Flask Application
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/smartedu
Environment="PATH=/home/ubuntu/smartedu/venv/bin"
ExecStart=/home/ubuntu/smartedu/venv/bin/gunicorn \
    --workers 2 \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile /var/log/smartedu-access.log \
    --error-logfile /var/log/smartedu-error.log \
    --log-level info \
    app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save and exit (`Ctrl + O`, `Enter`, `Ctrl + X`)

### Step 10.2: Start the Service

```bash
# Reload systemd to read new service file
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable smartedu

# Start the service
sudo systemctl start smartedu

# Check status
sudo systemctl status smartedu
```

You should see: `Active: active (running)` in green

**If you see any errors**, check the logs:
```bash
sudo journalctl -u smartedu -n 50
```

---

## Part 11: Verify Firewall Ports (Should Already Be Open!)

**Good news:** If you followed Part 1 correctly, your firewall should already be configured! Let's just verify.

### Step 11.1: Verify EC2 Security Group (AWS Console)

**This is done in your web browser:**

1. Go to AWS Console: https://console.aws.amazon.com/ec2/
2. Click **Instances** on the left menu
3. Find your instance (smartedu-server) and click on it
4. Scroll down to **Security** tab
5. Click on the **Security Group** name (looks like `smartedu-security-group`)
6. Check **Inbound rules** - you should already have these rules:

| Type  | Protocol | Port Range | Source    | Description       |
|-------|----------|------------|-----------|-------------------|
| SSH   | TCP      | 22         | My IP     | SSH access        |
| HTTP  | TCP      | 80         | 0.0.0.0/0 | Web access        |
| HTTPS | TCP      | 443        | 0.0.0.0/0 | Secure web access |

**What does this mean?**
- Port 22: Allows you to SSH (connect via terminal)
- Port 80: Allows anyone to access your website
- Port 443: For HTTPS (secure connections)

**If any rule is missing:**
1. Click **Edit inbound rules**
2. Click **Add rule**
3. Add the missing rule from the table above
4. Click **Save rules**

### Step 11.2: Check Ubuntu Firewall (on EC2)

```bash
# Check if UFW is active
sudo ufw status

# If it says "inactive", you're good!
# If it's active, run these:
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
```

---

## Part 12: Test Your Website!

### Step 12.1: Get Your Public IP

**Option A: From AWS Console**
1. Go to EC2 → Instances
2. Find your instance
3. Copy the "Public IPv4 address"

**Option B: From EC2 terminal**
```bash
curl http://checkip.amazonaws.com
```

### Step 12.2: Open in Browser

Open your web browser and go to:
```
http://YOUR_EC2_PUBLIC_IP
```

For example: `http://54.123.45.67`

**You should see the SmartEdu welcome page!** 🎉

---

## Part 13: Test All Features

### Test Checklist:

1. **Home page loads** ✓
   - Go to: `http://YOUR_IP/`

2. **Register a new user** ✓
   - Click Register
   - Fill in details
   - Upload profile picture

3. **Login** ✓
   - Use your new credentials

4. **Upload timetable** ✓
   - Upload a test PDF/Excel file
   - Check if it processes

5. **Generate study plan** ✓
   - Go through the planning wizard
   - Check if AI generates a plan

6. **Track study session** ✓
   - Start a study session
   - Check if tracker works

---

## Part 14: Update Browser Extension & Desktop App

### For Browser Extension:

**On your local computer:**

1. Open `smartedu-extension` folder
2. Edit `background.js`:
   - Find the line with `const SERVER_URL`
   - Change to: `const SERVER_URL = "http://YOUR_EC2_IP";`

3. Edit `manifest.json`:
   - Find `"host_permissions"`
   - Add: `"http://YOUR_EC2_IP/*"`

4. Load extension in Chrome:
   - Go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select your `smartedu-extension` folder

5. Test it:
   - Click the extension icon
   - Login with your credentials
   - Browse the web, it should track!

### For Desktop App:

**On your local computer:**

1. Open `smartedu_tray.py` in a text editor
2. Find line 53: `DEFAULT_SERVER_URL`
3. Change to: `DEFAULT_SERVER_URL = "http://YOUR_EC2_IP"`
4. Save the file
5. Run it: `python smartedu_tray.py`

---

## Part 15: View Logs (Troubleshooting)

If something doesn't work, check the logs:

### Application Logs:
```bash
# View last 50 lines
sudo journalctl -u smartedu -n 50

# Follow logs in real-time (press Ctrl+C to stop)
sudo journalctl -u smartedu -f

# View error log file
sudo tail -f /var/log/smartedu-error.log

# View access log
sudo tail -f /var/log/smartedu-access.log
```

### Nginx Logs:
```bash
# Error log
sudo tail -f /var/log/nginx/error.log

# Access log
sudo tail -f /var/log/nginx/access.log
```

---

## Part 16: Common Commands You'll Need

### Restart the App:
```bash
sudo systemctl restart smartedu
```

### Stop the App:
```bash
sudo systemctl stop smartedu
```

### Start the App:
```bash
sudo systemctl start smartedu
```

### Check App Status:
```bash
sudo systemctl status smartedu
```

### Update Code (if you make changes):
```bash
# On your local computer:
# 1. Make your changes
# 2. Commit and push to GitHub
git add .
git commit -m "Description of your changes"
git push

# On EC2, pull the latest changes:
ssh -i aws-key.pem ubuntu@YOUR_EC2_IP
cd /home/ubuntu/smartedu
git pull

# If you changed Python dependencies, reinstall:
source venv/bin/activate
pip install -r requirements.txt

# Restart the service
sudo systemctl restart smartedu
```

### Check if Ports are Open:
```bash
# Check what's listening on port 8000
sudo lsof -i :8000

# Check what's listening on port 80
sudo lsof -i :80
```

---

## Troubleshooting Common Issues

### Issue -1: "You have exceeded your quota" when creating EC2

**Meaning:** AWS limits on new accounts or free tier exhausted

**Solution:**
1. Go to AWS Console → **Service Quotas**
2. Check your EC2 limits for the region
3. Options:
   - Try a different region (top-right dropdown)
   - Request quota increase (takes 24-48 hours)
   - Stop/terminate unused instances
   - Upgrade to paid tier if needed

### Issue 0: Can't connect to EC2 - "Connection timeout"

**Solution:**
1. Check Security Group has SSH (port 22) open
2. Check your instance is **Running** (not Stopped)
3. Verify you're using the correct Public IP
4. Check your internet connection
5. If using "My IP" in security group, your IP might have changed - update it

### Issue 0.5: "Permission denied" when git cloning from GitHub

**Meaning:** GitHub repository is private and EC2 can't access it

**Solution Option A - Make repo public (easiest for hackathon):**
1. Go to your GitHub repository
2. Click **Settings** → **Danger Zone**
3. Click "Change visibility" → "Make public"
4. Now retry: `git clone https://github.com/YOUR_USERNAME/smartedu.git`

**Solution Option B - Use SSH keys (more secure):**
```bash
# On EC2, generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter 3 times (accept defaults)

# Display public key
cat ~/.ssh/id_ed25519.pub
# Copy the entire output

# Add to GitHub:
# 1. Go to GitHub → Settings → SSH and GPG keys
# 2. Click "New SSH key"
# 3. Paste the key
# 4. Save

# Now clone using SSH format:
git clone git@github.com:YOUR_USERNAME/smartedu.git
```

### Issue 1: "Connection Refused" when opening in browser

**Solution:**
```bash
# Check if Nginx is running
sudo systemctl status nginx

# Check if Gunicorn is running
sudo systemctl status smartedu

# Restart both
sudo systemctl restart nginx
sudo systemctl restart smartedu
```

### Issue 2: App won't start

**Solution:**
```bash
# Check error logs
sudo journalctl -u smartedu -n 100

# Common issues:
# - Missing .env file
# - Wrong Python path
# - Missing dependencies
```

### Issue 3: "502 Bad Gateway" in browser

**Meaning:** Nginx is working but can't connect to your Flask app

**Solution:**
```bash
# Check if Gunicorn is running on port 8000
curl http://localhost:8000

# If it doesn't respond, check Gunicorn logs
sudo journalctl -u smartedu -f
```

### Issue 4: Can't upload files

**Solution:**
```bash
# Create uploads directory
cd /home/ubuntu/smartedu
mkdir -p uploads/timetables
mkdir -p frontend/static/profile_pics

# Set permissions
chmod -R 755 uploads
chmod -R 755 frontend/static/profile_pics

# Restart app
sudo systemctl restart smartedu
```

### Issue 5: Database errors

**Solution:**
```bash
# Recreate database
cd /home/ubuntu/smartedu
source venv/bin/activate
rm users.db
python3 -c "from database import DatabaseHelper; DatabaseHelper()"

# Restart app
sudo systemctl restart smartedu
```

---

## Important Notes

### 1. Your EC2 Public IP Might Change!

If you stop and start your EC2 instance, the public IP will change!

**Solution - Allocate an Elastic IP (permanent IP):**

1. Go to EC2 Console → **Elastic IPs** (left menu)
2. Click **Allocate Elastic IP address**
3. Click **Allocate**
4. Select the new Elastic IP
5. Click **Actions** → **Associate Elastic IP address**
6. Select your instance (smartedu-server)
7. Click **Associate**

Now your IP won't change! ✓

**Note:** Elastic IPs are free when associated with a running instance, but cost ~$0.005/hour if not used!

### 2. Don't Lose Your .pem/.ppk File!

**Without it, you can't connect to the server!**

**What to do:**
- ✅ Keep it safe in a secure folder
- ✅ Make a backup copy (on USB drive, cloud, etc.)
- ❌ Don't share it with anyone
- ❌ Don't upload it to GitHub!
- ❌ Don't email it

**If you lose it:**
Unfortunately, you CANNOT get it back. You'll need to:
1. Create a new key pair
2. Stop your instance
3. Detach the volume, attach to another instance
4. Add new public key to `~/.ssh/authorized_keys`
5. Or easier: create a new instance and redeploy

**Pro tip:** Create a backup key pair now:
- EC2 Console → Key Pairs → Create key pair
- Name: `smartedu-key-backup`
- Download and save securely
- Connect to EC2 and add this public key too

### 3. Monitor Your AWS Costs

**Set up billing alerts to avoid surprise charges!**

1. Go to: https://console.aws.amazon.com/billing/
2. Click **Billing preferences** (left menu)
3. Enable: **Receive Billing Alerts** ✓
4. Save preferences
5. Go to CloudWatch: https://console.aws.amazon.com/cloudwatch/
6. Change region to **US East (N. Virginia)** (top-right) - billing is only here!
7. Click **Alarms** → **Create alarm**
8. Click **Select metric** → **Billing** → **Total Estimated Charge**
9. Set threshold: `$5` (or your limit)
10. Set up email notification
11. Create alarm

**You'll get an email if your bill exceeds $5!**

**Typical costs for SmartEdu:**
- EC2 t2.micro (free tier): $0
- EC2 t2.micro (after free tier): ~$8/month
- Bedrock Claude API calls: ~$0.01-0.05 per study plan generated
- Storage 20GB: Free
- Data transfer (first 100GB): Free

**Expected total for hackathon (1-2 weeks):** $0-5

### 4. Keep Your Server Secure

```bash
# Update packages regularly (do this every few weeks)
sudo apt update && sudo apt upgrade -y

# Only allow SSH from your IP in Security Group (more secure)
# Don't share your .pem file
# Use strong passwords for your app users
# Keep your AWS access keys secret (never commit to GitHub!)
```

**Security best practices:**
- ✅ Use "My IP" for SSH in security group (not 0.0.0.0/0)
- ✅ Keep `.env` out of GitHub
- ✅ Rotate AWS access keys every 90 days
- ✅ Enable MFA on your AWS account
- ✅ Use HTTPS (Let's Encrypt) for production
- ❌ Don't run as root user
- ❌ Don't expose database ports (3306, 5432, 27017)
- ❌ Don't disable the firewall

---

## For Your Hackathon Submission

**Your Demo Link:**
```
http://YOUR_EC2_PUBLIC_IP
```

**Test Credentials** (create a demo account):
1. Register a new user: `demo` / `demo@example.com` / `demo123`
2. Share these credentials with judges

**What to Show:**
1. Working website
2. AI-generated study plans
3. Session tracking
4. Browser extension (optional)
5. Desktop app (optional)

---

## Quick Reference Card

Save this for quick access:

### Basic Commands:
```bash
# Connect to EC2
ssh -i smartedu-key.pem ubuntu@YOUR_EC2_IP

# Navigate to project
cd /home/ubuntu/smartedu
source venv/bin/activate

# Restart app
sudo systemctl restart smartedu

# View logs
sudo journalctl -u smartedu -f

# Check status
sudo systemctl status smartedu
sudo systemctl status nginx

# Get public IP
curl http://checkip.amazonaws.com
```

### GitHub Workflow (Making Updates):

**On your local computer:**
```bash
# 1. Make your code changes
# 2. Test locally first!

# 3. Commit and push
git add .
git commit -m "Brief description of changes"
git push
```

**On EC2 server:**
```bash
# 1. Connect to EC2
ssh -i smartedu-key.pem ubuntu@YOUR_EC2_IP

# 2. Navigate to project
cd /home/ubuntu/smartedu

# 3. Pull latest changes
git pull

# 4. If you changed requirements.txt:
source venv/bin/activate
pip install -r requirements.txt

# 5. If you changed database schema:
python3 -c "from database import DatabaseHelper; DatabaseHelper()"

# 6. Restart the app
sudo systemctl restart smartedu

# 7. Check if it worked
sudo systemctl status smartedu
```

### Emergency Rollback:
```bash
# If new code broke something, rollback to previous version
cd /home/ubuntu/smartedu
git log --oneline  # See recent commits
git reset --hard COMMIT_HASH  # Replace COMMIT_HASH with previous working version
sudo systemctl restart smartedu
```

---

## Managing Your EC2 Instance (Start/Stop to Save Money)

**If you're not using the server 24/7, stop it to save money!**

### How to Stop Your Instance:

1. Go to EC2 Console: https://console.aws.amazon.com/ec2/
2. Select your instance (smartedu-server)
3. Click **Instance state** → **Stop instance**
4. Confirm

**What happens when stopped:**
- ✅ Your code and data are preserved
- ✅ You stop paying for compute time
- ✅ You only pay for storage (~$2/month for 20GB)
- ❌ Your website goes offline
- ❌ Your public IP changes (unless you use Elastic IP)

### How to Start Your Instance Again:

1. Go to EC2 Console
2. Select your instance
3. Click **Instance state** → **Start instance**
4. Wait 1-2 minutes
5. Check the new Public IP (if not using Elastic IP)
6. Your website is back online!

**Cost Comparison:**
- **Running 24/7**: ~$8-10/month (after free tier)
- **Running only during demos**: ~$2-3/month
- **Stopped when not in use**: ~$2/month (just storage)

**Pro tip for hackathon:**
- Keep it running during the hackathon event
- Stop it after the hackathon ends
- Start it only when you need to demo

### How to Terminate (Delete) Your Instance:

**⚠️ WARNING: This permanently deletes everything! Cannot be undone!**

Only do this when you're completely done:

1. **Backup important data first!**
   ```bash
   # Download database
   scp -i smartedu-key.pem ubuntu@YOUR_EC2_IP:/home/ubuntu/smartedu/users.db ./backup/
   
   # Download uploaded files
   scp -i smartedu-key.pem -r ubuntu@YOUR_EC2_IP:/home/ubuntu/smartedu/uploads ./backup/
   ```

2. Go to EC2 Console
3. Select your instance
4. Click **Instance state** → **Terminate instance**
5. Type "terminate" to confirm
6. Everything is deleted

**Don't forget to also:**
- Release Elastic IP (if you allocated one) - or you'll keep paying!
- Delete unused snapshots/volumes
- Delete IAM users you created
- Remove Bedrock model access if not needed

---

## Next Steps After Hackathon

1. **Add a domain name** (optional)
   - Use a free service like DuckDNS.org
   - Point it to your EC2 IP

2. **Add HTTPS** (optional)
   - Use Let's Encrypt (free SSL)
   - Makes your site secure

3. **Monitor your app**
   - Set up CloudWatch (AWS monitoring)
   - Get alerts if something breaks

---

## Need Help?

**Common places to get help:**
1. Check the logs first (most errors are explained there)
2. Google the error message
3. Ask your advisor
4. Stack Overflow
5. AWS Documentation

**Useful AWS Documentation:**
- EC2 Getting Started: https://docs.aws.amazon.com/ec2/
- Security Groups: https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html

---

## Congratulations! 🎉

If you made it this far, your app should be live on the internet!

**Your demo link:** `http://YOUR_EC2_PUBLIC_IP`

Good luck with your hackathon! 🚀
