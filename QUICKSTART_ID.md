# Panduan Cepat - iClock Server Linux Edition

## 🚀 Instalasi Cepat (Ubuntu/Debian)

### Opsi 1: Instalasi Otomatis (Direkomendasikan)

```bash
# 1. Download dan jalankan script instalasi
curl -sSL https://raw.githubusercontent.com/your-repo/iclock-server/main/install.sh | sudo bash

# 2. Ikuti petunjuk untuk membuat admin user
```

### Opsi 2: Instalasi Manual

```bash
# 1. Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv postgresql nginx redis-server git

# 2. Setup database
sudo -u postgres createdb iclock_db
sudo -u postgres createuser iclock_user -P

# 3. Clone/copy aplikasi
sudo mkdir -p /opt/iclock_server
cd /opt/iclock_server

# 4. Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Konfigurasi
cp .env.example .env
nano .env  # Edit sesuai kebutuhan

# 6. Migrasi database
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic

# 7. Setup service
sudo cp deploy/iclock.service /etc/systemd/system/
sudo cp deploy/nginx.conf /etc/nginx/sites-available/iclock
sudo ln -s /etc/nginx/sites-available/iclock /etc/nginx/sites-enabled/
sudo systemctl daemon-reload
sudo systemctl enable --now iclock nginx
```

## 📋 Akses Aplikasi

Setelah instalasi selesai:

### Admin Panel Django
- **URL**: http://your-server-ip/admin/
- **Login**: username dan password yang dibuat saat `createsuperuser`

Fitur admin panel:
- ✅ Manajemen User (CRUD)
- ✅ Manajemen Device
- ✅ Monitoring Attendance
- ✅ Approval Cuti/Leave
- ✅ Laporan Kehadiran

### Dashboard Web
- **URL**: http://your-server-ip/
- **Login**: Gunakan kredensial yang sama

Fitur dashboard:
- ✅ Statistik real-time
- ✅ Monitor attendance hari ini
- ✅ Daftar user dan device
- ✅ Recent activities

## 👥 Manajemen User

### Membuat User Baru

**Via Admin Panel:**
1. Login ke http://your-server-ip/admin/
2. Pilih "Users" → "Add User"
3. Isi form:
   - Username (required)
   - Email
   - Password
   - Role: Admin / Manager / User
   - Employee ID
   - Department
4. Klik "Save"

**Via Command Line:**
```bash
cd /opt/iclock_server
source venv/bin/activate
python manage.py createsuperuser  # Untuk admin
```

**Via API:**
```bash
curl -X POST http://your-server-ip/api/auth/users/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "employee1",
    "email": "employee1@company.com",
    "password": "securepass123",
    "employee_id": "EMP001",
    "department": "IT",
    "role": "user"
  }'
```

### Role & Permission

1. **Admin**: 
   - Full akses semua fitur
   - Bisa manage semua user
   - Approve/reject leave requests
   - Manage devices

2. **Manager**:
   - Manage user di department sendiri
   - Approve/reject leave untuk department
   - View reports department

3. **User**:
   - View attendance sendiri
   - Submit leave request
   - Update profile sendiri

## 📱 Manajemen Device

### Menambah Device Baru

**Via Admin Panel:**
1. Login → "Devices" → "Add Device"
2. Isi informasi:
   - Serial Number
   - Name
   - IP Address
   - Port (default: 4370)
   - Location
   - Device Type
3. Save

**Via API:**
```bash
curl -X POST http://your-server-ip/api/devices/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "serial_number": "ZKT001",
    "name": "Main Entrance",
    "ip_address": "192.168.1.100",
    "port": 4370,
    "location": "Building A - Lobby",
    "device_type": "ZKTeco"
  }'
```

## 📊 API Endpoints

### Authentication
```bash
# Login
POST /api/auth/login/
{
  "username": "admin",
  "password": "password"
}

# Logout
POST /api/auth/logout/
Header: Authorization: Token YOUR_TOKEN
```

### User Management
```bash
# List users
GET /api/auth/users/
Header: Authorization: Token YOUR_TOKEN

# Get current user
GET /api/auth/users/me/
Header: Authorization: Token YOUR_TOKEN

# Create user
POST /api/auth/users/
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "role": "user"
}

# Update user
PATCH /api/auth/users/{id}/
{
  "department": "Marketing"
}
```

### Device Management
```bash
# List devices
GET /api/devices/

# Get device detail
GET /api/devices/{id}/

# Update device status
POST /api/devices/{id}/ping/
```

### Attendance
```bash
# Submit attendance
POST /api/attendance/records/
{
  "user": 1,
  "device": 1,
  "timestamp": "2024-01-05T08:00:00",
  "verify_type": 1,
  "verify_code": 0
}

# Get daily attendance
GET /api/attendance/daily/

# Get attendance report
GET /api/attendance/daily/report/?start_date=2024-01-01&end_date=2024-01-31
```

### Leave Management
```bash
# Submit leave request
POST /api/attendance/leaves/
{
  "leave_type": "sick",
  "start_date": "2024-01-10",
  "end_date": "2024-01-12",
  "reason": "Sakit demam"
}

# Approve leave
POST /api/attendance/leaves/{id}/approve/

# Reject leave
POST /api/attendance/leaves/{id}/reject/
{
  "notes": "Alasan penolakan"
}
```

## 🔧 Perintah Maintenance

### Service Management
```bash
# Start
sudo systemctl start iclock

# Stop
sudo systemctl stop iclock

# Restart
sudo systemctl restart iclock

# Status
sudo systemctl status iclock

# View logs
sudo journalctl -u iclock -f
```

### Database Backup
```bash
# Backup
pg_dump -U iclock_user iclock_db > backup_$(date +%Y%m%d).sql

# Restore
psql -U iclock_user iclock_db < backup_20240105.sql
```

### Update Aplikasi
```bash
cd /opt/iclock_server
source venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart iclock
```

## 🔒 Keamanan

### Checklist Keamanan

- [ ] Ganti password database default
- [ ] Ganti SECRET_KEY di .env
- [ ] Set DEBUG=False di production
- [ ] Enable firewall (ufw/firewalld)
- [ ] Install SSL certificate
- [ ] Setup regular backup
- [ ] Monitor logs
- [ ] Update sistem secara berkala

### Setup SSL (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
sudo certbot renew --dry-run
```

## 📝 Troubleshooting

### Service tidak mau start
```bash
# Cek logs
sudo journalctl -u iclock -n 50

# Test manual
cd /opt/iclock_server
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### Cannot connect to database
```bash
# Cek PostgreSQL
sudo systemctl status postgresql

# Test koneksi
psql -U iclock_user -d iclock_db -h localhost
```

### Permission denied
```bash
# Fix ownership
sudo chown -R www-data:www-data /opt/iclock_server

# Fix permissions
sudo chmod -R 755 /opt/iclock_server
```

## 📞 Support

Untuk bantuan lebih lanjut:
1. Cek file logs di `/var/log/iclock/`
2. Review dokumentasi lengkap di `DEPLOYMENT.md`
3. Hubungi administrator sistem

---
**Versi**: 1.0.0  
**Tanggal**: 2024-01-05  
**Platform**: Ubuntu 20.04+, Debian 10+, CentOS 8+
