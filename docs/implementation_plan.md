# Implementation Plan: Hindu Panchanga Converter

## Goal
Implement a robust Python script to convert Gregorian date/time and location into Hindu Panchanga.

## Proposed Changes

### Environment Setup
*   Install necessary dependencies:
    ```bash
    pip install pyswisseph geopy timezonefinder pytz
    ```

### Phase 1: Core Utilities
*   **[NEW] `utils/location.py`**: Logic to fetch Lat/Long/Timezone from a location string.
*   **[NEW] `utils/astronomy.py`**: Integration with `pyswisseph` to get Sun/Moon longitudes with Ayanamsha support.

### Phase 2: Panchanga Logic
*   **[NEW] `panchanga/calculations.py`**:
    *   Functions for Tithi, Nakshatra, Yoga, and Karana.
    *   Logic for Vara based on Sunrise-to-Sunrise duration.
    *   Logic for Masa (Lunar months) and Samvatsara (60-year cycle).

### Phase 3: CLI Interface
*   **[NEW] `panchanga_converter.py`**: The main entry point script that takes arguments or user input and orchestrates the flow.

## Verification Plan

### Automated Tests
*   **Unit Tests:** Verify individual calculations (e.g., Tithi calculation for a known date).
*   **Integration Tests:** Verify the full flow from location name to final report.

### Manual Verification
*   Compare the output for 5 diverse scenarios (different dates, times, and globally distributed locations) against [Drik Panchang](https://www.drikpanchang.com/).
    *   **Scenario 1:** Solar eclipse/Lunar eclipse dates (extreme accuracy check).
    *   **Scenario 2:** New Year (Ugadi/Vishu) to check Samvatsara and Masa logic.
    *   **Scenario 3:** Middle of the night time entry to check Vara transitions (after midnight but before sunrise).

## User Review Required
> [!IMPORTANT]
> The `pyswisseph` library requires C-extensions. I will ensure the environment supports building it or use pre-compiled binaries if available.
> I will use **Lahiri Ayanamsha** as the default, as it is the standard for most Indian Panchangas.
