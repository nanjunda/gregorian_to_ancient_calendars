# One-Pager: Hindu Panchanga Converter v2.0 (iCal Integration)

## Objective
To extend the existing **v1.0** implementation to support the generation of recurring calendar events in iCal (.ics) format. These events will recur based on specific Hindu Panchanga attributes: **Masa** (Month), **Paksha**, and **Tithi**.

## Confirmations
1.  **Codebase:** This will be a direct enhancement of the existing v1.0 Flask and Python logic. The core astronomical engine will remain `skyfield`.
2.  **Artifacts:** All design documents, plans, and instructions will be saved in the `docs/` directory for persistence and transparency.
3.  **Visuals:** A detailed workflow diagram is provided in the Architecture document to visualize the recurrence calculation engine.

## Key Features
*   **Title Input:** Users can provide a descriptive title (e.g., "Parent's Anniversary").
*   **Vedic Recurrence Logic:** Calculates the Gregorian date for the next ~10 years that matches the target **Masa**, **Paksha**, and **Tithi**.
* 3.  **iCal (.ics) Generation:** A downloadable file containing these calculated dates. Each event will include the full "Hindu Panchanga Report" in its description field for that specific occurrence.
4.  **Web UI Enhancement:** The interface will include a "Title" field and a "Download iCal" button. with glassmorphism styling.

## Recurrence Strategy
Since lunar calendars shift against the solar calendar, the system will:
1.  Identify target attributes from the user's initial date.
2.  For each future year, perform a "Binary Search" or "Scanning" approach within a +/- 30 day window of the previous occurrence to find the matching Tithi/Masa combination.
3.  Generate the `.ics` string using the `ics` library or manual VEVENT formatting.
