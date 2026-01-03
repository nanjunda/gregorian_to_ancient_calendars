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

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            title: document.getElementById('title').value,
            date: document.getElementById('date').value,
            time: document.getElementById('time').value,
            location: locationInput.value,
            lang: selectedLang
        };

        // Show loader, hide results
        loader.classList.remove('hidden');
        resultContainer.classList.add('hidden');

        try {
            const response = await fetch('/api/panchanga', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (result.success) {
                renderResult(result.data);
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            console.error('Fetch error:', error);
            alert('An error occurred while fetching Panchanga data.');
        } finally {
            loader.classList.add('hidden');
        }
    });

    const downloadBtn = document.getElementById('download-ical-btn');
    downloadBtn.addEventListener('click', async () => {
        const data = {
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
            downloadBtn.textContent = 'Download 20-Year iCal (.ics)';
            downloadBtn.disabled = false;
        }
    });

    function renderResult(data) {
        // Use user-provided title for the header
        document.getElementById('res-title').textContent = document.getElementById('title').value || 'Panchanga Result';
        document.getElementById('res-location').textContent = `${data.address} (${data.timezone})`;

        document.getElementById('res-samvatsara').textContent = data.samvatsara;
        document.getElementById('res-masa').textContent = data.masa;
        document.getElementById('res-paksha').textContent = data.paksha;
        document.getElementById('res-tithi').textContent = data.tithi;
        document.getElementById('res-vara').textContent = data.vara;
        document.getElementById('res-nakshatra').textContent = data.nakshatra;
        document.getElementById('res-yoga').textContent = data.yoga;
        document.getElementById('res-rashi').textContent = data.rashi.name;
        document.getElementById('res-lagna').textContent = data.lagna.name;

        // Simplified educational fact cards
        const factContainer = document.getElementById('fact-cards-container');
        factContainer.innerHTML = '';
        const angular = data.angular_data;
        const westernZodiacs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];
        const sunIdx = Math.floor(angular.sun_sidereal / 30) % 12;
        const moonIdx = Math.floor(angular.moon_sidereal / 30) % 12;
        const facts = [];
        facts.push({ title: 'Sun', text: `${westernZodiacs[sunIdx]} (sidereal)` });
        facts.push({ title: 'Moon', text: `${westernZodiacs[moonIdx]} (sidereal)` });
        // Moon phase description
        let phaseDesc = '';
        if (angular.phase_angle === 0) phaseDesc = 'New Moon';
        else if (angular.phase_angle === 180) phaseDesc = 'Full Moon';
        else phaseDesc = `${angular.phase_angle.toFixed(1)}° separation`;
        facts.push({ title: 'Moon Phase', text: phaseDesc });
        // Precision correction (Ayanamsha)
        facts.push({ title: 'Precision correction (Ayanamsha)', text: `${angular.ayanamsha.toFixed(2)}°` });
        // Render cards
        facts.forEach(f => {
            const card = document.createElement('div');
            card.className = 'grid-item';
            const label = document.createElement('span');
            label.className = 'label';
            label.textContent = f.title;
            const value = document.createElement('span');
            value.className = 'value';
            value.textContent = f.text;
            card.appendChild(label);
            card.appendChild(value);
            factContainer.appendChild(card);
        });

        // Populate sunrise and sunset times
        document.getElementById('res-sunrise').textContent = data.sunrise || '-';
        document.getElementById('res-sunset').textContent = data.sunset || '-';

        // Show the fact cards section
        document.getElementById('fact-cards').classList.remove('hidden');

        // Show result grid again
        resultContainer.classList.remove('hidden');
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }
});
