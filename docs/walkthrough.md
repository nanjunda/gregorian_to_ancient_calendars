# Walkthrough: Hindu Panchanga Converter

I have implemented a Python-based Hindu Panchanga Converter that takes a Gregorian date, time, and location to provide traditional Vedic calendar elements.

## Version 2.0: iCal & Vedic Recurrence
I have enhanced the application to support recurring Vedic events saved in iCal (.ics) format.

### New Features in v2.0
*   **Title Support:** Specify a title for your event (e.g., "Father's Birthday").
*   **Vedic Recurrence Engine:** Automatically finds the Gregorian dates for the same **Masa**, **Paksha**, and **Tithi** for the next 10 years.
*   **Detailed iCal Description:** Every event in the generated calendar file includes the full "Hindu Panchanga Report" for that specific day.
*   **Downloadable iCal (.ics):** A button is available in the Web UI to download the generated file for import into Google/Apple/Outlook calendars.

### Technical Search Logic
The system uses a **+/- 30-day search window** around the anniversary date to account for lunar-solar drift and "Adhika Masa" (intercalary months), ensuring the Vedic attributes are perfectly matched.

## Web User Interface
The UI has been updated with a "Title" field and a "Download 10-Year iCal" button.

## Features Implemented
*   **Geolocation:** Automatic resolution of coordinates and timezones using `geopy` and `timezonefinder`.
*   **Astronomical Precision:** High-precision Sun and Moon positions using `skyfield`.
*   **Vedic Logic:** Accurate derivation of the "Five Limbs" (Panchanga):
    *   **Vara:** Weekday adjusted for Sunrise.
    *   **Tithi:** Lunar day with Paksha (Shukla/Krishna).
    *   **Nakshatra:** Lunar mansion.
    *   **Yoga:** Auspicious angular relationship.
    *   **Karana:** Half-Tithi division.
*   **Calendrical Context:** Correct identification of **Masa** (Lunar month) and **Samvatsara** (60-year cycle).

## Verification Results

### Scenario 1: Future Date (Dec 30, 2025 in Bangalore)
Command run:
```bash
python3 panchanga_converter.py --date 2025-12-30 --time 16:17 --location "Bangalore, India"
```

Output:
```text
========================================
       HINDU PANCHANGA REPORT
========================================
Input Date/Time : 2025-12-30 16:17:00 (Asia/Kolkata)
Location        : Bengaluru, Bangalore North, Bengaluru Urban, Karnataka, India
Sunrise         : 06:40:56
Sunset          : 18:03:23
----------------------------------------
Samvatsara      : Vishvavasu
Masa (Month)    : Pausha
Paksha          : Shukla
Tithi           : Ekadashi
Vara (Weekday)  : Mangalavara
Nakshatra       : Bharani
Yoga            : Siddha
Karana (Index)  : 21
========================================
```

### Scenario 2: Historical Verification (Dec 30, 2024 in Bangalore)
Result: **Somavara** (Monday), **Krodhi** Samvatsara, **Amavasya** Tithi. This matches the known Panchanga for that date.

## How to Run
1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
2. Run the script:
   ```bash
   python3 panchanga_converter.py --date YYYY-MM-DD --time HH:MM --location "City, Country"
   ```
