document.addEventListener('DOMContentLoaded', () => {
    // Initialize Vanta Background
    const vantaEffect = VANTA.NET({
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

    const cards = document.querySelectorAll('.level-card');
    const cardsWrapper = document.getElementById('cards-wrapper');
    const hero = document.getElementById('main-hero');
    const resultsSection = document.getElementById('results-section');
    const resultsIcon = document.getElementById('results-icon');
    const resultsTitle = document.getElementById('results-title');
    const resultsContent = document.getElementById('results-content').querySelector('p');
    const backBtn = document.getElementById('back-btn');

    const levelData = {
        beginner: {
            icon: '🌱',
            title: 'Welcome Beginner!',
            content: 'We will start with the absolute fundamentals. Get ready to build your strong foundation. Redirecting to your learning path...'
        },
        intermediate: {
            icon: '🚀',
            title: 'Welcome Intermediate!',
            content: 'Nice! You have the basics down. Time to master core concepts and practical logic. Redirecting to your learning path...'
        },
        pro: {
            icon: '⚡',
            title: 'Pro Level Unlocked!',
            content: 'Ready for the complex stuff? We will dive deep into real-world architectures and advanced patterns. Redirecting to your learning path...'
        }
    };

    cards.forEach(card => {
        card.addEventListener('click', () => {
            const level = card.getAttribute('data-level');
            
            // Save level to localStorage
            localStorage.setItem('userLevel', level);

            // UI Transition
            hero.style.opacity = '0';
            cardsWrapper.style.opacity = '0';
            
            setTimeout(() => {
                hero.style.display = 'none';
                cardsWrapper.style.display = 'none';
                
                // Populate results
                resultsIcon.textContent = levelData[level].icon;
                resultsTitle.textContent = levelData[level].title;
                resultsContent.textContent = levelData[level].content;
                
                resultsSection.classList.remove('hidden');

                // Redirect after brief delay
                setTimeout(() => {
                    window.location.href = `/learning?level=${level}`;
                }, 2000);
            }, 500);
        });
    });

    backBtn.addEventListener('click', () => {
        resultsSection.classList.add('hidden');
        hero.style.display = 'block';
        cardsWrapper.style.display = 'flex';
        setTimeout(() => {
            hero.style.opacity = '1';
            cardsWrapper.style.opacity = '1';
        }, 10);
    });
});
