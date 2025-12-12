async function loginUser() {
    const email = document.getElementById('email')?.value?.trim() || '';
    const password = document.getElementById('password')?.value || '';
    const isAdmin = document.getElementById('isAdmin')?.checked || false;

    if (!email || !password) {
        alert('Please enter email and password');
        return;
    }

    try {
        const url = isAdmin ? '/api/auth/admin-login' : '/api/auth/login';
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json().catch(()=>({}));
        if (!res.ok) {
            alert(`Login failed: ${data.detail || data.error || 'Unknown'}`);
            return;
        }
        localStorage.setItem('access_token', data.access_token);
        // go to dashboard page
        window.location.href = '/dashboard';
    } catch (err) {
        console.error(err);
        alert('Login error. Check console.');
    }
}
window.loginUser = loginUser;
