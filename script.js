document.addEventListener('DOMContentLoaded', () => {
    const dashboardGrid = document.getElementById('dashboardGrid');
    const sportNav = document.getElementById('sportNav');

    // Embedded Data for compatibility (CORS-free)
    const sportsData = [
        {
            "id": "soccer",
            "name": "Soccer",
            "icon": "⚽",
            "matches": [
                {"home": "Man City", "away": "Arsenal", "league": "EPL", "prob_home": 0.54, "prob_draw": 0.26, "prob_away": 0.20, "score_home": 2, "score_away": 1, "status": "Upcoming"},
                {"home": "Real Madrid", "away": "Barcelona", "league": "La Liga", "prob_home": 0.48, "prob_draw": 0.22, "prob_away": 0.30, "score_home": 2, "score_away": 1, "status": "Live"},
                {"home": "Ulsan HD", "away": "Jeonbuk", "league": "K-League", "prob_home": 0.45, "prob_draw": 0.30, "prob_away": 0.25, "score_home": 1, "score_away": 0, "status": "Upcoming"}
            ]
        },
        {
            "id": "basketball",
            "name": "Basketball",
            "icon": "🏀",
            "matches": [
                {"home": "LA Lakers", "away": "Golden State", "league": "NBA", "prob_home": 0.49, "prob_away": 0.51, "score_home": 112, "score_away": 115, "status": "Upcoming"},
                {"home": "Anyang KGC", "away": "Seoul SK", "league": "KBL", "prob_home": 0.42, "prob_away": 0.58, "score_home": 82, "score_away": 88, "status": "Finished"}
            ]
        },
        {
            "id": "baseball",
            "name": "Baseball",
            "icon": "⚾",
            "matches": [
                {"home": "LG Twins", "away": "KT Wiz", "league": "KBO", "prob_home": 0.52, "prob_away": 0.48, "score_home": 5, "score_away": 4, "status": "Live"},
                {"home": "NY Yankees", "away": "Boston Red Sox", "league": "MLB", "prob_home": 0.55, "prob_away": 0.45, "score_home": 7, "score_away": 5, "status": "Upcoming"}
            ]
        },
        {
            "id": "volleyball",
            "name": "Volleyball",
            "icon": "🏐",
            "matches": [
                {"home": "Korean Air", "away": "Hyundai Capital", "league": "V-League (M)", "prob_home": 0.60, "prob_away": 0.40, "score_home": 3, "score_away": 2, "status": "Upcoming"}
            ]
        }
    ];

    // Initialize UI
    renderMatches('all');
    setupNavigation();

    function setupNavigation() {
        sportNav.addEventListener('click', (e) => {
            const navItem = e.target.closest('.nav-item');
            if (!navItem) return;

            // Update UI
            document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
            navItem.classList.add('active');

            // Filter data
            const sportId = navItem.dataset.sport;
            renderMatches(sportId);
        });
    }

    function renderMatches(sportId) {
        dashboardGrid.innerHTML = '';
        
        let matchesToRender = [];
        if (sportId === 'all') {
            sportsData.forEach(sport => {
                sport.matches.forEach(match => {
                    matchesToRender.push({ ...match, sportName: sport.name, sportIcon: sport.icon });
                });
            });
        } else {
            const sport = sportsData.find(s => s.id === sportId);
            if (sport) {
                sport.matches.forEach(match => {
                    matchesToRender.push({ ...match, sportName: sport.name, sportIcon: sport.icon });
                });
            }
        }

        if (matchesToRender.length === 0) {
            dashboardGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: #94a3b8;">해당 종목의 예정된 매치가 없습니다.</div>';
            return;
        }

        matchesToRender.forEach(match => {
            const card = createMatchCard(match);
            dashboardGrid.appendChild(card);
        });
    }

    function createMatchCard(match) {
        const div = document.createElement('div');
        div.className = 'match-card';
        
        const isLive = match.status === 'Live';
        const probHome = (match.prob_home * 100).toFixed(0);
        const probDraw = match.prob_draw ? (match.prob_draw * 100).toFixed(0) : 0;
        // Total prob for draw logic
        const totalProb = match.prob_draw ? (match.prob_home + match.prob_draw + match.prob_away) : (match.prob_home + match.prob_away);
        const probAway = (match.prob_away * 100).toFixed(0);

        div.innerHTML = `
            <div class="league-badge">${match.league}</div>
            <div class="match-status">
                ${isLive ? '<span class="dot-live"></span>' : ''}
                ${match.status}
            </div>
            
            <div class="teams">
                <div class="team">
                    <div class="team-logo">${match.sportIcon}</div>
                    <div class="team-name">${match.home}</div>
                </div>
                <div class="vs">VS</div>
                <div class="team">
                    <div class="team-logo">${match.sportIcon}</div>
                    <div class="team-name">${match.away}</div>
                </div>
            </div>

            <div class="prediction-section">
                <div class="prob-labels">
                    <span>Home ${probHome}%</span>
                    ${match.prob_draw ? `<span>Draw ${probDraw}%</span>` : ''}
                    <span>Away ${probAway}%</span>
                </div>
                <div class="prob-container">
                    <div class="prob-home" style="width: ${probHome}%"></div>
                    ${match.prob_draw ? `<div class="prob-draw" style="width: ${probDraw}%"></div>` : ''}
                    <div class="prob-away" style="width: ${probAway}%"></div>
                </div>
            </div>

            <div style="margin-top: 1.5rem; text-align: center; font-size: 0.9rem; color: #94a3b8;">
                AI Score Prediction: <span style="color: #CCFF00; font-weight: 700;">${match.score_home} - ${match.score_away}</span>
            </div>
        `;

        return div;
    }
});
