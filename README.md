# iClock Server - Linux Edition

## Overview
Versi Linux dari iClock Server dengan fitur admin login untuk manajemen user dan device attendance system.

## Features
- ✅ Cross-platform (Linux compatible)
- ✅ Admin Dashboard dengan authentication
- ✅ User Management (CRUD)
- ✅ Device Management
- ✅ Attendance Tracking
- ✅ RESTful API
- ✅ Modern Web Interface
- ✅ Systemd Service Integration

## Technology Stack
- **Backend**: Django 3.2+ with Django REST Framework
- **Database**: PostgreSQL / MySQL
- **Frontend**: Modern HTML5 + CSS3 + Vanilla JavaScript
- **Cache**: Redis (optional, dengan fallback)
- **Web Server**: Gunicorn + Nginx

## System Requirements
### Minimum Requirements
- Ubuntu 20.04+ / Debian 10+ / CentOS 8+
- Python 3.8+
- 2GB RAM
- 10GB Disk Space

### Recommended
- Ubuntu 22.04 LTS
- Python 3.10+
- 4GB RAM
- 20GB Disk Space

## Installation

### 1. Install System Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv \
    postgresql postgresql-contrib \
    nginx redis-server \
    git build-essential libpq-dev

# CentOS/RHEL
sudo yum install -y python3 python3-pip \
    postgresql postgresql-server \
    nginx redis \
    git gcc postgresql-devel
```

### 2. Setup Database
```bash
# PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE iclock_db;
CREATE USER iclock_user WITH PASSWORD 'your_secure_password';
ALTER ROLE iclock_user SET client_encoding TO 'utf8';
ALTER ROLE iclock_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE iclock_user SET timezone TO 'Asia/Jakarta';
GRANT ALL PRIVILEGES ON DATABASE iclock_db TO iclock_user;
\q
EOF
```

### 3. Setup Application
```bash
# Clone or copy the application
cd /opt
sudo git clone <repository_url> iclock_server
# Or: sudo cp -r /path/to/iclock_server /opt/

cd /opt/iclock_server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit database credentials
```

### 4. Initialize Database
```bash
# Run migrations
python manage.py migrate

# Create superuser (Admin)
python manage.py createsuperuser

# Load initial data (optional)
python manage.py loaddata initial_data.json
```

### 5. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 6. Setup Systemd Service
```bash
# Copy service file
sudo cp deploy/iclock.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable iclock
sudo systemctl start iclock

# Check status
sudo systemctl status iclock
```

### 7. Setup Nginx
```bash
# Copy nginx configuration
sudo cp deploy/nginx.conf /etc/nginx/sites-available/iclock
sudo ln -s /etc/nginx/sites-available/iclock /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

## Configuration

### Environment Variables (.env)
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database
DB_ENGINE=postgresql
DB_NAME=iclock_db
DB_USER=iclock_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Cache (optional)
CACHE_BACKEND=redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# Security
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Usage

### Access Admin Panel
1. Open browser: `http://your-server-ip/admin/`
2. Login with superuser credentials
3. Manage users, devices, and attendance records

### Default Admin Account
After installation, create your admin account using:
```bash
python manage.py createsuperuser
```

### API Endpoints
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/users/` - List users (admin only)
- `POST /api/users/` - Create user (admin only)
- `GET /api/devices/` - List devices
- `POST /api/attendance/` - Submit attendance record
- `GET /api/attendance/` - Get attendance records

### Managing Services
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

## Default Ports
- **Web Interface**: 80 (HTTP) / 443 (HTTPS via Nginx)
- **Application**: 8000 (Gunicorn, internal)
- **Database**: 5432 (PostgreSQL)
- **Redis**: 6379

## Security Considerations

### 1. Change Default Credentials
Always change default database passwords and Django secret key.

### 2. Enable Firewall
```bash
# UFW (Ubuntu)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 3. SSL/TLS Certificate
```bash
# Using Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 4. Regular Updates
```bash
# Update system
sudo apt update && sudo apt upgrade

# Update Python packages
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## Troubleshooting

### Service Won't Start
```bash
# Check logs
sudo journalctl -u iclock -n 50

# Check permissions
sudo chown -R www-data:www-data /opt/iclock_server

# Check database connection
python manage.py dbshell
```

### Database Connection Issues
```bash
# Verify PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U iclock_user -d iclock_db
```

### Permission Issues
```bash
# Fix ownership
sudo chown -R www-data:www-data /opt/iclock_server

# Fix permissions
sudo chmod -R 755 /opt/iclock_server
sudo chmod -R 775 /opt/iclock_server/media
sudo chmod -R 775 /opt/iclock_server/static
```

## Backup and Restore

### Backup Database
```bash
# PostgreSQL
pg_dump -U iclock_user iclock_db > backup_$(date +%Y%m%d).sql

# MySQL
mysqldump -u iclock_user -p iclock_db > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
# PostgreSQL
psql -U iclock_user iclock_db < backup_20240101.sql

# MySQL
mysql -u iclock_user -p iclock_db < backup_20240101.sql
```

## Migration from Windows Version

### 1. Export Data
On Windows server:
```bash
python manage.py dumpdata > data_export.json
```

### 2. Transfer Data
Copy `data_export.json` to Linux server.

### 3. Import Data
On Linux server:
```bash
python manage.py loaddata data_export.json
```

## Support
For issues and support, please contact the development team.

## License
Proprietary - All rights reserved
