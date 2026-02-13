# API Documentation - iClock Server

Base URL: `http://your-server-ip/api/`

## Authentication

All API requests (except login/register) require authentication token in header:
```
Authorization: Token YOUR_AUTH_TOKEN
```

### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "role_display": "Administrator"
  },
  "message": "Login successful."
}
```

### Logout
```http
POST /api/auth/logout/
Authorization: Token YOUR_TOKEN
```

### Register (if enabled)
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepass123",
  "employee_id": "EMP001"
}
```

## User Management

### List Users
```http
GET /api/auth/users/
Authorization: Token YOUR_TOKEN
```

**Query Parameters:**
- `role`: Filter by role (admin, manager, user)
- `is_active`: Filter by active status (true, false)
- `department`: Filter by department
- `search`: Search username, email, employee_id

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "employee_id": "EMP001",
      "department": "IT",
      "phone": "+628123456789",
      "role": "user",
      "role_display": "Regular User",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Current User
```http
GET /api/auth/users/me/
Authorization: Token YOUR_TOKEN
```

### Create User
```http
POST /api/auth/users/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "username": "employee1",
  "email": "emp1@company.com",
  "password": "securepass123",
  "first_name": "Employee",
  "last_name": "One",
  "employee_id": "EMP002",
  "department": "Sales",
  "phone": "+628123456789",
  "role": "user"
}
```

### Update User
```http
PATCH /api/auth/users/{id}/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "department": "Marketing",
  "phone": "+628987654321"
}
```

### Change Password
```http
POST /api/auth/users/{id}/change_password/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "old_password": "oldpass123",
  "new_password": "newpass456",
  "confirm_password": "newpass456"
}
```

### Activate/Deactivate User
```http
POST /api/auth/users/{id}/activate/
Authorization: Token YOUR_TOKEN
```

## Device Management

### List Devices
```http
GET /api/devices/
Authorization: Token YOUR_TOKEN
```

**Query Parameters:**
- `status`: Filter by status (online, offline, maintenance)
- `is_active`: Filter by active status
- `device_type`: Filter by device type
- `search`: Search name, serial_number, ip_address

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "serial_number": "ZKT001",
      "name": "Main Entrance",
      "location": "Building A - Lobby",
      "ip_address": "192.168.1.100",
      "port": 4370,
      "device_type": "ZKTeco",
      "firmware_version": "6.60",
      "status": "online",
      "status_display": "Online",
      "last_online": "2024-01-05T12:00:00Z",
      "is_active": true
    }
  ]
}
```

### Create Device
```http
POST /api/devices/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "serial_number": "ZKT002",
  "name": "Back Entrance",
  "ip_address": "192.168.1.101",
  "port": 4370,
  "location": "Building A - Back Door",
  "device_type": "ZKTeco"
}
```

### Update Device
```http
PATCH /api/devices/{id}/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "status": "online",
  "firmware_version": "6.61"
}
```

### Ping Device
```http
POST /api/devices/{id}/ping/
Authorization: Token YOUR_TOKEN
```

**Response:**
```json
{
  "status": "online",
  "last_online": "2024-01-05T12:30:00Z"
}
```

### Get Device Logs
```http
GET /api/devices/{id}/logs/
Authorization: Token YOUR_TOKEN
```

## Attendance Records

### List Attendance Records
```http
GET /api/attendance/records/
Authorization: Token YOUR_TOKEN
```

**Query Parameters:**
- `user`: Filter by user ID
- `device`: Filter by device ID
- `verify_type`: Filter by verification type (0-4)
- `verify_code`: Filter by verification code (0=Check In, 1=Check Out)
- `is_processed`: Filter by processed status

**Response:**
```json
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_name": "john_doe",
      "device": 1,
      "device_name": "Main Entrance",
      "timestamp": "2024-01-05T08:00:00Z",
      "verify_type": 1,
      "verify_type_display": "Fingerprint",
      "verify_code": 0,
      "temperature": 36.5,
      "is_processed": true
    }
  ]
}
```

### Create Attendance Record
```http
POST /api/attendance/records/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "user": 1,
  "device": 1,
  "timestamp": "2024-01-05T08:00:00",
  "verify_type": 1,
  "verify_code": 0,
  "temperature": 36.5
}
```

### Bulk Create Records
```http
POST /api/attendance/records/bulk_create/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

