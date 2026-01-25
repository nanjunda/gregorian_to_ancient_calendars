        // Global toggle function
        function toggleSignificance(btn) {
            const container = btn.parentElement;
            container.classList.toggle('minimized');
            btn.textContent = container.classList.contains('minimized') ? '+' : '−';
        }

        // ... existing scripts ...
        document.addEventListener('DOMContentLoaded', async () => {
            console.log("Insights page initialized.");

            // Priority 1: Data passed directly from server (v5.0 robust delivery)
            const activeCiv = "{{ active_civ }}";
            let insightData = {% if initial_data %}{{ initial_data | tojson | safe }}{% else %}null{% endif %};

        // Priority 2: Fallback to storage if page was refreshed or direct access
        if (!insightData) {
            console.log("No server-side data found, checking local storage...");
            const storageKey = activeCiv === 'panchanga' ? 'lastPanchangaResult' : `last${activeCiv.charAt(0).toUpperCase() + activeCiv.slice(1)}Result`;
            const rawData = localStorage.getItem(storageKey) || localStorage.getItem('lastHubResult');
            if (rawData) {
                try { insightData = JSON.parse(rawData); } catch (e) { }
            }
        }

        const display = document.getElementById('insight-display');
        const loader = document.getElementById('loading-insights');
        const configTitle = document.getElementById('config-title');

        if (!insightData) {
            display.innerHTML = `
                    <div style="text-align: center; padding: 2rem;">
                        <p style="color: var(--secondary); font-weight: bold; font-size: 1.2rem;">⚠️ Astronomical Configuration Missing</p>
                        <p>The Wisdom Engine needs a specific moment in time to explain.</p>
                        <p style="margin-top: 1rem;"><strong>Please go back, run a conversion, then click Explore Insights.</strong></p>
                    </div>
                `;
            display.classList.remove('hidden');
            loader.classList.add('hidden');
            return;
        }

        if (activeCiv === 'mayan') {
            configTitle.textContent = `${insightData.long_count.formatted} | ${insightData.tzolkin.formatted}`;
        } else {
            configTitle.textContent = `${insightData.masa} ${insightData.samvatsara} | ${insightData.tithi}`;
        }

        try {
            const response = await fetch('/api/ai-explain', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(insightData)
            });

            const result = await response.json();

            if (result.success) {
                // Defensive Parsing
                let rawInsight = result.insight || "";
                if (typeof rawInsight !== 'string') rawInsight = JSON.stringify(rawInsight);

                let htmlContent = "";
                function robustMarkdown(text) {
                    // Custom high-resilience student-friendly fallback
                    return text
                        .replace(/^# (.*$)/gim, '<h1 style="color:var(--secondary);border-bottom:2px solid var(--secondary);padding-bottom:10px;margin-bottom:20px;">🚀 $1</h1>')
                        .replace(/^## (.*$)/gim, '<h2 style="color:var(--secondary);margin-top:30px;">🛰️ $1</h2>')
                        .replace(/^### (.*$)/gim, '<h3 style="color:var(--secondary);margin-top:20px;">🔬 $1</h3>')
                        .replace(/^\s*[\-\*] (.*$)/gim, '<li style="margin-left:20px;list-style:none;">✨ $1</li>')
                        .replace(/\*\*(.*?)\*\*/gim, '<strong style="color:var(--secondary);">$1</strong>')
                        .replace(/\n/g, '<br>');
                }

                try {
                    htmlContent = robustMarkdown(rawInsight);
                } catch (pe) {
                    console.error("Markdown parse failed:", pe);
                    htmlContent = rawInsight.replace(/\n/g, '<br>');
                }

                const panchangaGlossary = {
                    'epoch': { def: 'A fixed point in time used as a reference point.', target: null },
                    'jovian': { def: 'Relating to Jupiter. The 60-year Samvatsara cycle follows Jupiter\'s path.', target: 'SAMVATSARA_RESONANCE' },
                    'precession': { def: 'The slow conical wobble of Earth\'s axis (25,800 year cycle).', target: 'PRECESSION_WOBBLE' },
                    'sidereal': { def: 'Measured relative to fixed stars (Hindu system).', target: 'ZODIAC_COMPARISON' },
                    'ayanamsha': { def: 'The angular drift (24°) between seasons and stars.', target: 'ZODIAC_COMPARISON' },
                    'tithi': { def: 'A lunar day, defined by every 12° of Sun-Moon separation.', target: 'MOON_PHASE_3D' },
                    'nakshatra': { def: 'Star clusters the moon visits daily.', target: 'CONSTELLATION_MAP' },
                    'masa': { def: 'A month in the Hindu calendar. It can be Solar (Saura) or Lunar (Chandra).', target: null },
                    'saura mana': { def: 'Solar Month system. Defined by the Sun\'s entry into a new Zodiac sign.', target: 'ZODIAC_COMPARISON' },
                    'chandra mana': { def: 'Luni-Solar Month system. Defined by the Moon\'s phase cycle.', target: 'MOON_PHASE_3D' },
                    'adhik masa': { def: 'The \'Extra Month\' (Pit Stop) added every ~3 years to let the Sun catch up.', target: 'CALENDAR_DRIFT' }
                };



                const glossary = panchangaGlossary;

                for (const [term, data] of Object.entries(glossary)) {
                    const regex = new RegExp(`\\b${term}\\b`, 'gi');
                    htmlContent = htmlContent.replace(regex, (match) => {
                        return `<span class="reactive-term" onclick="triggerVisualHighlight('${data.target}')">${match}<span class="tooltip-bubble">${data.def} ${data.target ? '<br><i>(Click to see 3D visual)</i>' : ''}</span></span>`;
                    });
                }

                // Dynamic 3D Tag Injection (v5.0 Penthouse Edition)
                const renderTags = {
                    'ZODIAC_COMPARISON': {
                        id: 'visual-zodiac',
                        url: '/visuals/zodiac-comparison',
                        preferredHeight: '800px',
                        caption: 'Interactive Zodiac Aligner',
                        significance: 'This simulation shows the "Great Drift" between Modern and Hindu astronomy.'
                    },
                    'MOON_PHASE_3D': {
                        id: 'visual-moon',
                        url: '/visuals/moon-phase',
                        preferredHeight: '520px',
                        caption: 'Tithi Phase Protractor',
                        significance: 'A Tithi (Lunar Day) is not a 24-hour clock. It is a geometric measurement of the angle between the Sun and Moon. Every 12° of separation creates one Tithi. This protractor shows how the phases we see from Earth are actually results of this specific celestial angle.'
                    },
                    'PRECESSION_WOBBLE': {
                        id: 'visual-precession',
                        url: '/visuals/precession',
                        preferredHeight: '520px',
                        caption: 'The Earth\'s Great Wobble',
                        significance: 'Imagine Earth as a spinning top that is starting to tilt. This "Precession" takes 25,800 years for one full circle. This wobble is the reason the Zodiac Aligner (above) needs a shift—the "beginning" of the stars has moved relative to our seasons!'
                    },
                    'CONSTELLATION_MAP': {
                        id: 'visual-constellations',
                        url: '/visuals/constellation',
                        preferredHeight: '520px',
                        caption: 'Sky Focus: Lunar Tracking',
                        significance: 'Interactive 3D Zodiac belt with symbols and names. Moon is shown in the foreground with slow orbital motion and simulated phases. Use mouse to rotate and zoom the view.'
                    },
                    'SAMVATSARA_RESONANCE': {
                        id: 'visual-samvatsara',
                        url: '/visuals/samvatsara',
                        preferredHeight: '520px',
                        caption: 'Jovian-Saturn Samvatsara Resonance',
                        significance: 'This visual shows why the Samvatsara cycle is 60 years. It tracks the resonance between Jupiter (~11.86y) and Saturn (~29.46y). Broadly, every 5 Jupiter orbits align with 2 Saturn orbits, creating a rhythmic "Great Conjunction" that resets the traditional calendar cycle.'
                    },
                };

                function parseVisualTags(content) {
                    return content.replace(/\[\[RENDER:(.*?)\]\]/g, (match, tagName) => {
                        const tag = renderTags[tagName.trim()];
                        if (tag) {
                            return `
                                    <div id="${tag.id}" class="visual-block-wrapper" style="margin: 2.5rem 0;">
                                        <div class="visual-block card glass" style="margin-bottom: 0;">
                                            <div class="visual-loading">Launching 3D Module...</div>
                                            <div class="visual-wrapper" style="height: ${tag.preferredHeight};">
                                                <iframe class="visual-iframe" style="height: 100%;" src="${tag.url}?samvatsara=${encodeURIComponent(insightData.samvatsara || '')}&tithi=${encodeURIComponent(insightData.tithi || '')}&rashi=${encodeURIComponent(insightData.rashi?.name || 'Leo')}" onload="this.parentElement.previousElementSibling.style.display='none'"></iframe>
                                            </div>
                                            <div class="visual-caption">🖥️ ${tag.caption}</div>
                                        </div>
                                        <div class="visual-significance">
                                            <button class="minimize-btn" onclick="toggleSignificance(this)">−</button>
                                            <strong>Significance:</strong> ${tag.significance}
                                        </div>
                                    </div>
                                `;
                        }
                        return `<p style="color:red">[System: Rendering ${tagName} failed - Module not found]</p>`;
                    });
                }

                htmlContent = parseVisualTags(htmlContent);

                display.innerHTML = htmlContent;
                display.classList.remove('hidden');
                loader.classList.add('hidden');

            } else {
                display.innerHTML = `<p>Error generating insights: ${result.error}</p>`;
                display.classList.remove('hidden');
                loader.classList.add('hidden');
            }
        } catch (error) {
            console.error("Fetch Error:", error);
            display.innerHTML = "<p>Failed to connect to the Wisdom Engine. Please try again later.</p>";
            display.classList.remove('hidden');
            loader.classList.add('hidden');
        }
        });

        // Global function for Reactive Glossary triggers
        function triggerVisualHighlight(tagId) {
            if (!tagId) return;

            const renderTags = {
                'ZODIAC_COMPARISON': 'visual-zodiac',
                'MOON_PHASE_3D': 'visual-moon',
                'PRECESSION_WOBBLE': 'visual-precession',
                'CONSTELLATION_MAP': 'visual-constellations',
                'SAMVATSARA_RESONANCE': 'visual-samvatsara',
                'CALENDAR_DRIFT': 'time-machine-section',
                'VIGESEL_ODOOMETER': 'visual-mayan-gears',
                'GEAR_INTERLOCK_52YR': 'visual-calendar-round',
                'VENUS_MARS_ALIGNMENT': 'visual-venus-cycle'
            };

            const elementId = renderTags[tagId];
            const targetEl = document.getElementById(elementId);

            if (targetEl) {
                // 1. Smooth Scroll to Visual
                targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });

                // 2. Visual Feedback (Flash)
                targetEl.style.transition = "box-shadow 0.5s";
                targetEl.style.boxShadow = "0 0 30px var(--secondary)";
                setTimeout(() => {
                    targetEl.style.boxShadow = "none";
                }, 1000);

                // 3. Message Passing (v5.1 Advanced)
                const iframe = targetEl.querySelector('iframe');
                if (iframe && iframe.contentWindow) {
                    iframe.contentWindow.postMessage({ action: 'pulse', term: tagId }, '*');
                }
            }
        }

        // Chatbot Functionality (v5.4)
        function toggleChat() {
            const window = document.getElementById('chat-window');
            window.classList.toggle('active');
        }

        async function sendMessage() {
            const input = document.getElementById('chat-input');
            const messages = document.getElementById('chat-messages');
            const text = input.value.trim();
            if (!text) return;

            // 1. Append User Message
            const userMsg = document.createElement('div');
            userMsg.className = 'message user';
            userMsg.textContent = text;
            messages.appendChild(userMsg);
            input.value = '';
            messages.scrollTop = messages.scrollHeight;

            // 2. Append Loading Sages
            const botMsg = document.createElement('div');
            botMsg.className = 'message bot';
            botMsg.innerHTML = 'Analyzing the heavens<span class="dots"></span>';
            messages.appendChild(botMsg);
            messages.scrollTop = messages.scrollHeight;

            try {
                // Get context from global insightData
                // Get context safely - chat can happen even if insightData is partial
                const context = {
                    address: (typeof insightData !== 'undefined') ? insightData?.address : "Unknown Location",
                    samvatsara: (typeof insightData !== 'undefined') ? insightData?.samvatsara : "Unknown",
                    masa: (typeof insightData !== 'undefined') ? insightData?.masa : "Unknown",
                    tithi: (typeof insightData !== 'undefined') ? insightData?.tithi : "Unknown",
                    nakshatra: (typeof insightData !== 'undefined') ? insightData?.nakshatra : "Unknown"
                };

                const response = await fetch('/api/ai-chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, context })
                });

                const result = await response.json();
                botMsg.textContent = result.success ? result.response : "The star-link is fuzzy... " + result.error;
            } catch (err) {
                botMsg.textContent = "Connection Error: " + err.message;
                console.error("Chat Error:", err);
            }
            messages.scrollTop = messages.scrollHeight;
        }

        // --- Version 6.0 Engagement Logic ---

        function initMaestrosChallenge() {
            const quizSection = document.getElementById('quiz-section');
            const questionEl = document.getElementById('quiz-question');
            const optionsEl = document.getElementById('quiz-options');
            const feedbackEl = document.getElementById('quiz-feedback');

            const questions = [
                {
                    q: "Why does the 'Panchanga Birthday' drift away from the Gregorian date?",
                    options: [
                        "Earth's rotation slowing down",
                        "The ~11 day gap between Lunar and Solar years",
                        "Magnetic pole reversal",
                        "Standard human error"
                    ],
                    correct: 1,
                    explanation: "Correct! A lunar year is roughly 354 days, while a solar year is 365. This 11-day gap causes the drift."
                },
                {
                    q: "What is the 60-year Jupiter-Saturn cycle called?",
                    options: [
                        "Masa",
                        "Tithi",
                        "Samvatsara",
                        "Yoga"
                    ],
                    correct: 2,
                    explanation: "Exactly! Samvatsara cycles align with the major resonances of our solar system's giants."
                }
            ];

            const quiz = questions[Math.floor(Math.random() * questions.length)];
            questionEl.textContent = quiz.q;
            optionsEl.innerHTML = '';
            feedbackEl.textContent = '';
            quizSection.classList.remove('hidden');

            quiz.options.forEach((opt, idx) => {
                const btn = document.createElement('div');
                btn.className = 'quiz-option';
                btn.textContent = opt;
                btn.onclick = () => {
                    if (feedbackEl.textContent) return; // Prevent multiple clicks
                    if (idx === quiz.correct) {
                        btn.classList.add('correct');
                        feedbackEl.textContent = "🌟 " + quiz.explanation;
                        feedbackEl.style.color = "#00ff7f";
                    } else {
                        btn.classList.add('wrong');
                        feedbackEl.textContent = "🔭 Not quite! The correct answer was: " + quiz.options[quiz.correct];
                        feedbackEl.style.color = "#ff5733";
                    }
                };
                optionsEl.appendChild(btn);
            });
        }

        function initBirthdayTimeMachine() {
            const tmSection = document.getElementById('time-machine-section');
            const scrubber = document.getElementById('timeline-scrubber');
            const yearDisplay = document.getElementById('year-display-huge');
            const pointer = document.getElementById('sync-pointer');
            const expl = document.getElementById('drift-explanation');

            tmSection.classList.remove('hidden');

            function updateTimeMachine(year) {
                yearDisplay.textContent = year;

                // Deterministic Drift Physics (v6.0.1)
                // Base: Lunar year is 11 days shorter than Solar.
                // Reset: Every 3 years (approx) an Adhika Masa (30 days) pulls it back.
                const anchorYear = 2025;
                const yearsPassed = year - anchorYear;

                // Cumulative raw drift in days
                let rawDrift = yearsPassed * 11;

                // Number of Adhika Masas added (approx 1 every 2.7 years)
                const leapMonths = Math.floor((yearsPassed + 1.2) / 2.7);
                const effectiveDrift = (rawDrift - (leapMonths * 30)) % 30;

                // Map effectiveDrift (-15 to +15 ideally) to the Sync Meter (10% to 90%)
                const percentage = 50 + (effectiveDrift * 2.5);
                pointer.style.left = `${Math.max(5, Math.min(95, percentage))}%`;

                const driftAbs = Math.abs(Math.round(effectiveDrift));
                const direction = effectiveDrift > 0 ? "later" : "earlier";

                let physicsNote = "";
                if (driftAbs < 3) {
                    physicsNote = " ✨ <strong>COSMIC SYNC!</strong> In this year, the solar and lunar cycles align perfectly.";
                } else if (leapMonths !== Math.floor((year - 1 - anchorYear + 1.2) / 2.7)) {
                    physicsNote = " 🚀 <strong>ADHIKA MASA RESET!</strong> A leap month was added recently to stop your birthday from drifting out of its season.";
                }

                expl.innerHTML = `<strong>Year ${year}:</strong> Your Panchanga birthday falls approximately <strong>${driftAbs} days ${direction}</strong> than your Gregorian birthday. Since the Moon travels faster than our seasonal calendar, it creates this rhythmic drift.${physicsNote}`;
            }

            scrubber.oninput = (e) => updateTimeMachine(parseInt(e.target.value));

            // Start at 2025
            updateTimeMachine(2025);
        }

        // Add to main initialization
        window.addEventListener('load', () => {
            setTimeout(() => {
                initMaestrosChallenge();
                initBirthdayTimeMachine();
            }, 2000);
        });
