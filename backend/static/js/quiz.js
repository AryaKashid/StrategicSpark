document.addEventListener('DOMContentLoaded', () => {
    // Initialize Vanta
    VANTA.NET({
        el: "#vanta-bg",
        mouseControls: true,
        touchControls: true,
        gyroControls: false,
        minHeight: 200.00,
        minWidth: 200.00,
        scale: 1.00,
        scaleMobile: 1.00,
        color: 0x6366f1,
        backgroundColor: 0x0a192f,
        points: 12.00,
        maxDistance: 20.00,
        spacing: 16.00
    });

    const urlParams = new URLSearchParams(window.location.search);
    const topic = urlParams.get('topic') || 'General Knowledge';
    const authToken = localStorage.getItem('authToken');

    if (!authToken) {
        window.location.href = '/';
        return;
    }

    let questions = [];
    let currentIdx = 0;
    let userAnswers = [];
    let currentLevel = 'beginner';

    const elements = {
        overlay: document.getElementById('loading-overlay'),
        content: document.getElementById('quiz-content'),
        qText: document.getElementById('question-text'),
        options: document.getElementById('options-container'),
        progress: document.getElementById('progress-fill'),
        count: document.getElementById('question-count'),
        nextBtn: document.getElementById('next-btn'),
        qMeta: document.getElementById('question-meta'),
    };

    // Fetch Questions
    async function startQuiz() {
        try {
            const res = await fetch('/api/quiz/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({ topic })
            });
            const data = await res.json();
            
            if (res.ok) {
                questions = data.questions;
                currentLevel = data.level;
                elements.overlay.classList.add('hidden');
                elements.content.classList.remove('hidden');
                renderQuestion();
            } else {
                alert(data.message || "Failed to generate quiz.");
                window.location.href = '/dashboard';
            }
        } catch (err) {
            console.error(err);
            alert("Connection error. Try again.");
        }
    }

    function renderQuestion() {
        const q = questions[currentIdx];
        elements.qText.textContent = q.question;
        elements.qMeta.textContent = `${topic.toUpperCase()} - LEVEL: ${currentLevel.toUpperCase()}`;
        elements.options.innerHTML = '';
        
        q.options.forEach(opt => {
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.textContent = opt;
            btn.onclick = () => selectOption(btn, opt);
            elements.options.appendChild(btn);
        });

        elements.count.textContent = `Question ${currentIdx + 1} of 5`;
        elements.progress.style.width = `${(currentIdx + 1) * 20}%`;
        elements.nextBtn.disabled = true;
        elements.nextBtn.dataset.answered = 'false';

        // Update button text for last question
        if (currentIdx === questions.length - 1) {
            elements.nextBtn.textContent = 'Submit Quiz';
            elements.nextBtn.style.background = 'linear-gradient(135deg, #a855f7, #6366f1)';
        } else {
            elements.nextBtn.textContent = 'Next Question';
            elements.nextBtn.style.background = '';
        }
    }

    function selectOption(btn, value) {
        if (elements.nextBtn.dataset.answered === 'true') return;

        const q = questions[currentIdx];
        const isCorrect = (value === q.answer);
        
        // Mark selected
        btn.classList.add('selected');

        // Apply visual feedback to all buttons
        document.querySelectorAll('.option-btn').forEach(b => {
            b.classList.add('disabled');
            if (b.textContent === q.answer) {
                b.classList.add('correct');
            } else if (b === btn && !isCorrect) {
                b.classList.add('incorrect');
            }
        });

        userAnswers[currentIdx] = value;
        elements.nextBtn.disabled = false;
        elements.nextBtn.dataset.answered = 'true';
    }

    elements.nextBtn.onclick = () => {
        if (currentIdx < questions.length - 1) {
            currentIdx++;
            renderQuestion();
        } else {
            submitQuiz();
        }
    };

    async function submitQuiz() {
        elements.content.classList.add('hidden');
        elements.overlay.classList.remove('hidden');
        document.getElementById('loading-text').textContent = 'Generating deep performance analysis...';

        try {
            const res = await fetch('/api/quiz/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    topic,
                    answers: userAnswers,
                    questions: questions
                })
            });
            
            if (res.ok) {
                const data = await res.json();
                // Store results temporarily for the results page
                localStorage.setItem('lastQuizResult', JSON.stringify({
                    topic: topic,
                    score: data.score,
                    total: data.total,
                    analysis: data.analysis,
                    results: data.results
                }));
                window.location.href = '/results';
            } else {
                alert("Failed to submit quiz.");
                window.location.href = '/dashboard';
            }
        } catch (err) {
            console.error(err);
            alert("Error submitting quiz results.");
        }
    }


    startQuiz();
});

function speakQuestion() {
    const text = document.getElementById('question-text').textContent;
    if (text && !text.includes('Loading')) {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9; // Slightly slower for better clarity
        utterance.pitch = 1.0;
        
        // Use a generic English voice if available
        const voices = window.speechSynthesis.getVoices();
        const englishVoice = voices.find(v => v.lang.startsWith('en'));
        if (englishVoice) utterance.voice = englishVoice;
        
        window.speechSynthesis.speak(utterance);
    }
}
