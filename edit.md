# Edit Log
This file tracks all changes made to the codebase for debugging purposes.

## Changes:
- **`Sidebar.tsx`**: Replaced the mock timeout loop in `simulateUpload` with an actual `handleUpload` function that uses the real `uploadPdf` API call imported from `client.ts`. Preserved UI states (uploading -> parsing -> indexed) by emitting state updates conditionally.
- **`ChatArea.tsx`**: Replaced the `setTimeout` simulation in `handleSubmit` with real `sendChat` API call. Handled successful server responses and surfaced detailed error messages from backend or network failures.
- **`ingestion/chunker.py`**: Fixed a critical bug that caused `ValueError: No text chunks extracted`. Previously, the chunker would silently discard all narrative text if the document didn't start with a `Title` element. Now it defaults to a `"General"` section name when processing orphaned text blocks. 
- **`ingestion/router.py`**: Broadened the allowed routed types for text elements to include `"Text"`, `"ListItem"`, and `"UncategorizedText"` to prevent unstructured parsing from missing text blocks entirely.
- **`Dockerfile` & `requirements.txt` (Production Server)**: Replaced the default Flask development server with `gunicorn`. Updated CMD to run Gunicorn with 2 workers and a 120-second timeout to handle concurrent users and slow LLM inferences optimally over port 7860.
