# Life Wrapped
https://life-wrapped-app-2782afb29d43.herokuapp.com/
Life Wrapped is a full-stack web app that turns your daily life journal and Spotify listening habits into playful “receipts” and visual summaries. Upload your Excel log to see month-by-month stats, generate per-month calendar heatmaps, and connect Spotify to pull in your top tracks.

## Features

- **Excel receipt generator** – Parse a spreadsheet of daily scores and highlights, bucket by month, and render printable receipt-style summaries.
- **Calendar heatmaps** – For every month in the upload, auto-generate a colour-coded calendar image showing day scores.
- **Spotify integration** – OAuth login pulls your most-played tracks (supports `user-top-read` and `user-read-recently-played` scopes) and displays them alongside receipts.
- **Session persistence** – Uploaded summaries, heatmaps, and Spotify results are stored in the Flask session so they rehydrate on refresh.
- **Heroku-friendly** – Configured to run on Heroku via Gunicorn (`Procfile`, `runtime.txt`) with static assets served from the Vite-built frontend.

## Tech Stack

| Layer      | Tech                                                   |
|------------|--------------------------------------------------------|
| Frontend   | React 19 + Vite, vanilla CSS                           |
| Backend    | Flask, Flask-Session, Flask-CORS                       |
| Data       | NumPy, Matplotlib for calendar heatmaps                |
| Build/Run  | Node 20.x for frontend, Python 3.11 for backend        |

## Data Flow

1. **Excel Upload** → `life_wrapped.io.load_days_from_excel` → `bucket_by_month` → `monthly_summary` → receipts.
2. **Heatmaps** → `generate_calendar_heatmaps` (Matplotlib/NumPy) → PNGs saved under `life_wrapped/outputs`.
3. **Spotify** → OAuth token exchange → `GET /me/top/tracks` (`short_term`) → shown in the “Top songs” gallery.

All three data sets are saved into the Flask session so refreshing the browser retains the latest state.

Ensure you activate the virtual env first.

## Troubleshooting

- **Spotify 401s**: Tokens expire; the backend attempts refresh but requires the `user-top-read` scope. Re-run `/auth/login` if needed.
- **Missing heatmaps**: Verify Matplotlib and NumPy installed correctly (`pip install -r requirements.txt`). Heatmaps render when day score data exists.
- **CORS issues**: Confirm `FRONTEND_URL` matches the origin hitting the backend, and restart the server after changes.
- **Static assets not loading**: When deploying, run `npm run build` so `frontend/dist` contains the bundled app served by Flask.

## Project Structure

```
backend/                 Flask app (server.py)
frontend/                React app (Vite)
life_wrapped/            Domain logic, models, renderers, statistics
  └─ renderers/          Calendar heatmap utilities
tests/                   Unit tests
requirements.txt         Python dependencies
package.json             Root dev convenience scripts (optional)
```

