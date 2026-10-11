# M3 Observatory

React + TypeScript dashboard for the M3 FastAPI experiment server. It reads saved evidence and polls every three seconds. The application contains no demonstration data or fabricated experiment values.

## Run

```sh
npm install
npm run dev
```

Open http://127.0.0.1:5173 with the FastAPI server on http://127.0.0.1:8000. Vite proxies `/api` to the backend. For a packaged deployment, serve `dist/` from FastAPI or configure the reverse proxy to route `/api` to that server.

```sh
npm test
npm run build
```

Optional read-only integration checks against a running API with official CSV and live collector results:

```powershell
$env:M3_API_URL = 'http://127.0.0.1:8000'
npm test -- --run src/integration.test.tsx
```

These checks read existing experiments and never create runs or write synthetic evidence.

## Evidence interpretation

- Source and execution mode appear on every selected experiment.
- Unavailable measurements display their reason, never a replacement zero.
- Comparison is restricted to completed runs matching source, mode, scenario, observation unit, feature schema, dataset checksum, and model/window/warm-up/record-limit settings.
- Each comparison row is an individual trial. The Pareto plot uses measured F1 and measured overhead only; it does not automatically select a knee point.
- Timelines request up to 1,000 predictions and show the returned series without inventing missing observations.
- Live runs and saved runs share the same read-only result contract. Execution is controlled by the experiment runner.

Synthetic fixtures exist exclusively in tests.
