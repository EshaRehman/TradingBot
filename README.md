# 🧠 TradingView MailBot

A powerful email-based trading alert system that combines TradingView signals with OpenAI and Anthropic AI analysis.

## 🚀 Setup Instructions

### 1️⃣ Prerequisites

Make sure you have [Anaconda](https://www.anaconda.com/products/distribution) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed on your system.

### 2️⃣ Create Conda Environment

Open a terminal or PowerShell and run the following commands to create and activate your conda environment:

```bash
conda create -n mailbot_env python=3.10 -y
conda activate mailbot_env
```

### 3️⃣ Install Requirements

Install all necessary dependencies by running:

```bash
pip install -r requirements.txt
```
## Modifications in .env

### 4️⃣ Configure Environment Variables

#### API Keys
```env
# OpenAI API Key
OPENAI_API_KEY=""

# Anthropic API Key
ANTHROPIC_API_KEY=""
```

#### Email Configuration
```env
# Email sender address (your Gmail account)
EMAIL_SENDER=""

# Email receiver address (can be the same as sender)
EMAIL_RECEIVER=""

# Email password (App password from Gmail)
EMAIL_PASSWORD=""
```

### 5️⃣ Gmail App Password Setup

To generate an app password for Gmail:

1. Go to your Google Account settings
2. Navigate to Security > 2-Step Verification
3. Scroll down to "App passwords"
4. Select "Mail" and your device
5. Generate the password and copy it to your `.env` file

### 6️⃣ Run the Application

Start the UI by running:

```bash
python run_ui.py
``