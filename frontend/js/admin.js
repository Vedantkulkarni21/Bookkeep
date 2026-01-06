const token = localStorage.getItem('token');
const role = localStorage.getItem('role');

if (!token || role !== 'admin') {
  window.location.href = '/login';
}

async function loadUsers() {
  const container = document.getElementById('users');
  
  try {
    const res = await fetch('/api/auth/admin/users', {
      headers: { 'Authorization': 'Bearer ' + token }
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
      div.innerHTML = `
        <div class="user-left">
          <div class="avatar">${(u.name||'U').charAt(0).toUpperCase()}</div>
          <div class="user-info">
            <div class="name" onclick="openUser(${u.id})">
User Name: ${u.name || '—'}</div>
            <div class="meta">Role Type: ${u.role || 'user'}</div>
            <div class="meta">Email: ${u.email || '—'}</div>
          </div>
        </div>
      `;
      container.appendChild(div);
    });
  } catch (err) {
    container.innerHTML = '<div class="empty">Error loading users.</div>';
    console.error(err);
  }
}

// async function viewUserDetails(userId, event) {
//   event.stopPropagation();
  
//   try {
//     const res = await fetch(`/api/auth/admin/users/${userId}/documents`, {
//       headers: { 'Authorization': 'Bearer ' + token }
//     });

//     if (!res.ok) {
//       alert('Error loading user details');
//       return;
//     }

//     const data = await res.json();
//     const user = data.user;
//     const docs = data.documents || [];

//     // Update detail view
//     document.getElementById('detailName').textContent = user.name;
//     document.getElementById('detailRole').textContent = user.role;
//     document.getElementById('detailEmail').textContent = user.email;
//     document.getElementById('uploadStatus').textContent = `Document Upload Status: ${docs.length}/${docs.length || 0}`;

//     // Populate documents table
//     const tbody = document.getElementById('docTable');
//     if (docs.length === 0) {
//       tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#6b7a86">No documents uploaded</td></tr>';
//     } else {
//       tbody.innerHTML = docs.map(d => `
//         <tr>
//           <td>${d.filename}</td>
//           <td><button class="view-btn" onclick="viewDocument('${d.drive_file_id}')">View</button></td>
//           <td><input type="checkbox"></td>
//           <td><input type="checkbox"></td>
//           <td><span style="font-size:12px">— 0 +</span></td>
//         </tr>
//       `).join('');
//     }

//     // Switch views
//     document.getElementById('listView').style.display = 'none';
//     document.getElementById('detailView').classList.add('active');
//   } catch (err) {
//     alert('Error: ' + err.message);
//   }
// }

// function goBack() {
//   document.getElementById('listView').style.display = 'block';
//   document.getElementById('detailView').classList.remove('active');
// }

function viewDocument(fileId) {
  // Open document in new tab
  window.open(`https://drive.google.com/file/d/${fileId}/view`, '_blank');
}

function openUser(userId) {
  window.location.href = `/admin-user-detail?user_id=${userId}`;
}


// Load users on page load
loadUsers();