let storyTextEl = document.getElementById("story-text");
let readBtn = document.getElementById("read-btn");
let pauseBtn = document.getElementById("pause-btn");
let langSelect = document.getElementById("lang-select");

let utterance = null;
let isPaused = false;


// ⭐ Change story text & heading when user switches languages
function updateStory() {
    const lang = langSelect.value;

    const newText = storyTextEl.dataset[lang];
    const heading = document.querySelector(".chapter-heading");

    storyTextEl.textContent = newText;

    const titles = {
        en: storyTextEl.dataset.enTitle,
        ta: storyTextEl.dataset.taTitle,
        te: storyTextEl.dataset.teTitle
    };

    heading.textContent = titles[lang] || titles.en;
}


// ⭐ Highlight Function
function highlight(words, index) {
    let html = "";
    words.forEach((word, i) => {
        if (i === index) {
            html += `<span class="highlight">${word}</span> `;
        } else {
            html += word + " ";
        }
    });
    storyTextEl.innerHTML = html;
}


// ⭐ Read Aloud
readBtn.addEventListener("click", () => {
    const lang = langSelect.value;
    let text = storyTextEl.textContent.trim();
    let words = text.split(" ");

    window.speechSynthesis.cancel(); // stop ongoing audio

    utterance = new SpeechSynthesisUtterance(text);

    // language settings
    utterance.lang = {
        en: "en-US",
        ta: "ta-IN",
        te: "te-IN"
    }[lang];

    utterance.rate = 1;
    utterance.pitch = 1;

    let index = 0;
    utterance.onboundary = (e) => {
        if (e.name === "word") {
            highlight(words, index);
            index++;
        }
    };

    speechSynthesis.speak(utterance);
    isPaused = false;
    pauseBtn.textContent = "⏸ Pause";
});


// ⭐ Pause / Resume
pauseBtn.addEventListener("click", () => {
    if (!utterance) return;

    if (!isPaused) {
        speechSynthesis.pause();
        pauseBtn.textContent = "▶ Resume";
        isPaused = true;
    } else {
        speechSynthesis.resume();
        pauseBtn.textContent = "⏸ Pause";
        isPaused = false;
    }
});


// ⭐ Language selector
langSelect.addEventListener("change", () => {
    window.speechSynthesis.cancel();
    updateStory();
});
