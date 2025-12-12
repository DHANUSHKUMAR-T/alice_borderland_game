const music = document.getElementById("bg-music");
const toggleBtn = document.getElementById("audio-toggle");

// Set volume
music.volume = 0.05;

// Load mute state
let isMuted = localStorage.getItem("audioMuted") === "true";

// Load last played time
let savedTime = localStorage.getItem("audioTime");
if (savedTime) {
    music.currentTime = parseFloat(savedTime);
}

// Update button icon
function updateButton() {
    toggleBtn.textContent = isMuted ? "🔇" : "🔊";
}

updateButton();

// Mute / play based on saved state
if (isMuted) {
    music.pause();
} else {
    music.play().catch(() => {});
}

// Save audio time every second
setInterval(() => {
    if (!music.paused) {
        localStorage.setItem("audioTime", music.currentTime);
    }
}, 1000);

// Toggle audio
toggleBtn.addEventListener("click", () => {
    isMuted = !isMuted;

    if (isMuted) {
        music.pause();
    } else {
        music.play();
    }

    localStorage.setItem("audioMuted", isMuted);
    updateButton();
});
