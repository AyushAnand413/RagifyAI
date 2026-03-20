# Edit Log
This file tracks all changes made to the codebase for debugging purposes.

## Changes:
- **`Sidebar.tsx`**: Replaced the mock timeout loop in `simulateUpload` with an actual `handleUpload` function that uses the real `uploadPdf` API call imported from `client.ts`. Preserved UI states (uploading -> parsing -> indexed) by emitting state updates conditionally.
- **`ChatArea.tsx`**: Replaced the `setTimeout` simulation in `handleSubmit` with real `sendChat` API call. Handled successful server responses and surfaced detailed error messages from backend or network failures.