[
  {
    "user": 1,
    "device": 1,
    "timestamp": "2024-01-05T08:00:00",
    "verify_type": 1,
    "verify_code": 0
  },
  {
    "user": 2,
    "device": 1,
    "timestamp": "2024-01-05T08:05:00",
    "verify_type": 1,
    "verify_code": 0
  }
]
```

## Daily Attendance

### List Daily Attendance
```http
GET /api/attendance/daily/
Authorization: Token YOUR_TOKEN
```

**Query Parameters:**
- `user`: Filter by user ID
- `date`: Filter by specific date (YYYY-MM-DD)
- `status`: Filter by status (present, late, absent, leave)
- `is_approved`: Filter by approval status

**Response:**
```json
{
  "count": 30,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_name": "john_doe",
      "user_employee_id": "EMP001",
      "date": "2024-01-05",
      "check_in": "2024-01-05T08:00:00Z",
      "check_out": "2024-01-05T17:00:00Z",
      "status": "present",
      "status_display": "Present",
      "work_hours": 9.0,
      "overtime_hours": 0.0,
      "late_minutes": 0,
      "is_approved": true
    }
  ]
}
```

### Approve Daily Attendance
```http
POST /api/attendance/daily/{id}/approve/
Authorization: Token YOUR_TOKEN
```

### Get Attendance Report
```http
GET /api/attendance/daily/report/
Authorization: Token YOUR_TOKEN
```

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `user_id`: User ID

**Response:**
```json
{
  "summary": {
    "total_days": 20,
    "present_days": 18,
    "late_days": 2,
    "absent_days": 0,
    "leave_days": 0,
    "total_late_minutes": 30,
    "total_work_hours": 180.0
  },
  "records": [...]
}
```

## Leave Requests

### List Leave Requests
```http
GET /api/attendance/leaves/
Authorization: Token YOUR_TOKEN
```

**Query Parameters:**
- `user`: Filter by user ID
- `leave_type`: Filter by type (annual, sick, personal, emergency)
- `status`: Filter by status (pending, approved, rejected)

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_name": "john_doe",
      "leave_type": "sick",
      "leave_type_display": "Sick Leave",
      "start_date": "2024-01-10",
      "end_date": "2024-01-12",
      "days_count": 3,
      "reason": "Common cold",
      "status": "pending",
      "status_display": "Pending",
      "reviewed_by": null,
      "created_at": "2024-01-09T10:00:00Z"
    }
  ]
}
```

### Create Leave Request
```http
POST /api/attendance/leaves/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "leave_type": "sick",
  "start_date": "2024-01-10",
  "end_date": "2024-01-12",
  "reason": "Medical treatment",
  "attachment": "base64_encoded_file"
}
```

### Approve Leave Request
```http
POST /api/attendance/leaves/{id}/approve/
Authorization: Token YOUR_TOKEN
```

### Reject Leave Request
```http
POST /api/attendance/leaves/{id}/reject/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "notes": "Reason for rejection"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "field_name": ["Error message for this field"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "error": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

## Rate Limiting

- **Anonymous requests**: 100/hour
- **Authenticated requests**: 1000/hour

## Pagination

List endpoints support pagination:
```
GET /api/auth/users/?page=2&page_size=20
```

## Filtering & Search

Most list endpoints support:
- **Filtering**: `?field_name=value`
- **Search**: `?search=query`
- **Ordering**: `?ordering=-created_at` (- for descending)

---
**API Version**: 1.0  
**Last Updated**: 2024-01-05
