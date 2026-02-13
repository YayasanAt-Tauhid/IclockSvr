# Deployment Guide - iClock Server Linux Edition

## Quick Start (Ubuntu 20.04+)

```bash
# 1. Download the installation script
wget https://your-server.com/install.sh

# 2. Make it executable
chmod +x install.sh

# 3. Run installation (as root)
sudo ./install.sh

# 4. Follow the prompts to create superuser
```

## Manual Installation

### Step 1: System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv \
    postgresql postgresql-contrib \
    nginx redis-server \
    git build-essential libpq-dev
```

### Step 2: Database Setup

```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres psql << EOF
CREATE DATABASE iclock_db;
CREATE USER iclock_user WITH PASSWORD 'your_password_here';
ALTER ROLE iclock_user SET client_encoding TO 'utf8';
ALTER ROLE iclock_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE iclock_user SET timezone TO 'Asia/Jakarta';
GRANT ALL PRIVILEGES ON DATABASE iclock_db TO iclock_user;
\q
EOF
```

### Step 3: Application Setup

```bash
# Create application directory
sudo mkdir -p /opt/iclock_server
cd /opt/iclock_server

# Copy application files here
# (Upload or git clone your code)

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your settings
```

### Step 4: Database Migration

```bash
# Activate virtual environment
source /opt/iclock_server/venv/bin/activate
cd /opt/iclock_server

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Step 5: Systemd Service

```bash
# Copy service file
sudo cp deploy/iclock.service /etc/systemd/system/

# Create socket directory
sudo mkdir -p /run/iclock
sudo chown www-data:www-data /run/iclock

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable iclock
sudo systemctl start iclock

# Check status
sudo systemctl status iclock
```

### Step 6: Nginx Configuration

```bash
# Copy nginx config
sudo cp deploy/nginx.conf /etc/nginx/sites-available/iclock
sudo ln -s /etc/nginx/sites-available/iclock /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### Step 7: Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## SSL/TLS Setup (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
sudo certbot renew --dry-run
```

## Production Settings

### Recommended .env Configuration

```env
SECRET_KEY=generate-a-strong-random-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

DB_ENGINE=postgresql
DB_NAME=iclock_db
DB_USER=iclock_user
DB_PASSWORD=strong_password_here
DB_HOST=localhost
DB_PORT=5432

CACHE_BACKEND=redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

### Set Proper Permissions

```bash
sudo chown -R www-data:www-data /opt/iclock_server
sudo chmod -R 755 /opt/iclock_server
sudo chmod -R 775 /opt/iclock_server/media
sudo chmod -R 775 /opt/iclock_server/logs
```

## Maintenance Commands

### Service Management

```bash
# Start service
sudo systemctl start iclock

# Stop service
sudo systemctl stop iclock

# Restart service
sudo systemctl restart iclock

# View logs
sudo journalctl -u iclock -f

# Check status
sudo systemctl status iclock
```

### Database Backup

```bash
# Backup database
pg_dump -U iclock_user iclock_db > backup_$(date +%Y%m%d).sql

# Restore database
psql -U iclock_user iclock_db < backup_20240101.sql
```

### Application Updates

```bash
# Pull latest code
cd /opt/iclock_server
git pull

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart service
sudo systemctl restart iclock
```

## Monitoring

### Check Application Health

```bash
# Check if service is running
systemctl status iclock

# Check nginx status
systemctl status nginx

# Check Redis status
systemctl status redis

# Check PostgreSQL status
systemctl status postgresql

# View application logs
tail -f /var/log/iclock/iclock.log

# View nginx access logs
tail -f /var/log/nginx/iclock_access.log

# View nginx error logs
tail -f /var/log/nginx/iclock_error.log
```

### Performance Optimization

```bash
# Increase worker processes (edit service file)
sudo nano /etc/systemd/system/iclock.service
# Change --workers 4 to match CPU cores

# Reload service
sudo systemctl daemon-reload
sudo systemctl restart iclock
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u iclock -n 100

# Check configuration
source /opt/iclock_server/venv/bin/activate
cd /opt/iclock_server
python manage.py check

# Test manually
gunicorn iclock_server.wsgi:application
```

### Database Connection Issues

```bash
# Test database connection
psql -U iclock_user -d iclock_db -h localhost

# Check PostgreSQL status
sudo systemctl status postgresql

# View PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Permission Denied Errors

```bash
# Fix ownership
sudo chown -R www-data:www-data /opt/iclock_server

# Fix permissions
sudo chmod -R 755 /opt/iclock_server
sudo chmod -R 775 /opt/iclock_server/media
sudo chmod -R 775 /opt/iclock_server/logs
```

### Nginx 502 Bad Gateway

```bash
# Check if gunicorn is running
sudo systemctl status iclock

# Check socket file exists
ls -la /run/iclock/iclock.sock

# Restart both services
sudo systemctl restart iclock
sudo systemctl restart nginx
```

## Security Best Practices

1. **Change default passwords** immediately after installation
2. **Enable firewall** and only allow necessary ports
3. **Use SSL/TLS** certificates for production
4. **Regular backups** of database and media files
5. **Keep system updated** with security patches
6. **Monitor logs** for suspicious activity
7. **Use strong SECRET_KEY** in production
8. **Disable DEBUG** mode in production
9. **Limit database user** privileges
10. **Use fail2ban** to prevent brute force attacks

## Support

For issues or questions:
- Check logs first
- Review documentation
- Contact your system administrator

---
Last updated: 2024-01-05
