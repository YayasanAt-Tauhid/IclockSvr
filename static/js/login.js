// Login functionality
(function () {
    'use strict';

    const loginForm = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');
    const btnText = loginBtn.querySelector('.btn-text');
    const btnLoader = loginBtn.querySelector('.btn-loader');
    const errorMessage = document.getElementById('errorMessage');

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

    // Show error message
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';

        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }

    // Set loading state
    function setLoading(loading) {
        if (loading) {
            loginBtn.disabled = true;
            btnText.style.display = 'none';
            btnLoader.style.display = 'block';
        } else {
            loginBtn.disabled = false;
            btnText.style.display = 'block';
            btnLoader.style.display = 'none';
        }
    }

    // Handle form submission
    loginForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const remember = document.getElementById('remember').checked;

        // Validate inputs
        if (!username || !password) {
            showError('Please enter both username and password.');
            return;
        }

        setLoading(true);

        try {
            const response = await fetch('/api/auth/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Store token
                localStorage.setItem('authToken', data.token);
                localStorage.setItem('userData', JSON.stringify(data.user));

                if (remember) {
                    localStorage.setItem('rememberMe', 'true');
                }

                // Show success animation
                loginBtn.innerHTML = '<span style="display: flex; align-items: center; gap: 0.5rem;"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> Success!</span>';

                // Redirect to dashboard
                setTimeout(() => {
                    window.location.href = '/dashboard/';
                }, 1000);
            } else {
                // Show error
                const errorMsg = data.non_field_errors
                    ? data.non_field_errors[0]
                    : 'Invalid username or password. Please try again.';
                showError(errorMsg);
                setLoading(false);
            }
        } catch (error) {
            console.error('Login error:', error);
            showError('An error occurred. Please try again later.');
            setLoading(false);
        }
    });

    // Check if already logged in
    const authToken = localStorage.getItem('authToken');
    if (authToken) {
        // Verify token is still valid
        fetch('/api/auth/users/me/', {
            headers: {
                'Authorization': `Token ${authToken}`
            }
        })
            .then(response => {
                if (response.ok) {
                    window.location.href = '/dashboard/';
                } else {
                    // Token invalid, clear storage
                    localStorage.removeItem('authToken');
                    localStorage.removeItem('userData');
                }
            })
            .catch(error => {
                console.error('Token verification error:', error);
            });
    }

    // Input animations
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', function () {
            this.parentElement.style.transform = 'scale(1.02)';
        });

        input.addEventListener('blur', function () {
            this.parentElement.style.transform = 'scale(1)';
        });
    });

})();
