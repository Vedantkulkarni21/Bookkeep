// // const token = localStorage.getItem('token');
// // const role = localStorage.getItem('role');

// // if (!token || role !== 'admin') {
// //   window.location.href = '/login';
// // }

// // async function loadUsers() {
// //   const container = document.getElementById('users');

// //   try {
// //     const res = await fetch('/api/auth/admin/users', {
// //       headers: { Authorization: 'Bearer ' + token }
// //     });

// //     if (res.status === 401 || res.status === 403) {
// //       localStorage.clear();
// //       window.location.href = '/login';
// //       return;
// //     }

// //     const users = await res.json();

// //     if (!Array.isArray(users) || users.length === 0) {
// //       container.innerHTML = '<div class="empty">No users found.</div>';
// //       return;
// //     }

// //     container.innerHTML = '';

// //     users.forEach(u => {

// //       const div = document.createElement('div');
// //       div.className = 'user-card';
// //       div.style.cursor = 'pointer';

// //       // 👉 whole card opens profile
// //       div.addEventListener('click', () => openUser(u.id));

// //       div.innerHTML = `
// //         <div class="user-left">
// //           <div class="avatar">
// //             ${(u.name || 'U').charAt(0).toUpperCase()}
// //           </div>

// //           <div class="user-info">
// //             <div class="name">User Name: ${u.name || '—'}</div>
// //             <div class="meta">Role Type: ${u.role || 'user'}</div>
// //             <div class="meta">Email: ${u.email || '—'}</div>
// //           </div>
// //         </div>
// //       `;

// //       // ❌ removed stopPropagation — this was blocking mobile taps

// //       container.appendChild(div);
// //     });

// //   } catch (err) {
// //     container.innerHTML = '<div class="empty">Error loading users.</div>';
// //     console.error(err);
// //   }
// // }

// // function openUser(userId) {
// //   window.location.href = `/admin-user-detail?user_id=${userId}`;
// // }

// // function viewDocument(fileId) {
// //   window.open(`https://drive.google.com/file/d/${fileId}/view`, '_blank');
// // }

// // loadUsers();





// const token = localStorage.getItem('token');
// const role = localStorage.getItem('role');

// if (!token || role !== 'admin') {
//   window.location.href = '/login';
// }

// async function loadUsers() {
//   const container = document.getElementById('users');

//   try {
//     const res = await fetch('/api/auth/admin/users', {
//       headers: { Authorization: 'Bearer ' + token }
//     });

//     if (res.status === 401 || res.status === 403) {
//       localStorage.clear();
//       window.location.href = '/login';
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
//       div.dataset.userId = u.id;   // 👉 store id on card
//       div.style.cursor = 'pointer';

//       div.innerHTML = `
//         <div class="user-left">
//           <div class="avatar">
//             ${(u.name || 'U').charAt(0).toUpperCase()}
//           </div>

//           <div class="user-info">
//             <div class="name">User Name: ${u.name || '—'}</div>
//             <div class="meta">Role Type: ${u.role || 'user'}</div>
//             <div class="meta">Email: ${u.email || '—'}</div>
//           </div>
//         </div>
//       `;

//       container.appendChild(div);
//     });

//   } catch (err) {
//     container.innerHTML = '<div class="empty">Error loading users.</div>';
//     console.error(err);
//   }
// }

// /* ✅ EVENT DELEGATION — ANY CLICK INSIDE CARD OPENS IT */
// document.addEventListener('click', e => {
//   const card = e.target.closest('.user-card');
//   if (!card) return;

//   const userId = card.dataset.userId;
//   if (userId) {
//     openUser(userId);
//   }
// });

// function openUser(userId) {
//   window.location.href = `/admin-user-detail?user_id=${userId}`;
// }

// function viewDocument(fileId) {
//   window.open(`https://drive.google.com/file/d/${fileId}/view`, '_blank');
// }

// loadUsers();



const token = localStorage.getItem('token');
const role = localStorage.getItem('role');

if (!token || role !== 'admin') {
  window.location.href = '/login';
}

async function loadUsers() {
  const container = document.getElementById('users');

  try {
    const res = await fetch('/api/auth/admin/users', {
      headers: { Authorization: 'Bearer ' + token }
    });

    if (res.status === 401 || res.status === 403) {
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
      div.style.cursor = 'pointer';

      // store id
      div.dataset.userId = u.id;

      // card html
      div.innerHTML = `
        <div class="user-left">
          <div class="avatar">
            ${(u.name || 'U').charAt(0).toUpperCase()}
          </div>

          <div class="user-info">
            <div class="name">User Name: ${u.name || '—'}</div>
            <div class="meta">Role Type: ${u.role || 'user'}</div>
            <div class="meta">Email: ${u.email || '—'}</div>
          </div>
        </div>
      `;

      /* ✅ make whole card clickable */
      div.addEventListener('click', () => openUser(u.id));

      container.appendChild(div);
    });

  } catch (err) {
    container.innerHTML = '<div class="empty">Error loading users.</div>';
    console.error(err);
  }
}

function openUser(userId) {
  window.location.href = `/admin-user-detail?user_id=${userId}`;
}

function viewDocument(fileId) {
  window.open(`https://drive.google.com/file/d/${fileId}/view`, '_blank');
}

loadUsers();
