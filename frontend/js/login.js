// // simple login handler - sends role and stores token+role returned by server
// async function loginUser(role = "user") {
//   const email = document.getElementById("email").value;
//   const password = document.getElementById("password").value;
//   if (!email || !password) { alert("Enter email and password"); return; }

//   try {
//     const res = await fetch("/api/auth/login", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ email, password, role })
//     });

//     let data = {};
//     try { data = await res.json(); } catch (e) { /* ignore JSON parse errors */ }

//     if (!res.ok) {
//       alert(data.detail || data.message || "Login failed");
//       return;
//     }

//     localStorage.setItem("token", data.access_token);
//     localStorage.setItem("role", data.role);
//     localStorage.setItem("user_id", data.user_id);

//     if (data.role === "admin") {
//       window.location.href = "/admin-dashboard";
//     } else {
//       window.location.href = "/dashboard";
//     }
//   } catch (err) {
//     alert("Network error");
//     console.error(err);
//   }
// }

// // wire buttons and form once
// document.addEventListener("DOMContentLoaded", () => {
//   const userBtn = document.getElementById("userLoginBtn");
//   const adminBtn = document.getElementById("adminLoginBtn");
//   const form = document.getElementById("loginForm");

//   if (userBtn) userBtn.addEventListener("click", (e) => { e.preventDefault(); loginUser("user"); });
//   if (adminBtn) adminBtn.addEventListener("click", (e) => { e.preventDefault(); loginUser("admin"); });

//   // support Enter key (submit) — default to user login
//   if (form) form.addEventListener("submit", (e) => { e.preventDefault(); loginUser("user"); });
// });




async function loginUser(expectedRole = null) {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  if (!email || !password) {
    alert("Enter email and password");
    return;
  }

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }) // ❗ NO role sent
    });

    const data = await res.json();

    if (!res.ok) {
      alert(data.detail || "Login failed");
      return;
    }

    // Optional: block wrong portal login
    if (expectedRole && data.role !== expectedRole) {
      alert(`You are not authorized as ${expectedRole}`);
      return;
    }

    localStorage.setItem("token", data.access_token);
    localStorage.setItem("role", data.role);
    localStorage.setItem("user_id", data.user_id);

    if (data.role === "admin") {
      window.location.href = "/admin-dashboard";
    } else {
      window.location.href = "/dashboard";
    }
  } catch (err) {
    console.error(err);
    alert("Network error");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("userLoginBtn")
    .addEventListener("click", (e) => {
      e.preventDefault();
      loginUser("user");
    });

  document.getElementById("adminLoginBtn")
    .addEventListener("click", (e) => {
      e.preventDefault();
      loginUser("admin");
    });

  document.getElementById("loginForm")
    .addEventListener("submit", (e) => {
      e.preventDefault();
      loginUser("user");
    });
});
