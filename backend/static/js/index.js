if (!localStorage.getItem("authToken")) {
    window.location.href = "auth.html";
} else {
    const user = JSON.parse(localStorage.getItem("authUser"));
    if (user && user.name) {
        document.getElementById("userNameDisplay").textContent = user.name;
        document.getElementById("userInitial").textContent = user.name.charAt(0).toUpperCase();
    }
}

function logout() {
    if (confirm("Do you want to log out?")) {
        localStorage.removeItem("authToken");
        localStorage.removeItem("authUser");
        window.location.href = "auth.html";
    }
}

VANTA.NET({
    el: "#vanta-canvas",
    mouseControls: true,
    touchControls: true,
    gyroControls: false,
    minHeight: 200.00,
    minWidth: 200.00,
    scale: 1.00,
    scaleMobile: 1.00,
    color: 0x3f51b5,
    backgroundColor: 0x0a192f,
    points: 10.00,
    maxDistance: 20.00,
    spacing: 15.00
});

const message = "Hello User, Your unique career journey starts here. Explore 500+ paths...";
const display = document.getElementById("typewriter");
let i = 0;

function typeWriter() {
    if (i < message.length) {
        display.innerHTML += message.charAt(i);
        i++;
        setTimeout(typeWriter, 50);
    }
}

window.onload = typeWriter;
