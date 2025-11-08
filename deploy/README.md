# Deployment Guide

This directory contains deployment configuration files for the omislisi-accounting dashboard.

## Files

- `nginx.conf` - Nginx configuration template for serving the static dashboard
- `production/htpasswd` - SOPS-encrypted HTTP Basic Auth password file

## Initial Setup

### 1. Install Fabric

```bash
pip install fabric
```

### 2. Create HTTP Basic Auth Users

First, create an unencrypted htpasswd file:

```bash
# Create the production directory if it doesn't exist
mkdir -p deploy/production

# Create htpasswd file with first user
htpasswd -c deploy/production/htpasswd username

# Add additional users (without -c flag)
htpasswd deploy/production/htpasswd another_user
```

Then encrypt it with SOPS:

```bash
fab encrypt_htpasswd
```

Or manually:

```bash
sops --encrypt --in-place deploy/production/htpasswd
```

### 3. Initial Server Setup

Run the initial setup on the server:

```bash
fab web setup
```

This will:
- Deploy nginx configuration
- Set up SSL certificate via Let's Encrypt
- Upload HTTP Basic Auth password file
- Reload nginx

## Deployment Workflow

### Deploy to Server

```bash
fab web deploy
```

This will:
- Generate dashboard locally (from your transaction data)
- Sync dashboard files to server
- Reload nginx

**Note:** The dashboard is automatically generated as part of the deployment process. You don't need to run `oa generate-dashboard` separately.

## Managing Users

### Add a New User

```bash
fab add_user:username
```

This will:
- Decrypt htpasswd file
- Add the user (will prompt for password)
- Re-encrypt the file

### Edit Users Manually

```bash
fab edit_htpasswd
```

This opens the encrypted htpasswd file in your editor (VS Code by default).

## SSL Certificate Management

### Set Up Certificate (Initial Setup)

```bash
fab web setup_certbot
```

### Renew Certificates

```bash
fab web renew_certbot
```

Note: Certificates are typically renewed automatically via cron on the server.

## Troubleshooting

### Dashboard Generation Fails

If dashboard generation fails during deployment, check:
- Virtual environment is activated (if needed)
- `oa` command is available in PATH
- Transaction data files are accessible
- `config.yaml` is properly configured

You can also generate the dashboard manually first to debug:

```bash
oa generate-dashboard --output-dir ./dashboard
fab web sync_dashboard
fab web nginxreload
```

### Permission Errors

If you encounter permission errors, ensure SSH keys are set up correctly and you have sudo access on the server.

### Nginx Configuration Issues

Test nginx configuration:

```bash
fab web nginxconfig  # Deploy config
fab web nginxreload  # Reload nginx
```

### HTTP Basic Auth Not Working

Ensure the htpasswd file is set up:

```bash
fab web setup_htpasswd
```

## Server Details

- **Server**: web.omisli.si
- **User**: omislisi
- **Subdomain**: fin.omisli.si
- **Web Directory**: `/home/omislisi/fin.omisli.si`
- **Nginx Config**: `/etc/nginx/sites-enabled/fin-omislisi.conf`
- **htpasswd File**: `/etc/nginx/htpasswd-fin`

