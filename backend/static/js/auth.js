        // Initialize Vanta Background as requested
        window.addEventListener('DOMContentLoaded', () => {
            VANTA.NET({
                el: "body",
                mouseControls: true,
                touchControls: true,
                gyroControls: false,
                minHeight: 200.00,
                minWidth: 200.00,
                scale: 1.00,
                scaleMobile: 1.00,
                color: 0x3f51b5,           /* The dots and lines (Indigo Blue) */
                backgroundColor: 0x0a192f, /* Dark Navy Blue Background */
                points: 10.00,             /* Amount of dots */
                maxDistance: 20.00,        /* Line connection distance */
                spacing: 15.00             /* Density of the net */
            });
        });

        const API_BASE = "http://127.0.0.1:5000/api";
        const loginForm = document.getElementById("loginForm");
        const registerForm = document.getElementById("registerForm");
        const messageDiv = document.getElementById("message");

        function toggleForms() {
            loginForm.classList.toggle("hidden");
            registerForm.classList.toggle("hidden");
            messageDiv.textContent = "";
        }

        function showMessage(text, isError = false) {
            messageDiv.textContent = text;
            messageDiv.className = isError ? 'error' : 'success';
        }

        // Handle Login
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("loginEmail").value;
            const password = document.getElementById("loginPassword").value;

            try {
                const res = await fetch(`${API_BASE}/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                const data = await res.json();

                if (res.ok) {
                    showMessage("Login Successful! Redirecting...");
                    localStorage.setItem("authToken", data.token);
                    localStorage.setItem("authUser", JSON.stringify(data.user));
                    setTimeout(() => {
                        window.location.href = "/dashboard";
                    }, 1000);
                } else {
                    showMessage(data.message || "Login failed", true);
                }
            } catch (err) {
                showMessage("Connection error. Is backend running?", true);
            }
        });

        // Handle Registration
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const name = document.getElementById("regName").value;
            const email = document.getElementById("regEmail").value;
            const password = document.getElementById("regPassword").value;

            try {
                const res = await fetch(`${API_BASE}/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, password })
                });

                const data = await res.json();

                if (res.ok) {
                    showMessage("Registration successful! Please sign in.");
                    setTimeout(() => toggleForms(), 1500);
                } else {
                    showMessage(data.message || "Registration failed", true);
                }
            } catch (err) {
                showMessage("Connection error. Is backend running?", true);
            }
        });
