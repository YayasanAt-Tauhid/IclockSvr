// Dashboard functionality
(function () {
    'use strict';

    const authToken = localStorage.getItem('authToken');
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');

    // Redirect if not logged in
    if (!authToken) {
        window.location.href = '/';
        return;
    }

    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    // API fetch wrapper
    async function apiFetch(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Authorization': `Token ${authToken}`,
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        };

        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        const response = await fetch(endpoint, mergedOptions);

        if (response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('authToken');
            localStorage.removeItem('userData');
            window.location.href = '/';
            return null;
        }

        return response;
    }

    // Load user info
    function loadUserInfo() {
        const userName = document.getElementById('userName');
        const userRole = document.getElementById('userRole');
        const userAvatar = document.getElementById('userAvatar');

        if (userData.first_name && userData.last_name) {
            userName.textContent = `${userData.first_name} ${userData.last_name}`;
            userAvatar.textContent = userData.first_name.charAt(0).toUpperCase();
        } else if (userData.username) {
            userName.textContent = userData.username;
            userAvatar.textContent = userData.username.charAt(0).toUpperCase();
        }

        if (userData.role_display) {
            userRole.textContent = userData.role_display;
        }
    }

    // Load statistics
    async function loadStats() {
        try {
            // Load total users
            const usersResponse = await apiFetch('/api/auth/users/');
            if (usersResponse && usersResponse.ok) {
                const usersData = await usersResponse.json();
                document.getElementById('totalUsers').textContent = usersData.count || usersData.length || 0;
            }

            // Load total devices
            const devicesResponse = await apiFetch('/api/devices/');
            if (devicesResponse && devicesResponse.ok) {
                const devicesData = await devicesResponse.json();
                document.getElementById('totalDevices').textContent = devicesData.count || devicesData.results?.length || 0;
            }

            // Load today's attendance
            const today = new Date().toISOString().split('T')[0];
            const attendanceResponse = await apiFetch(`/api/attendance/daily/?date=${today}`);
            if (attendanceResponse && attendanceResponse.ok) {
                const attendanceData = await attendanceResponse.json();
                document.getElementById('todayAttendance').textContent = attendanceData.count || attendanceData.results?.length || 0;
            }

            // Load pending leaves
            const leavesResponse = await apiFetch('/api/attendance/leaves/?status=pending');
            if (leavesResponse && leavesResponse.ok) {
                const leavesData = await leavesResponse.json();
                document.getElementById('pendingLeaves').textContent = leavesData.count || leavesData.results?.length || 0;
            }
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }

    // Load recent attendance
    async function loadRecentAttendance() {
        try {
            const response = await apiFetch('/api/attendance/records/?limit=10');
            if (response && response.ok) {
                const data = await response.json();
                const records = data.results || data;
                const tbody = document.getElementById('recentAttendance');

                if (records.length === 0) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="5" style="text-align: center; padding: 2rem; color: var(--gray-500);">
                                No attendance records found
                            </td>
                        </tr>
                    `;
                    return;
                }

                tbody.innerHTML = records.map(record => {
                    const date = new Date(record.timestamp);
                    const time = date.toLocaleTimeString('id-ID', {
                        hour: '2-digit',
                        minute: '2-digit'
                    });

                    const verifyTypes = {
                        0: 'Password',
                        1: 'Fingerprint',
                        2: 'Card',
                        3: 'Face',
                        4: 'Iris',
                        15: 'Palm'
                    };

                    const verifyCodes = {
                        0: { text: 'Check In', class: 'badge-success' },
                        1: { text: 'Check Out', class: 'badge-danger' },
                        2: { text: 'Break Out', class: 'badge-warning' },
                        3: { text: 'Break In', class: 'badge-info' },
                        4: { text: 'OT In', class: 'badge-info' },
                        5: { text: 'OT Out', class: 'badge-info' }
                    };

                    const verifyCode = verifyCodes[record.verify_code] || { text: 'Unknown', class: 'badge-info' };

                    return `
                        <tr>
                            <td>
                                <div style="font-weight: 500;">${record.user?.username || 'Unknown'}</div>
                                <div style="font-size: 0.75rem; color: var(--gray-500);">${record.user?.employee_id || '-'}</div>
                            </td>
                            <td>${record.device?.name || 'Unknown Device'}</td>
                            <td>${time}</td>
                            <td>${verifyTypes[record.verify_type] || 'Unknown'}</td>
                            <td><span class="badge ${verifyCode.class}">${verifyCode.text}</span></td>
                        </tr>
                    `;
                }).join('');
            }
        } catch (error) {
            console.error('Error loading recent attendance:', error);
            document.getElementById('recentAttendance').innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; padding: 2rem; color: var(--danger-color);">
                        Error loading data
                    </td>
                </tr>
            `;
        }
    }

    // Logout function
    document.getElementById('logoutBtn').addEventListener('click', async function (e) {
        e.preventDefault();

        try {
            await apiFetch('/api/auth/logout/', { method: 'POST' });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            localStorage.removeItem('authToken');
            localStorage.removeItem('userData');
            localStorage.removeItem('rememberMe');
            window.location.href = '/';
        }
    });

    // Initialize dashboard
    loadUserInfo();
    loadStats();
    loadRecentAttendance();

    // Refresh stats every 30 seconds
    setInterval(loadStats, 30000);

    // Refresh attendance every 10 seconds
    setInterval(loadRecentAttendance, 10000);

})();
