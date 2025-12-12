// (async function(){
//   const container = document.getElementById('users');
//   const token = localStorage.getItem('token');
//   const role = localStorage.getItem('role');

//   if (!token || role !== 'admin') {
//     // not logged in or not admin
//     window.location.href = '/login.html';
//     return;
//   }

//   try {
//     const res = await fetch('/api/auth/admin/users', {
//       headers: { 'Authorization': 'Bearer ' + token }
//     });

//     if (res.status === 401 || res.status === 403) {
//       alert('Not authorized');
//       localStorage.clear();
//       window.location.href = '/login.html';
//       return;
//     }

//     const users = await res.json();
//     if (!Array.isArray(users) || users.length === 0) {
//       container.innerHTML = '<div class="empty">No users found.</div>';
//       return;
//     }

//     container.innerHTML = '';
//     users.forEach(u => {
//       const div = document.createElement('div');
//       div.className = 'user-card';
//       div.innerHTML = `
//         <div class="user-left">
//           <div class="avatar">${(u.name||'U').charAt(0).toUpperCase()}</div>
//           <div class="user-info">
//             <div class="name">User Name: ${u.name || '—'}</div>
//             <div class="meta">Role Type: ${u.role || 'user'}</div>
//             <div class="meta">Email: ${u.email || '—'}</div>
//           </div>
//         </div>
//         <div><a class="btn-view" href="/user/${u.id}">›</a></div>
//       `;
//       container.appendChild(div);
//     });
//   } catch (err) {
//     container.innerHTML = '<div class="empty">Error loading users.</div>';
//     console.error(err);
//   }
// })();






(async function(){
  const container = document.getElementById('users');
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');

  if (!token || role !== 'admin') {
    window.location.href = '/login';
    return;
  }

  try {
    const res = await fetch('/api/auth/admin/users', {
      headers: { 'Authorization': 'Bearer ' + token }
    });

    if (res.status === 401 || res.status === 403) {
      alert('Not authorized');
      localStorage.clear();
      window.location.href = '/login';
      return;
    }

    const users = await res.json();
    if (!Array.isArray(users) || users.length === 0) {
      container.innerHTML = '<div class="empty">No users found.</div>';
      return;
    }

    container.innerHTML = '';
    users.forEach(u => {
      const div = document.createElement('div');
      div.className = 'user-card';
      div.innerHTML = `
        <div class="user-left">
          <div class="avatar">${(u.name||'U').charAt(0).toUpperCase()}</div>
          <div class="user-info">
            <div class="name">User Name: ${u.name || '—'}</div>
            <div class="meta">Role Type: ${u.role || 'user'}</div>
            <div class="meta">Email: ${u.email || '—'}</div>
          </div>
        </div>
        <div><a class="btn-view" href="/user/${u.id}">›</a></div>
      `;
      container.appendChild(div);
    });
  } catch (err) {
    container.innerHTML = '<div class="empty">Error loading users.</div>';
    console.error(err);
  }
})();