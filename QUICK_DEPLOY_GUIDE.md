# Quick Deploy Guide - SmartEdu on AWS EC2
## For Hackathon Demo (30 minutes setup!)

---

## 🎯 What You Need

- AWS Account (free tier works!)
- Your SmartEdu code on your laptop
- 30-45 minutes

---

## 📋 Quick Steps Overview

```
1. Push code to GitHub (5 min)
2. Create EC2 instance (5 min)
3. Connect & clone code (5 min)
4. Setup & run (15 min)
5. Test your demo! (5 min)
```

---

## Step 1: Push to GitHub (5 min)

### Check .gitignore first:
```bash
cd C:\Users\User\Downloads\version_24_AUTO_planning+replanning

# Make sure .env is NOT tracked
cat .gitignore | grep ".env"
```

### Push to GitHub:
```bash
# If not initialized yet
git init
git add .
git commit -m "Ready for deployment"

# Create repo on GitHub (https://github.com/new)
# Name it: aegis-SmartEdu

# Push
git remote add origin https://github.com/YOUR_USERNAME/aegis-SmartEdu.git
git branch -M main
git push -u origin main
```

**Make repo public** (easier for demo) - Settings → Change visibility

---

## Step 2: Create EC2 Instance (5 min)

### 2.1 Launch Instance
1. Go to: https://console.aws.amazon.com/ec2/
2. Click **"Launch Instance"** (orange button)

### 2.2 Configure (Quick Settings):
```
Name: smartedu-demo

OS: Ubuntu Server 24.04 LTS (Free tier)

Instance type: t2.micro (Free tier)

Key pair: 
  - Click "Create new key pair"
  - Name: smartedu-key
  - Type: RSA
  - Format: .pem (or .ppk for Windows PuTTY)
  - Download and SAVE IT!

Network Settings → Edit:
  ✓ SSH (port 22)
  ✓ HTTP (port 80) - Source: Anywhere
  ✓ HTTPS (port 443) - Source: Anywhere

Storage: 20 GB
```

3. Click **"Launch Instance"**
4. Wait 1 minute for it to start
5. **Copy the Public IP** (looks like: 54.123.45.67)

---

## Step 3: Connect to EC2 (5 min)

### Windows (PowerShell):
```bash
cd C:\Users\User\Downloads
# (wherever you saved your .pem file)

# Set permissions
icacls smartedu-key.pem /inheritance:r
icacls smartedu-key.pem /grant:r "$($env:USERNAME):(R)"

# Connect (replace with YOUR IP)
ssh -i smartedu-key.pem ubuntu@YOUR_EC2_IP
```

### If asked about fingerprint, type: `yes`

You should see: `ubuntu@ip-xxx:~$`

---

## Step 4: Setup on EC2 (15 min)

**Copy and paste these commands** (all at once is fine):

```bash
# Update system
sudo apt update -y && sudo apt upgrade -y

# Install Python 3, Nginx, Git
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx git

# Clone your code
cd ~
git clone https://github.com/YOUR_USERNAME/aegis-SmartEdu.git
cd aegis-SmartEdu

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create .env file
nano .env
```

**Paste this into .env** (update AWS keys!):
```env
SECRET_KEY=hackathon-demo-key-12345
FLASK_ENV=production

# AWS Bedrock - GET THESE FROM AWS CONSOLE!
AWS_ACCESS_KEY_ID=your-key-here
AWS_SECRET_ACCESS_KEY=your-secret-here
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

BEDROCK_MAX_TOKENS=12000
BEDROCK_RETRY_MAX_TOKENS=18000
USE_MOCK_LLM=0
```

**Save:** `Ctrl+O`, `Enter`, `Ctrl+X`

```bash
# Initialize database
python3 -c "from database import DatabaseHelper; DatabaseHelper()"

# Create upload directories
mkdir -p uploads/timetables frontend/static/profile_pics

# Configure Nginx
sudo nano /etc/nginx/sites-available/aegis-smartedu
```

**Paste this Nginx config:**
To receives and forwards all HTTP requests (the "gateway")
```nginx
server {
    listen 80;
    server_name _;
    client_max_body_size 20M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /home/ubuntu/aegis-SmartEdu/frontend/static;
    }
}
```

**Save:** `Ctrl+O`, `Enter`, `Ctrl+X`

```bash
# Enable Nginx config
sudo ln -s /etc/nginx/sites-available/aegis-smartedu /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Create Gunicorn service

# Gunicorn make to run your Flask app as a production server
# Manages multiple worker processes
# Keeps your app running continuously
sudo nano /etc/systemd/system/aegis-smartedu.service
```

