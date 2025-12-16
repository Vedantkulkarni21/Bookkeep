// // async function loginUser() {
// //     const email = document.getElementById('email')?.value?.trim() || '';
// //     const password = document.getElementById('password')?.value || '';
// //     const isAdmin = document.getElementById('isAdmin')?.checked || false;

// //     if (!email || !password) {
// //         alert('Please enter email and password');
// //         return;
// //     }

// //     try {
// //         const url = isAdmin ? '/api/auth/admin-login' : '/api/auth/login';
// //         const res = await fetch(url, {
// //             method: 'POST',
// //             headers: { 'Content-Type': 'application/json' },
// //             body: JSON.stringify({ email, password })
// //         });
// //         const data = await res.json().catch(()=>({}));
// //         if (!res.ok) {
// //             alert(`Login failed: ${data.detail || data.error || 'Unknown'}`);
// //             return;
// //         }
// //         localStorage.setItem('access_token', data.access_token);
// //         // go to dashboard page
// //         window.location.href = '/dashboard';
// //     } catch (err) {
// //         console.error(err);
// //         alert('Login error. Check console.');
// //     }
// // }
// // window.loginUser = loginUser;





// // async function loginUser(role) {
// //   const email = document.getElementById('email').value;
// //   const password = document.getElementById('password').value;

// //   try {
// //     const response = await fetch('/api/login', {
// //       method: 'POST',
// //       headers: { 'Content-Type': 'application/json' },
// //       body: JSON.stringify({ email, password, role: role || 'user' })
// //     });

// //     const data = await response.json();
// //     if (response.ok) {
// //       localStorage.setItem('token', data.access_token);
// //       localStorage.setItem('role', data.role);
// //       localStorage.setItem('user_id', data.user_id);
// //       window.location.href = role === 'admin' ? '/admin-dashboard' : '/dashboard';
// //     } else {
// //       alert(data.detail || 'Login failed');
// //     }
// //   } catch (error) {
// //     alert('Error: ' + error.message);
// //   }
// // }




// // async function loginUser(role = 'user') {
// //     const email = document.getElementById('email').value;
// //     const password = document.getElementById('password').value;

// //     const res = await fetch('/api/auth/login', { // <- updated endpoint
// //         method: 'POST',
// //         headers: { 'Content-Type': 'application/json' },
// //         body: JSON.stringify({ email, password, role })
// //     });

// //     const data = await res.json();
// //     if (res.ok) {
// //         localStorage.setItem('token', data.access_token);
// //         localStorage.setItem('role', data.role);
// //         localStorage.setItem('user_id', data.user_id);
// //         window.location.href = data.role === 'admin' ? '/admin-dashboard' : '/dashboard';
// //     } else {
// //         alert(data.detail || 'Login failed');
// //     }
// // }


// async function loginUser(role = 'user') {
//   const email = document.getElementById('email').value.trim();
//   const password = document.getElementById('password').value;

//   if (!email || !password) {
//     alert("Email and password required");
//     return;
//   }

//   try {
//     const res = await fetch('/api/auth/login', {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({ email, password, role })
//     });

//     const data = await res.json();

//     if (!res.ok) {
//       alert(data.detail || 'Login failed');
//       return;
//     }

//     localStorage.setItem('token', data.access_token);
//     localStorage.setItem('role', data.role);
//     localStorage.setItem('user_id', data.user_id);

//     window.location.href =
//       data.role === 'admin' ? '/admin-dashboard' : '/dashboard';

//   } catch (err) {
//     console.error(err);
//     alert('Login error');
//   }
// }





async function loginUser(role = 'user') {
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;

  if (!email || !password) {
    alert("Email and password required");
    return;
  }

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, role })
    });

    const data = await res.json();

    if (!res.ok) {
      alert(data.detail || 'Login failed');
      return;
    }

    localStorage.setItem('token', data.access_token);
    localStorage.setItem('role', data.role);
    localStorage.setItem('user_id', data.user_id);

    window.location.href =
      data.role === 'admin'
        ? '/admin-dashboard'
        : '/dashboard';

  } catch (err) {
    console.error(err);
    alert('Login error');
  }
}
