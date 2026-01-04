# Hindu Panchanga Converter v4.1 - Design Guide

## 1. Introduction
The **Hindu Panchanga Converter** is a high-precision astronomical and Vedic calendar engine. Its primary objective is to bridge the gap between ancient Vedic science and modern celestial mechanics. Version 4.1 makes the engine **Generic**—allowing it to convert any Gregorian event (Birth, Festival, Muhurta) into its full Vedic equivalent with supporting cosmic visualizations.

---

## 2. Universal Strategy (v4.1 Updates)
1. **Hybrid Naming**: Nakshatras, Rashis, Lagnas, and Planets now display the Vedic name followed by the Western equivalent (e.g., *Mesha (Aries)* or *Budha (Mercury)*).
2. **Dynamic Canvas Scaling**: The "Cosmic Alignment" canvas is increased by 23% to accommodate high-detail hybrid naming.
3. **Optimized Visuals**: Sky-map titles are repositioned to prevent clipping, and terminologies are shifted from "Birth" to "Cosmic" to fit any event type.
4. **Next 20 Occurrences**: The iCal engine now finds exactly the next 20 occurrences of a Vedic date (Anniversaries), ideal for recurring annual festivals or birthdays.
5. **Universal Location Guidance**: Improved the location input with guided placeholders and generic hints (Village, Town, City, or Landmark) to resolve geocoding ambiguity.

---

## 3. High-Level Architecture
The application follows a modular **Client-Server Architecture**. It is designed to be lightweight, stateless on the client side, and highly accurate on the backend.

### System Architecture Diagram
```mermaid
graph TD
    User([User's Browser]) <--> |HTTPS Port 58921| Nginx{Nginx Reverse Proxy}
    
    subgraph "Oracle Linux 9 Server (OCI)"
        Nginx <--> |Unix Socket/Localhost| Gunicorn[Gunicorn Web Server]
        
        subgraph "Flask Application"
            Gunicorn --> App[app.py - Routing & Orchestration]
            
            subgraph "Core Engines"
                App --> Calc[panchanga/ - Vedic Logic]
                App --> Astro[utils/astronomy.py - Skyfield Wrapper]
                App --> Viz[utils/visualize - Matplotlib Engines]
            end
            
            subgraph "Data Layer"
                Astro --> JPL[NASA JPL de421.bsp]
                Viz --> Cache[(Image Cache - 15m TTL)]
            end
        end
    end
```

---

## 3. Major Components

### A. Presentation Layer (Frontend)
- **Tech Stack**: HTML5, Vanilla CSS3 (Glassmorphism), Vanilla JavaScript.
- **Key Features**:
    - **Geolocation**: Uses browser APIs and Nominatim reverse geocoding to resolve UTC offsets and coordinates.
    - **Asynchronous Loading**: Panchanga data loads first; high-resolution images load in parallel via a separate API path to ensure high responsiveness.
    - **Base64 Rendering**: For privacy, images are rendered from data streams rather than public URLs.

### B. API Layer (Flask)
- acts as the **Orchestrator**.
- **Endpoints**:
    - `/api/panchanga`: Returns the core 5-limb status (Tithi, Vara, Nakshatra, Yoga, Karana), Rashi, and Lagna.
    - `/api/skyshot`: Generates a 2D ecliptic wheel of the Moon and Stars (Nakshatras).
    - `/api/solar-system`: Generates a 3D-projected heliocentric view of the solar system.
    - `/api/generate-ical`: Calculates 20-year recurrences and packages them into a `.ics` file.

### C. Astronomical Engine (`utils/astronomy.py`)
- **Engine**: Skyfield (Python).
- **Ephemeris**: Uses NASA JPL DE421 developmental ephemeris (standard for 1900-2050).
- **Ayanamsha**: Implements high-precision **Chitra Paksha (Lahiri)** ayanamsha using polynomial series for sub-arcsecond accuracy.

### D. Visualization Engine
- **Modules**: `utils/skyshot.py` and `utils/solar_system.py`.
- **Backend**: Matplotlib with `Agg` (non-interactive) backend.
- **Thread Safety**: Uses **Object-Oriented Matplotlib** (Figure object) to prevent shared state issues when multiple users generate images concurrently.

---

## 4. Implementation Logic

### Data Flow Diagram (Panchanga Request)
```mermaid
sequenceDiagram
    participant U as User Browser
    participant A as app.py
    participant S as Astronomy Engine
    participant V as Vedic Logic
    participant G as Graphics Engine

    U->>A: POST (Date, Time, Location)
    A->>S: Request JD (Julia Date) & Planet Positions
    S-->>A: UTC Time + Sidereal Longitudes
    A->>V: Map Longitudes to Tithi/Nakshatra
    V-->>A: Panchanga Elements
    A->>G: Request Sky Map & Solar View (Base64)
    G-->>A: Encoded Image Data
    A-->>U: JSON (Report + Images)
```

### Privacy "Stealth Mode" Implementation
To protect sensitive birth data:
1. **Filename Hashing**: User inputs are hashed (MD5) so the server never stores filenames that describe a specific person.
2. **Base64 Tunnelling**: Images are read from disk, converted to Base64, and sent in the JSON stream.
3. **Internal-Only Folders**: Nginx is configured to block direct public access to `/static/skyshots/`.
4. **15-Min Expire**: A cron job deletes the physical images 15 minutes after creation.

---

## 5. Deployment Stack (Oracle Linux 9)
The app is hardened for secure enterprise-grade deployment:
- **Nginx**: SSL termination on Port 58921.
- **SELinux**: Explicit `httpd_sys_content_t` contexts for assets and `bin_t` for Gunicorn.
- **Fapolicyd**: Handled/Disabled to allow custom Python binary execution.
- **Logrotate**: Hourly rotation of PII-sensitive logs.

---

---

## 7. Modern & Vedic Hybrid Strategy (v4.1.1)
Version 4.1.1 introduces a deeper integration between modern scientific data and traditional Vedic concepts.

### A. Modern Planets (Uranus & Neptune)
- **Role**: Included in the **Cosmic Alignment** (Solar System) view for scientific completeness.
- **Naming**: Referred to as **Aruna (Uranus)** and **Varuna (Neptune)**—the modern Sanskrit approximations.
- **Styling**: Rendered with lower opacity and dashed orbits to distinguish them from the traditional Navagrahas.
- **Mathematics**: Uses **Logarithmic Scaling** ($4.5 \times \ln(1+d)$) to allow these distant bodies (30+ AU) to fit on the same canvas as Mercury (0.38 AU) without squashing the internal orbits.

### B. Lunar Nodes (Rahu & Ketu)
- **Concept**: Visualized in the **Celestial Perspective** (Sky-Shot) as mathematical intersection points.
- **Astronomical Reality**: Rahu and Ketu are not physical rocks but the **Lunar Nodes**—the two points where the Moon's 5-degree tilted orbit intersects the Earth's Ecliptic Plane.
- **Markers**: Plotted using their international astronomical symbols (☊ for North Node, ☋ for South Node).
- **Predictive Power**: Their inclusion helps users understand why they are known as "Eclipse Points"—as eclipses only happen when the Sun and Moon are near these markers.

---

## 8. Developer Guidelines
- **Modifying Calculations**: Edit `panchanga/calculations.py`. All astronomical calls must pass through `utils/astronomy.py`.
- **Changing Styles**: Centralized in `static/css/style.css` using CSS Variables (`--primary`, `--accent`).
- **Memory Management**: Ephemeris data (`eph`) is global and shared between modules to minimize RAM usage on 1GB instances.
