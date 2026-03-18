# OpenClaw Daily Usage Alert - Setup Guide

## Quick Start

1. Create a new GitHub repository
2. Copy all files from this folder to the repository
3. Configure secrets (see below)
4. The alert will run daily at 8:00 AM EST

## GitHub Repository Secrets

Go to your repo: **Settings > Secrets and variables > Actions > New repository secret**

Add these two secrets:

| Secret Name | Value |
|-------------|-------|
| `GMAIL_ADDRESS` | Your Gmail address (e.g., you@gmail.com) |
| `GMAIL_APP_PASSWORD` | Your 16-character Gmail App Password |

## Adjust Schedule

Edit the cron in `.github/workflows/daily-alert.yml`:

```yaml
schedule:
  - cron: '0 13 * * *'  # 8:00 AM EST (UTC-5)
```

Common times:
- `0 13 * * *` = 8:00 AM EST
- `0 14 * * *` = 9:00 AM EST
- `0 16 * * *` = 8:00 AM PST

## Test Manually

1. Go to your repo on GitHub
2. Click **Actions** tab
3. Select "OpenClaw Daily Usage Alert"
4. Click **Run workflow**

## Troubleshooting

- **SMTP auth failed**: Use a Gmail App Password, not your regular password. Enable 2FA first at myaccount.google.com/security.
- **Chart not found**: The page structure may have changed — adjust the `ancestor::div[3]` level in `scraper.py`.
- **Blank/wrong area captured**: Increase the `page.wait_for_timeout` value to give the chart more time to render.
