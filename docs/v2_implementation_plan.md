# Implementation Plan: Panchanga v2.0 (iCal & Recurrence)

## Goal
Enhance the existing v1.0 application to support title-based iCal generation with recurring Vedic dates (Masa, Paksha, Tithi) and detailed reports in the description field.

## Proposed Changes

### 1. Recurrence Logic
*   **[NEW] `panchanga/recurrence.py`**:
    *   Implement `find_next_occurrences(base_dt, location_name, num_years=10)`:
        *   Identify target Masa, Paksha, and Tithi.
        *   Iterate through future years.
        *   Search +/- 30 days window around expected date.
        *   Collect matching dates and their full Panchanga reports.

### 2. iCal Generation
*   **[NEW] `utils/ical_gen.py`**:
    *   Implement `create_ical_file(title, occurrences)`:
        *   Use `ics` or `vobject` (or manual template) to create `.ics` string.
        *   Map `title` to `SUMMARY`.
        *   Map Panchanga report to `DESCRIPTION`.

### 3. Web UI Updates
*   **[MODIFY] `templates/index.html`**: Add "Title" input field.
*   **[MODIFY] `static/js/main.js`**: 
    *   Include "Title" in form submission.
    *   Add "Download iCal" button that triggers the new API.
*   **[MODIFY] `app.py`**:
    *   New Endpoint `/api/generate-ical` to handle recurrence and file download.

### 4. Dependencies
*   **[MODIFY] `requirements.txt`**: Add `ics`.

## Verification Plan
*   **Functional Test:** Generate an iCal for "Ekadashi" starting from 2025-12-30. Verify that future events in the `.ics` file match the Pausha-Shukla-Ekadashi combination for those years.
*   **Import Test:** Import the generated file into Google Calendar and verify the description field contains the ASCII report.
*   **UI Test:** Confirm the Title field and Download button are styled correctly and functional.
