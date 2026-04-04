document.addEventListener('DOMContentLoaded', () => {
    // Initialize Vanta
    if (typeof VANTA !== 'undefined') {
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
    }

    const quizData = JSON.parse(localStorage.getItem('lastQuizResult'));

    if (!quizData) {
        window.location.href = '/dashboard';
        return;
    }

    renderResults(quizData);

    const retakeBtn = document.getElementById('retake-btn');
    if (retakeBtn) {
        retakeBtn.onclick = () => {
            window.location.href = `/quiz_page?topic=${encodeURIComponent(quizData.topic)}`;
        };
    }

    function renderResults(data) {
        const analysis = data.analysis;

        // Update Metrics
        const accVal = document.getElementById('accuracy-value');
        const masteryVal = document.getElementById('mastery-value');
        const scoreVal = document.getElementById('score-value');
        
        if (accVal) {
            const acc = Math.round(analysis.accuracy);
            accVal.textContent = `${acc}%`;
            document.getElementById('accuracy-circle').style.background = `conic-gradient(var(--primary) 0%, var(--primary) ${acc}%, rgba(255, 255, 255, 0.1) ${acc}%, rgba(255, 255, 255, 0.1) 100%)`;
        }
        if (masteryVal) {
            const mast = Math.round(analysis.mastery);
            masteryVal.textContent = `${mast}%`;
            document.getElementById('mastery-circle').style.background = `conic-gradient(var(--secondary) 0%, var(--secondary) ${mast}%, rgba(255, 255, 255, 0.1) ${mast}%, rgba(255, 255, 255, 0.1) 100%)`;
        }
        if (scoreVal) {
            const scorePercent = (data.score / data.total) * 100;
            scoreVal.textContent = `${data.score}/${data.total}`;
            const scoreCircle = document.getElementById('score-circle');
            if (scoreCircle) {
                scoreCircle.style.background = `conic-gradient(#10b981 0%, #10b981 ${scorePercent}%, rgba(255, 255, 255, 0.1) ${scorePercent}%, rgba(255, 255, 255, 0.1) 100%)`;
            }
        }

        // Expert Remark (Top)
        const topRemark = document.getElementById('top-remark-content');
        if (topRemark) {
            topRemark.textContent = "Great job finishing the quiz! Review your detailed expert analysis below.";
        }

        // Expert Feedback (Bottom)
        const bottomSummary = document.getElementById('bottom-summary-content');
        if (bottomSummary) {
            bottomSummary.textContent = analysis.summary;
        }

        // Concept Weaver Logic
        const cw = analysis.concept_weaver;
        const cwContainer = document.getElementById('concept-weaver-container');
        if (cw && cw.foundational_gap && cwContainer) {
            cwContainer.classList.remove('hidden');
            document.getElementById('foundational-gap-title').textContent = `Foundational Gap: ${cw.foundational_gap}`;
            document.getElementById('bridge-lesson-text').textContent = cw.bridge_lesson;
            document.getElementById('why-it-matters-text').textContent = cw.why_it_matters;

            const voiceBtn = document.getElementById('voice-lesson-btn');
            if (voiceBtn) voiceBtn.onclick = () => speakLesson(cw.bridge_lesson, voiceBtn);

            const videoBtn = document.getElementById('video-lesson-btn');
            if (videoBtn) {
                videoBtn.onclick = () => {
                    const query = encodeURIComponent(cw.youtube_query || cw.foundational_gap);
                    window.open(`https://www.youtube.com/results?search_query=${query}`, '_blank');
                };
            }
        }

        // Recommendations
        const recContainer = document.getElementById('course-recommendations');
        const recommendationsSection = document.getElementById('recommendations-section');
        if (recContainer && recommendationsSection && analysis.recommendations && analysis.recommendations.length > 0) {
            recommendationsSection.classList.remove('hidden');
            recContainer.innerHTML = '';
            analysis.recommendations.forEach(rec => {
                const card = document.createElement('div');
                card.className = 'course-card';
                card.innerHTML = `
                    <div class="course-platform">${rec.platform}</div>
                    <h4 class="course-title">${rec.title}</h4>
                    <p class="course-desc">${rec.description}</p>
                    <a href="${rec.link}" target="_blank" class="course-link">View Course →</a>
                `;
                recContainer.appendChild(card);
            });
        }

        // Wrong Answers Review
        const wrongContainer = document.getElementById('wrong-answers-container');
        const toggleBtn = document.getElementById('toggle-review-btn');
        const reviewSection = document.getElementById('review-section');

        if (wrongContainer) {
            wrongContainer.innerHTML = '';
            const wrongAnswers = data.results.filter(r => !r.is_correct);

            if (wrongAnswers.length === 0) {
                wrongContainer.innerHTML = '<p class="success-msg">Perfect score! No mistakes to review. 🌟</p>';
            } else {
                if (toggleBtn) toggleBtn.classList.remove('hidden');
                wrongAnswers.forEach((ans, index) => {
                    const explainObj = analysis.wrong_answers.find(w => w.question === ans.question);
                    const card = document.createElement('div');
                    card.className = 'review-card wrong';
                    card.style.animationDelay = `${index * 0.1}s`;
                    
                    card.innerHTML = `
                        <div class="review-q">${ans.question}</div>
                        <div class="review-ans-row">
                            <span class="label">Your Answer</span>
                            <span class="val wrong">${ans.user_answer}</span>
                        </div>
                        <div class="review-ans-row">
                            <span class="label">Correct Answer</span>
                            <span class="val correct">${ans.correct_answer}</span>
                        </div>
                        <div class="review-explanation">
                            ${explainObj ? explainObj.explanation : 'Check your foundational knowledge of this topic.'}
                        </div>
                    `;
                    wrongContainer.appendChild(card);
                });
            }
        }

        if (toggleBtn && reviewSection) {
            toggleBtn.onclick = () => {
                const isHidden = reviewSection.classList.toggle('hidden');
                toggleBtn.textContent = isHidden ? 'View Details & Mistakes →' : 'Hide Detailed Review';
                if (!isHidden) {
                    reviewSection.scrollIntoView({ behavior: 'smooth' });
                }
            };
        }
    }
});

function speakLesson(text, btn) {
    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        btn.classList.remove('active');
        btn.innerHTML = '<span class="btn-icon">🔊</span> Listen to Mentor';
        return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1.0;

    utterance.onstart = () => {
        btn.classList.add('active');
        btn.innerHTML = '<span class="btn-icon">⏹️</span> Stop Listening';
    };

    utterance.onend = () => {
        btn.classList.remove('active');
        btn.innerHTML = '<span class="btn-icon">🔊</span> Listen to Mentor';
    };

    window.speechSynthesis.speak(utterance);
}
