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
            location: locationInput.value
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
            location: locationInput.value
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
            downloadBtn.textContent = 'Download 10-Year iCal (.ics)';
            downloadBtn.disabled = false;
        }
    });

    function renderResult(data) {
        document.getElementById('res-samvatsara').textContent = data.samvatsara;
        document.getElementById('res-location').textContent = `${data.address} (${data.timezone})`;

        document.getElementById('res-masa').textContent = data.masa;
        document.getElementById('res-paksha').textContent = data.paksha;
        document.getElementById('res-tithi').textContent = data.tithi;
        document.getElementById('res-vara').textContent = data.vara;
        document.getElementById('res-nakshatra').textContent = data.nakshatra;
        document.getElementById('res-yoga').textContent = data.yoga;

        document.getElementById('res-sunrise').textContent = data.sunrise;
        document.getElementById('res-sunset').textContent = data.sunset;

        resultContainer.classList.remove('hidden');
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }
});
