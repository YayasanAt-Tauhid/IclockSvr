# Setup Lokal Windows - iClock Server

## Prasyarat

**PENTING**: Anda memerlukan **Python 3.8 atau lebih tinggi**

### Cek Python yang Terinstall

Buka Command Prompt atau PowerShell:
```cmd
python --version
```

Jika menampilkan "Python 2.x" atau error, silakan install Python 3.

### Download Python 3

1. Kunjungi: https://www.python.org/downloads/
2. Download **Python 3.11** atau **3.10** (recommended)
3. Jalankan installer
4. **PENTING**: ✅ Centang **"Add Python to PATH"**
5. Klik "Install Now"

## Instalasi Otomatis (Recommended)

### Cara Tercepat:

1. Buka **Command Prompt** atau **PowerShell** sebagai Administrator
2. Masuk ke folder aplikasi:
   ```cmd
   cd C:\iclockSvr\linux_version
   ```
3. Jalankan setup script:
   ```cmd
   setup-windows.bat
   ```
4. Ikuti petunjuk untuk membuat admin user
5. Selesai! 🎉

## Instalasi Manual

Jika ingin install manual:

### 1. Buat Virtual Environment
```cmd
cd C:\iclockSvr\linux_version
python -m venv venv
```

### 2. Aktivasi Virtual Environment
```cmd
venv\Scripts\activate
```
Anda akan melihat `(venv)` di awal prompt.

### 3. Install Dependencies
```cmd
pip install -r requirements-dev.txt
```

### 4. Setup Environment
```cmd
copy .env.dev .env
```

### 5. Buat Database
```cmd
python manage.py makemigrations
python manage.py migrate
```

### 6. Buat Admin User
```cmd
python manage.py createsuperuser
```
Masukkan:
- Username: `admin`
- Email: `admin@example.com`
- Password: (password pilihan Anda)

### 7. Collect Static Files
```cmd
python manage.py collectstatic --noinput
```

### 8. Jalankan Server
```cmd
python manage.py runserver
```

## Akses Aplikasi

Setelah server berjalan:

### 🌐 Web Interface
- **Login Page**: http://127.0.0.1:8000/
- **Dashboard**: http://127.0.0.1:8000/dashboard/

### 🔧 Admin Panel Django
- **Admin URL**: http://127.0.0.1:8000/admin/
- Login dengan user yang dibuat tadi

### 📡 API Endpoints
- **Base URL**: http://127.0.0.1:8000/api/
- **Login**: http://127.0.0.1:8000/api/auth/login/
- **Users**: http://127.0.0.1:8000/api/auth/users/
- **Devices**: http://127.0.0.1:8000/api/devices/
- **Attendance**: http://127.0.0.1:8000/api/attendance/

## Testing dengan Browser

### 1. Login ke Dashboard
1. Buka: http://127.0.0.1:8000/
2. Masukkan username dan password
3. Anda akan diarahkan ke dashboard

### 2. Login ke Admin Panel
1. Buka: http://127.0.0.1:8000/admin/
2. Login dengan kredensial superuser
3. Eksplorasi fitur:
   - User Management
   - Device Management
   - Attendance Records
   - Leave Requests

## Testing dengan API

### Login via API (PowerShell)
```powershell
$body = @{
    username = "admin"
    password = "yourpassword"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/login/" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

$token = $response.token
echo "Token: $token"
```

### Create User via API
```powershell
$headers = @{
    "Authorization" = "Token $token"
    "Content-Type" = "application/json"
}

$body = @{
    username = "employee1"
    email = "emp1@company.com"
    password = "pass123"
    employee_id = "EMP001"
    role = "user"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/users/" `
    -Method POST `
    -Headers $headers `
    -Body $body
```

## Troubleshooting

### Error: Python tidak ditemukan
**Solusi**: Install Python 3 dan pastikan "Add to PATH" dicentang

### Error: pip tidak ditemukan
**Solusi**: 
```cmd
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

### Error: Module tidak ditemukan
**Solusi**: Pastikan virtual environment aktif
```cmd
venv\Scripts\activate
pip install -r requirements-dev.txt
```

### Error: Port sudah digunakan
**Solusi**: Gunakan port lain
```cmd
python manage.py runserver 8001
```

### Database error
**Solusi**: Hapus database dan buat ulang
```cmd
del db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Static files tidak muncul
**Solusi**:
```cmd
python manage.py collectstatic --clear --noinput
```

## Menghentikan Server

Tekan `Ctrl + C` di terminal untuk menghentikan server.

## Menjalankan Ulang

Setelah setup awal, untuk menjalankan server:

```cmd
cd C:\iclockSvr\linux_version
venv\Scripts\activate
python manage.py runserver
```

## Fitur yang Bisa Dicoba

### ✅ User Management
1. Buat user baru via admin panel
2. Set role (Admin/Manager/User)
3. Edit profile user
4. Non-aktifkan user

### ✅ Device Management
1. Tambah device baru
2. Set IP address dan port
3. Monitor status device
4. View device logs

### ✅ Attendance
1. Buat attendance record manual
2. View daily attendance
3. Generate reports
4. Approve attendance

### ✅ Leave Requests
1. Submit leave request
2. Approve/reject sebagai manager
3. View leave history

## Quick Commands

```cmd
# Aktivasi venv
venv\Scripts\activate

# Run server
python manage.py runserver

# Create admin
python manage.py createsuperuser

# Reset database
del db.sqlite3
python manage.py migrate

# View routes
python manage.py show_urls

# Django shell
python manage.py shell

# Check for errors
python manage.py check
```

## Development Tips

### Auto-reload
Server akan otomatis reload saat ada perubahan file Python.

### Debug Mode
Saat `DEBUG=True`, error akan ditampilkan detail di browser.

### Database Browser
Gunakan tools seperti **DB Browser for SQLite** untuk melihat database:
- Download: https://sqlitebrowser.org/

### API Testing
Gunakan **Postman** atau **Thunder Client** (VS Code extension) untuk test API.

## Struktur Database

Setelah migrasi, database akan memiliki tabel:
- `users` - Data user
- `user_profiles` - Profile user
- `devices` - Data device attendance
- `device_users` - User yang terdaftar di device
- `attendance_records` - Record attendance
- `daily_attendance` - Summary harian
- `leave_requests` - Pengajuan cuti

## Next Steps

Setelah berhasil run:
1. ✅ Eksplorasi admin panel
2. ✅ Buat beberapa user test
3. ✅ Tambah device dummy
4. ✅ Test API dengan Postman
5. ✅ Coba fitur leave management

---
**Happy coding!** 🚀

Jika ada masalah, cek file logs di folder `logs/` atau jalankan dengan `DEBUG=True`.
