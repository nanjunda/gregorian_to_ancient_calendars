document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('panchanga-form');
    const resultContainer = document.getElementById('result-container');
    const loader = document.getElementById('loader');
    const geoBtn = document.getElementById('geo-btn');
    const locationInput = document.getElementById('location');

    // Set default date and time to now
    const now = new Date();
    document.getElementById('date').value = now.toISOString().split('T')[0];
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    document.getElementById('time').value = `${hours}:${minutes}`;

    let selectedLang = 'EN';

    // Language Selector
    const langBtns = document.querySelectorAll('.lang-btn');
    langBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            langBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedLang = btn.getAttribute('data-lang');
        });
    });

    // Geolocation Support
    geoBtn.addEventListener('click', () => {
        if (!navigator.geolocation) {
            alert('Geolocation is not supported by your browser');
            return;
        }

        geoBtn.style.opacity = '0.3';
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                // For simplicity in this demo, we can just put the coords
                // But typically you'd reverse geocode here. 
                // Our backend handles names, so let's use Lat/Long directly if nominatim supports it
                locationInput.value = `${lat}, ${lon}`;
                geoBtn.style.opacity = '1';
            },
            (error) => {
                alert('Unable to retrieve your location');
                geoBtn.style.opacity = '1';
            }
        );
    });

    // Get active civilization from URL path if possible
    const pathParts = window.location.pathname.split('/');
    const activeCiv = pathParts[pathParts.length - 1] || 'panchanga';

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            calendar: activeCiv,
            date: document.getElementById('date').value,
            time: document.getElementById('time').value,
            location: locationInput.value,
            lang: selectedLang,
            title: document.getElementById('title').value
        };

        // Show loader, hide results
        loader.classList.remove('hidden');
        resultContainer.classList.add('hidden');

        try {
            const response = await fetch('/api/v2/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (result.status === "success") {
                renderResult(result);
            } else {
                alert('Error: ' + (result.message || result.error));
            }
        } catch (error) {
            console.error('Fetch error:', error);
            alert('An error occurred while fetching data.');
        } finally {
            loader.classList.add('hidden');
        }
    });

    const downloadBtn = document.getElementById('download-ical-btn');
    downloadBtn.addEventListener('click', async () => {
        const data = {
            calendar: activeCiv,
            title: document.getElementById('title').value,
            date: document.getElementById('date').value,
            time: document.getElementById('time').value,
            location: locationInput.value,
            lang: selectedLang
        };

        downloadBtn.textContent = 'Generating...';
        downloadBtn.disabled = true;

        try {
            const response = await fetch('/api/generate-ical', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${data.title.replace(/\s+/g, '_')}.ics`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                const err = await response.json();
                alert('Error generating iCal: ' + err.error);
            }
        } catch (error) {
            console.error('iCal error:', error);
            alert('Failed to generate iCal file.');
        } finally {
            downloadBtn.textContent = 'Download Next 20 Occurrences (.ics)';
            downloadBtn.disabled = false;
        }
    });

    function renderResult(fullResponse) {
        const data = fullResponse.results;
        const metadata = fullResponse.metadata;
        const civSpecific = data.civilization_specific;

        // Use user-provided title for the header
        document.getElementById('res-title').textContent = document.getElementById('title').value || `${activeCiv.toUpperCase()} Result`;
        document.getElementById('res-location').textContent = `${locationInput.value}`;

        // Clear and rebuild the grid dynamically
        const grid = document.querySelector('.grid');
        grid.innerHTML = '';

        // Function to build a grid item
        const addGridItem = (label, value) => {
            const item = document.createElement('div');
            item.className = 'grid-item';
            item.innerHTML = `
                <span class="label">${label}</span>
                <span class="value">${value}</span>
            `;
            grid.appendChild(item);
        };

        // Logic for different civilizations
        if (activeCiv === 'panchanga') {
            addGridItem('Samvatsara', civSpecific.samvatsara);
            addGridItem('Saka Varsha', civSpecific.saka_year);
            addGridItem('Masa', civSpecific.masa);
            addGridItem('Paksha', civSpecific.paksha);
            addGridItem('Tithi', civSpecific.tithi);
            addGridItem('Vara', civSpecific.vara);
            addGridItem('Nakshatra', civSpecific.nakshatra);
            addGridItem('Yoga', civSpecific.yoga);
            addGridItem('Rashi', data.coordinates.rashi.name);
            addGridItem('Lagna', data.coordinates.lagna.name);
        } else if (activeCiv === 'mayan') {
            addGridItem('Long Count', civSpecific.long_count.formatted);
            addGridItem('Tzolk\'in', civSpecific.tzolkin.formatted);
            addGridItem('Haab\'', civSpecific.haab.formatted);
            addGridItem('Baktun', civSpecific.long_count.baktun);
            addGridItem('Katun', civSpecific.long_count.katun);
            addGridItem('Tun', civSpecific.long_count.tun);
            addGridItem('Uinal', civSpecific.long_count.uinal);
            addGridItem('Kin', civSpecific.long_count.kin);
        }

        // Persist data for AI insights page (Zero Mutation for Panchanga)
        try {
            const insightData = {
                ...civSpecific,
                ...data.coordinates,
                ...data.astronomy,
                metadata: metadata,
                input_datetime: `${document.getElementById('date').value} ${document.getElementById('time').value}`
            };
            const dataStr = JSON.stringify(insightData);

            // 1. Separate Storage for zero mutation
            if (activeCiv === 'panchanga') {
                localStorage.setItem('lastPanchangaResult', dataStr);
                sessionStorage.setItem('lastPanchangaResult', dataStr);
            } else {
                localStorage.setItem(`last${activeCiv.charAt(0).toUpperCase() + activeCiv.slice(1)}Result`, dataStr);
            }

            // 2. Unified hub storage for the new /insights page
            localStorage.setItem('lastHubResult', dataStr);
            console.log(`${activeCiv.toUpperCase()} results persisted.`);
        } catch (e) {
            console.warn("Storage warning: Could not persist data for AI insights.", e);
        }

        // Handle AI Insight Link (Dynamic Routing)
        const aiLink = document.getElementById('ai-insight-link');
        if (aiLink) {
            aiLink.onclick = (e) => {
                e.preventDefault();
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = `/insights/${activeCiv}`;
                const hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'hub_data'; // Renamed for hub generality
                hiddenInput.value = localStorage.getItem('lastHubResult');
                form.appendChild(hiddenInput);
                document.body.appendChild(form);
                form.submit();
            };
        }

        // Next Occurrence
        const eventTitle = document.getElementById('title').value || 'Event';
        const nextLabel = activeCiv === 'panchanga' ? 'Hindu Panchanga' : 'Mayan Calendar Round';
        document.getElementById('res-next-occurrence-label').textContent = `✨ Next occurrence as per ${nextLabel}: ${eventTitle}`;
        document.getElementById('res-next-birthday').textContent = data.astronomy.next_birthday || 'See iCal for details';

        // Sunrise/Sunset
        document.getElementById('res-sunrise').textContent = data.astronomy.sunrise || '-';
        document.getElementById('res-sunset').textContent = data.astronomy.sunset || '-';

        // Show result grid again
        resultContainer.classList.remove('hidden');
        resultContainer.scrollIntoView({ behavior: 'smooth' });

        // Load visual snippets
        loadSkyshot({
            calendar: activeCiv,
            date: document.getElementById('date').value,
            time: document.getElementById('time').value,
            location: locationInput.value,
            title: document.getElementById('title').value
        });

        loadSolarSystem({
            calendar: activeCiv,
            date: document.getElementById('date').value,
            time: document.getElementById('time').value,
            location: locationInput.value,
            title: document.getElementById('title').value
        });
    }

    async function loadSkyshot(data) {
        const skyshotSection = document.getElementById('skyshot-section');
        const skyshotImage = document.getElementById('skyshot-image');
        const skyshotLoader = document.getElementById('skyshot-loader');
        const skyshotCaption = document.getElementById('skyshot-caption');
        const skyshotMainTitle = document.getElementById('skyshot-main-title');
        const skyshotTitleArea = document.getElementById('skyshot-dynamic-title');

        // Show section and loader
        skyshotSection.classList.remove('hidden');
        skyshotLoader.classList.remove('hidden');
        skyshotTitleArea.style.opacity = '0.3'; // Dim title while loading
        skyshotImage.style.display = 'none';

        try {
            const response = await fetch('/api/skyshot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                // Update HTML Title Area (v4.1 fix for truncation)
                // Zero Mutation: Keep 'Nakshatra' for Panchanga, use 'Long Count' for Mayan
                const displayTitle = (activeCiv === 'panchanga') ? (result.nakshatra || 'Unknown Nakshatra') : (civSpecific.long_count ? `Long Count: ${civSpecific.long_count.formatted}` : 'Celestial Alignment');
                skyshotMainTitle.textContent = displayTitle;
                skyshotTitleArea.style.opacity = '1';

                // Use Base64 data directly
                skyshotImage.src = result.image_data;
                skyshotImage.style.display = 'block';
                skyshotLoader.classList.add('hidden');

                // Update caption with coordinates
                if (result.moon_longitude) {
                    skyshotCaption.innerHTML = `Moon Position: <strong>${result.moon_longitude}°</strong> Sidereal  |  Phase: <strong>${result.phase_angle || 0}°</strong>`;
                }
            } else {
                console.error('Skyshot error:', result.error);
                skyshotSection.classList.add('hidden');
            }
        } catch (error) {
            console.error('Skyshot fetch error:', error);
            skyshotSection.classList.add('hidden');
        }
    }

    async function loadSolarSystem(data) {
        const solarSection = document.getElementById('solar-system-section');
        const solarImage = document.getElementById('solar-system-image');
        const solarLoader = document.getElementById('solar-loader');
        const solarTitleArea = document.getElementById('solar-dynamic-title');
        const solarMainTitle = document.getElementById('solar-main-title');

        // Show section and loader
        solarSection.classList.remove('hidden');
        solarLoader.classList.remove('hidden');
        solarTitleArea.style.opacity = '0.3'; // Dim while loading
        solarImage.style.display = 'none';

        try {
            const response = await fetch('/api/solar-system', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                // Update HTML Title (v4.1)
                solarMainTitle.textContent = data.title || 'Cosmic Alignment';
                solarTitleArea.style.opacity = '1';

                // Use Base64 data directly
                solarImage.src = result.image_data;
                solarImage.style.display = 'block';
                solarLoader.classList.add('hidden');

                // Show Astronomical Insights (v4.1.1)
                document.getElementById('astronomical-insights').classList.remove('hidden');
            } else {
                console.error('Solar System error:', result.error);
                solarSection.classList.add('hidden');
            }
        } catch (error) {
            console.error('Solar System fetch error:', error);
            solarSection.classList.add('hidden');
        }
    }
});
