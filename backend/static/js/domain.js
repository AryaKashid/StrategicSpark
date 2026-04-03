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

function startLearning(topicName) {
    // Redirect to the quiz page with the selected topic
    window.location.href = `/quiz_page?topic=${encodeURIComponent(topicName)}`;
}
