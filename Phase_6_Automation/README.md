# Groww Weekly Pulse - Automation

## Setup GitHub Actions

To ensure the automated GitHub Actions workflow runs successfully every week, you need to set up the following text variables as **Repository Secrets**.

1. Go to your GitHub Repository -> **Settings** tab.
2. On the left sidebar, click **Secrets and variables** -> **Actions**.
3. Under *Repository secrets*, click **New repository secret**.
4. Add the following keys with their corresponding values (same as your local `.env` file):

| Secret Name | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq LLM API Key |
| `EMAIL_SENDER` | The Gmail address sending the report (e.g., `catanya567@gmail.com`) |
| `EMAIL_PASSWORD` | The 16-character App Password for the Gmail account |
| `EMAIL_RECIPIENT` | The email address to receive the report |
| `EMAIL_RECIPIENT_NAME`| The name used in the email greeting |

Once these are set, GitHub Actions will safely inject these values into a temporary `.env` file whenever the scheduled pipeline runs!
