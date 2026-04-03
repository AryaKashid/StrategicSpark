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
        results: document.getElementById('results-screen'),
        qText: document.getElementById('question-text'),
        options: document.getElementById('options-container'),
        progress: document.getElementById('progress-fill'),
        count: document.getElementById('question-count'),
        nextBtn: document.getElementById('next-btn'),
        qMeta: document.getElementById('question-meta'),
        finalScore: document.getElementById('final-score'),
        analysis: document.getElementById('analysis-text')
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
            const data = await res.json();

            if (res.ok) {
                elements.overlay.classList.add('hidden');
                renderResults(data);
            }
        } catch (err) {
            console.error(err);
            alert("Error submitting quiz results.");
        }
    }

    function renderResults(data) {
        const analysis = data.analysis;
        elements.results.style.display = 'block';
        
        // Update Metrics
        document.getElementById('accuracy-value').textContent = Math.round(analysis.accuracy) + '%';
        document.getElementById('precision-value').textContent = Math.round(analysis.precision) + '%';
        
        // Animate Circles (simple way)
        document.getElementById('accuracy-circle').style.borderTopColor = `hsl(${analysis.accuracy * 1.2}, 70%, 50%)`;
        document.getElementById('precision-circle').style.borderTopColor = `hsl(${analysis.precision * 1.2}, 70%, 50%)`;

        // Summary
        document.getElementById('summary-content').textContent = analysis.summary;

        // Wrong Answers
        const wrongContainer = document.getElementById('wrong-answers-container');
        const reviewSection = document.getElementById('review-section');
        wrongContainer.innerHTML = '';
        
        if (analysis.wrong_answers && analysis.wrong_answers.length > 0) {
            reviewSection.classList.remove('hidden');
            analysis.wrong_answers.forEach(w => {
                const card = document.createElement('div');
                card.className = 'wrong-answer-card';
                card.innerHTML = `
                    <h4>${w.question}</h4>
                    <p style="color: rgba(255,255,255,0.6); margin: 0.5rem 0;">
                        Your answer: <span style="color: #ef4444;">${w.user_answer}</span> | 
                        Correct: <span style="color: #10b981;">${w.correct_answer}</span>
                    </p>
                    <p class="exp"><strong>Review Note:</strong> ${w.explanation}</p>
                `;
                wrongContainer.appendChild(card);
            });
        }

        // Recommendations
        const recContainer = document.getElementById('course-recommendations');
        const recSection = document.getElementById('recommendations-section');
        recContainer.innerHTML = '';

        if (analysis.recommendations && analysis.recommendations.length > 0) {
            recSection.classList.remove('hidden');
            analysis.recommendations.forEach(r => {
                const card = document.createElement('div');
                card.className = 'course-card';
                card.innerHTML = `
                    <span class="course-platform">${r.platform}</span>
                    <h4 class="course-title">${r.title}</h4>
                    <p style="font-size: 0.9rem; color: rgba(255,255,255,0.6);">${r.description}</p>
                    <a href="${r.link}" target="_blank" class="course-link">View Course →</a>
                `;
                recContainer.appendChild(card);
            });
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