**Paste this service config:**
```ini
[Unit]
Description=SmartEdu Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/aegis-SmartEdu
Environment="PATH=/home/ubuntu/aegis-SmartEdu/venv/bin"
ExecStart=/home/ubuntu/aegis-SmartEdu/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8000 --timeout 120 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**Save:** `Ctrl+O`, `Enter`, `Ctrl+X`

```bash
# Start the service
sudo systemctl daemon-reload
sudo systemctl enable aegis-smartedu
sudo systemctl start aegis-smartedu

# Check if it's running
sudo systemctl status aegis-smartedu
```

Should see: `Active: active (running)` in green ✓

---

## Step 5: Get AWS Bedrock Keys (10 min)

### 5.1 Create IAM User:
1. Go to: https://console.aws.amazon.com/iam/
2. Users → Create user
3. Name: `smartedu-bedrock`
4. Next → Attach policies directly
5. Search and select: **AmazonBedrockFullAccess**
6. Create user
7. Click on user → Security credentials → Create access key
8. Use case: **Application running outside AWS**
9. Create → **COPY THE KEYS!**

### 5.2 Enable Bedrock Models:
1. Go to: https://console.aws.amazon.com/bedrock/
2. Left menu → **Model access**
3. Click **Manage model access**
4. Enable:
   - ✓ Claude 3.5 Sonnet v2
   - ✓ Claude 3.5 Sonnet
   - ✓ Claude 3 Haiku
5. Request access (usually instant)

### 5.3 Update .env:
```bash
# Back on EC2
cd ~/aegis-SmartEdu
nano .env

# Update these lines with your actual keys:
AWS_ACCESS_KEY_ID=AKIA..................
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxx...
```

**Save and restart:**
```bash
sudo systemctl restart aegis-smartedu
```

---

## 🎉 Test Your Demo!

### Open in browser:
```
http://YOUR_EC2_IP
```

### Test these features:
1. ✓ Register new user
2. ✓ Login
3. ✓ Upload timetable
4. ✓ Generate study plan (tests Bedrock!)
5. ✓ Track session

---

## 🔧 Quick Commands

### View logs:
```bash
sudo journalctl -u aegis-smartedu -f
```

### Restart app:
```bash
sudo systemctl restart aegis-smartedu
```

### Update code:
```bash
# On your laptop
git add .
git commit -m "Updates"
git push

# On EC2
cd ~/aegis-SmartEdu
git pull
sudo systemctl restart aegis-smartedu
```

---

## ❗ Troubleshooting

### App won't start?
```bash
# Check logs
sudo journalctl -u aegis-smartedu -n 50

# Common fixes:
cd ~/aegis-SmartEdu
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart aegis-smartedu
```

### Can't connect to website?
```bash
# Check if services are running
sudo systemctl status aegis-smartedu
sudo systemctl status nginx

# Restart both
sudo systemctl restart nginx
sudo systemctl restart aegis-smartedu
```

### "502 Bad Gateway"?
```bash
# Gunicorn might not be running on port 8000
curl http://localhost:8000
sudo systemctl restart aegis-smartedu
```

---

## 💰 After Your Demo

### Stop instance to save money:
1. EC2 Console → Instances
2. Select instance → Instance state → Stop

**Costs nothing when stopped!** (just ~$2/month for storage)

### Start again:
1. Instance state → Start
2. **Note:** Public IP will change! (unless you use Elastic IP)

### Delete everything:
1. **Backup first!** Download your database:
   ```bash
   scp -i smartedu-key.pem ubuntu@YOUR_IP:/home/ubuntu/aegis-SmartEdu/users.db ./
   ```
2. EC2 Console → Terminate instance

---

## 📝 Demo Script for Advisors

**Your demo link:** `http://YOUR_EC2_IP`

**What to show:**
1. "Here's our live web app deployed on AWS EC2"
2. Register → Login
3. Upload timetable (PDF/Excel)
4. Generate AI study plan (powered by AWS Bedrock Claude)
5. Track study session
6. Show browser extension (optional)

**Tech highlights:**
- Flask backend, SQLite database
- AWS Bedrock for AI (Claude 3.5 Sonnet)
- Nginx + Gunicorn production setup
- GitHub for version control
- Responsive design

---

## 🎯 Your Demo Info

```
Demo URL: http://_________________
Test User: demo@example.com
Password: demo123

GitHub: https://github.com/YOUR_USERNAME/aegis-SmartEdu
Tech Stack: Python, Flask, AWS Bedrock (Claude), SQLite
```

**Good luck with your hackathon! 🚀**
