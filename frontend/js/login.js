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
