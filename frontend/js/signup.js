async function signupUser() {
    console.log('signupUser called');
    const name = document.getElementById('name')?.value?.trim() || '';
    const email = document.getElementById('email')?.value?.trim() || '';
    const phone = document.getElementById('phone')?.value?.trim() || '';
    const password = document.getElementById('password')?.value || '';

    if (!name || !email || !password) {
        alert('Please fill in all required fields');
        return;
    }

    try {
        console.log('Sending signup request to /api/auth/signup', { name, email, phone });
        const res = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, phone, password })
        });

        console.log('Signup response status:', res.status);
        const data = await res.json().catch(()=>({}));
        console.log('Signup response data:', data);

        if (!res.ok) {
            alert(`Signup failed: ${data.detail || data.error || 'Unknown'}`);
            return;
        }

        // Save token if returned
        if (data.access_token) {
            localStorage.setItem('access_token', data.access_token);
        }

        alert('Signup successful! Redirecting to login.');
        window.location.href = '/login';
    } catch (err) {
        console.error('Signup error', err);
        alert('Signup error. Check console for details.');
    }
}
window.signupUser = signupUser;
