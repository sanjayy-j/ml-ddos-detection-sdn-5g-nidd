# Frontend: source and line-by-line explanation

This guide follows the current checked-out frontend source. Line numbers restart for each file and refer to physical source lines, including blank lines. Each file has a complete original source listing and a numbered explanation table. Application files were not changed.

## What the frontend currently does

The current UI is **M3 Observatory**, a read-only M3 experiment dashboard. The proposed unified M1/M2/M3 screen is not currently implemented here. This UI displays saved evidence; it has no controls for training, starting experiments, or collecting telemetry.

The browser loads index.html → main.tsx → App. App asks api.ts for /api/runs and /api/overview, chooses a run, then requests that run's summary and /series?limit=1000. api.ts validates JSON. evidence.ts formats metrics and groups comparable trials. App draws SVG charts and HTML tables. style.css controls layout. In development, Vite forwards /api to FastAPI on port 8000.

Auto-refresh schedules the next request 3 seconds after the previous one completes. Manual Refresh restarts reads. The frontend does not calculate model predictions or reconstruct missing measurements.

## Syntax to recognize

- `const` prevents binding reassignment; objects bound with const can still change. `let` permits reassignment.
- `(x) => ...` is an arrow function. `map` transforms array items; `filter` retains them; `some` asks whether any match.
- `...` spreads object/array members. `{name}` can destructure fields; JSX braces evaluate JavaScript.
- Type annotations, interfaces, casts, type imports, and non-null `!` assertions aid TypeScript checking and disappear at runtime. They do not validate JSON.
- `?.` safely accesses a nullable object. `??` defaults null/undefined; `||` defaults any falsy value. `condition ? a : b` selects one expression.
- JSX becomes React operations. `className` selects CSS styling; `htmlFor` links labels; `onChange` and `onClick` receive callbacks.
- `useState` stores [value,setter]; setters rerender. `useEffect` handles external work and cleanup; `useMemo` caches derived values; `useCallback` caches a function.
- `async` functions return promises; `await` reads their eventual result. `Promise.all` awaits requests together. `try/catch/finally` handles success, failure, and always-run work.
- Tests use `expect` for assertions and `vi.fn` for mocks; resolved/rejected mock values simulate successful/failed asynchronous requests.

## Coverage

| File | Physical lines |
| --- | ---: |
| `frontend/index.html` | 14 |
| `frontend/src/main.tsx` | 6 |
| `frontend/src/types.ts` | 48 |
| `frontend/src/api.ts` | 76 |
| `frontend/src/evidence.ts` | 37 |
| `frontend/src/App.tsx` | 169 |
| `frontend/src/style.css` | 9 |
| `frontend/src/test-fixtures.ts` | 19 |
| `frontend/src/test-setup.ts` | 4 |
| `frontend/src/App.test.tsx` | 41 |
| `frontend/src/api.test.ts` | 27 |
| `frontend/src/evidence.test.ts` | 31 |
| `frontend/src/integration.test.tsx` | 65 |
| `frontend/package.json` | 27 |
| `frontend/tsconfig.json` | 18 |
| `frontend/vite.config.ts` | 8 |
| `frontend/README.md` | 37 |
| Total | 636 |

The generated package-lock.json is described after the walkthrough. Every physical lockfile line is documented in [Reference data and generated files](reference-data.md).

## frontend/index.html

Browser document and mounting point. The page initially contains only #root; main.tsx supplies its contents.

### Complete source

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#102334" />
    <meta name="description" content="M3 sampled telemetry and adaptive DDoS detection experiment observatory." />
    <title>M3 Observatory · 5G-NIDD</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

### Every physical line

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>&lt;!doctype html&gt;</code> | Declares HTML5 document parsing. |
| 2 | <code>&lt;html lang=&quot;en&quot;&gt;</code> | Starts the HTML document and identifies English as its language for browser/accessibility tools. |
| 3 | <code>  &lt;head&gt;</code> | Starts nonvisual document metadata. |
| 4 | <code>    &lt;meta charset=&quot;UTF-8&quot; /&gt;</code> | Declares UTF-8 so punctuation, labels, arrows, and non-ASCII text decode correctly. |
| 5 | <code>    &lt;meta name=&quot;viewport&quot; content=&quot;width=device-width, initial-scale=1.0&quot; /&gt;</code> | Sets responsive viewport width to device width and initial zoom to 1. |
| 6 | <code>    &lt;meta name=&quot;theme-color&quot; content=&quot;#102334&quot; /&gt;</code> | Suggests the dark header color to supporting browser chrome. |
| 7 | <code>    &lt;meta name=&quot;description&quot; content=&quot;M3 sampled telemetry and adaptive DDoS detection experiment observatory.&quot; /&gt;</code> | Provides the page description for previews/search metadata; this is not experiment evidence. |
| 8 | <code>    &lt;title&gt;M3 Observatory · 5G-NIDD&lt;/title&gt;</code> | Sets the browser-tab/window title. |
| 9 | <code>  &lt;/head&gt;</code> | Closes document metadata. |
| 10 | <code>  &lt;body&gt;</code> | Starts the visible document body. |
| 11 | <code>    &lt;div id=&quot;root&quot;&gt;&lt;/div&gt;</code> | Provides the empty #root mounting element used by main.tsx. |
| 12 | <code>    &lt;script type=&quot;module&quot; src=&quot;/src/main.tsx&quot;&gt;&lt;/script&gt;</code> | Loads the TypeScript/JSX entry through an ES-module script; Vite transforms it during development/build. |
| 13 | <code>  &lt;/body&gt;</code> | Closes the document body. |
| 14 | <code>&lt;/html&gt;</code> | Closes the HTML document. |

## frontend/src/main.tsx

Browser entry point. Connects index.html, React, App, and the stylesheet.

### Complete source

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './style.css';

ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
```

### Every physical line

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>import React from &#39;react&#39;;</code> | Imports React for the StrictMode wrapper. |
| 2 | <code>import ReactDOM from &#39;react-dom/client&#39;;</code> | Imports the browser ReactDOM client that mounts components into an HTML element. |
| 3 | <code>import App from &#39;./App&#39;;</code> | Imports the dashboard component. |
| 4 | <code>import &#39;./style.css&#39;;</code> | Imports global CSS as a Vite-handled style dependency. |
| 5 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 6 | <code>ReactDOM.createRoot(document.getElementById(&#39;root&#39;)!).render(&lt;React.StrictMode&gt;&lt;App /&gt;&lt;/React.StrictMode&gt;);</code> | Finds index.html's #root element, asserts it exists at compile time with !, creates the React root, and renders App inside StrictMode. Development StrictMode can rerun effects with cleanup to reveal lifecycle mistakes. |

## frontend/src/types.ts

Compile-time vocabulary for the saved-evidence API. Interfaces disappear at runtime; api.ts performs explicit runtime checks.

### Complete source

```typescript
export interface Metric {
  value: number | null;
  unit: string;
  status: 'measured' | 'estimated' | 'unavailable';
  reason: string | null;
}

export interface RunSummary {
  schema_version: 1;
  run_id: string;
  source: string;
  mode: 'csv_replay' | 'pcap_replay' | 'live_sflow';
  status: 'running' | 'completed' | 'failed';
  sampling_rate: number;
  seed: number;
  scenario: string;
  unit: 'flow' | 'window';
  created_at: string;
  ended_at: string | null;
  counts: { input: number; sampled: number; evaluated: number; warmup: number; excluded: number; unlabeled: number };
  metrics: Record<string, Metric>;
  drift_count: number;
  error: string | null;
  config: Record<string, unknown>;
  provenance?: { sha256?: string | null; [key: string]: unknown } | null;
  feature_schema?: string;
}

export interface Prediction {
  index: number;
  time: number | string;
  y_true: number | boolean | null;
  y_pred: number | boolean | null;
  score: number | null;
  latency_ms: number | null;
  phase: string;
  attack_family: string | null;
}
export interface Resource {
  time: number | string;
  cpu_percent: number | null;
  rss_mb: number | null;
  telemetry_bytes: number | null;
  controller_cpu_percent: number | null;
}
export interface DriftEvent { time: number | string; index: number; event: string; detector: string }
export interface Series { predictions: Prediction[]; resources: Resource[]; drift: DriftEvent[] }
export interface Overview { total_runs: number; completed_runs: number; running_runs: number; failed_runs: number; best_run_id: string | null }
```

### Every physical line

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>export interface Metric {</code> | Declares and exports the compile-time shape for a metric plus its measurement evidence. |
| 2 | <code>  value: number &#124; null;</code> | Metric value is numeric or null; null means no numeric measurement. |
| 3 | <code>  unit: string;</code> | Carries a unit string such as ratio, ms, %, or kbit/s. |
| 4 | <code>  status: &#39;measured&#39; &#124; &#39;estimated&#39; &#124; &#39;unavailable&#39;;</code> | Restricts evidence status to measured, estimated, or unavailable string literals. |
| 5 | <code>  reason: string &#124; null;</code> | Allows a textual limitation/reason or null. |
| 6 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 7 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 8 | <code>export interface RunSummary {</code> | Declares the summary object shared by frontend API helpers and components. |
| 9 | <code>  schema_version: 1;</code> | Literal type 1 ties this interface to result schema version 1. |
| 10 | <code>  run_id: string;</code> | Identifies one saved experiment. |
| 11 | <code>  source: string;</code> | Carries the dataset/collection source; strings are extensible rather than a closed union. |
| 12 | <code>  mode: &#39;csv_replay&#39; &#124; &#39;pcap_replay&#39; &#124; &#39;live_sflow&#39;;</code> | Limits execution mode to CSV replay, capture replay, or live sFlow. |
| 13 | <code>  status: &#39;running&#39; &#124; &#39;completed&#39; &#124; &#39;failed&#39;;</code> | Limits lifecycle status to running, completed, or failed. |
| 14 | <code>  sampling_rate: number;</code> | Carries denominator N in 1/N sampling. |
| 15 | <code>  seed: number;</code> | Carries the run's repeatability seed. |
| 16 | <code>  scenario: string;</code> | Identifies the scenario, for example baseline or unseen-attack setup. |
| 17 | <code>  unit: &#39;flow&#39; &#124; &#39;window&#39;;</code> | States whether observation accounting is flow-based or window-based. |
| 18 | <code>  created_at: string;</code> | Stores run creation timestamp as text. |
| 19 | <code>  ended_at: string &#124; null;</code> | Stores end timestamp or null if no end was saved. |
| 20 | <code>  counts: { input: number; sampled: number; evaluated: number; warmup: number; excluded: number; unlabeled: number };</code> | Requires all six independent accounting counters: total input, kept sample, evaluated labels, warm-up records, excluded records, and unlabeled records. |
| 21 | <code>  metrics: Record&lt;string, Metric&gt;;</code> | Allows metric names as string keys while requiring every value to follow Metric. |
| 22 | <code>  drift_count: number;</code> | Stores saved drift-alarm count. |
| 23 | <code>  error: string &#124; null;</code> | Carries the failure description or null. |
| 24 | <code>  config: Record&lt;string, unknown&gt;;</code> | Allows configuration entries with unknown values; callers must narrow them before treating them as numbers or strings. |
| 25 | <code>  provenance?: { sha256?: string &#124; null; [key: string]: unknown } &#124; null;</code> | Optional nullable provenance object; its SHA-256 is optional/nullable, and its index signature permits additional provenance attributes. |
| 26 | <code>  feature_schema?: string;</code> | Optional feature-schema identifier, used in comparison compatibility. |
| 27 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 28 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 29 | <code>export interface Prediction {</code> | Declares a saved per-observation prediction shape. |
| 30 | <code>  index: number;</code> | Stores observation sequence index used for plotting. |
| 31 | <code>  time: number &#124; string;</code> | Allows elapsed time as a number or timestamp text. |
| 32 | <code>  y_true: number &#124; boolean &#124; null;</code> | Allows ground truth as numeric/boolean binary label or null. |
| 33 | <code>  y_pred: number &#124; boolean &#124; null;</code> | Allows predicted class as numeric/boolean binary label or null. |
| 34 | <code>  score: number &#124; null;</code> | Stores attack score/probability or null. |
| 35 | <code>  latency_ms: number &#124; null;</code> | Stores per-prediction latency in milliseconds or null. |
| 36 | <code>  phase: string;</code> | Identifies stream phase, such as warm-up/evaluation. |
| 37 | <code>  attack_family: string &#124; null;</code> | Stores attack family name or null when unspecified. |
| 38 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 39 | <code>export interface Resource {</code> | Declares a saved resource-observation shape. |
| 40 | <code>  time: number &#124; string;</code> | Stores resource measurement time in the same string/numeric style. |
| 41 | <code>  cpu_percent: number &#124; null;</code> | Stores detector CPU percentage or null. |
| 42 | <code>  rss_mb: number &#124; null;</code> | Stores resident memory in megabytes or null. |
| 43 | <code>  telemetry_bytes: number &#124; null;</code> | Stores telemetry byte count or null. |
| 44 | <code>  controller_cpu_percent: number &#124; null;</code> | Stores separately observed controller CPU percentage or null. |
| 45 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 46 | <code>export interface DriftEvent { time: number &#124; string; index: number; event: string; detector: string }</code> | Defines one drift alarm with time, observation index, event name, and detector name in a compact single-line interface. |
| 47 | <code>export interface Series { predictions: Prediction[]; resources: Resource[]; drift: DriftEvent[] }</code> | Groups typed prediction, resource, and drift arrays returned by the series endpoint. |
| 48 | <code>export interface Overview { total_runs: number; completed_runs: number; running_runs: number; failed_runs: number; best_run_id: string &#124; null }</code> | Defines four overview counters and optional-in-value best-run ID (required field, nullable value). The current UI does not use best_run_id. |

## frontend/src/api.ts

Read-only HTTP boundary. Fetches FastAPI routes and rejects malformed supported-contract responses before components display them.

### Complete source

```typescript
import type { RunSummary, Series, Overview } from './types';

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

export function validateRun(value: unknown): RunSummary {
  if (!record(value) || value.schema_version !== 1 || typeof value.run_id !== 'string' ||
      typeof value.source !== 'string' || !['csv_replay', 'pcap_replay', 'live_sflow'].includes(String(value.mode)) ||
      !['running', 'completed', 'failed'].includes(String(value.status)) ||
      typeof value.sampling_rate !== 'number' || !Number.isInteger(value.sampling_rate) || value.sampling_rate < 1 ||
      !['flow', 'window'].includes(String(value.unit)) || typeof value.scenario !== 'string' ||
      typeof value.seed !== 'number' || !Number.isFinite(value.seed) ||
      typeof value.created_at !== 'string' || typeof value.drift_count !== 'number' || !Number.isFinite(value.drift_count) ||
      !(value.ended_at === null || typeof value.ended_at === 'string') ||
      !(value.error === null || typeof value.error === 'string') ||
      !record(value.counts) || !record(value.metrics) || !record(value.config)) {
    throw new Error('The server returned an unsupported run format. Expected result schema version 1.');
  }
  for (const key of ['input', 'sampled', 'evaluated', 'warmup', 'excluded', 'unlabeled']) {
    if (typeof value.counts[key] !== 'number' || !Number.isFinite(value.counts[key]) || Number(value.counts[key]) < 0) {
      throw new Error('The server returned invalid run counts.');
    }
  }
  for (const metric of Object.values(value.metrics)) {
    if (!record(metric) || !['measured', 'estimated', 'unavailable'].includes(String(metric.status)) ||
        !(metric.value === null || (typeof metric.value === 'number' && Number.isFinite(metric.value))) ||
        typeof metric.unit !== 'string' || !(metric.reason === null || typeof metric.reason === 'string')) throw new Error('The server returned invalid metric evidence.');
  }
  return value as unknown as RunSummary;
}

async function get(path: string, signal?: AbortSignal): Promise<unknown> {
  const response = await fetch(path, { signal, headers: { Accept: 'application/json' } });
  if (!response.ok) throw new Error(`Could not load experiment evidence (HTTP ${response.status}).`);
  try { return await response.json(); } catch { throw new Error('The experiment server did not return JSON.'); }
}

export async function getRuns(signal?: AbortSignal): Promise<RunSummary[]> {
  const data = await get('/api/runs', signal);
  if (!record(data) || !Array.isArray(data.runs)) throw new Error('The server returned an invalid run list.');
  return data.runs.map(validateRun);
}
export async function getRun(id: string, signal?: AbortSignal): Promise<RunSummary> {
  return validateRun(await get(`/api/runs/${encodeURIComponent(id)}`, signal));
}
export async function getSeries(id: string, signal?: AbortSignal): Promise<Series> {
  const data = await get(`/api/runs/${encodeURIComponent(id)}/series?limit=1000`, signal);
  if (!record(data) || !Array.isArray(data.predictions) || !Array.isArray(data.resources) || !Array.isArray(data.drift)) {
    throw new Error('The server returned invalid timeline evidence.');
  }
  for (const point of data.predictions) {
    if (!record(point) || typeof point.index !== 'number' || !Number.isFinite(point.index) ||
        !(point.score === null || (typeof point.score === 'number' && Number.isFinite(point.score) && point.score >= 0 && point.score <= 1)) ||
        ![0, 1, true, false, null].includes(point.y_true as number | boolean | null) ||
        !(typeof point.time === 'string' || (typeof point.time === 'number' && Number.isFinite(point.time)))) {
      throw new Error('The server returned an invalid prediction.');
    }
  }
  for (const event of data.drift) {
    if (!record(event) || typeof event.index !== 'number' || !Number.isFinite(event.index) ||
        typeof event.event !== 'string' || typeof event.detector !== 'string' ||
        !(typeof event.time === 'string' || (typeof event.time === 'number' && Number.isFinite(event.time)))) {
      throw new Error('The server returned an invalid drift event.');
    }
  }
  return data as unknown as Series;
}
export async function getOverview(signal?: AbortSignal): Promise<Overview> {
  const data = await get('/api/overview', signal);
  if (!record(data) || !['total_runs', 'completed_runs', 'running_runs', 'failed_runs'].every(key =>
    typeof data[key] === 'number' && Number.isFinite(data[key]) && Number(data[key]) >= 0)) {
    throw new Error('The server returned an invalid experiment overview.');
  }
  return data as unknown as Overview;
}
```

### Every physical line

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>import type { RunSummary, Series, Overview } from &#39;./types&#39;;</code> | Imports compile-time API response shapes, removed from runtime output. |
| 2 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 3 | <code>function record(value: unknown): value is Record&lt;string, unknown&gt; {</code> | Defines a type guard: a true result tells TypeScript the unknown input is an object indexed by string keys. |
| 4 | <code>  return typeof value === &#39;object&#39; &amp;&amp; value !== null &amp;&amp; !Array.isArray(value);</code> | Accepts non-null non-array objects only; this prevents treating arrays/null as JSON records. |
| 5 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 6 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 7 | <code>export function validateRun(value: unknown): RunSummary {</code> | Exports the runtime run-summary validator; network JSON starts as unknown, not automatically trusted TypeScript data. |
| 8 | <code>  if (!record(value) &#124;&#124; value.schema_version !== 1 &#124;&#124; typeof value.run_id !== &#39;string&#39; &#124;&#124;</code> | Begins a compound rejection condition requiring an object, exact schema version 1, and string run ID. |
| 9 | <code>      typeof value.source !== &#39;string&#39; &#124;&#124; ![&#39;csv_replay&#39;, &#39;pcap_replay&#39;, &#39;live_sflow&#39;].includes(String(value.mode)) &#124;&#124;</code> | Requires a string provenance source and one of the three supported execution modes. |
| 10 | <code>      ![&#39;running&#39;, &#39;completed&#39;, &#39;failed&#39;].includes(String(value.status)) &#124;&#124;</code> | Restricts status to running, completed, or failed. |
| 11 | <code>      typeof value.sampling_rate !== &#39;number&#39; &#124;&#124; !Number.isInteger(value.sampling_rate) &#124;&#124; value.sampling_rate &lt; 1 &#124;&#124;</code> | Requires sampling N to be a numeric integer at least 1. |
| 12 | <code>      ![&#39;flow&#39;, &#39;window&#39;].includes(String(value.unit)) &#124;&#124; typeof value.scenario !== &#39;string&#39; &#124;&#124;</code> | Requires flow/window observation units and a string scenario name. |
| 13 | <code>      typeof value.seed !== &#39;number&#39; &#124;&#124; !Number.isFinite(value.seed) &#124;&#124;</code> | Requires the random seed to be a finite number. |
| 14 | <code>      typeof value.created_at !== &#39;string&#39; &#124;&#124; typeof value.drift_count !== &#39;number&#39; &#124;&#124; !Number.isFinite(value.drift_count) &#124;&#124;</code> | Requires creation time as a string and drift count as a finite number; this line does not parse dates or enforce nonnegative integer drift count. |
| 15 | <code>      !(value.ended_at === null &#124;&#124; typeof value.ended_at === &#39;string&#39;) &#124;&#124;</code> | Allows end time to be either null (unfinished) or a string. |
| 16 | <code>      !(value.error === null &#124;&#124; typeof value.error === &#39;string&#39;) &#124;&#124;</code> | Allows error to be absent semantically as null or represented by a string. |
| 17 | <code>      !record(value.counts) &#124;&#124; !record(value.metrics) &#124;&#124; !record(value.config)) {</code> | Requires counts, metrics, and config to be object records and opens the rejection body. |
| 18 | <code>    throw new Error(&#39;The server returned an unsupported run format. Expected result schema version 1.&#39;);</code> | Throws one schema-format error if any preceding top-level requirement failed; throwing rejects the async API operation later. |
| 19 | <code>  }</code> | Closes the current function, interface, or control block begun above. |
| 20 | <code>  for (const key of [&#39;input&#39;, &#39;sampled&#39;, &#39;evaluated&#39;, &#39;warmup&#39;, &#39;excluded&#39;, &#39;unlabeled&#39;]) {</code> | Checks each required accounting field by its exact key. |
| 21 | <code>    if (typeof value.counts[key] !== &#39;number&#39; &#124;&#124; !Number.isFinite(value.counts[key]) &#124;&#124; Number(value.counts[key]) &lt; 0) {</code> | Rejects missing/non-numeric/nonfinite/negative counts. This checks numbers, not integer-ness or cross-field sums. |
| 22 | <code>      throw new Error(&#39;The server returned invalid run counts.&#39;);</code> | Throws a count-specific validation error. |
| 23 | <code>    }</code> | Closes the current function, interface, or control block begun above. |
| 24 | <code>  }</code> | Closes the current function, interface, or control block begun above. |
| 25 | <code>  for (const metric of Object.values(value.metrics)) {</code> | Iterates every metric object provided by the backend, including extra metric names not hardcoded in the UI. |
| 26 | <code>    if (!record(metric) &#124;&#124; ![&#39;measured&#39;, &#39;estimated&#39;, &#39;unavailable&#39;].includes(String(metric.status)) &#124;&#124;</code> | Requires each metric to be an object and have a known evidence status. |
| 27 | <code>        !(metric.value === null &#124;&#124; (typeof metric.value === &#39;number&#39; &amp;&amp; Number.isFinite(metric.value))) &#124;&#124;</code> | Allows metric.value to be null or a finite numeric value; NaN and infinity fail. |
| 28 | <code>        typeof metric.unit !== &#39;string&#39; &#124;&#124; !(metric.reason === null &#124;&#124; typeof metric.reason === &#39;string&#39;)) throw new Error(&#39;The server returned invalid metric evidence.&#39;);</code> | Requires a string unit and null/string reason; any violated metric rule throws invalid metric evidence. |
| 29 | <code>  }</code> | Closes the current function, interface, or control block begun above. |
| 30 | <code>  return value as unknown as RunSummary;</code> | Returns the validated object with a compile-time RunSummary cast through unknown. The cast itself adds no runtime validation. |
| 31 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 32 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 33 | <code>async function get(path: string, signal?: AbortSignal): Promise&lt;unknown&gt; {</code> | Defines the shared asynchronous GET helper with optional cancellation and an unknown JSON result. |
| 34 | <code>  const response = await fetch(path, { signal, headers: { Accept: &#39;application/json&#39; } });</code> | Fetches the relative URL, forwards AbortSignal, and requests application/json using the Accept header. |
| 35 | <code>  if (!response.ok) throw new Error(`Could not load experiment evidence (HTTP ${response.status}).`);</code> | Throws for any non-success HTTP status, including the status number for debugging. |
| 36 | <code>  try { return await response.json(); } catch { throw new Error(&#39;The experiment server did not return JSON.&#39;); }</code> | Parses JSON and returns it; JSON parse failure becomes a clear server-did-not-return-JSON error. |
| 37 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 38 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 39 | <code>export async function getRuns(signal?: AbortSignal): Promise&lt;RunSummary[]&gt; {</code> | Exports the run-list reader returning a promise of validated summaries. |
| 40 | <code>  const data = await get(&#39;/api/runs&#39;, signal);</code> | Requests the backend's /api/runs route with optional cancellation. |
| 41 | <code>  if (!record(data) &#124;&#124; !Array.isArray(data.runs)) throw new Error(&#39;The server returned an invalid run list.&#39;);</code> | Requires a response object containing an array named runs. |
| 42 | <code>  return data.runs.map(validateRun);</code> | Validates each array entry, so one unsupported summary rejects this list response. |
| 43 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 44 | <code>export async function getRun(id: string, signal?: AbortSignal): Promise&lt;RunSummary&gt; {</code> | Exports the single-run reader accepting ID and optional AbortSignal. |
| 45 | <code>  return validateRun(await get(`/api/runs/${encodeURIComponent(id)}`, signal));</code> | URL-encodes ID so characters such as slash remain part of the ID; fetches then validates the returned summary. |
| 46 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 47 | <code>export async function getSeries(id: string, signal?: AbortSignal): Promise&lt;Series&gt; {</code> | Exports the selected-run timeline reader. |
| 48 | <code>  const data = await get(`/api/runs/${encodeURIComponent(id)}/series?limit=1000`, signal);</code> | Requests the series route with a 1,000-point limit. The browser does not synthesize omitted records. |
| 49 | <code>  if (!record(data) &#124;&#124; !Array.isArray(data.predictions) &#124;&#124; !Array.isArray(data.resources) &#124;&#124; !Array.isArray(data.drift)) {</code> | Requires all three series arrays: predictions, resources, and drift. |
| 50 | <code>    throw new Error(&#39;The server returned invalid timeline evidence.&#39;);</code> | Throws the timeline-contract error when an expected array is absent or wrongly typed. |
| 51 | <code>  }</code> | Closes the current function, interface, or control block begun above. |
| 52 | <code>  for (const point of data.predictions) {</code> | Examines each returned prediction record. |
| 53 | <code>    if (!record(point) &#124;&#124; typeof point.index !== &#39;number&#39; &#124;&#124; !Number.isFinite(point.index) &#124;&#124;</code> | Requires a prediction object with a finite numeric observation index. |
| 54 | <code>        !(point.score === null &#124;&#124; (typeof point.score === &#39;number&#39; &amp;&amp; Number.isFinite(point.score) &amp;&amp; point.score &gt;= 0 &amp;&amp; point.score &lt;= 1)) &#124;&#124;</code> | Requires score to be null or a finite probability between 0 and 1 inclusive. |
| 55 | <code>        ![0, 1, true, false, null].includes(point.y_true as number &#124; boolean &#124; null) &#124;&#124;</code> | Allows ground truth 0/1/true/false/null only; the TypeScript assertion helps includes typechecking and does not coerce the value. |
| 56 | <code>        !(typeof point.time === &#39;string&#39; &#124;&#124; (typeof point.time === &#39;number&#39; &amp;&amp; Number.isFinite(point.time)))) {</code> | Allows timestamp strings or finite numeric relative times, then opens rejection handling. |
| 57 | <code>      throw new Error(&#39;The server returned an invalid prediction.&#39;);</code> | Throws invalid prediction when any tested field fails. |
| 58 | <code>    }</code> | Closes the current function, interface, or control block begun above. |
| 59 | <code>  }</code> | Closes the current function, interface, or control block begun above. |
| 60 | <code>  for (const event of data.drift) {</code> | Examines each drift event independently. |
| 61 | <code>    if (!record(event) &#124;&#124; typeof event.index !== &#39;number&#39; &#124;&#124; !Number.isFinite(event.index) &#124;&#124;</code> | Requires a drift event object and finite numeric index. |
| 62 | <code>        typeof event.event !== &#39;string&#39; &#124;&#124; typeof event.detector !== &#39;string&#39; &#124;&#124;</code> | Requires detector and event names as strings. |
| 63 | <code>        !(typeof event.time === &#39;string&#39; &#124;&#124; (typeof event.time === &#39;number&#39; &amp;&amp; Number.isFinite(event.time)))) {</code> | Allows event time as a string or finite number. |
| 64 | <code>      throw new Error(&#39;The server returned an invalid drift event.&#39;);</code> | Throws the drift-event-specific error. |
| 65 | <code>    }</code> | Closes the current function, interface, or control block begun above. |
| 66 | <code>  }</code> | Closes the current function, interface, or control block begun above. |
| 67 | <code>  return data as unknown as Series;</code> | Casts structurally checked series to Series. Resource element fields and several prediction fields are not validated here; array presence is checked. |
| 68 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 69 | <code>export async function getOverview(signal?: AbortSignal): Promise&lt;Overview&gt; {</code> | Exports the aggregate-count reader. |
| 70 | <code>  const data = await get(&#39;/api/overview&#39;, signal);</code> | Requests /api/overview. |
| 71 | <code>  if (!record(data) &#124;&#124; ![&#39;total_runs&#39;, &#39;completed_runs&#39;, &#39;running_runs&#39;, &#39;failed_runs&#39;].every(key =&gt;</code> | Requires an object and begins checking all four known run counters. |
| 72 | <code>    typeof data[key] === &#39;number&#39; &amp;&amp; Number.isFinite(data[key]) &amp;&amp; Number(data[key]) &gt;= 0)) {</code> | Each counter must be a finite nonnegative number; this does not enforce integers, totals matching, or best_run_id type. |
| 73 | <code>    throw new Error(&#39;The server returned an invalid experiment overview.&#39;);</code> | Throws an overview-format error if any counter fails. |
| 74 | <code>  }</code> | Closes the current function, interface, or control block begun above. |
| 75 | <code>  return data as unknown as Overview;</code> | Returns the response cast as Overview after those checks. |
| 76 | <code>}</code> | Closes the current function, interface, or control block begun above. |

### Validation boundaries

These checks validate a supported response shape; they do not prove the experiment was scientifically correct. Run validation does not parse timestamp strings, enforce every counter is an integer, verify cross-field count relationships, or validate provenance. Series validation checks arrays and several prediction/drift fields, but does not validate each resource element or every Prediction field. Compile-time casts do not add missing runtime checks.

## frontend/src/evidence.ts

Pure evidence helpers. Formats values, separates comparison groups, and identifies measured Pareto-efficient trials without requests.

### Complete source

```typescript
import type { Metric, RunSummary } from './types';

const ratioKeys = new Set(['precision', 'recall', 'f1', 'roc_auc', 'false_positive_rate', 'unseen_attack_recall']);
export function metricValue(metric: Metric | undefined): number | null {
  return metric && metric.status !== 'unavailable' && typeof metric.value === 'number' && Number.isFinite(metric.value)
    ? metric.value : null;
}
export function formatMetric(key: string, metric: Metric | undefined): string {
  const value = metricValue(metric);
  if (value === null) return 'Unavailable';
  if (ratioKeys.has(key)) return `${(value * 100).toFixed(1)}%`;
  return `${new Intl.NumberFormat('en', { maximumFractionDigits: 2 }).format(value)}${metric?.unit ? ` ${metric.unit}` : ''}`;
}
export function sourceName(source: string) {
  return source === 'official_5g_nidd' ? 'Official 5G-NIDD' : source === 'fixture' ? 'Development fixture' : source === 'live_sflow' ? 'Live telemetry' : source.replaceAll('_', ' ');
}
export function modeName(mode: RunSummary['mode']) {
  return { csv_replay: 'CSV flow replay', pcap_replay: 'Packet capture replay', live_sflow: 'Live sFlow' }[mode];
}
export function compatibleRuns(runs: RunSummary[], selected: RunSummary): RunSummary[] {
  const settings = ['threshold', 'grace_period', 'drift_delta', 'window_seconds', 'warmup_records', 'warmup_seconds', 'max_records'];
  const signature = (run: RunSummary) => JSON.stringify(settings.map(key => [key, run.config[key] ?? null]));
  return runs.filter(run => run.status === 'completed' && run.source === selected.source && run.mode === selected.mode &&
    run.scenario === selected.scenario && run.unit === selected.unit &&
    run.feature_schema === selected.feature_schema &&
    (run.provenance?.sha256 ?? null) === (selected.provenance?.sha256 ?? null) &&
    signature(run) === signature(selected));
}
export function paretoRuns(runs: RunSummary[], costKey: string): Set<string> {
  const measured = runs.filter(run => run.metrics.f1?.status === 'measured' && run.metrics[costKey]?.status === 'measured' &&
    metricValue(run.metrics.f1) !== null && metricValue(run.metrics[costKey]) !== null);
  return new Set(measured.filter(run => !measured.some(other => {
    const q = metricValue(run.metrics.f1)!; const c = metricValue(run.metrics[costKey])!;
    const oq = metricValue(other.metrics.f1)!; const oc = metricValue(other.metrics[costKey])!;
    return oq >= q && oc <= c && (oq > q || oc < c);
  })).map(run => run.run_id));
}
```

### Every physical line

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>import type { Metric, RunSummary } from &#39;./types&#39;;</code> | Imports metric and run types for compile-time checking. |
| 2 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 3 | <code>const ratioKeys = new Set([&#39;precision&#39;, &#39;recall&#39;, &#39;f1&#39;, &#39;roc_auc&#39;, &#39;false_positive_rate&#39;, &#39;unseen_attack_recall&#39;]);</code> | Stores metric keys whose numeric values are fractions and should display as percentages. |
| 4 | <code>export function metricValue(metric: Metric &#124; undefined): number &#124; null {</code> | Exports one central numeric-extraction rule, accepting a missing metric and returning a number or null. |
| 5 | <code>  return metric &amp;&amp; metric.status !== &#39;unavailable&#39; &amp;&amp; typeof metric.value === &#39;number&#39; &amp;&amp; Number.isFinite(metric.value)</code> | Only accepts an existing metric with status other than unavailable and a finite numeric value; measured zero passes. |
| 6 | <code>    ? metric.value : null;</code> | Returns the valid number, otherwise null. Estimated values can display; later Pareto filtering explicitly requires measured. |
| 7 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 8 | <code>export function formatMetric(key: string, metric: Metric &#124; undefined): string {</code> | Exports a display formatter parameterized by metric name and optional evidence object. |
| 9 | <code>  const value = metricValue(metric);</code> | Normalizes presence/evidence status with metricValue. |
| 10 | <code>  if (value === null) return &#39;Unavailable&#39;;</code> | Shows Unavailable for null/missing/nonfinite/unavailable evidence rather than replacing it with zero. |
| 11 | <code>  if (ratioKeys.has(key)) return `${(value * 100).toFixed(1)}%`;</code> | For listed ratio keys multiplies by 100 and fixes one decimal place, e.g. .8 becomes 80.0%. |
| 12 | <code>  return `${new Intl.NumberFormat(&#39;en&#39;, { maximumFractionDigits: 2 }).format(value)}${metric?.unit ? ` ${metric.unit}` : &#39;&#39;}`;</code> | For other numbers uses English locale with up to two decimals and appends a nonempty saved unit. |
| 13 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 14 | <code>export function sourceName(source: string) {</code> | Exports a friendly provenance-source label function. |
| 15 | <code>  return source === &#39;official_5g_nidd&#39; ? &#39;Official 5G-NIDD&#39; : source === &#39;fixture&#39; ? &#39;Development fixture&#39; : source === &#39;live_sflow&#39; ? &#39;Live telemetry&#39; : source.replaceAll(&#39;_&#39;, &#39; &#39;);</code> | Maps official, fixture, and live source codes to clear labels; unknown source names have underscores replaced with spaces. |
| 16 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 17 | <code>export function modeName(mode: RunSummary[&#39;mode&#39;]) {</code> | Accepts only a mode allowed by RunSummary using an indexed-access type. |
| 18 | <code>  return { csv_replay: &#39;CSV flow replay&#39;, pcap_replay: &#39;Packet capture replay&#39;, live_sflow: &#39;Live sFlow&#39; }[mode];</code> | Looks up the mode's UI description in an object mapping. |
| 19 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 20 | <code>export function compatibleRuns(runs: RunSummary[], selected: RunSummary): RunSummary[] {</code> | Exports the comparison-group filter; the selected run defines required compatibility. |
| 21 | <code>  const settings = [&#39;threshold&#39;, &#39;grace_period&#39;, &#39;drift_delta&#39;, &#39;window_seconds&#39;, &#39;warmup_records&#39;, &#39;warmup_seconds&#39;, &#39;max_records&#39;];</code> | Lists model/window/warm-up/record-limit settings that must match before runs are compared. |
| 22 | <code>  const signature = (run: RunSummary) =&gt; JSON.stringify(settings.map(key =&gt; [key, run.config[key] ?? null]));</code> | Creates a stable ordered JSON signature of those key-value pairs; null and missing settings normalize to null. |
| 23 | <code>  return runs.filter(run =&gt; run.status === &#39;completed&#39; &amp;&amp; run.source === selected.source &amp;&amp; run.mode === selected.mode &amp;&amp;</code> | Starts filtering: candidate must be completed and match selected source and execution mode. |
| 24 | <code>    run.scenario === selected.scenario &amp;&amp; run.unit === selected.unit &amp;&amp;</code> | Also requires matching scenario and observation unit. |
| 25 | <code>    run.feature_schema === selected.feature_schema &amp;&amp;</code> | Requires the same feature schema name. |
| 26 | <code>    (run.provenance?.sha256 ?? null) === (selected.provenance?.sha256 ?? null) &amp;&amp;</code> | Requires equal dataset SHA-256 values; both absent normalize to null and therefore compare equal. |
| 27 | <code>    signature(run) === signature(selected));</code> | Requires equal selected configuration signatures, then completes filter. Seed and sampling rate intentionally are not part of the signature so repeated trials and N values can be compared. |
| 28 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 29 | <code>export function paretoRuns(runs: RunSummary[], costKey: string): Set&lt;string&gt; {</code> | Exports Pareto classification returning a set of run IDs; costKey names the resource metric. |
| 30 | <code>  const measured = runs.filter(run =&gt; run.metrics.f1?.status === &#39;measured&#39; &amp;&amp; run.metrics[costKey]?.status === &#39;measured&#39; &amp;&amp;</code> | Starts by requiring measured evidence status for both F1 and chosen cost. |
| 31 | <code>    metricValue(run.metrics.f1) !== null &amp;&amp; metricValue(run.metrics[costKey]) !== null);</code> | Also requires both values to be numerically usable. |
| 32 | <code>  return new Set(measured.filter(run =&gt; !measured.some(other =&gt; {</code> | Keeps a run only when no measured run dominates it; !some implements absence of a counterexample. |
| 33 | <code>    const q = metricValue(run.metrics.f1)!; const c = metricValue(run.metrics[costKey])!;</code> | Reads the candidate run's F1 q and resource cost c; ! asserts non-null after filtering. |
| 34 | <code>    const oq = metricValue(other.metrics.f1)!; const oc = metricValue(other.metrics[costKey])!;</code> | Reads the competitor's F1 and resource cost. |
| 35 | <code>    return oq &gt;= q &amp;&amp; oc &lt;= c &amp;&amp; (oq &gt; q &#124;&#124; oc &lt; c);</code> | A competitor dominates if quality is no lower, cost no higher, and at least one is strictly better. Equal points do not dominate each other. |
| 36 | <code>  })).map(run =&gt; run.run_id));</code> | Maps remaining runs to IDs and constructs a Set for constant-time UI membership tests. This identifies a frontier, not a knee point. |
| 37 | <code>}</code> | Closes the current function, interface, or control block begun above. |

### Worked comparison example

A has F1 .80 and cost 10; B has F1 .85 and cost 5; C has F1 .70 and cost 2. B dominates A because quality improves and cost falls. B and C are both Pareto-efficient because C is cheaper but less accurate. That frontier does not itself choose a knee point.

compatibleRuns compares a listed set of settings, not every possible config field. Missing checksums/schema identifiers can compare equal. Experiment producers still need to record correct provenance.

## frontend/src/App.tsx

Main M3 dashboard and its chart/card components. Owns polling, selection, errors, and rendering saved evidence.

### Complete source

```tsx
import { useCallback, useEffect, useMemo, useState } from 'react';
import { getOverview, getRun, getRuns, getSeries } from './api';
import { compatibleRuns, formatMetric, metricValue, modeName, paretoRuns, sourceName } from './evidence';
import type { Metric, Overview, RunSummary, Series } from './types';

const POLL_MS = 3000;
const emptySeries: Series = { predictions: [], resources: [], drift: [] };
const number = (value: number) => value.toLocaleString('en');
const timeLabel = (value: number | string) => typeof value === 'number' ? `${value.toFixed(2)} s` : value;
const dateLabel = (value: string) => {
  const date = new Date(value);
  return Number.isNaN(date.valueOf()) ? value : date.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
};

function Badge({ children, tone = '' }: { children: React.ReactNode; tone?: string }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

function MetricCard({ name, metricKey, metric, caption }: { name: string; metricKey: string; metric?: Metric; caption: string }) {
  const missing = metricValue(metric) === null;
  return <article className={`metric-card ${missing ? 'metric-missing' : ''}`}>
    <div className="metric-label">{name}<span className="metric-symbol" aria-hidden="true">↗</span></div>
    <div className="metric-value">{formatMetric(metricKey, metric)}</div>
    <p>{missing ? metric?.reason || 'No measurement saved for this run.' : caption}</p>
    <span className={`evidence-tag ${metric?.status || 'unavailable'}`}>{missing ? 'unavailable' : metric?.status}</span>
  </article>;
}

function Timeline({ series, unit, threshold }: { series: Series; unit: string; threshold: number }) {
  const points = series.predictions;
  if (!points.length) return <div className="chart-empty"><span className="empty-glyph" aria-hidden="true">⌁</span><h3>No predictions recorded yet</h3><p>This panel will show detection probabilities and ground truth when the run saves evaluated observations.</p></div>;
  const width = 840, height = 240, left = 45, right = 20, top = 15, bottom = 40;
  const min = Math.min(...points.map(p => p.index)), max = Math.max(...points.map(p => p.index));
  const x = (i: number) => left + ((i - min) / Math.max(1, max - min)) * (width - left - right);
  const y = (score: number) => top + (1 - Math.min(1, Math.max(0, score))) * (height - top - bottom);
  let penDown = false;
  const path = points.map(point => {
    if (point.score === null) { penDown = false; return ''; }
    const command = penDown ? 'L' : 'M'; penDown = true;
    return `${command}${x(point.index).toFixed(2)},${y(point.score).toFixed(2)}`;
  }).join(' ');
  const attackCount = points.filter(p => p.y_true === 1 || p.y_true === true).length;
  return <>
    <div className="chart-legend"><span><i className="legend-line" />Attack probability</span><span><i className="legend-dot attack" />Attack ground truth</span><span><i className="legend-dot benign" />Benign ground truth</span><span><i className="legend-line drift" />Drift alarm</span></div>
    <svg className="timeline-svg" viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`Prediction timeline with ${points.length} ${unit} observations, ${attackCount} attack labels, and ${series.drift.length} drift events.`}>
      {[0, .25, .5, .75, 1].map(tick => <g key={tick}><line className="grid-line" x1={left} y1={y(tick)} x2={width - right} y2={y(tick)} /><text className="axis-label" x={left - 12} y={y(tick) + 4} textAnchor="end">{tick.toFixed(2)}</text></g>)}
      <line className="threshold-line" x1={left} y1={y(threshold)} x2={width - right} y2={y(threshold)} />
      {points.filter(p => p.y_true !== null).map(p => <circle key={p.index} cx={x(p.index)} cy={y(p.y_true === 1 || p.y_true === true ? 1 : 0)} r="2.3" className={p.y_true === 1 || p.y_true === true ? 'truth-attack' : 'truth-benign'}><title>{`Observation ${p.index}: ${p.attack_family || (p.y_true ? 'attack' : 'benign')}; ${p.phase}; ${timeLabel(p.time)}`}</title></circle>)}
      {series.drift.filter(d => d.index >= min && d.index <= max).map((d, i) => <line key={i} className="drift-line" x1={x(d.index)} y1={top} x2={x(d.index)} y2={height - bottom}><title>{`${d.detector}: ${d.event} at ${d.index}`}</title></line>)}
      <path d={path} className="probability-line" />
      {[0, .25, .5, .75, 1].map(t => <text key={t} className="axis-label" x={x(min + t * (max - min))} y={height - bottom + 22} textAnchor="middle">{Math.round(min + t * (max - min))}</text>)}
      <text className="axis-title" x={width / 2} y={height - 2} textAnchor="middle">{unit === 'flow' ? 'Flow' : 'Window'} observation index</text>
    </svg>
    <p className="chart-note">Up to 1,000 observations, spread across long runs. Dashed line: decision threshold {threshold}. Warm-up and unlabeled records may appear in this timeline; reported quality metrics use evaluated labels only.</p>
  </>;
}

function Tradeoff({ runs, selectedId }: { runs: RunSummary[]; selectedId: string }) {
  const [costKey, setCostKey] = useState(() => runs.some(run =>
    run.metrics.telemetry_bandwidth_kbps?.status === 'measured' && metricValue(run.metrics.telemetry_bandwidth_kbps) !== null)
    ? 'telemetry_bandwidth_kbps' : 'cpu_percent_mean');
  const frontier = useMemo(() => paretoRuns(runs, costKey), [runs, costKey]);
  const available = runs.filter(run => run.metrics.f1?.status === 'measured' && run.metrics[costKey]?.status === 'measured' && metricValue(run.metrics.f1) !== null && metricValue(run.metrics[costKey]) !== null);
  const costName = costKey === 'telemetry_bandwidth_kbps' ? 'Telemetry bandwidth (kbit/s)' : 'Detector CPU (%)';
  const w = 480, h = 240, left = 55, right = 30, top = 20, bottom = 45;
  const maxCost = Math.max(1, ...available.map(run => metricValue(run.metrics[costKey])!)) * 1.1;
  const x = (c: number) => left + c / maxCost * (w - left - right);
  const y = (q: number) => top + (1 - q) * (h - top - bottom);
  return <>
    <label className="inline-control" htmlFor="cost-axis">Overhead measure<select id="cost-axis" value={costKey} onChange={e => setCostKey(e.target.value)}><option value="telemetry_bandwidth_kbps">Telemetry bandwidth</option><option value="cpu_percent_mean">Detector CPU</option></select></label>
    {available.length ? <>
      <svg className="tradeoff-svg" viewBox={`0 0 ${w} ${h}`} role="img" aria-label={`${available.length} compatible measured trials comparing F1 and ${costName}. ${frontier.size} Pareto-efficient trials.`}>
        {[0, .25, .5, .75, 1].map(q => <g key={q}><line className="grid-line" x1={left} y1={y(q)} x2={w - right} y2={y(q)} /><text className="axis-label" x={left - 10} y={y(q) + 4} textAnchor="end">{Math.round(q * 100)}%</text></g>)}
        {[0, .5, 1].map(c => <text key={c} className="axis-label" x={x(c * maxCost)} y={h - bottom + 20} textAnchor="middle">{(c * maxCost).toFixed(1)}</text>)}
        {available.map(run => <g key={run.run_id}><circle cx={x(metricValue(run.metrics[costKey])!)} cy={y(metricValue(run.metrics.f1)!)} r={run.run_id === selectedId ? 7 : 5} className={frontier.has(run.run_id) ? 'pareto-point' : 'comparison-point'}><title>{`${run.run_id}: N=${run.sampling_rate}, F1 ${formatMetric('f1', run.metrics.f1)}, cost ${formatMetric(costKey, run.metrics[costKey])}${frontier.has(run.run_id) ? ', Pareto efficient' : ''}`}</title></circle><text className="point-label" x={x(metricValue(run.metrics[costKey])!) + 9} y={y(metricValue(run.metrics.f1)!) - 7}>N={run.sampling_rate}</text></g>)}
        <text className="axis-title" x={w / 2} y={h - 4} textAnchor="middle">{costName} · lower is better</text>
      </svg>
      <div className="chart-legend"><span><i className="legend-dot pareto" />Pareto efficient</span><span><i className="legend-dot comparison" />Other measured trials</span></div>
    </> : <div className="chart-empty compact"><h3>Trade-off evidence pending</h3><p>At least one completed trial with measured F1 and {costName.toLowerCase()} is required.</p></div>}
    <p className="chart-note">Only completed trials matching this run's source, mode, scenario, feature schema, dataset checksum, and model settings are compared. Estimated or unavailable costs are excluded.</p>
  </>;
}

const detailMetrics: [string, string][] = [
  ['roc_auc', 'ROC-AUC'], ['false_positive_rate', 'False-positive rate'], ['detection_time_seconds', 'Detection time'],
  ['packets_to_detect', 'Packets to detect'], ['unseen_attack_recall', 'Unseen-attack recall'], ['post_drift_recovery_seconds', 'Post-drift recovery'],
  ['cpu_percent_mean', 'Detector CPU · mean'], ['cpu_percent_p95', 'Detector CPU · p95'], ['controller_cpu_percent_mean', 'Controller CPU · mean'],
  ['controller_cpu_percent_p95', 'Controller CPU · p95'], ['telemetry_bandwidth_kbps', 'Telemetry bandwidth'],
  ['openflow_bandwidth_kbps', 'OpenFlow bandwidth'], ['flow_table_entries', 'Flow-table entries'],
];

export default function App() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [overview, setOverview] = useState<Overview | null>(null);
  const [selectedId, setSelectedId] = useState('');
  const [selected, setSelected] = useState<RunSummary | null>(null);
  const [series, setSeries] = useState<Series>(emptySeries);
  const [listLoading, setListLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState('');
  const [detailError, setDetailError] = useState('');
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);
  const refresh = useCallback(() => setRefreshKey(key => key + 1), []);

  useEffect(() => {
    const controller = new AbortController(); let timer: ReturnType<typeof setTimeout>;
    const load = async () => {
      try {
        const [nextRuns, nextOverview] = await Promise.all([getRuns(controller.signal), getOverview(controller.signal)]);
        if (controller.signal.aborted) return;
        setRuns(nextRuns); setOverview(nextOverview); setError(''); setUpdatedAt(new Date());
        setSelectedId(current => nextRuns.some(run => run.run_id === current) ? current : nextRuns[0]?.run_id || '');
      } catch (e) { if (!controller.signal.aborted) setError(e instanceof Error ? e.message : 'Could not connect to the experiment server.'); }
      finally {
        if (!controller.signal.aborted) { setListLoading(false); if (autoRefresh) timer = setTimeout(load, POLL_MS); }
      }
    };
    void load();
    return () => { controller.abort(); clearTimeout(timer); };
  }, [autoRefresh, refreshKey]);

  useEffect(() => {
    if (!selectedId) { setSelected(null); setSeries(emptySeries); return; }
    const controller = new AbortController(); let timer: ReturnType<typeof setTimeout>;
    setSelected(null); setSeries(emptySeries); setDetailError(''); setDetailLoading(true);
    const load = async () => {
      try {
        const [run, data] = await Promise.all([getRun(selectedId, controller.signal), getSeries(selectedId, controller.signal)]);
        if (!controller.signal.aborted) { setSelected(run); setSeries(data); setDetailError(''); }
      } catch (e) { if (!controller.signal.aborted) setDetailError(e instanceof Error ? e.message : 'Could not load this run.'); }
      finally {
        if (!controller.signal.aborted) { setDetailLoading(false); if (autoRefresh) timer = setTimeout(load, POLL_MS); }
      }
    };
    void load();
    return () => { controller.abort(); clearTimeout(timer); };
  }, [selectedId, autoRefresh, refreshKey]);

  const comparisons = useMemo(() => selected ? compatibleRuns(runs, selected).sort((a, b) => a.sampling_rate - b.sampling_rate || a.seed - b.seed) : [], [runs, selected]);
  return <>
    <a className="skip-link" href="#main">Skip to experiment results</a>
    <header className="topbar"><div className="brand"><span className="brand-icon" aria-hidden="true"><i /><i /><i /></span><span>M3<span className="brand-divider"> / </span><span className="brand-light">Observatory</span></span></div><span className="topbar-subtitle">ADAPTIVE DDOS DETECTION</span><span className="project-tag">5G-NIDD · SDN</span></header>
    <main id="main">
      <div className="page-heading"><div><div className="eyebrow">EXPERIMENT WORKSPACE <span>01 / M3</span></div><h1>Less telemetry. <span>Measured detection.</span></h1><p>Sampling, adaptive learning, and the evidence behind every result.</p></div><div className="refresh-tools"><label className="refresh-toggle"><input type="checkbox" checked={autoRefresh} onChange={e => setAutoRefresh(e.target.checked)} />Auto-refresh · 3s</label><button onClick={refresh} className="button"><span aria-hidden="true">↻</span> Refresh</button></div></div>
      <div className="connection-line" role="status"><span className={`connection-dot ${error ? 'offline' : updatedAt ? 'online' : ''}`} />{error ? 'Evidence connection unavailable' : updatedAt ? `Connected · updated ${updatedAt.toLocaleTimeString()}` : 'Connecting to experiment server…'}{!autoRefresh && <span className="paused-label">Polling paused</span>}</div>
      {error && <div className="error-banner" role="alert"><strong>Could not refresh experiments.</strong><span>{error} {runs.length ? 'Previously loaded evidence remains visible.' : 'Start the FastAPI server on port 8000, then refresh.'}</span></div>}
      <section className="overview-strip" aria-label="Experiment overview">{[['Saved runs', overview?.total_runs], ['Completed', overview?.completed_runs], ['Running', overview?.running_runs], ['Failed', overview?.failed_runs]].map(([label, value]) => <div key={String(label)}><span>{label}</span><strong>{value === undefined ? '—' : number(Number(value))}</strong></div>)}<div className="overview-description"><span>METHOD</span><strong>Hoeffding Adaptive Tree <span>+ ADWIN</span></strong></div></section>
      {listLoading ? <div className="state-panel" role="status"><span className="loader" /><h2>Loading experiment evidence</h2><p>Reading saved runs and current experiment status.</p></div> : !runs.length ? <div className="state-panel"><div className="empty-icon" aria-hidden="true">⌁</div><div className="eyebrow">{error ? 'WAITING FOR EXPERIMENT EVIDENCE' : 'READY FOR THE FIRST RUN'}</div><h2>{error ? 'Connect the experiment server' : 'No experiment results yet'}</h2><p>{error ? 'Saved results cannot be checked until the experiment server responds. Start the server on port 8000 and refresh this page.' : 'Run the M3 experiment runner with verified official 5G-NIDD data. Saved results will appear here automatically.'}</p>{!error && <div className="empty-steps"><span>01 · Verify dataset</span><span>02 · Run N = 1 baseline</span><span>03 · Compare sampling rates</span></div>}</div> : <>
        <section className="run-toolbar" aria-label="Run selection"><div className="run-label"><span className="eyebrow">INSPECT EXPERIMENT</span><label htmlFor="run-select">Selected run</label></div><select id="run-select" value={selectedId} onChange={e => setSelectedId(e.target.value)}>{runs.map(run => <option key={run.run_id} value={run.run_id}>{run.run_id} · N={run.sampling_rate} · {run.scenario} · {run.status}</option>)}</select><div className="selection-count">{runs.length} saved {runs.length === 1 ? 'run' : 'runs'}</div></section>
        {detailError && <div className="error-banner" role="alert"><strong>Run evidence could not be loaded.</strong><span>{detailError} {selected ? 'Shown run details are from the last successful refresh.' : ''}</span></div>}
        {detailLoading ? <div className="state-panel small" role="status"><span className="loader" /><p>Loading selected run…</p></div> : selected && <>
          <section className="run-context"><div className="run-context-head"><div><Badge tone={selected.status}>{selected.status}</Badge><Badge tone={selected.source === 'fixture' ? 'fixture' : 'source'}>{sourceName(selected.source)}</Badge><Badge>{modeName(selected.mode)}</Badge><h2>{selected.scenario.replaceAll('_', ' ')}</h2></div><div className="sampling-emblem"><span>SAMPLING RATE</span><strong>1<span> / </span>{selected.sampling_rate}</strong></div></div><div className="context-bottom"><span>Run <code>{selected.run_id}</code></span><span>Seed {selected.seed}</span><span>Evaluation unit: <strong>{selected.unit}</strong></span><span>Started {dateLabel(selected.created_at)}</span></div></section>
          {selected.source !== 'official_5g_nidd' && <div className="notice">This run is labeled <strong>{sourceName(selected.source)}</strong>. Its results do not establish performance on official 5G-NIDD.</div>}
          <details className="provenance-details"><summary>Dataset and feature provenance</summary><pre>{JSON.stringify({ feature_schema: selected.feature_schema ?? 'Not recorded', provenance: selected.provenance ?? 'Not recorded' }, null, 2)}</pre></details>
          {selected.mode === 'csv_replay' && <div className="notice">This run samples flow records. Packet sampling and live SDN overhead require capture replay or live sFlow measurements.</div>}
          {selected.status === 'failed' && <div className="error-banner" role="alert"><strong>This run failed.</strong><span>{selected.error || 'No error detail was saved.'}</span></div>}
          <section className="metric-grid" aria-label="Detection metrics"><MetricCard name="Precision" metricKey="precision" metric={selected.metrics.precision} caption="How often attack predictions are correct" /><MetricCard name="Recall" metricKey="recall" metric={selected.metrics.recall} caption="Share of labeled attacks detected" /><MetricCard name="F1 score" metricKey="f1" metric={selected.metrics.f1} caption="Balance of precision and recall" /><MetricCard name="Inference latency" metricKey="inference_latency_ms" metric={selected.metrics.inference_latency_ms} caption="Average time per prediction" /></section>
          <section className="panel timeline-panel"><div className="panel-heading"><div><span className="eyebrow">DETECTION THROUGH TIME</span><h2>Adaptive learning timeline</h2></div><Badge>{number(selected.drift_count)} drift {selected.drift_count === 1 ? 'alarm' : 'alarms'}</Badge></div><Timeline series={series} unit={selected.unit} threshold={typeof selected.config.threshold === 'number' ? selected.config.threshold : .5} /></section>
          <div className="analysis-grid"><section className="panel"><div className="panel-heading"><div><span className="eyebrow">ACCURACY × OVERHEAD</span><h2>Sampling trade-off</h2></div></div><Tradeoff runs={comparisons} selectedId={selected.run_id} /></section><section className="panel"><div className="panel-heading"><div><span className="eyebrow">STREAM ACCOUNTING</span><h2>Every observation accounted for</h2></div></div><dl className="count-list">{Object.entries(selected.counts).map(([key, value]) => <div key={key}><dt>{key.replaceAll('_', ' ')}</dt><dd>{number(value)}</dd></div>)}</dl><div className="account-note">Input and sampling counts are recorded independently from evaluated labels. Warm-up, exclusions, and unlabeled records are retained in the evidence.</div></section></div>
          <section className="panel"><div className="panel-heading"><div><span className="eyebrow">COMPATIBLE COMPLETED TRIALS</span><h2>Sampling comparison</h2></div><Badge>{comparisons.length} trials</Badge></div><div className="table-scroll"><table><caption className="sr-only">Individual compatible trials; no implicit averaging of repeated trials.</caption><thead><tr><th scope="col">Run / seed</th><th scope="col">Sampling</th><th scope="col">F1</th><th scope="col">Recall</th><th scope="col">CPU mean</th><th scope="col">Telemetry</th><th scope="col">Drift alarms</th></tr></thead><tbody>{comparisons.map(run => <tr key={run.run_id} className={run.run_id === selected.run_id ? 'selected-row' : ''}><th scope="row"><button className="run-link" onClick={() => setSelectedId(run.run_id)}>{run.run_id}</button><small>Seed {run.seed}</small></th><td><Badge>1 / {run.sampling_rate}</Badge></td>{['f1', 'recall', 'cpu_percent_mean', 'telemetry_bandwidth_kbps'].map(key => <td key={key}>{formatMetric(key, run.metrics[key])}{run.metrics[key]?.status === 'estimated' && <small>estimated</small>}</td>)}<td>{run.drift_count}</td></tr>)}{!comparisons.length && <tr><td colSpan={7}>No compatible completed trials yet.</td></tr>}</tbody></table></div></section>
          <div className="analysis-grid details-grid"><section className="panel"><div className="panel-heading"><div><span className="eyebrow">METRIC EVIDENCE</span><h2>Measurements & limitations</h2></div></div><div className="evidence-list">{detailMetrics.map(([key, label]) => <div key={key}><div><strong>{label}</strong><small>{metricValue(selected.metrics[key]) === null ? selected.metrics[key]?.reason || 'No measurement saved.' : selected.metrics[key]?.reason || selected.metrics[key]?.status}</small></div><span>{formatMetric(key, selected.metrics[key])}</span></div>)}</div></section><section className="panel"><div className="panel-heading"><div><span className="eyebrow">ADWIN / HAT</span><h2>Drift event log</h2></div></div>{series.drift.length ? <ol className="drift-log">{series.drift.map((event, i) => <li key={`${event.index}-${i}`}><span className="event-dot" /><div><strong>{event.event.replaceAll('_', ' ')}</strong><p>{event.detector} · observation {event.index}</p><small>{timeLabel(event.time)}</small></div></li>)}</ol> : <div className="chart-empty compact"><h3>No drift events saved</h3><p>Absence of an alarm does not establish absence of a distribution change.</p></div>}<details className="config-details"><summary>Run configuration and provenance</summary><pre>{JSON.stringify(selected.config, null, 2)}</pre></details></section></div>
        </>}
      </>}
      <footer><span>M3 Observatory <span className="footer-dot">·</span> 5G-NIDD sampled telemetry</span><span>Evidence first. Every number traces to a saved run.</span></footer>
    </main>
  </>;
}
```

### Every physical line

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>import { useCallback, useEffect, useMemo, useState } from &#39;react&#39;;</code> | Imports React hooks: state stores changing values, effects handle requests, memo caches computed comparisons, callback keeps a stable refresh function. |
| 2 | <code>import { getOverview, getRun, getRuns, getSeries } from &#39;./api&#39;;</code> | Imports the four backend readers used for the run list, overview, selected summary, and timeline. |
| 3 | <code>import { compatibleRuns, formatMetric, metricValue, modeName, paretoRuns, sourceName } from &#39;./evidence&#39;;</code> | Imports presentation and evidence rules; this component delegates metric formatting, comparison grouping, and Pareto calculation to evidence.ts. |
| 4 | <code>import type { Metric, Overview, RunSummary, Series } from &#39;./types&#39;;</code> | Imports compile-time shapes only; TypeScript removes these type imports from emitted JavaScript. |
| 5 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 6 | <code>const POLL_MS = 3000;</code> | Sets the delay between completed polling requests to 3,000 milliseconds. |
| 7 | <code>const emptySeries: Series = { predictions: [], resources: [], drift: [] };</code> | Defines a typed empty timeline; reset and initial states use three empty arrays instead of invented observations. |
| 8 | <code>const number = (value: number) =&gt; value.toLocaleString(&#39;en&#39;);</code> | Formats counts with English grouping separators, e.g. 12000 becomes 12,000. |
| 9 | <code>const timeLabel = (value: number &#124; string) =&gt; typeof value === &#39;number&#39; ? `${value.toFixed(2)} s` : value;</code> | Formats numeric relative times to two decimal places plus seconds; timestamp strings remain as supplied. |
| 10 | <code>const dateLabel = (value: string) =&gt; {</code> | Begins a helper accepting a saved creation-time string. |
| 11 | <code>  const date = new Date(value);</code> | Parses that string as a JavaScript Date. |
| 12 | <code>  return Number.isNaN(date.valueOf()) ? value : date.toLocaleString(undefined, { month: &#39;short&#39;, day: &#39;numeric&#39;, hour: &#39;2-digit&#39;, minute: &#39;2-digit&#39; });</code> | Returns the original string if parsing failed; otherwise uses the user's locale for abbreviated month/day and two-digit hour/minute. |
| 13 | <code>};</code> | Closes the function/object expression and terminates its declaration. |
| 14 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 15 | <code>function Badge({ children, tone = &#39;&#39; }: { children: React.ReactNode; tone?: string }) {</code> | Defines a reusable badge with arbitrary React children and optional CSS tone; destructuring gives tone an empty default. |
| 16 | <code>  return &lt;span className={`badge ${tone}`}&gt;{children}&lt;/span&gt;;</code> | Renders badge text/content in a span whose classes combine base badge styling with its supplied tone. |
| 17 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 18 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 19 | <code>function MetricCard({ name, metricKey, metric, caption }: { name: string; metricKey: string; metric?: Metric; caption: string }) {</code> | Defines a metric card; the metric is optional because some run summaries have no value for a particular measurement. |
| 20 | <code>  const missing = metricValue(metric) === null;</code> | Uses the evidence helper to classify missing, unavailable, or nonfinite measurements as missing; a valid measured zero remains present. |
| 21 | <code>  return &lt;article className={`metric-card ${missing ? &#39;metric-missing&#39; : &#39;&#39;}`}&gt;</code> | Starts an article and adds metric-missing styling only when there is no usable numeric value. |
| 22 | <code>    &lt;div className=&quot;metric-label&quot;&gt;{name}&lt;span className=&quot;metric-symbol&quot; aria-hidden=&quot;true&quot;&gt;↗&lt;/span&gt;&lt;/div&gt;</code> | Displays the metric name and a decorative arrow excluded from screen-reader announcements. |
| 23 | <code>    &lt;div className=&quot;metric-value&quot;&gt;{formatMetric(metricKey, metric)}&lt;/div&gt;</code> | Formats the metric by key, so ratios become percentages and other measures retain units. |
| 24 | <code>    &lt;p&gt;{missing ? metric?.reason &#124;&#124; &#39;No measurement saved for this run.&#39; : caption}&lt;/p&gt;</code> | For missing metrics shows their saved reason or a fallback; otherwise explains the metric using the supplied caption. |
| 25 | <code>    &lt;span className={`evidence-tag ${metric?.status &#124;&#124; &#39;unavailable&#39;}`}&gt;{missing ? &#39;unavailable&#39; : metric?.status}&lt;/span&gt;</code> | Adds evidence-status styling, defaulting to unavailable; visible text also says unavailable when the numeric value is missing. |
| 26 | <code>  &lt;/article&gt;;</code> | Closes the metric article returned by this component. |
| 27 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 28 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 29 | <code>function Timeline({ series, unit, threshold }: { series: Series; unit: string; threshold: number }) {</code> | Defines the timeline renderer using saved predictions, observation-unit label, and decision threshold. |
| 30 | <code>  const points = series.predictions;</code> | Uses only the prediction array as the line/ground-truth dataset; resources are not charted here. |
| 31 | <code>  if (!points.length) return &lt;div className=&quot;chart-empty&quot;&gt;&lt;span className=&quot;empty-glyph&quot; aria-hidden=&quot;true&quot;&gt;⌁&lt;/span&gt;&lt;h3&gt;No predictions recorded yet&lt;/h3&gt;&lt;p&gt;This panel will show detection probabilities and ground truth when the run saves evaluated observations.&lt;/p&gt;&lt;/div&gt;;</code> | Returns an empty-state explanation when no predictions exist, avoiding a fabricated empty graph. |
| 32 | <code>  const width = 840, height = 240, left = 45, right = 20, top = 15, bottom = 40;</code> | Defines SVG virtual width/height and margins; these are drawing coordinates, while CSS controls displayed size. |
| 33 | <code>  const min = Math.min(...points.map(p =&gt; p.index)), max = Math.max(...points.map(p =&gt; p.index));</code> | Finds smallest/largest saved observation index for the x-axis using mapped index arrays and spread arguments. |
| 34 | <code>  const x = (i: number) =&gt; left + ((i - min) / Math.max(1, max - min)) * (width - left - right);</code> | Maps an observation index into plot x coordinates; Math.max prevents division by zero for a one-observation series. |
| 35 | <code>  const y = (score: number) =&gt; top + (1 - Math.min(1, Math.max(0, score))) * (height - top - bottom);</code> | Maps probability to SVG y coordinates, clamps to [0,1], and inverts because SVG y grows downward. |
| 36 | <code>  let penDown = false;</code> | Tracks whether the SVG path currently has a previous point to connect to. |
| 37 | <code>  const path = points.map(point =&gt; {</code> | Begins converting prediction records into SVG path instructions. |
| 38 | <code>    if (point.score === null) { penDown = false; return &#39;&#39;; }</code> | An unknown score lifts the drawing pen and emits no coordinates, so missing probabilities create visible gaps. |
| 39 | <code>    const command = penDown ? &#39;L&#39; : &#39;M&#39;; penDown = true;</code> | Chooses L (line to) after a previous point or M (move to) after a gap, then marks the pen active. |
| 40 | <code>    return `${command}${x(point.index).toFixed(2)},${y(point.score).toFixed(2)}`;</code> | Outputs a move/line command with x,y coordinates rounded to two decimals. |
| 41 | <code>  }).join(&#39; &#39;);</code> | Joins commands with spaces into the single SVG path-data string. |
| 42 | <code>  const attackCount = points.filter(p =&gt; p.y_true === 1 &#124;&#124; p.y_true === true).length;</code> | Counts attack labels represented as numeric 1 or boolean true; unknown labels are not counted as attacks. |
| 43 | <code>  return &lt;&gt;</code> | Starts a React fragment so the legend, SVG, and note can be returned as siblings without a wrapper element. |
| 44 | <code>    &lt;div className=&quot;chart-legend&quot;&gt;&lt;span&gt;&lt;i className=&quot;legend-line&quot; /&gt;Attack probability&lt;/span&gt;&lt;span&gt;&lt;i className=&quot;legend-dot attack&quot; /&gt;Attack ground truth&lt;/span&gt;&lt;span&gt;&lt;i className=&quot;legend-dot benign&quot; /&gt;Benign ground truth&lt;/span&gt;&lt;span&gt;&lt;i className=&quot;legend-line drift&quot; /&gt;Drift alarm&lt;/span&gt;&lt;/div&gt;</code> | Builds four legend entries matching probability, attack/benign truth dots, and drift styling. |
| 45 | <code>    &lt;svg className=&quot;timeline-svg&quot; viewBox={`0 0 ${width} ${height}`} role=&quot;img&quot; aria-label={`Prediction timeline with ${points.length} ${unit} observations, ${attackCount} attack labels, and ${series.drift.length} drift events.`}&gt;</code> | Opens a responsive SVG with image semantics and an accessible description containing real point, attack, and drift counts. |
| 46 | <code>      {[0, .25, .5, .75, 1].map(tick =&gt; &lt;g key={tick}&gt;&lt;line className=&quot;grid-line&quot; x1={left} y1={y(tick)} x2={width - right} y2={y(tick)} /&gt;&lt;text className=&quot;axis-label&quot; x={left - 12} y={y(tick) + 4} textAnchor=&quot;end&quot;&gt;{tick.toFixed(2)}&lt;/text&gt;&lt;/g&gt;)}</code> | Draws horizontal grid lines at probabilities 0, .25, .5, .75, and 1 and labels them with two decimals; stable tick values are React keys. |
| 47 | <code>      &lt;line className=&quot;threshold-line&quot; x1={left} y1={y(threshold)} x2={width - right} y2={y(threshold)} /&gt;</code> | Draws the decision-threshold reference line using the same probability-to-y mapping. |
| 48 | <code>      {points.filter(p =&gt; p.y_true !== null).map(p =&gt; &lt;circle key={p.index} cx={x(p.index)} cy={y(p.y_true === 1 &#124;&#124; p.y_true === true ? 1 : 0)} r=&quot;2.3&quot; className={p.y_true === 1 &#124;&#124; p.y_true === true ? &#39;truth-attack&#39; : &#39;truth-benign&#39;}&gt;&lt;title&gt;{`Observation ${p.index}: ${p.attack_family &#124;&#124; (p.y_true ? &#39;attack&#39; : &#39;benign&#39;)}; ${p.phase}; ${timeLabel(p.time)}`}&lt;/title&gt;&lt;/circle&gt;)}</code> | Draws one truth dot for each labeled point; attack dots sit at 1, benign at 0. Tooltips contain index, attack family/fallback, phase, and formatted time; null labels are omitted. |
| 49 | <code>      {series.drift.filter(d =&gt; d.index &gt;= min &amp;&amp; d.index &lt;= max).map((d, i) =&gt; &lt;line key={i} className=&quot;drift-line&quot; x1={x(d.index)} y1={top} x2={x(d.index)} y2={height - bottom}&gt;&lt;title&gt;{`${d.detector}: ${d.event} at ${d.index}`}&lt;/title&gt;&lt;/line&gt;)}</code> | Draws vertical drift lines only for events within the current index range; SVG titles expose detector, event, and index. |
| 50 | <code>      &lt;path d={path} className=&quot;probability-line&quot; /&gt;</code> | Draws the probability trace from the previously computed SVG path string. |
| 51 | <code>      {[0, .25, .5, .75, 1].map(t =&gt; &lt;text key={t} className=&quot;axis-label&quot; x={x(min + t * (max - min))} y={height - bottom + 22} textAnchor=&quot;middle&quot;&gt;{Math.round(min + t * (max - min))}&lt;/text&gt;)}</code> | Places five evenly spaced x labels across the observed index range, rounded to whole observation indices. |
| 52 | <code>      &lt;text className=&quot;axis-title&quot; x={width / 2} y={height - 2} textAnchor=&quot;middle&quot;&gt;{unit === &#39;flow&#39; ? &#39;Flow&#39; : &#39;Window&#39;} observation index&lt;/text&gt;</code> | Labels the x-axis Flow observation index for flow units and Window observation index otherwise. |
| 53 | <code>    &lt;/svg&gt;</code> | Closes the SVG graphic. |
| 54 | <code>    &lt;p className=&quot;chart-note&quot;&gt;Up to 1,000 observations, spread across long runs. Dashed line: decision threshold {threshold}. Warm-up and unlabeled records may appear in this timeline; reported quality metrics use evaluated labels only.&lt;/p&gt;</code> | Explains the 1,000-point request limit, threshold, and why warm-up/unlabeled timeline points do not all contribute to quality metrics. |
| 55 | <code>  &lt;/&gt;;</code> | Closes the returned React fragment. |
| 56 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 57 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 58 | <code>function Tradeoff({ runs, selectedId }: { runs: RunSummary[]; selectedId: string }) {</code> | Defines a trade-off chart of compatible run summaries and the currently selected run ID. |
| 59 | <code>  const [costKey, setCostKey] = useState(() =&gt; runs.some(run =&gt;</code> | Begins lazy initialization of the cost-axis state by checking whether any supplied run has usable measured bandwidth. |
| 60 | <code>    run.metrics.telemetry_bandwidth_kbps?.status === &#39;measured&#39; &amp;&amp; metricValue(run.metrics.telemetry_bandwidth_kbps) !== null)</code> | Requires bandwidth evidence to be measured and numerically available for choosing it as the initial axis. |
| 61 | <code>    ? &#39;telemetry_bandwidth_kbps&#39; : &#39;cpu_percent_mean&#39;);</code> | Chooses bandwidth initially if such evidence exists; otherwise chooses mean detector CPU. This initializer runs on component mount, not every prop update. |
| 62 | <code>  const frontier = useMemo(() =&gt; paretoRuns(runs, costKey), [runs, costKey]);</code> | Recomputes the set of nondominated run IDs only when the runs or selected cost metric change. |
| 63 | <code>  const available = runs.filter(run =&gt; run.metrics.f1?.status === &#39;measured&#39; &amp;&amp; run.metrics[costKey]?.status === &#39;measured&#39; &amp;&amp; metricValue(run.metrics.f1) !== null &amp;&amp; metricValue(run.metrics[costKey]) !== null);</code> | Keeps chart points only when both F1 and the selected cost are measured and have usable numeric values. |
| 64 | <code>  const costName = costKey === &#39;telemetry_bandwidth_kbps&#39; ? &#39;Telemetry bandwidth (kbit/s)&#39; : &#39;Detector CPU (%)&#39;;</code> | Sets the human-readable cost-axis title and its units according to the dropdown. |
| 65 | <code>  const w = 480, h = 240, left = 55, right = 30, top = 20, bottom = 45;</code> | Defines the trade-off SVG's virtual canvas and plot margins. |
| 66 | <code>  const maxCost = Math.max(1, ...available.map(run =&gt; metricValue(run.metrics[costKey])!)) * 1.1;</code> | Computes a maximum cost with a minimum base of 1 and 10% headroom; non-null assertions rely on earlier filtering. |
| 67 | <code>  const x = (c: number) =&gt; left + c / maxCost * (w - left - right);</code> | Maps cost to horizontal coordinates, where smaller costs lie farther left. |
| 68 | <code>  const y = (q: number) =&gt; top + (1 - q) * (h - top - bottom);</code> | Maps F1 to vertical coordinates, where larger quality values lie higher. |
| 69 | <code>  return &lt;&gt;</code> | Starts the fragment containing control, chart/empty state, and evidence note. |
| 70 | <code>    &lt;label className=&quot;inline-control&quot; htmlFor=&quot;cost-axis&quot;&gt;Overhead measure&lt;select id=&quot;cost-axis&quot; value={costKey} onChange={e =&gt; setCostKey(e.target.value)}&gt;&lt;option value=&quot;telemetry_bandwidth_kbps&quot;&gt;Telemetry bandwidth&lt;/option&gt;&lt;option value=&quot;cpu_percent_mean&quot;&gt;Detector CPU&lt;/option&gt;&lt;/select&gt;&lt;/label&gt;</code> | Renders a labeled controlled select; changing its value updates costKey and therefore available points, title, and Pareto classification. |
| 71 | <code>    {available.length ? &lt;&gt;</code> | Branches on whether at least one measured point exists; a nonempty set enters the SVG branch. |
| 72 | <code>      &lt;svg className=&quot;tradeoff-svg&quot; viewBox={`0 0 ${w} ${h}`} role=&quot;img&quot; aria-label={`${available.length} compatible measured trials comparing F1 and ${costName}. ${frontier.size} Pareto-efficient trials.`}&gt;</code> | Starts the trade-off image and announces the number of compatible measured trials and frontier members. |
| 73 | <code>        {[0, .25, .5, .75, 1].map(q =&gt; &lt;g key={q}&gt;&lt;line className=&quot;grid-line&quot; x1={left} y1={y(q)} x2={w - right} y2={y(q)} /&gt;&lt;text className=&quot;axis-label&quot; x={left - 10} y={y(q) + 4} textAnchor=&quot;end&quot;&gt;{Math.round(q * 100)}%&lt;/text&gt;&lt;/g&gt;)}</code> | Draws five F1 grid levels and converts their labels from ratios into integer percentages. |
| 74 | <code>        {[0, .5, 1].map(c =&gt; &lt;text key={c} className=&quot;axis-label&quot; x={x(c * maxCost)} y={h - bottom + 20} textAnchor=&quot;middle&quot;&gt;{(c * maxCost).toFixed(1)}&lt;/text&gt;)}</code> | Labels cost zero, midpoint, and maximum with one decimal place. |
| 75 | <code>        {available.map(run =&gt; &lt;g key={run.run_id}&gt;&lt;circle cx={x(metricValue(run.metrics[costKey])!)} cy={y(metricValue(run.metrics.f1)!)} r={run.run_id === selectedId ? 7 : 5} className={frontier.has(run.run_id) ? &#39;pareto-point&#39; : &#39;comparison-point&#39;}&gt;&lt;title&gt;{`${run.run_id}: N=${run.sampling_rate}, F1 ${formatMetric(&#39;f1&#39;, run.metrics.f1)}, cost ${formatMetric(costKey, run.metrics[costKey])}${frontier.has(run.run_id) ? &#39;, Pareto efficient&#39; : &#39;&#39;}`}&lt;/title&gt;&lt;/circle&gt;&lt;text className=&quot;point-label&quot; x={x(metricValue(run.metrics[costKey])!) + 9} y={y(metricValue(run.metrics.f1)!) - 7}&gt;N={run.sampling_rate}&lt;/text&gt;&lt;/g&gt;)}</code> | Draws each measured run at (cost,F1), enlarges the selected run, colors nondominated points, adds a detailed tooltip, and labels sampling N. The ! assertions do not validate values; the earlier filter does. |
| 76 | <code>        &lt;text className=&quot;axis-title&quot; x={w / 2} y={h - 4} textAnchor=&quot;middle&quot;&gt;{costName} · lower is better&lt;/text&gt;</code> | Labels the horizontal axis and states that lower resource cost is better. |
| 77 | <code>      &lt;/svg&gt;</code> | Closes the trade-off SVG. |
| 78 | <code>      &lt;div className=&quot;chart-legend&quot;&gt;&lt;span&gt;&lt;i className=&quot;legend-dot pareto&quot; /&gt;Pareto efficient&lt;/span&gt;&lt;span&gt;&lt;i className=&quot;legend-dot comparison&quot; /&gt;Other measured trials&lt;/span&gt;&lt;/div&gt;</code> | Explains point colors for Pareto-efficient and other measured trials. |
| 79 | <code>    &lt;/&gt; : &lt;div className=&quot;chart-empty compact&quot;&gt;&lt;h3&gt;Trade-off evidence pending&lt;/h3&gt;&lt;p&gt;At least one completed trial with measured F1 and {costName.toLowerCase()} is required.&lt;/p&gt;&lt;/div&gt;}</code> | Closes the nonempty branch or displays a pending-evidence message stating the F1 and selected-cost requirements. |
| 80 | <code>    &lt;p className=&quot;chart-note&quot;&gt;Only completed trials matching this run&#39;s source, mode, scenario, feature schema, dataset checksum, and model settings are compared. Estimated or unavailable costs are excluded.&lt;/p&gt;</code> | Explains that only compatible completed trials are compared and estimated/unavailable costs are excluded; the graph does not choose a knee automatically. |
| 81 | <code>  &lt;/&gt;;</code> | Closes the trade-off component's fragment. |
| 82 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 83 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 84 | <code>const detailMetrics: [string, string][] = [</code> | Declares an array of [metric key, display label] string tuples used to render detailed evidence consistently. |
| 85 | <code>  [&#39;roc_auc&#39;, &#39;ROC-AUC&#39;], [&#39;false_positive_rate&#39;, &#39;False-positive rate&#39;], [&#39;detection_time_seconds&#39;, &#39;Detection time&#39;],</code> | Adds ROC-AUC, false-positive rate, and attack detection time to the detail list. |
| 86 | <code>  [&#39;packets_to_detect&#39;, &#39;Packets to detect&#39;], [&#39;unseen_attack_recall&#39;, &#39;Unseen-attack recall&#39;], [&#39;post_drift_recovery_seconds&#39;, &#39;Post-drift recovery&#39;],</code> | Adds packets until detection, recall for unseen attacks, and post-drift recovery time. |
| 87 | <code>  [&#39;cpu_percent_mean&#39;, &#39;Detector CPU · mean&#39;], [&#39;cpu_percent_p95&#39;, &#39;Detector CPU · p95&#39;], [&#39;controller_cpu_percent_mean&#39;, &#39;Controller CPU · mean&#39;],</code> | Adds detector CPU mean/p95 and controller CPU mean; these refer to separate processes. |
| 88 | <code>  [&#39;controller_cpu_percent_p95&#39;, &#39;Controller CPU · p95&#39;], [&#39;telemetry_bandwidth_kbps&#39;, &#39;Telemetry bandwidth&#39;],</code> | Adds controller CPU p95 and telemetry bandwidth. |
| 89 | <code>  [&#39;openflow_bandwidth_kbps&#39;, &#39;OpenFlow bandwidth&#39;], [&#39;flow_table_entries&#39;, &#39;Flow-table entries&#39;],</code> | Adds OpenFlow bandwidth and flow-table occupancy. |
| 90 | <code>];</code> | Ends the detail-metric array. |
| 91 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 92 | <code>export default function App() {</code> | Exports the main dashboard component as the default module export. |
| 93 | <code>  const [runs, setRuns] = useState&lt;RunSummary[]&gt;([]);</code> | Stores the fetched run list, initially empty. |
| 94 | <code>  const [overview, setOverview] = useState&lt;Overview &#124; null&gt;(null);</code> | Stores the optional aggregate overview, initially unknown rather than zero. |
| 95 | <code>  const [selectedId, setSelectedId] = useState(&#39;&#39;);</code> | Stores the selected run ID; an empty string means no selection. |
| 96 | <code>  const [selected, setSelected] = useState&lt;RunSummary &#124; null&gt;(null);</code> | Stores the selected run's full summary, initially absent. |
| 97 | <code>  const [series, setSeries] = useState&lt;Series&gt;(emptySeries);</code> | Stores timeline/resource/drift arrays with the typed empty value initially. |
| 98 | <code>  const [listLoading, setListLoading] = useState(true);</code> | Tracks initial run-list loading, initially active. |
| 99 | <code>  const [detailLoading, setDetailLoading] = useState(false);</code> | Tracks selected-run loading, initially inactive. |
| 100 | <code>  const [error, setError] = useState(&#39;&#39;);</code> | Stores run-list/overview request error text separately from selected-run errors. |
| 101 | <code>  const [detailError, setDetailError] = useState(&#39;&#39;);</code> | Stores selected-summary/timeline error text. |
| 102 | <code>  const [updatedAt, setUpdatedAt] = useState&lt;Date &#124; null&gt;(null);</code> | Stores the time of the most recent successful list+overview refresh. |
| 103 | <code>  const [autoRefresh, setAutoRefresh] = useState(true);</code> | Controls automatic polling; enabled initially. |
| 104 | <code>  const [refreshKey, setRefreshKey] = useState(0);</code> | Stores an integer refresh trigger so a manual refresh can restart effects even without another state change. |
| 105 | <code>  const refresh = useCallback(() =&gt; setRefreshKey(key =&gt; key + 1), []);</code> | Memoizes a callback that increments the refresh trigger with the current-state updater; its empty dependency array keeps function identity stable. |
| 106 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 107 | <code>  useEffect(() =&gt; {</code> | Starts the effect responsible for fetching and polling run list/overview. |
| 108 | <code>    const controller = new AbortController(); let timer: ReturnType&lt;typeof setTimeout&gt;;</code> | Creates an AbortController shared by the effect's requests and declares its future timeout handle. |
| 109 | <code>    const load = async () =&gt; {</code> | Defines the asynchronous polling operation inside the effect so it captures that effect's controller and settings. |
| 110 | <code>      try {</code> | Starts exception handling for list and overview requests. |
| 111 | <code>        const [nextRuns, nextOverview] = await Promise.all([getRuns(controller.signal), getOverview(controller.signal)]);</code> | Requests run list and overview concurrently; destructuring preserves Promise.all argument order. |
| 112 | <code>        if (controller.signal.aborted) return;</code> | Stops processing results if cleanup already canceled this effect. |
| 113 | <code>        setRuns(nextRuns); setOverview(nextOverview); setError(&#39;&#39;); setUpdatedAt(new Date());</code> | Commits both responses, clears the previous list error, and records successful refresh time. |
| 114 | <code>        setSelectedId(current =&gt; nextRuns.some(run =&gt; run.run_id === current) ? current : nextRuns[0]?.run_id &#124;&#124; &#39;&#39;);</code> | Keeps the current selection if still present; otherwise selects the first returned run or clears selection if the list is empty. |
| 115 | <code>      } catch (e) { if (!controller.signal.aborted) setError(e instanceof Error ? e.message : &#39;Could not connect to the experiment server.&#39;); }</code> | Stores a readable failure message only while this effect remains active; aborts do not produce user errors. |
| 116 | <code>      finally {</code> | Starts cleanup logic that runs after either successful or failed requests. |
| 117 | <code>        if (!controller.signal.aborted) { setListLoading(false); if (autoRefresh) timer = setTimeout(load, POLL_MS); }</code> | Ends initial loading and schedules the next load 3 seconds after completion if auto-refresh is enabled; this avoids interval overlap. |
| 118 | <code>      }</code> | Closes the finally block. |
| 119 | <code>    };</code> | Ends the local asynchronous load function. |
| 120 | <code>    void load();</code> | Invokes load immediately; void intentionally discards its promise because errors are handled internally. |
| 121 | <code>    return () =&gt; { controller.abort(); clearTimeout(timer); };</code> | Returns React cleanup that aborts in-flight requests and clears the pending timeout. |
| 122 | <code>  }, [autoRefresh, refreshKey]);</code> | Restarts this effect when polling is toggled or a manual-refresh trigger changes. |
| 123 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 124 | <code>  useEffect(() =&gt; {</code> | Starts a separate selected-run/timeline polling effect. |
| 125 | <code>    if (!selectedId) { setSelected(null); setSeries(emptySeries); return; }</code> | When there is no selected ID, clears stale details and series and exits without requesting a run. |
| 126 | <code>    const controller = new AbortController(); let timer: ReturnType&lt;typeof setTimeout&gt;;</code> | Creates cancellation and timeout controls for the selected-run request loop. |
| 127 | <code>    setSelected(null); setSeries(emptySeries); setDetailError(&#39;&#39;); setDetailLoading(true);</code> | Clears prior selection evidence/errors and enables the detail loading state when this effect starts. |
| 128 | <code>    const load = async () =&gt; {</code> | Defines the selected-run asynchronous fetch operation. |
| 129 | <code>      try {</code> | Begins request exception handling. |
| 130 | <code>        const [run, data] = await Promise.all([getRun(selectedId, controller.signal), getSeries(selectedId, controller.signal)]);</code> | Loads the selected summary and its bounded time series concurrently with the same abort signal. |
| 131 | <code>        if (!controller.signal.aborted) { setSelected(run); setSeries(data); setDetailError(&#39;&#39;); }</code> | Stores both responses and clears the detail error only if this effect is still active. |
| 132 | <code>      } catch (e) { if (!controller.signal.aborted) setDetailError(e instanceof Error ? e.message : &#39;Could not load this run.&#39;); }</code> | Reports selected-run failures while ignoring canceled effects. |
| 133 | <code>      finally {</code> | Starts the selected-detail finally block. |
| 134 | <code>        if (!controller.signal.aborted) { setDetailLoading(false); if (autoRefresh) timer = setTimeout(load, POLL_MS); }</code> | Ends detail loading and schedules another selected-detail load after the polling delay when enabled. |
| 135 | <code>      }</code> | Closes the finally block. |
| 136 | <code>    };</code> | Closes the detail load function. |
| 137 | <code>    void load();</code> | Starts the first detail load immediately. |
| 138 | <code>    return () =&gt; { controller.abort(); clearTimeout(timer); };</code> | Aborts old detail requests and clears their timeout on effect cleanup, including when selection changes. |
| 139 | <code>  }, [selectedId, autoRefresh, refreshKey]);</code> | Reruns the detail effect for a new selected ID, refresh setting, or manual refresh. |
| 140 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 141 | <code>  const comparisons = useMemo(() =&gt; selected ? compatibleRuns(runs, selected).sort((a, b) =&gt; a.sampling_rate - b.sampling_rate &#124;&#124; a.seed - b.seed) : [], [runs, selected]);</code> | Memoizes compatible completed trials; sorts by sampling N then seed. With no selected summary returns an empty list. |
| 142 | <code>  return &lt;&gt;</code> | Begins returning the entire dashboard as a React fragment. |
| 143 | <code>    &lt;a className=&quot;skip-link&quot; href=&quot;#main&quot;&gt;Skip to experiment results&lt;/a&gt;</code> | Provides a keyboard skip link that jumps to the main content element. |
| 144 | <code>    &lt;header className=&quot;topbar&quot;&gt;&lt;div className=&quot;brand&quot;&gt;&lt;span className=&quot;brand-icon&quot; aria-hidden=&quot;true&quot;&gt;&lt;i /&gt;&lt;i /&gt;&lt;i /&gt;&lt;/span&gt;&lt;span&gt;M3&lt;span className=&quot;brand-divider&quot;&gt; / &lt;/span&gt;&lt;span className=&quot;brand-light&quot;&gt;Observatory&lt;/span&gt;&lt;/span&gt;&lt;/div&gt;&lt;span className=&quot;topbar-subtitle&quot;&gt;ADAPTIVE DDOS DETECTION&lt;/span&gt;&lt;span className=&quot;project-tag&quot;&gt;5G-NIDD · SDN&lt;/span&gt;&lt;/header&gt;</code> | Renders the M3 Observatory header, decorative bar logo, adaptive-detection subtitle, and dataset/project label. Branding is static; evidence provenance is shown per run below. |
| 145 | <code>    &lt;main id=&quot;main&quot;&gt;</code> | Starts the main semantic content region and supplies the skip link's target ID. |
| 146 | <code>      &lt;div className=&quot;page-heading&quot;&gt;&lt;div&gt;&lt;div className=&quot;eyebrow&quot;&gt;EXPERIMENT WORKSPACE &lt;span&gt;01 / M3&lt;/span&gt;&lt;/div&gt;&lt;h1&gt;Less telemetry. &lt;span&gt;Measured detection.&lt;/span&gt;&lt;/h1&gt;&lt;p&gt;Sampling, adaptive learning, and the evidence behind every result.&lt;/p&gt;&lt;/div&gt;&lt;div className=&quot;refresh-tools&quot;&gt;&lt;label className=&quot;refresh-toggle&quot;&gt;&lt;input type=&quot;checkbox&quot; checked={autoRefresh} onChange={e =&gt; setAutoRefresh(e.target.checked)} /&gt;Auto-refresh · 3s&lt;/label&gt;&lt;button onClick={refresh} className=&quot;button&quot;&gt;&lt;span aria-hidden=&quot;true&quot;&gt;↻&lt;/span&gt; Refresh&lt;/button&gt;&lt;/div&gt;&lt;/div&gt;</code> | Renders the page title and controlled auto-refresh checkbox; the Refresh button calls refresh, restarting both polling effects. |
| 147 | <code>      &lt;div className=&quot;connection-line&quot; role=&quot;status&quot;&gt;&lt;span className={`connection-dot ${error ? &#39;offline&#39; : updatedAt ? &#39;online&#39; : &#39;&#39;}`} /&gt;{error ? &#39;Evidence connection unavailable&#39; : updatedAt ? `Connected · updated ${updatedAt.toLocaleTimeString()}` : &#39;Connecting to experiment server…&#39;}{!autoRefresh &amp;&amp; &lt;span className=&quot;paused-label&quot;&gt;Polling paused&lt;/span&gt;}&lt;/div&gt;</code> | Announces connection status: current request error, latest successful time, or initial connecting state. Shows Polling paused when automatic requests are disabled. |
| 148 | <code>      {error &amp;&amp; &lt;div className=&quot;error-banner&quot; role=&quot;alert&quot;&gt;&lt;strong&gt;Could not refresh experiments.&lt;/strong&gt;&lt;span&gt;{error} {runs.length ? &#39;Previously loaded evidence remains visible.&#39; : &#39;Start the FastAPI server on port 8000, then refresh.&#39;}&lt;/span&gt;&lt;/div&gt;}</code> | Displays an alert for list refresh errors; if prior runs exist says saved evidence remains visible, otherwise offers server-start guidance. |
| 149 | <code>      &lt;section className=&quot;overview-strip&quot; aria-label=&quot;Experiment overview&quot;&gt;{[[&#39;Saved runs&#39;, overview?.total_runs], [&#39;Completed&#39;, overview?.completed_runs], [&#39;Running&#39;, overview?.running_runs], [&#39;Failed&#39;, overview?.failed_runs]].map(([label, value]) =&gt; &lt;div key={String(label)}&gt;&lt;span&gt;{label}&lt;/span&gt;&lt;strong&gt;{value === undefined ? &#39;—&#39; : number(Number(value))}&lt;/strong&gt;&lt;/div&gt;)}&lt;div className=&quot;overview-description&quot;&gt;&lt;span&gt;METHOD&lt;/span&gt;&lt;strong&gt;Hoeffding Adaptive Tree &lt;span&gt;+ ADWIN&lt;/span&gt;&lt;/strong&gt;&lt;/div&gt;&lt;/section&gt;</code> | Maps four overview counters into cards, shows an em dash until each value exists, and states the method; optional chaining prevents accessing a null overview. |
| 150 | <code>      {listLoading ? &lt;div className=&quot;state-panel&quot; role=&quot;status&quot;&gt;&lt;span className=&quot;loader&quot; /&gt;&lt;h2&gt;Loading experiment evidence&lt;/h2&gt;&lt;p&gt;Reading saved runs and current experiment status.&lt;/p&gt;&lt;/div&gt; : !runs.length ? &lt;div className=&quot;state-panel&quot;&gt;&lt;div className=&quot;empty-icon&quot; aria-hidden=&quot;true&quot;&gt;⌁&lt;/div&gt;&lt;div className=&quot;eyebrow&quot;&gt;{error ? &#39;WAITING FOR EXPERIMENT EVIDENCE&#39; : &#39;READY FOR THE FIRST RUN&#39;}&lt;/div&gt;&lt;h2&gt;{error ? &#39;Connect the experiment server&#39; : &#39;No experiment results yet&#39;}&lt;/h2&gt;&lt;p&gt;{error ? &#39;Saved results cannot be checked until the experiment server responds. Start the server on port 8000 and refresh this page.&#39; : &#39;Run the M3 experiment runner with verified official 5G-NIDD data. Saved results will appear here automatically.&#39;}&lt;/p&gt;{!error &amp;&amp; &lt;div className=&quot;empty-steps&quot;&gt;&lt;span&gt;01 · Verify dataset&lt;/span&gt;&lt;span&gt;02 · Run N = 1 baseline&lt;/span&gt;&lt;span&gt;03 · Compare sampling rates&lt;/span&gt;&lt;/div&gt;}&lt;/div&gt; : &lt;&gt;</code> | Selects initial loading, no-runs explanation, or the run-content fragment. Empty-state text distinguishes connection failure from a successfully retrieved empty list. |
| 151 | <code>        &lt;section className=&quot;run-toolbar&quot; aria-label=&quot;Run selection&quot;&gt;&lt;div className=&quot;run-label&quot;&gt;&lt;span className=&quot;eyebrow&quot;&gt;INSPECT EXPERIMENT&lt;/span&gt;&lt;label htmlFor=&quot;run-select&quot;&gt;Selected run&lt;/label&gt;&lt;/div&gt;&lt;select id=&quot;run-select&quot; value={selectedId} onChange={e =&gt; setSelectedId(e.target.value)}&gt;{runs.map(run =&gt; &lt;option key={run.run_id} value={run.run_id}&gt;{run.run_id} · N={run.sampling_rate} · {run.scenario} · {run.status}&lt;/option&gt;)}&lt;/select&gt;&lt;div className=&quot;selection-count&quot;&gt;{runs.length} saved {runs.length === 1 ? &#39;run&#39; : &#39;runs&#39;}&lt;/div&gt;&lt;/section&gt;</code> | Renders an accessible controlled run selector showing ID, N, scenario and status for each run; changing selection triggers the detail effect. |
| 152 | <code>        {detailError &amp;&amp; &lt;div className=&quot;error-banner&quot; role=&quot;alert&quot;&gt;&lt;strong&gt;Run evidence could not be loaded.&lt;/strong&gt;&lt;span&gt;{detailError} {selected ? &#39;Shown run details are from the last successful refresh.&#39; : &#39;&#39;}&lt;/span&gt;&lt;/div&gt;}</code> | Shows selected-detail errors and, if old selected evidence remains, explains that it is from the last successful refresh. |
| 153 | <code>        {detailLoading ? &lt;div className=&quot;state-panel small&quot; role=&quot;status&quot;&gt;&lt;span className=&quot;loader&quot; /&gt;&lt;p&gt;Loading selected run…&lt;/p&gt;&lt;/div&gt; : selected &amp;&amp; &lt;&gt;</code> | Shows selected-run loading first; otherwise renders detail content only when a selected summary exists. |
| 154 | <code>          &lt;section className=&quot;run-context&quot;&gt;&lt;div className=&quot;run-context-head&quot;&gt;&lt;div&gt;&lt;Badge tone={selected.status}&gt;{selected.status}&lt;/Badge&gt;&lt;Badge tone={selected.source === &#39;fixture&#39; ? &#39;fixture&#39; : &#39;source&#39;}&gt;{sourceName(selected.source)}&lt;/Badge&gt;&lt;Badge&gt;{modeName(selected.mode)}&lt;/Badge&gt;&lt;h2&gt;{selected.scenario.replaceAll(&#39;_&#39;, &#39; &#39;)}&lt;/h2&gt;&lt;/div&gt;&lt;div className=&quot;sampling-emblem&quot;&gt;&lt;span&gt;SAMPLING RATE&lt;/span&gt;&lt;strong&gt;1&lt;span&gt; / &lt;/span&gt;{selected.sampling_rate}&lt;/strong&gt;&lt;/div&gt;&lt;/div&gt;&lt;div className=&quot;context-bottom&quot;&gt;&lt;span&gt;Run &lt;code&gt;{selected.run_id}&lt;/code&gt;&lt;/span&gt;&lt;span&gt;Seed {selected.seed}&lt;/span&gt;&lt;span&gt;Evaluation unit: &lt;strong&gt;{selected.unit}&lt;/strong&gt;&lt;/span&gt;&lt;span&gt;Started {dateLabel(selected.created_at)}&lt;/span&gt;&lt;/div&gt;&lt;/section&gt;</code> | Renders status/source/mode badges, readable scenario, 1/N sampling emblem, ID, seed, unit, and formatted start time. |
| 155 | <code>          {selected.source !== &#39;official_5g_nidd&#39; &amp;&amp; &lt;div className=&quot;notice&quot;&gt;This run is labeled &lt;strong&gt;{sourceName(selected.source)}&lt;/strong&gt;. Its results do not establish performance on official 5G-NIDD.&lt;/div&gt;}</code> | Shows a provenance notice for every source except official_5g_nidd so fixture/live results are not represented as official dataset performance. |
| 156 | <code>          &lt;details className=&quot;provenance-details&quot;&gt;&lt;summary&gt;Dataset and feature provenance&lt;/summary&gt;&lt;pre&gt;{JSON.stringify({ feature_schema: selected.feature_schema ?? &#39;Not recorded&#39;, provenance: selected.provenance ?? &#39;Not recorded&#39; }, null, 2)}&lt;/pre&gt;&lt;/details&gt;</code> | Creates a native expandable details panel and pretty-prints feature schema and provenance; missing fields explicitly say Not recorded. |
| 157 | <code>          {selected.mode === &#39;csv_replay&#39; &amp;&amp; &lt;div className=&quot;notice&quot;&gt;This run samples flow records. Packet sampling and live SDN overhead require capture replay or live sFlow measurements.&lt;/div&gt;}</code> | For CSV replay explains that flow-record subsampling does not itself measure packet sampling or live-network overhead. |
| 158 | <code>          {selected.status === &#39;failed&#39; &amp;&amp; &lt;div className=&quot;error-banner&quot; role=&quot;alert&quot;&gt;&lt;strong&gt;This run failed.&lt;/strong&gt;&lt;span&gt;{selected.error &#124;&#124; &#39;No error detail was saved.&#39;}&lt;/span&gt;&lt;/div&gt;}</code> | Displays a failed-run alert with its saved error or an explicit missing-detail fallback. |
| 159 | <code>          &lt;section className=&quot;metric-grid&quot; aria-label=&quot;Detection metrics&quot;&gt;&lt;MetricCard name=&quot;Precision&quot; metricKey=&quot;precision&quot; metric={selected.metrics.precision} caption=&quot;How often attack predictions are correct&quot; /&gt;&lt;MetricCard name=&quot;Recall&quot; metricKey=&quot;recall&quot; metric={selected.metrics.recall} caption=&quot;Share of labeled attacks detected&quot; /&gt;&lt;MetricCard name=&quot;F1 score&quot; metricKey=&quot;f1&quot; metric={selected.metrics.f1} caption=&quot;Balance of precision and recall&quot; /&gt;&lt;MetricCard name=&quot;Inference latency&quot; metricKey=&quot;inference_latency_ms&quot; metric={selected.metrics.inference_latency_ms} caption=&quot;Average time per prediction&quot; /&gt;&lt;/section&gt;</code> | Renders precision, recall, F1, and inference latency cards using actual saved metrics and short plain-language captions. |
| 160 | <code>          &lt;section className=&quot;panel timeline-panel&quot;&gt;&lt;div className=&quot;panel-heading&quot;&gt;&lt;div&gt;&lt;span className=&quot;eyebrow&quot;&gt;DETECTION THROUGH TIME&lt;/span&gt;&lt;h2&gt;Adaptive learning timeline&lt;/h2&gt;&lt;/div&gt;&lt;Badge&gt;{number(selected.drift_count)} drift {selected.drift_count === 1 ? &#39;alarm&#39; : &#39;alarms&#39;}&lt;/Badge&gt;&lt;/div&gt;&lt;Timeline series={series} unit={selected.unit} threshold={typeof selected.config.threshold === &#39;number&#39; ? selected.config.threshold : .5} /&gt;&lt;/section&gt;</code> | Renders the timeline heading and drift-count badge; passes the run's numeric threshold, falling back to .5 if absent/non-numeric. |
| 161 | <code>          &lt;div className=&quot;analysis-grid&quot;&gt;&lt;section className=&quot;panel&quot;&gt;&lt;div className=&quot;panel-heading&quot;&gt;&lt;div&gt;&lt;span className=&quot;eyebrow&quot;&gt;ACCURACY × OVERHEAD&lt;/span&gt;&lt;h2&gt;Sampling trade-off&lt;/h2&gt;&lt;/div&gt;&lt;/div&gt;&lt;Tradeoff runs={comparisons} selectedId={selected.run_id} /&gt;&lt;/section&gt;&lt;section className=&quot;panel&quot;&gt;&lt;div className=&quot;panel-heading&quot;&gt;&lt;div&gt;&lt;span className=&quot;eyebrow&quot;&gt;STREAM ACCOUNTING&lt;/span&gt;&lt;h2&gt;Every observation accounted for&lt;/h2&gt;&lt;/div&gt;&lt;/div&gt;&lt;dl className=&quot;count-list&quot;&gt;{Object.entries(selected.counts).map(([key, value]) =&gt; &lt;div key={key}&gt;&lt;dt&gt;{key.replaceAll(&#39;_&#39;, &#39; &#39;)}&lt;/dt&gt;&lt;dd&gt;{number(value)}&lt;/dd&gt;&lt;/div&gt;)}&lt;/dl&gt;&lt;div className=&quot;account-note&quot;&gt;Input and sampling counts are recorded independently from evaluated labels. Warm-up, exclusions, and unlabeled records are retained in the evidence.&lt;/div&gt;&lt;/section&gt;&lt;/div&gt;</code> | Creates the trade-off and observation-accounting columns; Object.entries turns count fields into readable labels and formatted numbers, with a note separating sampled input from evaluated labels. |
| 162 | <code>          &lt;section className=&quot;panel&quot;&gt;&lt;div className=&quot;panel-heading&quot;&gt;&lt;div&gt;&lt;span className=&quot;eyebrow&quot;&gt;COMPATIBLE COMPLETED TRIALS&lt;/span&gt;&lt;h2&gt;Sampling comparison&lt;/h2&gt;&lt;/div&gt;&lt;Badge&gt;{comparisons.length} trials&lt;/Badge&gt;&lt;/div&gt;&lt;div className=&quot;table-scroll&quot;&gt;&lt;table&gt;&lt;caption className=&quot;sr-only&quot;&gt;Individual compatible trials; no implicit averaging of repeated trials.&lt;/caption&gt;&lt;thead&gt;&lt;tr&gt;&lt;th scope=&quot;col&quot;&gt;Run / seed&lt;/th&gt;&lt;th scope=&quot;col&quot;&gt;Sampling&lt;/th&gt;&lt;th scope=&quot;col&quot;&gt;F1&lt;/th&gt;&lt;th scope=&quot;col&quot;&gt;Recall&lt;/th&gt;&lt;th scope=&quot;col&quot;&gt;CPU mean&lt;/th&gt;&lt;th scope=&quot;col&quot;&gt;Telemetry&lt;/th&gt;&lt;th scope=&quot;col&quot;&gt;Drift alarms&lt;/th&gt;&lt;/tr&gt;&lt;/thead&gt;&lt;tbody&gt;{comparisons.map(run =&gt; &lt;tr key={run.run_id} className={run.run_id === selected.run_id ? &#39;selected-row&#39; : &#39;&#39;}&gt;&lt;th scope=&quot;row&quot;&gt;&lt;button className=&quot;run-link&quot; onClick={() =&gt; setSelectedId(run.run_id)}&gt;{run.run_id}&lt;/button&gt;&lt;small&gt;Seed {run.seed}&lt;/small&gt;&lt;/th&gt;&lt;td&gt;&lt;Badge&gt;1 / {run.sampling_rate}&lt;/Badge&gt;&lt;/td&gt;{[&#39;f1&#39;, &#39;recall&#39;, &#39;cpu_percent_mean&#39;, &#39;telemetry_bandwidth_kbps&#39;].map(key =&gt; &lt;td key={key}&gt;{formatMetric(key, run.metrics[key])}{run.metrics[key]?.status === &#39;estimated&#39; &amp;&amp; &lt;small&gt;estimated&lt;/small&gt;}&lt;/td&gt;)}&lt;td&gt;{run.drift_count}&lt;/td&gt;&lt;/tr&gt;)}{!comparisons.length &amp;&amp; &lt;tr&gt;&lt;td colSpan={7}&gt;No compatible completed trials yet.&lt;/td&gt;&lt;/tr&gt;}&lt;/tbody&gt;&lt;/table&gt;&lt;/div&gt;&lt;/section&gt;</code> | Renders individual compatible trials in a scrollable table. Each ID button selects that run; current row is highlighted; N, F1, recall, CPU, telemetry and drift count are displayed, estimated values marked, and an empty row spans seven columns when none qualify. |
| 163 | <code>          &lt;div className=&quot;analysis-grid details-grid&quot;&gt;&lt;section className=&quot;panel&quot;&gt;&lt;div className=&quot;panel-heading&quot;&gt;&lt;div&gt;&lt;span className=&quot;eyebrow&quot;&gt;METRIC EVIDENCE&lt;/span&gt;&lt;h2&gt;Measurements &amp; limitations&lt;/h2&gt;&lt;/div&gt;&lt;/div&gt;&lt;div className=&quot;evidence-list&quot;&gt;{detailMetrics.map(([key, label]) =&gt; &lt;div key={key}&gt;&lt;div&gt;&lt;strong&gt;{label}&lt;/strong&gt;&lt;small&gt;{metricValue(selected.metrics[key]) === null ? selected.metrics[key]?.reason &#124;&#124; &#39;No measurement saved.&#39; : selected.metrics[key]?.reason &#124;&#124; selected.metrics[key]?.status}&lt;/small&gt;&lt;/div&gt;&lt;span&gt;{formatMetric(key, selected.metrics[key])}&lt;/span&gt;&lt;/div&gt;)}&lt;/div&gt;&lt;/section&gt;&lt;section className=&quot;panel&quot;&gt;&lt;div className=&quot;panel-heading&quot;&gt;&lt;div&gt;&lt;span className=&quot;eyebrow&quot;&gt;ADWIN / HAT&lt;/span&gt;&lt;h2&gt;Drift event log&lt;/h2&gt;&lt;/div&gt;&lt;/div&gt;{series.drift.length ? &lt;ol className=&quot;drift-log&quot;&gt;{series.drift.map((event, i) =&gt; &lt;li key={`${event.index}-${i}`}&gt;&lt;span className=&quot;event-dot&quot; /&gt;&lt;div&gt;&lt;strong&gt;{event.event.replaceAll(&#39;_&#39;, &#39; &#39;)}&lt;/strong&gt;&lt;p&gt;{event.detector} · observation {event.index}&lt;/p&gt;&lt;small&gt;{timeLabel(event.time)}&lt;/small&gt;&lt;/div&gt;&lt;/li&gt;)}&lt;/ol&gt; : &lt;div className=&quot;chart-empty compact&quot;&gt;&lt;h3&gt;No drift events saved&lt;/h3&gt;&lt;p&gt;Absence of an alarm does not establish absence of a distribution change.&lt;/p&gt;&lt;/div&gt;}&lt;details className=&quot;config-details&quot;&gt;&lt;summary&gt;Run configuration and provenance&lt;/summary&gt;&lt;pre&gt;{JSON.stringify(selected.config, null, 2)}&lt;/pre&gt;&lt;/details&gt;&lt;/section&gt;&lt;/div&gt;</code> | Builds detailed metric evidence with saved reasons/status, plus the drift-event list or no-alarm explanation. Event keys combine index and position; a native details panel pretty-prints the selected config. |
| 164 | <code>        &lt;/&gt;}</code> | Closes the selected-summary fragment and its conditional rendering expression. |
| 165 | <code>      &lt;/&gt;}</code> | Closes the runs-present fragment and the outer loading/empty/list conditional expression. |
| 166 | <code>      &lt;footer&gt;&lt;span&gt;M3 Observatory &lt;span className=&quot;footer-dot&quot;&gt;·&lt;/span&gt; 5G-NIDD sampled telemetry&lt;/span&gt;&lt;span&gt;Evidence first. Every number traces to a saved run.&lt;/span&gt;&lt;/footer&gt;</code> | Renders static footer branding and a reminder that displayed numbers originate in saved runs. |
| 167 | <code>    &lt;/main&gt;</code> | Closes the main content element. |
| 168 | <code>  &lt;/&gt;;</code> | Closes the dashboard's returned fragment. |
| 169 | <code>}</code> | Closes the App function. |

## frontend/src/style.css

Appearance, layout, SVG styling, responsive breakpoints, keyboard focus, and reduced-motion behavior. The source is compressed into nine physical lines; the appendix expands individual rules.

### Complete source

```css
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root{font-family:'DM Sans',system-ui,-apple-system,sans-serif;color:#203648;background:#f4f7f8;font-synthesis:none;text-rendering:optimizeLegibility;font-size:14px;--navy:#102b3d;--muted:#607787;--teal:#087e82;--line:#dfE7eb;--orange:#dc8032}
*{box-sizing:border-box}body{margin:0}button,input,select{font:inherit}button,select{cursor:pointer}button:disabled{cursor:default}a{color:var(--teal)}button:focus-visible,select:focus-visible,input:focus-visible,summary:focus-visible,a:focus-visible{outline:3px solid #e69745;outline-offset:4px}button{transition:background .15s}h1,h2,h3,p{margin:0}h1,h2,h3{font-family:'Manrope',system-ui,sans-serif}h2{font-size:19px;letter-spacing:-.6px}h3{font-size:16px}p{line-height:1.6}.topbar{height:76px;background:#102334;color:#fff;padding:0 max(4vw,24px);display:flex;align-items:center;gap:34px;border-bottom:1px solid #254356}.brand{display:flex;align-items:center;gap:12px;font-family:'Manrope',sans-serif;font-size:23px;font-weight:800;letter-spacing:-1px}.brand-light{font-weight:500;letter-spacing:-.7px}.brand-divider{color:#708b9b;padding:0 5px}.brand-icon{height:29px;width:29px;display:flex;gap:4px;align-items:flex-end}.brand-icon i{display:block;width:6px;background:#66d2c7;border-radius:2px}.brand-icon i:nth-child(1){height:12px}.brand-icon i:nth-child(2){height:22px}.brand-icon i:nth-child(3){height:29px}.topbar-subtitle{font-size:10px;color:#a9bdca;letter-spacing:2px;padding-left:30px;border-left:1px solid #345060}.project-tag{margin-left:auto;border:1px solid #3c5869;border-radius:5px;padding:7px 12px;font-size:11px;letter-spacing:.8px;color:#c9d9e1}main{max-width:1390px;margin:auto;padding:40px max(3.8vw,24px) 0}.page-heading{display:flex;align-items:center;justify-content:space-between;gap:24px}.eyebrow{font-size:10px;font-weight:700;letter-spacing:1.7px;color:var(--teal);margin-bottom:10px}.eyebrow>span{color:#8699a5;margin-left:13px}h1{font-size:clamp(27px,2.5vw,36px);font-weight:800;letter-spacing:-1.5px;line-height:1.3;color:var(--navy)}h1>span{font-weight:500;color:#577181}.page-heading p{margin-top:9px;color:var(--muted);font-size:14px}.refresh-tools{display:flex;align-items:center;gap:18px}.refresh-toggle{display:flex;align-items:center;gap:7px;font-size:12px;color:var(--muted);white-space:nowrap}.refresh-toggle input{accent-color:var(--teal);width:15px;height:15px}.button{display:flex;align-items:center;gap:8px;background:#fff;border:1px solid #cfdbE1;border-radius:6px;padding:9px 14px;color:#294c5e;font-weight:600}.button:hover{background:#eaf3f4}.button span{font-size:20px;line-height:20px}.connection-line{display:flex;align-items:center;gap:7px;color:#718590;font-size:11px;margin:23px 0 16px;min-height:16px}.connection-dot{height:6px;width:6px;border-radius:50%;background:#b8c7cd}.connection-dot.online{background:#078e77;box-shadow:0 0 0 3px #078e7712}.connection-dot.offline{background:#c66a45}.paused-label{margin-left:8px;color:#9a5a25}.overview-strip{display:flex;background:#fff;border:1px solid var(--line);border-radius:9px;padding:22px 25px;margin-bottom:24px;box-shadow:0 2px 4px #10233403}.overview-strip>div{min-width:130px;padding-right:28px;margin-right:28px;border-right:1px solid var(--line);display:flex;flex-direction:column;gap:7px}.overview-strip span{font-size:11px;color:#788b96}.overview-strip strong{font-size:24px;font-family:'Manrope',sans-serif;color:var(--navy)}.overview-strip>.overview-description{margin:0;padding:0;min-width:0;border:none;margin-left:auto;justify-content:center}.overview-description>span{font-size:9px;letter-spacing:1.5px}.overview-description strong{font-size:13px;line-height:1.5}.overview-description strong span{display:block;font-size:12px;color:var(--teal);font-weight:500}.error-banner{border:1px solid #ecc9bd;border-left:3px solid #bf5135;background:#fff4ef;color:#893f2a;border-radius:6px;padding:14px 18px;display:flex;flex-direction:column;gap:5px;margin-bottom:20px;font-size:12px}.error-banner strong{font-size:13px}.state-panel{min-height:360px;background:#fff;border:1px solid var(--line);border-radius:10px;text-align:center;display:flex;align-items:center;justify-content:center;flex-direction:column;padding:45px;gap:15px}.state-panel p{color:var(--muted);max-width:540px}.state-panel h2{font-size:24px}.state-panel.small{min-height:180px}.empty-icon{border:1px solid #d8e9ea;background:#edf7f6;height:66px;width:66px;border-radius:17px;color:var(--teal);font-size:48px;line-height:60px;margin-bottom:6px}.empty-steps{display:flex;gap:30px;color:#718b99;font-size:11px;margin-top:20px}.state-panel .eyebrow{margin:0}.loader{height:28px;width:28px;border:2px solid #d8e6e8;border-top-color:var(--teal);border-radius:50%;animation:spin 1s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}.run-toolbar{display:flex;align-items:center;gap:24px;margin:24px 0 18px}.run-label{min-width:150px}.run-label .eyebrow{font-size:9px;margin-bottom:5px}.run-label label{font-weight:600;font-size:13px}.run-toolbar select{min-width:0;flex:1;max-width:720px;background:#fff;border:1px solid #cbdbe2;border-radius:6px;padding:12px;color:#29495b}.selection-count{margin-left:auto;font-size:11px;color:var(--muted);white-space:nowrap}.run-context{background:var(--navy);color:#fff;border-radius:9px;overflow:hidden}.run-context-head{padding:23px 26px;display:flex;justify-content:space-between;gap:24px}.run-context h2{text-transform:capitalize;font-size:23px;margin-top:12px;font-weight:600;letter-spacing:-.5px}.badge{display:inline-block;border:1px solid #dde5ea;background:#f5f8fa;color:#56717f;border-radius:4px;padding:4px 8px;font-size:10px;font-weight:600;line-height:1.2;white-space:nowrap}.run-context .badge{background:#254455;border-color:#395567;color:#cedee5;margin-right:7px}.badge.completed,.run-context .badge.completed{background:#e8f6ef;border-color:#c8e9d8;color:#256953}.badge.running,.run-context .badge.running{background:#dff6f5;border-color:#aee4e3;color:#067a7d}.badge.failed,.run-context .badge.failed{background:#fff0e9;border-color:#edcbbd;color:#b7512b}.run-context .badge.source{background:#27495e;color:#c2e6f1}.run-context .badge.fixture{background:#fff0d6;border-color:#e5bd70;color:#845721}.sampling-emblem{text-align:right;min-width:120px}.sampling-emblem>span{display:block;font-size:9px;letter-spacing:1.5px;color:#9fb8c4}.sampling-emblem strong{font-size:34px;font-family:'Manrope',sans-serif;font-weight:700}.sampling-emblem strong span{font-size:26px;font-weight:400;color:#6e99ab}.context-bottom{border-top:1px solid #365162;padding:12px 26px;display:flex;gap:23px;font-size:10px;color:#a7c0cd;flex-wrap:wrap}.context-bottom strong{font-weight:500;color:#d5e4eb}.context-bottom code{font-size:10px;color:#d4e4eb;word-break:break-all}.notice{background:#eaf2f4;border:1px solid #d4e4e9;color:#50717e;padding:11px 17px;border-radius:6px;margin:14px 0;font-size:11px;line-height:1.6}.metric-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:22px 0}.metric-card{padding:20px 23px;background:#fff;border:1px solid var(--line);border-radius:8px;position:relative;min-width:0;box-shadow:0 2px 3px #10233403}.metric-label{font-size:12px;color:#536d7d;font-weight:500;display:flex;justify-content:space-between;align-items:center}.metric-symbol{color:#acc1c9;font-size:17px}.metric-value{font-family:'Manrope',sans-serif;font-weight:800;font-size:32px;letter-spacing:-1px;margin:12px 0 6px;color:var(--navy)}.metric-card p{font-size:10px;color:#81929d;min-height:32px}.metric-missing .metric-value{font-size:22px;margin:17px 0 13px;color:#8598a3}.evidence-tag{font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#088071;display:inline-block;margin-top:10px}.evidence-tag.estimated{color:#a47032}.evidence-tag.unavailable{color:#83929e}.panel{border:1px solid var(--line);border-radius:9px;background:#fff;padding:23px 25px;margin-bottom:20px;min-width:0;box-shadow:0 2px 3px #10233403}.panel-heading{display:flex;justify-content:space-between;align-items:center;gap:15px;margin-bottom:24px}.panel-heading .eyebrow{font-size:9px;margin-bottom:6px}.panel-heading h2{font-size:18px;font-weight:700}.panel-heading>.badge{font-weight:500}.chart-legend{display:flex;flex-wrap:wrap;gap:20px;font-size:10px;color:#718590;margin:0 0 12px}.chart-legend>span{display:flex;align-items:center;gap:7px}.legend-line{width:17px;height:2px;background:var(--teal);display:inline-block}.legend-line.drift{height:0;border-top:2px dashed var(--orange);background:transparent}.legend-dot{height:6px;width:6px;border-radius:50%;background:#798e9d;display:inline-block}.legend-dot.attack{background:#ca7647}.legend-dot.benign{background:#acc5ce}.legend-dot.pareto{background:var(--teal);box-shadow:0 0 0 2px #a0d9d5}.legend-dot.comparison{background:#8d9da8}.timeline-svg,.tradeoff-svg{display:block;width:100%;height:auto;overflow:visible}.timeline-svg{max-height:300px}.grid-line{stroke:#eaf0f2;stroke-width:1}.axis-label{font-size:10px;fill:#879ba7}.axis-title{font-size:10px;fill:#718895}.threshold-line{stroke:#bdced5;stroke-dasharray:5 5}.probability-line{fill:none;stroke:var(--teal);stroke-width:2;stroke-linejoin:round}.truth-attack{fill:#d99a73;opacity:.65}.truth-benign{fill:#a4bec9;opacity:.6}.drift-line{stroke:#d78a4b;stroke-width:1.5;stroke-dasharray:4 4}.chart-note{font-size:10px;color:#8698a2;line-height:1.65;margin-top:12px}.chart-empty{min-height:200px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:9px;text-align:center;padding:25px}.chart-empty p{font-size:12px;color:#7b909c;max-width:480px}.chart-empty h3{color:#536e7e;font-size:15px;font-weight:600}.chart-empty.compact{min-height:180px}.empty-glyph{font-size:42px;color:#98b7c0}.analysis-grid{display:grid;grid-template-columns:1.15fr 1fr;gap:20px}.analysis-grid>.panel{margin-bottom:20px}.inline-control{display:flex;justify-content:space-between;align-items:center;font-size:10px;color:#6b8391;margin-bottom:16px;gap:10px}.inline-control select{border:1px solid #dbe5e9;background:#f9fbfc;border-radius:5px;padding:7px;color:#486573;font-size:11px}.pareto-point{fill:#0e8c89;stroke:#a9d9d4;stroke-width:3}.comparison-point{fill:#849ca9;stroke:white;stroke-width:2}.point-label{font-size:9px;fill:#5e7988}.count-list{margin:0}.count-list>div{display:flex;justify-content:space-between;border-bottom:1px solid #ecf1f3;padding:12px 0}.count-list>div:last-child{border-bottom:none}.count-list dt{text-transform:capitalize;color:#6b8392;font-size:12px}.count-list dd{margin:0;font-weight:600;color:#2d4a5d;font-variant-numeric:tabular-nums}.account-note{font-size:10px;color:#7f94a0;line-height:1.7;background:#f4f8f9;border-radius:6px;padding:13px;margin-top:15px}.table-scroll{overflow:auto}table{width:100%;border-collapse:collapse;font-size:12px;text-align:left}thead th{font-weight:500;font-size:10px;color:#8496a3;padding:12px;border-bottom:1px solid #dce6ea;white-space:nowrap}tbody td,tbody th{padding:15px 12px;border-bottom:1px solid #edf1f3;white-space:nowrap;font-weight:400}tbody tr:last-child td,tbody tr:last-child th{border-bottom:none}tbody tr:hover{background:#f8fafb}.selected-row{background:#f0f8f8}.run-link{background:none;border:none;padding:0;color:#087d82;text-align:left;font-size:11px;max-width:190px;overflow:hidden;text-overflow:ellipsis}.run-link:hover{text-decoration:underline}table small{display:block;font-size:9px;color:#8398a4;margin-top:5px}.evidence-list>div{display:flex;align-items:flex-start;justify-content:space-between;border-bottom:1px solid #edf1f3;padding:10px 0;gap:16px}.evidence-list>div:last-child{border-bottom:none}.evidence-list strong{font-size:11px;font-weight:500;color:#506d7d}.evidence-list small{display:block;font-size:10px;color:#8b9da7;margin-top:3px;line-height:1.5}.evidence-list>div>span{font-size:11px;font-weight:500;color:#355568;text-align:right;white-space:nowrap}.details-grid{grid-template-columns:1.15fr 1fr}.drift-log{list-style:none;padding:0;margin:0;max-height:360px;overflow:auto}.drift-log li{display:flex;gap:13px;border-left:1px solid #e7edf0;margin-left:4px;padding:0 0 22px 18px;position:relative}.event-dot{position:absolute;left:-4px;top:4px;height:7px;width:7px;background:#d49153;border:2px solid #fff;box-shadow:0 0 0 1px #e2bf94;border-radius:50%}.drift-log strong{font-size:12px;font-weight:500;color:#4b6878;text-transform:capitalize}.drift-log p{font-size:10px;color:#8095a0;margin:5px 0}.drift-log small{font-size:10px;color:#9babb4}.config-details{border-top:1px solid #e5edf0;margin-top:20px;padding-top:16px}.config-details summary{font-size:11px;color:#597c8d;cursor:pointer}.config-details pre{font-size:10px;line-height:1.8;background:#f5f8fa;border-radius:5px;padding:16px;color:#5b7787;overflow:auto;max-height:350px}footer{border-top:1px solid #dde7eb;display:flex;justify-content:space-between;gap:20px;font-size:10px;color:#8b9da6;padding:24px 0;margin-top:10px;line-height:1.6}.footer-dot{padding:0 8px;color:#a4b5bd}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}.skip-link{position:absolute;left:16px;top:-100px;background:white;padding:10px;z-index:5}.skip-link:focus{top:10px}
@media(max-width:1100px){.overview-strip>div{min-width:100px;margin-right:20px;padding-right:20px}.topbar-subtitle{display:none}.overview-strip>.overview-description strong{font-size:11px}.metric-card{padding:18px}.metric-value{font-size:28px}.refresh-tools{gap:10px}.refresh-toggle{font-size:10px}}
@media(max-width:850px){.page-heading{align-items:flex-start;flex-direction:column;gap:20px}.refresh-tools{width:100%;justify-content:flex-end}.overview-strip{flex-wrap:wrap;gap:15px;padding:19px}.overview-strip>div{flex:1;min-width:75px;padding:0;margin:0}.overview-strip>.overview-description{display:none}.metric-grid{grid-template-columns:repeat(2,1fr)}.analysis-grid{grid-template-columns:1fr}.run-toolbar{flex-wrap:wrap;gap:12px}.run-toolbar select{flex-basis:100%;order:3;max-width:none}.selection-count{margin-left:auto}.panel{padding:20px}.empty-steps{flex-direction:column;gap:12px}h1>span{display:block}.context-bottom{gap:12px 20px}.run-context-head{padding:20px}.context-bottom{padding:12px 20px}.tradeoff-svg{max-height:300px}}
@media(max-width:480px){main{padding:26px 16px 0}.topbar{padding:0 16px;height:65px}.brand{font-size:19px}.project-tag{font-size:9px;padding:6px}.page-heading h1{font-size:27px}.run-context-head{gap:8px}.sampling-emblem{min-width:80px}.sampling-emblem strong{font-size:29px}.sampling-emblem>span{font-size:8px}.run-context .badge{margin:0 4px 5px 0;font-size:9px}.metric-grid{gap:10px}.metric-card{padding:16px 12px}.metric-value{font-size:25px}.metric-missing .metric-value{font-size:18px}.metric-card p{font-size:9px}.metric-label{font-size:11px}.panel-heading h2{font-size:16px}.chart-legend{gap:12px}.state-panel{padding:25px 20px}.overview-strip strong{font-size:21px}.overview-strip span{font-size:9px}.context-bottom code{font-size:9px}footer{flex-direction:column;gap:6px}.evidence-list>div>span{white-space:normal;min-width:80px}}
@media(prefers-reduced-motion:reduce){.loader{animation:none}button{transition:none}}
.provenance-details{margin:12px 0;color:#62818f;font-size:11px}.provenance-details summary{cursor:pointer}.provenance-details pre{padding:15px;background:#eaf2f4;border-radius:5px;overflow:auto;font-size:10px;line-height:1.7;max-height:220px}
```

### Every physical line

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>@import url(&#39;https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&amp;family=Manrope:wght@400;500;600;700;800&amp;display=swap&#39;);</code> | Imports two Google Fonts families and their weights with swap display behavior; fallback system fonts apply when the network/font request is unavailable. |
| 2 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 3 | <code>:root{font-family:&#39;DM Sans&#39;,system-ui,-apple-system,sans-serif;color:#203648;background:#f4f7f8;font-synthesis:none;text-rendering:optimizeLegibility;font-size:14px;--navy:#102b3d;--muted:#607787;--teal:#087e82;--line:#dfE7eb;--orange:#dc8032}</code> | Defines root typography, default foreground/background, rendering preferences, base 14px sizing, and shared navy/muted/teal/line/orange CSS variables. See the rule/declaration appendix below. |
| 4 | <code>*{box-sizing:border-box}body{margin:0}button,input,select{font:inherit}button,select{cursor:pointer}button:disabled{cursor:default}a{color:var(--teal)}button:focus-visible,select:focus-visible,input:focus-visible,summary:focus-visible,a:focus-visible{outline:3px solid #e69745;outline-offset:4px}button{transition:background .15s}h1,h2,h3,p{margin:0}h1,h2,h3{font-family:&#39;Manrope&#39;,system-ui,sans-serif}h2{font-size:19px;letter-spacing:-.6px}h3{font-size:16px}p{line-height:1.6}.topbar{height:76px;background:#102334;color:#fff;padding:0 max(4vw,24px);display:flex;align-items:center;gap:34px;border-bottom:1px solid #254356}.brand{display:flex;align-items:center;gap:12px;font-family:&#39;Manrope&#39;,sans-serif;font-size:23px;font-weight:800;letter-spacing:-1px}.brand-light{font-weight:500;letter-spacing:-.7px}.brand-divider{color:#708b9b;padding:0 5px}.brand-icon{height:29px;width:29px;display:flex;gap:4px;align-items:flex-end}.brand-icon i{display:block;width:6px;background:#66d2c7;border-radius:2px}.brand-icon i:nth-child(1){height:12px}.brand-icon i:nth-child(2){height:22px}.brand-icon i:nth-child(3){height:29px}.topbar-subtitle{font-size:10px;color:#a9bdca;letter-spacing:2px;padding-left:30px;border-left:1px solid #345060}.project-tag{margin-left:auto;border:1px solid #3c5869;border-radius:5px;padding:7px 12px;font-size:11px;letter-spacing:.8px;color:#c9d9e1}main{max-width:1390px;margin:auto;padding:40px max(3.8vw,24px) 0}.page-heading{display:flex;align-items:center;justify-content:space-between;gap:24px}.eyebrow{font-size:10px;font-weight:700;letter-spacing:1.7px;color:var(--teal);margin-bottom:10px}.eyebrow&gt;span{color:#8699a5;margin-left:13px}h1{font-size:clamp(27px,2.5vw,36px);font-weight:800;letter-spacing:-1.5px;line-height:1.3;color:var(--navy)}h1&gt;span{font-weight:500;color:#577181}.page-heading p{margin-top:9px;color:var(--muted);font-size:14px}.refresh-tools{display:flex;align-items:center;gap:18px}.refresh-toggle{display:flex;align-items:center;gap:7px;font-size:12px;color:var(--muted);white-space:nowrap}.refresh-toggle input{accent-color:var(--teal);width:15px;height:15px}.button{display:flex;align-items:center;gap:8px;background:#fff;border:1px solid #cfdbE1;border-radius:6px;padding:9px 14px;color:#294c5e;font-weight:600}.button:hover{background:#eaf3f4}.button span{font-size:20px;line-height:20px}.connection-line{display:flex;align-items:center;gap:7px;color:#718590;font-size:11px;margin:23px 0 16px;min-height:16px}.connection-dot{height:6px;width:6px;border-radius:50%;background:#b8c7cd}.connection-dot.online{background:#078e77;box-shadow:0 0 0 3px #078e7712}.connection-dot.offline{background:#c66a45}.paused-label{margin-left:8px;color:#9a5a25}.overview-strip{display:flex;background:#fff;border:1px solid var(--line);border-radius:9px;padding:22px 25px;margin-bottom:24px;box-shadow:0 2px 4px #10233403}.overview-strip&gt;div{min-width:130px;padding-right:28px;margin-right:28px;border-right:1px solid var(--line);display:flex;flex-direction:column;gap:7px}.overview-strip span{font-size:11px;color:#788b96}.overview-strip strong{font-size:24px;font-family:&#39;Manrope&#39;,sans-serif;color:var(--navy)}.overview-strip&gt;.overview-description{margin:0;padding:0;min-width:0;border:none;margin-left:auto;justify-content:center}.overview-description&gt;span{font-size:9px;letter-spacing:1.5px}.overview-description strong{font-size:13px;line-height:1.5}.overview-description strong span{display:block;font-size:12px;color:var(--teal);font-weight:500}.error-banner{border:1px solid #ecc9bd;border-left:3px solid #bf5135;background:#fff4ef;color:#893f2a;border-radius:6px;padding:14px 18px;display:flex;flex-direction:column;gap:5px;margin-bottom:20px;font-size:12px}.error-banner strong{font-size:13px}.state-panel{min-height:360px;background:#fff;border:1px solid var(--line);border-radius:10px;text-align:center;display:flex;align-items:center;justify-content:center;flex-direction:column;padding:45px;gap:15px}.state-panel p{color:var(--muted);max-width:540px}.state-panel h2{font-size:24px}.state-panel.small{min-height:180px}.empty-icon{border:1px solid #d8e9ea;background:#edf7f6;height:66px;width:66px;border-radius:17px;color:var(--teal);font-size:48px;line-height:60px;margin-bottom:6px}.empty-steps{display:flex;gap:30px;color:#718b99;font-size:11px;margin-top:20px}.state-panel .eyebrow{margin:0}.loader{height:28px;width:28px;border:2px solid #d8e6e8;border-top-color:var(--teal);border-radius:50%;animation:spin 1s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}.run-toolbar{display:flex;align-items:center;gap:24px;margin:24px 0 18px}.run-label{min-width:150px}.run-label .eyebrow{font-size:9px;margin-bottom:5px}.run-label label{font-weight:600;font-size:13px}.run-toolbar select{min-width:0;flex:1;max-width:720px;background:#fff;border:1px solid #cbdbe2;border-radius:6px;padding:12px;color:#29495b}.selection-count{margin-left:auto;font-size:11px;color:var(--muted);white-space:nowrap}.run-context{background:var(--navy);color:#fff;border-radius:9px;overflow:hidden}.run-context-head{padding:23px 26px;display:flex;justify-content:space-between;gap:24px}.run-context h2{text-transform:capitalize;font-size:23px;margin-top:12px;font-weight:600;letter-spacing:-.5px}.badge{display:inline-block;border:1px solid #dde5ea;background:#f5f8fa;color:#56717f;border-radius:4px;padding:4px 8px;font-size:10px;font-weight:600;line-height:1.2;white-space:nowrap}.run-context .badge{background:#254455;border-color:#395567;color:#cedee5;margin-right:7px}.badge.completed,.run-context .badge.completed{background:#e8f6ef;border-color:#c8e9d8;color:#256953}.badge.running,.run-context .badge.running{background:#dff6f5;border-color:#aee4e3;color:#067a7d}.badge.failed,.run-context .badge.failed{background:#fff0e9;border-color:#edcbbd;color:#b7512b}.run-context .badge.source{background:#27495e;color:#c2e6f1}.run-context .badge.fixture{background:#fff0d6;border-color:#e5bd70;color:#845721}.sampling-emblem{text-align:right;min-width:120px}.sampling-emblem&gt;span{display:block;font-size:9px;letter-spacing:1.5px;color:#9fb8c4}.sampling-emblem strong{font-size:34px;font-family:&#39;Manrope&#39;,sans-serif;font-weight:700}.sampling-emblem strong span{font-size:26px;font-weight:400;color:#6e99ab}.context-bottom{border-top:1px solid #365162;padding:12px 26px;display:flex;gap:23px;font-size:10px;color:#a7c0cd;flex-wrap:wrap}.context-bottom strong{font-weight:500;color:#d5e4eb}.context-bottom code{font-size:10px;color:#d4e4eb;word-break:break-all}.notice{background:#eaf2f4;border:1px solid #d4e4e9;color:#50717e;padding:11px 17px;border-radius:6px;margin:14px 0;font-size:11px;line-height:1.6}.metric-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:22px 0}.metric-card{padding:20px 23px;background:#fff;border:1px solid var(--line);border-radius:8px;position:relative;min-width:0;box-shadow:0 2px 3px #10233403}.metric-label{font-size:12px;color:#536d7d;font-weight:500;display:flex;justify-content:space-between;align-items:center}.metric-symbol{color:#acc1c9;font-size:17px}.metric-value{font-family:&#39;Manrope&#39;,sans-serif;font-weight:800;font-size:32px;letter-spacing:-1px;margin:12px 0 6px;color:var(--navy)}.metric-card p{font-size:10px;color:#81929d;min-height:32px}.metric-missing .metric-value{font-size:22px;margin:17px 0 13px;color:#8598a3}.evidence-tag{font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#088071;display:inline-block;margin-top:10px}.evidence-tag.estimated{color:#a47032}.evidence-tag.unavailable{color:#83929e}.panel{border:1px solid var(--line);border-radius:9px;background:#fff;padding:23px 25px;margin-bottom:20px;min-width:0;box-shadow:0 2px 3px #10233403}.panel-heading{display:flex;justify-content:space-between;align-items:center;gap:15px;margin-bottom:24px}.panel-heading .eyebrow{font-size:9px;margin-bottom:6px}.panel-heading h2{font-size:18px;font-weight:700}.panel-heading&gt;.badge{font-weight:500}.chart-legend{display:flex;flex-wrap:wrap;gap:20px;font-size:10px;color:#718590;margin:0 0 12px}.chart-legend&gt;span{display:flex;align-items:center;gap:7px}.legend-line{width:17px;height:2px;background:var(--teal);display:inline-block}.legend-line.drift{height:0;border-top:2px dashed var(--orange);background:transparent}.legend-dot{height:6px;width:6px;border-radius:50%;background:#798e9d;display:inline-block}.legend-dot.attack{background:#ca7647}.legend-dot.benign{background:#acc5ce}.legend-dot.pareto{background:var(--teal);box-shadow:0 0 0 2px #a0d9d5}.legend-dot.comparison{background:#8d9da8}.timeline-svg,.tradeoff-svg{display:block;width:100%;height:auto;overflow:visible}.timeline-svg{max-height:300px}.grid-line{stroke:#eaf0f2;stroke-width:1}.axis-label{font-size:10px;fill:#879ba7}.axis-title{font-size:10px;fill:#718895}.threshold-line{stroke:#bdced5;stroke-dasharray:5 5}.probability-line{fill:none;stroke:var(--teal);stroke-width:2;stroke-linejoin:round}.truth-attack{fill:#d99a73;opacity:.65}.truth-benign{fill:#a4bec9;opacity:.6}.drift-line{stroke:#d78a4b;stroke-width:1.5;stroke-dasharray:4 4}.chart-note{font-size:10px;color:#8698a2;line-height:1.65;margin-top:12px}.chart-empty{min-height:200px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:9px;text-align:center;padding:25px}.chart-empty p{font-size:12px;color:#7b909c;max-width:480px}.chart-empty h3{color:#536e7e;font-size:15px;font-weight:600}.chart-empty.compact{min-height:180px}.empty-glyph{font-size:42px;color:#98b7c0}.analysis-grid{display:grid;grid-template-columns:1.15fr 1fr;gap:20px}.analysis-grid&gt;.panel{margin-bottom:20px}.inline-control{display:flex;justify-content:space-between;align-items:center;font-size:10px;color:#6b8391;margin-bottom:16px;gap:10px}.inline-control select{border:1px solid #dbe5e9;background:#f9fbfc;border-radius:5px;padding:7px;color:#486573;font-size:11px}.pareto-point{fill:#0e8c89;stroke:#a9d9d4;stroke-width:3}.comparison-point{fill:#849ca9;stroke:white;stroke-width:2}.point-label{font-size:9px;fill:#5e7988}.count-list{margin:0}.count-list&gt;div{display:flex;justify-content:space-between;border-bottom:1px solid #ecf1f3;padding:12px 0}.count-list&gt;div:last-child{border-bottom:none}.count-list dt{text-transform:capitalize;color:#6b8392;font-size:12px}.count-list dd{margin:0;font-weight:600;color:#2d4a5d;font-variant-numeric:tabular-nums}.account-note{font-size:10px;color:#7f94a0;line-height:1.7;background:#f4f8f9;border-radius:6px;padding:13px;margin-top:15px}.table-scroll{overflow:auto}table{width:100%;border-collapse:collapse;font-size:12px;text-align:left}thead th{font-weight:500;font-size:10px;color:#8496a3;padding:12px;border-bottom:1px solid #dce6ea;white-space:nowrap}tbody td,tbody th{padding:15px 12px;border-bottom:1px solid #edf1f3;white-space:nowrap;font-weight:400}tbody tr:last-child td,tbody tr:last-child th{border-bottom:none}tbody tr:hover{background:#f8fafb}.selected-row{background:#f0f8f8}.run-link{background:none;border:none;padding:0;color:#087d82;text-align:left;font-size:11px;max-width:190px;overflow:hidden;text-overflow:ellipsis}.run-link:hover{text-decoration:underline}table small{display:block;font-size:9px;color:#8398a4;margin-top:5px}.evidence-list&gt;div{display:flex;align-items:flex-start;justify-content:space-between;border-bottom:1px solid #edf1f3;padding:10px 0;gap:16px}.evidence-list&gt;div:last-child{border-bottom:none}.evidence-list strong{font-size:11px;font-weight:500;color:#506d7d}.evidence-list small{display:block;font-size:10px;color:#8b9da7;margin-top:3px;line-height:1.5}.evidence-list&gt;div&gt;span{font-size:11px;font-weight:500;color:#355568;text-align:right;white-space:nowrap}.details-grid{grid-template-columns:1.15fr 1fr}.drift-log{list-style:none;padding:0;margin:0;max-height:360px;overflow:auto}.drift-log li{display:flex;gap:13px;border-left:1px solid #e7edf0;margin-left:4px;padding:0 0 22px 18px;position:relative}.event-dot{position:absolute;left:-4px;top:4px;height:7px;width:7px;background:#d49153;border:2px solid #fff;box-shadow:0 0 0 1px #e2bf94;border-radius:50%}.drift-log strong{font-size:12px;font-weight:500;color:#4b6878;text-transform:capitalize}.drift-log p{font-size:10px;color:#8095a0;margin:5px 0}.drift-log small{font-size:10px;color:#9babb4}.config-details{border-top:1px solid #e5edf0;margin-top:20px;padding-top:16px}.config-details summary{font-size:11px;color:#597c8d;cursor:pointer}.config-details pre{font-size:10px;line-height:1.8;background:#f5f8fa;border-radius:5px;padding:16px;color:#5b7787;overflow:auto;max-height:350px}footer{border-top:1px solid #dde7eb;display:flex;justify-content:space-between;gap:20px;font-size:10px;color:#8b9da6;padding:24px 0;margin-top:10px;line-height:1.6}.footer-dot{padding:0 8px;color:#a4b5bd}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}.skip-link{position:absolute;left:16px;top:-100px;background:white;padding:10px;z-index:5}.skip-link:focus{top:10px}</code> | Contains the compressed base stylesheet: resets, header, overview, loading/error/empty states, run selection/context, metrics, SVG charts, tables, logs, footer, and accessibility rules. Every selector and declaration is expanded below with its value and effect. |
| 5 | <code>@media(max-width:1100px){.overview-strip&gt;div{min-width:100px;margin-right:20px;padding-right:20px}.topbar-subtitle{display:none}.overview-strip&gt;.overview-description strong{font-size:11px}.metric-card{padding:18px}.metric-value{font-size:28px}.refresh-tools{gap:10px}.refresh-toggle{font-size:10px}}</code> | At viewport widths at most 1100px, tightens overview/card/refresh spacing and hides the header subtitle. |
| 6 | <code>@media(max-width:850px){.page-heading{align-items:flex-start;flex-direction:column;gap:20px}.refresh-tools{width:100%;justify-content:flex-end}.overview-strip{flex-wrap:wrap;gap:15px;padding:19px}.overview-strip&gt;div{flex:1;min-width:75px;padding:0;margin:0}.overview-strip&gt;.overview-description{display:none}.metric-grid{grid-template-columns:repeat(2,1fr)}.analysis-grid{grid-template-columns:1fr}.run-toolbar{flex-wrap:wrap;gap:12px}.run-toolbar select{flex-basis:100%;order:3;max-width:none}.selection-count{margin-left:auto}.panel{padding:20px}.empty-steps{flex-direction:column;gap:12px}h1&gt;span{display:block}.context-bottom{gap:12px 20px}.run-context-head{padding:20px}.context-bottom{padding:12px 20px}.tradeoff-svg{max-height:300px}}</code> | At widths at most 850px, stacks the heading and analysis panels, wraps overview/run controls, uses two metric columns, and adjusts chart/layout spacing. |
| 7 | <code>@media(max-width:480px){main{padding:26px 16px 0}.topbar{padding:0 16px;height:65px}.brand{font-size:19px}.project-tag{font-size:9px;padding:6px}.page-heading h1{font-size:27px}.run-context-head{gap:8px}.sampling-emblem{min-width:80px}.sampling-emblem strong{font-size:29px}.sampling-emblem&gt;span{font-size:8px}.run-context .badge{margin:0 4px 5px 0;font-size:9px}.metric-grid{gap:10px}.metric-card{padding:16px 12px}.metric-value{font-size:25px}.metric-missing .metric-value{font-size:18px}.metric-card p{font-size:9px}.metric-label{font-size:11px}.panel-heading h2{font-size:16px}.chart-legend{gap:12px}.state-panel{padding:25px 20px}.overview-strip strong{font-size:21px}.overview-strip span{font-size:9px}.context-bottom code{font-size:9px}footer{flex-direction:column;gap:6px}.evidence-list&gt;div&gt;span{white-space:normal;min-width:80px}}</code> | At widths at most 480px, reduces padding, font sizes, badge dimensions and card gaps, stacks the footer, and permits evidence values to wrap. |
| 8 | <code>@media(prefers-reduced-motion:reduce){.loader{animation:none}button{transition:none}}</code> | Respects reduced-motion preference by disabling the loading-spinner animation and button transitions. |
| 9 | <code>.provenance-details{margin:12px 0;color:#62818f;font-size:11px}.provenance-details summary{cursor:pointer}.provenance-details pre{padding:15px;background:#eaf2f4;border-radius:5px;overflow:auto;font-size:10px;line-height:1.7;max-height:220px}</code> | Styles the expandable provenance panel, its clickable summary, and its scrollable preformatted JSON with a 220px maximum height. |

## frontend/src/test-fixtures.ts

Synthetic run factory for tests. Invented measurements support assertions; they are not project performance claims.

### Complete source

```typescript
// Synthetic evidence for tests only. Never imported by the application.
import type { RunSummary } from './types';

export const fixtureRun = (id = 'test-run', n = 1, f1 = .8, cost = 10): RunSummary => ({
  schema_version: 1, run_id: id, source: 'fixture', mode: 'csv_replay', status: 'completed',
  sampling_rate: n, seed: 42, scenario: 'baseline', unit: 'flow',
  created_at: '2026-10-11T12:00:00Z', ended_at: '2026-10-11T12:01:00Z',
  counts: { input: 100, sampled: 100, evaluated: 90, warmup: 10, excluded: 0, unlabeled: 0 },
  metrics: {
    precision: { value: .9, unit: 'ratio', status: 'measured', reason: null },
    recall: { value: .7, unit: 'ratio', status: 'measured', reason: null },
    f1: { value: f1, unit: 'ratio', status: 'measured', reason: null },
    inference_latency_ms: { value: .12, unit: 'ms', status: 'measured', reason: null },
    telemetry_bandwidth_kbps: { value: cost, unit: 'kbit/s', status: 'measured', reason: null },
    controller_cpu_percent_mean: { value: null, unit: '%', status: 'unavailable', reason: 'No live controller in CSV replay.' },
  },
  drift_count: 0, error: null, config: { threshold: .5, grace_period: 200, max_records: 100, warmup_records: 10 },
  feature_schema: 'flow-v1', provenance: { sha256: 'test-only' },
});
```

### Every physical line

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>// Synthetic evidence for tests only. Never imported by the application.</code> | Documents that these invented values are test inputs only; runtime application files do not import this factory. |
| 2 | <code>import type { RunSummary } from &#39;./types&#39;;</code> | Imports the RunSummary compile-time contract so fixtures match the response shape. |
| 3 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 4 | <code>export const fixtureRun = (id = &#39;test-run&#39;, n = 1, f1 = .8, cost = 10): RunSummary =&gt; ({</code> | Exports a factory with overridable ID, sampling N, F1, and cost; defaults are test-run, 1, .8, and 10. Parentheses make the arrow return an object literal. |
| 5 | <code>  schema_version: 1, run_id: id, source: &#39;fixture&#39;, mode: &#39;csv_replay&#39;, status: &#39;completed&#39;,</code> | Creates schema v1 evidence clearly labeled fixture, CSV replay, completed. |
| 6 | <code>  sampling_rate: n, seed: 42, scenario: &#39;baseline&#39;, unit: &#39;flow&#39;,</code> | Stores the supplied sampling rate and fixed seed/scenario/flow unit. Synthetic counts are not recomputed from N because tests vary N for presentation/comparison. |
| 7 | <code>  created_at: &#39;2026-10-11T12:00:00Z&#39;, ended_at: &#39;2026-10-11T12:01:00Z&#39;,</code> | Uses fixed UTC timestamps so fixture tests are deterministic. |
| 8 | <code>  counts: { input: 100, sampled: 100, evaluated: 90, warmup: 10, excluded: 0, unlabeled: 0 },</code> | Defines a simple 100-input/100-sampled run with 10 warm-up and 90 evaluated records and no excluded/unlabeled records. |
| 9 | <code>  metrics: {</code> | Starts the test metric dictionary. |
| 10 | <code>    precision: { value: .9, unit: &#39;ratio&#39;, status: &#39;measured&#39;, reason: null },</code> | Provides measured precision .9 with ratio unit and no limitation. |
| 11 | <code>    recall: { value: .7, unit: &#39;ratio&#39;, status: &#39;measured&#39;, reason: null },</code> | Provides measured recall .7. |
| 12 | <code>    f1: { value: f1, unit: &#39;ratio&#39;, status: &#39;measured&#39;, reason: null },</code> | Uses the factory's F1 parameter, allowing Pareto tests to vary quality. |
| 13 | <code>    inference_latency_ms: { value: .12, unit: &#39;ms&#39;, status: &#39;measured&#39;, reason: null },</code> | Provides measured .12 ms inference latency. |
| 14 | <code>    telemetry_bandwidth_kbps: { value: cost, unit: &#39;kbit/s&#39;, status: &#39;measured&#39;, reason: null },</code> | Uses the cost parameter as measured telemetry kbit/s, allowing Pareto tests to vary overhead. |
| 15 | <code>    controller_cpu_percent_mean: { value: null, unit: &#39;%&#39;, status: &#39;unavailable&#39;, reason: &#39;No live controller in CSV replay.&#39; },</code> | Marks controller CPU unavailable with an explanatory reason, testing that absence is displayed honestly. |
| 16 | <code>  },</code> | Closes the metric dictionary. |
| 17 | <code>  drift_count: 0, error: null, config: { threshold: .5, grace_period: 200, max_records: 100, warmup_records: 10 },</code> | Provides zero drift alarms, no failure, and fixed threshold/grace-period/record-limit/warm-up settings. |
| 18 | <code>  feature_schema: &#39;flow-v1&#39;, provenance: { sha256: &#39;test-only&#39; },</code> | Provides feature schema flow-v1 and an explicitly synthetic test-only checksum. |
| 19 | <code>});</code> | Ends the returned fixture object and arrow function expression. |

## frontend/src/test-setup.ts

Shared DOM matcher registration and component cleanup for Vitest.

### Complete source

```typescript
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';
afterEach(cleanup);
```

### Every physical line

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>import &#39;@testing-library/jest-dom/vitest&#39;;</code> | Registers jest-dom's DOM-specific matchers with Vitest, including toBeInTheDocument and toHaveValue. |
| 2 | <code>import { cleanup } from &#39;@testing-library/react&#39;;</code> | Imports React Testing Library cleanup, which unmounts rendered components. |
| 3 | <code>import { afterEach } from &#39;vitest&#39;;</code> | Imports Vitest's afterEach lifecycle hook. |
| 4 | <code>afterEach(cleanup);</code> | Runs cleanup after every test, triggering component effect cleanup and preventing DOM/request-timer leakage between cases. |

## frontend/src/App.test.tsx

Component tests for empty/error/provenance/selection states using mocked API helpers.

### Complete source

```tsx
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import App from './App';
import * as api from './api';
import { fixtureRun } from './test-fixtures';

vi.mock('./api', () => ({ getRuns: vi.fn(), getOverview: vi.fn(), getRun: vi.fn(), getSeries: vi.fn() }));

beforeEach(() => {
  vi.mocked(api.getRuns).mockResolvedValue([]);
  vi.mocked(api.getOverview).mockResolvedValue({ total_runs: 0, completed_runs: 0, running_runs: 0, failed_runs: 0, best_run_id: null });
  vi.mocked(api.getSeries).mockResolvedValue({ predictions: [], resources: [], drift: [] });
});

describe('experiment dashboard', () => {
  it('shows a useful empty state without invented runs', async () => {
    render(<App />);
    expect(await screen.findByText('No experiment results yet')).toBeInTheDocument();
    expect(screen.queryByLabelText('Selected run')).not.toBeInTheDocument();
    expect(screen.getByText('02 · Run N = 1 baseline')).toBeInTheDocument();
  });
  it('shows server failures with a recovery action', async () => {
    vi.mocked(api.getRuns).mockRejectedValue(new Error('HTTP 503'));
    render(<App />);
    expect(await screen.findByRole('alert')).toHaveTextContent('HTTP 503');
    expect(screen.getByRole('button', { name: /Refresh/ })).toBeEnabled();
  });
  it('identifies fixtures, missing metrics and changes the selected run', async () => {
    const a = fixtureRun('trial-a'); const b = fixtureRun('trial-b', 10);
    vi.mocked(api.getRuns).mockResolvedValue([a, b]);
    vi.mocked(api.getOverview).mockResolvedValue({ total_runs: 2, completed_runs: 2, running_runs: 0, failed_runs: 0, best_run_id: null });
    vi.mocked(api.getRun).mockImplementation(async id => id === 'trial-b' ? b : a);
    render(<App />);
    expect(await screen.findByText('This run samples flow records. Packet sampling and live SDN overhead require capture replay or live sFlow measurements.')).toBeInTheDocument();
    expect(screen.getByText('No live controller in CSV replay.')).toBeInTheDocument();
    expect(screen.getByText(/Its results do not establish performance/)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Selected run'), { target: { value: 'trial-b' } });
    await waitFor(() => expect(api.getRun).toHaveBeenCalledWith('trial-b', expect.any(AbortSignal)));
    await waitFor(() => expect(screen.getByLabelText('Selected run')).toHaveValue('trial-b'));
  });
});
```

### Every physical line

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>import { fireEvent, render, screen, waitFor } from &#39;@testing-library/react&#39;;</code> | Imports component-testing utilities: render mounts JSX, screen queries DOM, fireEvent simulates DOM events, waitFor retries asynchronous assertions. |
| 2 | <code>import { beforeEach, describe, expect, it, vi } from &#39;vitest&#39;;</code> | Imports Vitest suite/test/assertion/mock functions and beforeEach setup. |
| 3 | <code>import App from &#39;./App&#39;;</code> | Imports the real dashboard component being tested. |
| 4 | <code>import * as api from &#39;./api&#39;;</code> | Imports the API module namespace so its mocked functions can be configured and inspected. |
| 5 | <code>import { fixtureRun } from &#39;./test-fixtures&#39;;</code> | Imports the synthetic run factory used only in tests. |
| 6 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 7 | <code>vi.mock(&#39;./api&#39;, () =&gt; ({ getRuns: vi.fn(), getOverview: vi.fn(), getRun: vi.fn(), getSeries: vi.fn() }));</code> | Replaces all four API readers with mock functions; these component tests make no real backend requests. |
| 8 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 9 | <code>beforeEach(() =&gt; {</code> | Starts setup that runs before each test case. |
| 10 | <code>  vi.mocked(api.getRuns).mockResolvedValue([]);</code> | Defaults the run reader to resolve an empty array. |
| 11 | <code>  vi.mocked(api.getOverview).mockResolvedValue({ total_runs: 0, completed_runs: 0, running_runs: 0, failed_runs: 0, best_run_id: null });</code> | Defaults overview to zero counters and null best run. |
| 12 | <code>  vi.mocked(api.getSeries).mockResolvedValue({ predictions: [], resources: [], drift: [] });</code> | Defaults selected series to empty arrays so tests focus on dashboard states. |
| 13 | <code>});</code> | Closes the current callback/object and its surrounding call. |
| 14 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 15 | <code>describe(&#39;experiment dashboard&#39;, () =&gt; {</code> | Groups component cases under the experiment dashboard suite. |
| 16 | <code>  it(&#39;shows a useful empty state without invented runs&#39;, async () =&gt; {</code> | Begins an asynchronous empty-state test. |
| 17 | <code>    render(&lt;App /&gt;);</code> | Mounts App in the test DOM. |
| 18 | <code>    expect(await screen.findByText(&#39;No experiment results yet&#39;)).toBeInTheDocument();</code> | Waits for the asynchronous request result and asserts the no-results explanation appears. |
| 19 | <code>    expect(screen.queryByLabelText(&#39;Selected run&#39;)).not.toBeInTheDocument();</code> | Uses a nonthrowing query and verifies a run selector is absent when there are no runs. |
| 20 | <code>    expect(screen.getByText(&#39;02 · Run N = 1 baseline&#39;)).toBeInTheDocument();</code> | Checks that baseline-run guidance exists in the empty state. |
| 21 | <code>  });</code> | Closes the current callback/object and its surrounding call. |
| 22 | <code>  it(&#39;shows server failures with a recovery action&#39;, async () =&gt; {</code> | Begins the server-failure recovery test. |
| 23 | <code>    vi.mocked(api.getRuns).mockRejectedValue(new Error(&#39;HTTP 503&#39;));</code> | Overrides getRuns to reject with HTTP 503. |
| 24 | <code>    render(&lt;App /&gt;);</code> | Mounts App, causing the mocked failing request. |
| 25 | <code>    expect(await screen.findByRole(&#39;alert&#39;)).toHaveTextContent(&#39;HTTP 503&#39;);</code> | Waits for the accessible alert and checks it contains the specific backend failure. |
| 26 | <code>    expect(screen.getByRole(&#39;button&#39;, { name: /Refresh/ })).toBeEnabled();</code> | Asserts the Refresh button remains enabled so users have a recovery action. |
| 27 | <code>  });</code> | Closes the current callback/object and its surrounding call. |
| 28 | <code>  it(&#39;identifies fixtures, missing metrics and changes the selected run&#39;, async () =&gt; {</code> | Begins the fixture/provenance/missing-metric/run-selection case. |
| 29 | <code>    const a = fixtureRun(&#39;trial-a&#39;); const b = fixtureRun(&#39;trial-b&#39;, 10);</code> | Creates two independent synthetic completed runs with N=1 and N=10. |
| 30 | <code>    vi.mocked(api.getRuns).mockResolvedValue([a, b]);</code> | Makes the run list contain both fixtures. |
| 31 | <code>    vi.mocked(api.getOverview).mockResolvedValue({ total_runs: 2, completed_runs: 2, running_runs: 0, failed_runs: 0, best_run_id: null });</code> | Provides matching completed/total overview counts. |
| 32 | <code>    vi.mocked(api.getRun).mockImplementation(async id =&gt; id === &#39;trial-b&#39; ? b : a);</code> | Makes getRun return b for trial-b, otherwise a; the async mock mimics a promise API. |
| 33 | <code>    render(&lt;App /&gt;);</code> | Mounts the dashboard and lets its initial requests execute. |
| 34 | <code>    expect(await screen.findByText(&#39;This run samples flow records. Packet sampling and live SDN overhead require capture replay or live sFlow measurements.&#39;)).toBeInTheDocument();</code> | Waits for and asserts the CSV flow-sampling limitation notice. |
| 35 | <code>    expect(screen.getByText(&#39;No live controller in CSV replay.&#39;)).toBeInTheDocument();</code> | Checks the controller-CPU unavailable reason is shown instead of a zero. |
| 36 | <code>    expect(screen.getByText(/Its results do not establish performance/)).toBeInTheDocument();</code> | Checks fixture results carry a notice that they do not establish official dataset performance. |
| 37 | <code>    fireEvent.change(screen.getByLabelText(&#39;Selected run&#39;), { target: { value: &#39;trial-b&#39; } });</code> | Simulates selecting trial-b through the labeled run dropdown. |
| 38 | <code>    await waitFor(() =&gt; expect(api.getRun).toHaveBeenCalledWith(&#39;trial-b&#39;, expect.any(AbortSignal)));</code> | Retries until getRun is called with trial-b and an AbortSignal, proving selection initiates the right detail request. |
| 39 | <code>    await waitFor(() =&gt; expect(screen.getByLabelText(&#39;Selected run&#39;)).toHaveValue(&#39;trial-b&#39;));</code> | Retries until the controlled dropdown reflects trial-b. |
| 40 | <code>  });</code> | Closes the current callback/object and its surrounding call. |
| 41 | <code>});</code> | Closes the current callback/object and its surrounding call. |

## frontend/src/api.test.ts

HTTP-boundary and schema checks with mocked fetch responses.

### Complete source

```typescript
import { afterEach, describe, expect, it, vi } from 'vitest';
import { getRun, getRuns, getSeries, validateRun } from './api';
import { fixtureRun } from './test-fixtures';

afterEach(() => vi.unstubAllGlobals());
describe('API contract', () => {
  it('accepts versioned evidence and rejects malformed metric values', () => {
    expect(validateRun(fixtureRun()).run_id).toBe('test-run');
    expect(() => validateRun({ ...fixtureRun(), schema_version: 2 })).toThrow('schema version 1');
    const bad = fixtureRun(); bad.metrics.f1.value = Number.NaN;
    expect(() => validateRun(bad)).toThrow('invalid metric evidence');
  });
  it('surfaces HTTP failures rather than displaying blank evidence', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 503 }));
    await expect(getRuns()).rejects.toThrow('HTTP 503');
  });
  it('encodes selected run IDs and validates response', async () => {
    const mock = vi.fn().mockResolvedValue({ ok: true, json: async () => fixtureRun('a/b') });
    vi.stubGlobal('fetch', mock);
    await getRun('a/b');
    expect(mock.mock.calls[0][0]).toBe('/api/runs/a%2Fb');
  });
  it('rejects invalid series', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({ predictions: [], drift: [] }) }));
    await expect(getSeries('test')).rejects.toThrow('invalid timeline evidence');
  });
});
```

### Every physical line

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>import { afterEach, describe, expect, it, vi } from &#39;vitest&#39;;</code> | Imports Vitest assertion, cleanup, suite, test, and mocking utilities. |
| 2 | <code>import { getRun, getRuns, getSeries, validateRun } from &#39;./api&#39;;</code> | Imports the real API readers and run validator under test. |
| 3 | <code>import { fixtureRun } from &#39;./test-fixtures&#39;;</code> | Imports the test-only run factory. |
| 4 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 5 | <code>afterEach(() =&gt; vi.unstubAllGlobals());</code> | Restores stubbed globals such as fetch after every test to prevent contamination. |
| 6 | <code>describe(&#39;API contract&#39;, () =&gt; {</code> | Starts the API-contract test suite. |
| 7 | <code>  it(&#39;accepts versioned evidence and rejects malformed metric values&#39;, () =&gt; {</code> | Begins testing schema-version and metric validation. |
| 8 | <code>    expect(validateRun(fixtureRun()).run_id).toBe(&#39;test-run&#39;);</code> | Checks that a valid fixture is accepted with its expected run ID. |
| 9 | <code>    expect(() =&gt; validateRun({ ...fixtureRun(), schema_version: 2 })).toThrow(&#39;schema version 1&#39;);</code> | Copies the fixture with schema_version 2 and asserts validation throws an error mentioning version 1. |
| 10 | <code>    const bad = fixtureRun(); bad.metrics.f1.value = Number.NaN;</code> | Creates a fresh fixture and deliberately corrupts its F1 value to NaN. |
| 11 | <code>    expect(() =&gt; validateRun(bad)).toThrow(&#39;invalid metric evidence&#39;);</code> | Asserts nonfinite metric evidence is rejected. |
| 12 | <code>  });</code> | Closes the current callback/object and its surrounding call. |
| 13 | <code>  it(&#39;surfaces HTTP failures rather than displaying blank evidence&#39;, async () =&gt; {</code> | Begins the HTTP-error propagation test. |
| 14 | <code>    vi.stubGlobal(&#39;fetch&#39;, vi.fn().mockResolvedValue({ ok: false, status: 503 }));</code> | Stubs global fetch with a response representing HTTP 503. |
| 15 | <code>    await expect(getRuns()).rejects.toThrow(&#39;HTTP 503&#39;);</code> | Awaits rejection from getRuns and requires the HTTP status in the error message. |
| 16 | <code>  });</code> | Closes the current callback/object and its surrounding call. |
| 17 | <code>  it(&#39;encodes selected run IDs and validates response&#39;, async () =&gt; {</code> | Begins checking safe URL construction for arbitrary run IDs. |
| 18 | <code>    const mock = vi.fn().mockResolvedValue({ ok: true, json: async () =&gt; fixtureRun(&#39;a/b&#39;) });</code> | Creates a fetch mock returning a valid fixture with slash-containing ID a/b. |
| 19 | <code>    vi.stubGlobal(&#39;fetch&#39;, mock);</code> | Installs that mock as global fetch. |
| 20 | <code>    await getRun(&#39;a/b&#39;);</code> | Requests a/b using the real getRun helper. |
| 21 | <code>    expect(mock.mock.calls[0][0]).toBe(&#39;/api/runs/a%2Fb&#39;);</code> | Inspects the first fetch-call URL and requires slash encoding as %2F. |
| 22 | <code>  });</code> | Closes the current callback/object and its surrounding call. |
| 23 | <code>  it(&#39;rejects invalid series&#39;, async () =&gt; {</code> | Begins testing malformed timeline response rejection. |
| 24 | <code>    vi.stubGlobal(&#39;fetch&#39;, vi.fn().mockResolvedValue({ ok: true, json: async () =&gt; ({ predictions: [], drift: [] }) }));</code> | Stubs a nominally successful JSON response missing the required resources array. |
| 25 | <code>    await expect(getSeries(&#39;test&#39;)).rejects.toThrow(&#39;invalid timeline evidence&#39;);</code> | Asserts getSeries rejects with the timeline-contract error. |
| 26 | <code>  });</code> | Closes the current callback/object and its surrounding call. |
| 27 | <code>});</code> | Closes the current callback/object and its surrounding call. |

## frontend/src/evidence.test.ts

Pure-function tests protecting missing-value handling, compatible comparisons, and Pareto classification.

### Complete source

```typescript
import { describe, expect, it } from 'vitest';
import { compatibleRuns, formatMetric, paretoRuns } from './evidence';
import type { RunSummary } from './types';
import { fixtureRun } from './test-fixtures';

describe('scientific evidence handling', () => {
  it('keeps measured zero distinct from unavailable', () => {
    expect(formatMetric('recall', { value: 0, unit: 'ratio', status: 'measured', reason: null })).toBe('0.0%');
    expect(formatMetric('recall', { value: null, unit: 'ratio', status: 'unavailable', reason: 'No attacks' })).toBe('Unavailable');
    expect(formatMetric('recall', { value: 0, unit: 'ratio', status: 'unavailable', reason: 'Missing' })).toBe('Unavailable');
  });
  it('does not combine different source, scenario, mode, feature or dataset evidence', () => {
    const base = fixtureRun();
    const different: RunSummary[] = [
      { ...base, source: 'official_5g_nidd' }, { ...base, scenario: 'unseen' },
      { ...base, mode: 'live_sflow' }, { ...base, feature_schema: 'other' },
      { ...base, provenance: { sha256: 'other' } }, { ...base, status: 'running' },
      { ...base, config: { ...base.config, max_records: 200 } },
      { ...base, config: { ...base.config, threshold: .8 } },
    ];
    expect(compatibleRuns([base, ...different], base)).toEqual([base]);
  });
  it('identifies strict Pareto dominance and excludes estimated costs', () => {
    const a = fixtureRun('a', 1, .8, 10);
    const b = fixtureRun('b', 2, .85, 5);
    const c = fixtureRun('c', 5, .7, 2);
    const estimated = fixtureRun('estimate', 10, .99, .1);
    estimated.metrics.telemetry_bandwidth_kbps.status = 'estimated';
    expect([...paretoRuns([a, b, c, estimated], 'telemetry_bandwidth_kbps')]).toEqual(['b', 'c']);
  });
});
```

### Every physical line

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>import { describe, expect, it } from &#39;vitest&#39;;</code> | Imports the Vitest test grouping and assertions. |
| 2 | <code>import { compatibleRuns, formatMetric, paretoRuns } from &#39;./evidence&#39;;</code> | Imports the real evidence formatting, compatibility, and Pareto functions. |
| 3 | <code>import type { RunSummary } from &#39;./types&#39;;</code> | Imports the RunSummary type only for the intentionally varied fixtures. |
| 4 | <code>import { fixtureRun } from &#39;./test-fixtures&#39;;</code> | Imports the synthetic fixture factory. |
| 5 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 6 | <code>describe(&#39;scientific evidence handling&#39;, () =&gt; {</code> | Starts the scientific-evidence behavior test suite. |
| 7 | <code>  it(&#39;keeps measured zero distinct from unavailable&#39;, () =&gt; {</code> | Begins distinguishing a true measured zero from a missing measurement. |
| 8 | <code>    expect(formatMetric(&#39;recall&#39;, { value: 0, unit: &#39;ratio&#39;, status: &#39;measured&#39;, reason: null })).toBe(&#39;0.0%&#39;);</code> | Requires measured recall zero to render 0.0%, preserving an actual zero result. |
| 9 | <code>    expect(formatMetric(&#39;recall&#39;, { value: null, unit: &#39;ratio&#39;, status: &#39;unavailable&#39;, reason: &#39;No attacks&#39; })).toBe(&#39;Unavailable&#39;);</code> | Requires unavailable null recall to display Unavailable. |
| 10 | <code>    expect(formatMetric(&#39;recall&#39;, { value: 0, unit: &#39;ratio&#39;, status: &#39;unavailable&#39;, reason: &#39;Missing&#39; })).toBe(&#39;Unavailable&#39;);</code> | Requires unavailable status to override even a numeric zero, preventing false measured-zero claims. |
| 11 | <code>  });</code> | Closes the current callback/object and its surrounding call. |
| 12 | <code>  it(&#39;does not combine different source, scenario, mode, feature or dataset evidence&#39;, () =&gt; {</code> | Begins the incompatible-evidence exclusion test. |
| 13 | <code>    const base = fixtureRun();</code> | Creates one baseline fixture used as the selected comparison reference. |
| 14 | <code>    const different: RunSummary[] = [</code> | Starts a typed array of deliberate comparison mismatches. |
| 15 | <code>      { ...base, source: &#39;official_5g_nidd&#39; }, { ...base, scenario: &#39;unseen&#39; },</code> | Copies the baseline once with a different source and once with a different scenario. |
| 16 | <code>      { ...base, mode: &#39;live_sflow&#39; }, { ...base, feature_schema: &#39;other&#39; },</code> | Adds copies with a different execution mode and feature schema. |
| 17 | <code>      { ...base, provenance: { sha256: &#39;other&#39; } }, { ...base, status: &#39;running&#39; },</code> | Adds copies with a different dataset checksum and unfinished running status. |
| 18 | <code>      { ...base, config: { ...base.config, max_records: 200 } },</code> | Adds a copy whose max-record cap differs while preserving its other config. |
| 19 | <code>      { ...base, config: { ...base.config, threshold: .8 } },</code> | Adds a copy with decision threshold .8 instead of .5. |
| 20 | <code>    ];</code> | Ends the mismatched-summary array. |
| 21 | <code>    expect(compatibleRuns([base, ...different], base)).toEqual([base]);</code> | Requires the compatibility filter to keep only the unchanged baseline. |
| 22 | <code>  });</code> | Closes the current callback/object and its surrounding call. |
| 23 | <code>  it(&#39;identifies strict Pareto dominance and excludes estimated costs&#39;, () =&gt; {</code> | Begins verifying Pareto dominance and measured-cost requirements. |
| 24 | <code>    const a = fixtureRun(&#39;a&#39;, 1, .8, 10);</code> | Defines trial a with N=1, F1 .8, cost 10. |
| 25 | <code>    const b = fixtureRun(&#39;b&#39;, 2, .85, 5);</code> | Defines trial b with N=2, F1 .85, cost 5; b beats a on both axes. |
| 26 | <code>    const c = fixtureRun(&#39;c&#39;, 5, .7, 2);</code> | Defines trial c with N=5, F1 .7, cost 2; cheaper than b but lower quality. |
| 27 | <code>    const estimated = fixtureRun(&#39;estimate&#39;, 10, .99, .1);</code> | Defines an apparently excellent .99-quality/.1-cost trial. |
| 28 | <code>    estimated.metrics.telemetry_bandwidth_kbps.status = &#39;estimated&#39;;</code> | Marks that last cost estimated, making it ineligible for measured Pareto evidence. |
| 29 | <code>    expect([...paretoRuns([a, b, c, estimated], &#39;telemetry_bandwidth_kbps&#39;)]).toEqual([&#39;b&#39;, &#39;c&#39;]);</code> | Expands the returned ID set and requires b and c only; a is dominated and estimated is excluded. |
| 30 | <code>  });</code> | Closes the current callback/object and its surrounding call. |
| 31 | <code>});</code> | Closes the current callback/object and its surrounding call. |

## frontend/src/integration.test.tsx

Optional read-only real-server checks. Skipped unless M3_API_URL is configured; the server must already contain expected runs.

### Complete source

```tsx
import { afterEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import App from './App';
import { getOverview, getRun, getRuns, getSeries } from './api';
import { compatibleRuns } from './evidence';

// Optional read-only integration check against an actual local API.
// No runs are created and no test data is written to the experiment repository.
const apiBase = (globalThis as unknown as { process: { env: Record<string, string | undefined> } }).process.env.M3_API_URL;
const actualFetch = globalThis.fetch;
afterEach(() => vi.unstubAllGlobals());

function connect() {
  // jsdom AbortSignal belongs to a different realm than Node's native fetch.
  vi.stubGlobal('fetch', (path: string, options?: RequestInit) => actualFetch(`${apiBase}${path}`, { ...options, signal: undefined }));
}

describe.skipIf(!apiBase)('real local experiment evidence', () => {
  it('accepts every saved summary and series and isolates comparison groups', async () => {
    connect();
    const runs = await getRuns();
    const overview = await getOverview();
    expect(overview.total_runs).toBe(runs.length);
    expect(runs.length).toBeGreaterThan(0);
    for (const run of runs) {
      expect((await getRun(run.run_id)).run_id).toBe(run.run_id);
      const series = await getSeries(run.run_id);
      expect(Array.isArray(series.predictions)).toBe(true);
      for (const candidate of compatibleRuns(runs, run)) {
        expect(candidate.source).toBe(run.source);
        expect(candidate.mode).toBe(run.mode);
        expect(candidate.feature_schema).toBe(run.feature_schema);
      }
    }
  }, 20000);

  it('renders a real official run with its timeline and provenance', async () => {
    connect();
    const runs = await getRuns();
    const official = runs.find(run => run.source === 'official_5g_nidd' && run.status === 'completed' && run.counts.evaluated > 0);
    expect(official).toBeDefined();
    render(<App />);
    const select = await screen.findByLabelText('Selected run', {}, { timeout: 10000 });
    fireEvent.change(select, { target: { value: official!.run_id } });
    await waitFor(() => expect(screen.getByText('Official 5G-NIDD')).toBeInTheDocument(), { timeout: 10000 });
    expect(await screen.findByRole('img', { name: /Prediction timeline/ })).toBeInTheDocument();
    expect(screen.getByText('Dataset and feature provenance')).toBeInTheDocument();
    expect(screen.getAllByText(official!.provenance!.sha256!, { exact: false }).length).toBeGreaterThan(0);
    expect(screen.queryByText('This run is labeled', { exact: false })).not.toBeInTheDocument();
  }, 20000);

  it('renders actual live collection with a distinct source and no official-data claim', async () => {
    connect();
    const runs = await getRuns();
    const live = runs.find(run => run.source === 'live_sflow' && run.mode === 'live_sflow');
    expect(live).toBeDefined();
    render(<App />);
    const select = await screen.findByLabelText('Selected run', {}, { timeout: 10000 });
    fireEvent.change(select, { target: { value: live!.run_id } });
    await waitFor(() => expect(screen.getAllByText('Live telemetry').length).toBeGreaterThan(0), { timeout: 10000 });
    expect(screen.getByText('Live sFlow')).toBeInTheDocument();
    expect(screen.getByText(/Its results do not establish performance on official/)).toBeInTheDocument();
    expect(screen.queryByText('Official 5G-NIDD')).not.toBeInTheDocument();
  }, 20000);
});
```

### Every physical line

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>import { afterEach, describe, expect, it, vi } from &#39;vitest&#39;;</code> | Imports Vitest lifecycle, suite/test, assertions, and global stubbing. |
| 2 | <code>import { fireEvent, render, screen, waitFor } from &#39;@testing-library/react&#39;;</code> | Imports actual dashboard DOM rendering, selection simulation, queries, and retry waits. |
| 3 | <code>import App from &#39;./App&#39;;</code> | Imports the real dashboard. |
| 4 | <code>import { getOverview, getRun, getRuns, getSeries } from &#39;./api&#39;;</code> | Imports real backend readers; unlike unit/component tests these are not mocked as API functions. |
| 5 | <code>import { compatibleRuns } from &#39;./evidence&#39;;</code> | Imports the actual comparison filter for integration assertions. |
| 6 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 7 | <code>// Optional read-only integration check against an actual local API.</code> | Documents the suite's purpose: optional requests to a running local server. |
| 8 | <code>// No runs are created and no test data is written to the experiment repository.</code> | Documents that the integration suite reads existing evidence and creates neither runs nor experiment files. |
| 9 | <code>const apiBase = (globalThis as unknown as { process: { env: Record&lt;string, string &#124; undefined&gt; } }).process.env.M3_API_URL;</code> | Reads M3_API_URL from the test process environment through a TypeScript cast; this supplies the actual server base URL. |
| 10 | <code>const actualFetch = globalThis.fetch;</code> | Saves original native fetch before temporarily replacing the global. |
| 11 | <code>afterEach(() =&gt; vi.unstubAllGlobals());</code> | Restores global stubs after every integration case. |
| 12 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 13 | <code>function connect() {</code> | Defines the fetch adapter used by each live-server test. |
| 14 | <code>  // jsdom AbortSignal belongs to a different realm than Node&#39;s native fetch.</code> | Explains the compatibility issue: jsdom AbortSignal is from a different JavaScript realm than native fetch expects. |
| 15 | <code>  vi.stubGlobal(&#39;fetch&#39;, (path: string, options?: RequestInit) =&gt; actualFetch(`${apiBase}${path}`, { ...options, signal: undefined }));</code> | Prefixes each app-relative path with the configured base URL, forwards options, and removes the jsdom signal; actual HTTP requests use native fetch. |
| 16 | <code>}</code> | Closes the current function, interface, or control block begun above. |
| 17 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 18 | <code>describe.skipIf(!apiBase)(&#39;real local experiment evidence&#39;, () =&gt; {</code> | Skips this entire suite when M3_API_URL is absent, so ordinary test runs do not require a server. |
| 19 | <code>  it(&#39;accepts every saved summary and series and isolates comparison groups&#39;, async () =&gt; {</code> | Begins validation of every existing run and comparison grouping. |
| 20 | <code>    connect();</code> | Installs the real-server fetch adapter. |
| 21 | <code>    const runs = await getRuns();</code> | Reads and validates the full saved run list. |
| 22 | <code>    const overview = await getOverview();</code> | Reads and validates the overview response. |
| 23 | <code>    expect(overview.total_runs).toBe(runs.length);</code> | Requires overview total count to match the returned run-list length. |
| 24 | <code>    expect(runs.length).toBeGreaterThan(0);</code> | Requires the server to contain at least one run; empty evidence is not enough for this integration test. |
| 25 | <code>    for (const run of runs) {</code> | Starts iterating through all returned runs. |
| 26 | <code>      expect((await getRun(run.run_id)).run_id).toBe(run.run_id);</code> | Fetches each summary by ID and requires the response ID to match. |
| 27 | <code>      const series = await getSeries(run.run_id);</code> | Fetches and validates this run's series response. |
| 28 | <code>      expect(Array.isArray(series.predictions)).toBe(true);</code> | Requires predictions to be an array. |
| 29 | <code>      for (const candidate of compatibleRuns(runs, run)) {</code> | Iterates the candidate comparison group returned for this run. |
| 30 | <code>        expect(candidate.source).toBe(run.source);</code> | Requires every candidate to have the same evidence source. |
| 31 | <code>        expect(candidate.mode).toBe(run.mode);</code> | Requires every candidate to use the same execution mode. |
| 32 | <code>        expect(candidate.feature_schema).toBe(run.feature_schema);</code> | Requires every candidate to use the same feature schema. Other compatibility fields are covered in evidence.test.ts. |
| 33 | <code>      }</code> | Closes the current function, interface, or control block begun above. |
| 34 | <code>    }</code> | Closes the current function, interface, or control block begun above. |
| 35 | <code>  }, 20000);</code> | Closes this test and allows 20,000 ms for its multiple HTTP requests. |
| 36 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 37 | <code>  it(&#39;renders a real official run with its timeline and provenance&#39;, async () =&gt; {</code> | Begins rendering an actual completed official-data run. |
| 38 | <code>    connect();</code> | Installs the real-server fetch adapter. |
| 39 | <code>    const runs = await getRuns();</code> | Loads the real saved summaries. |
| 40 | <code>    const official = runs.find(run =&gt; run.source === &#39;official_5g_nidd&#39; &amp;&amp; run.status === &#39;completed&#39; &amp;&amp; run.counts.evaluated &gt; 0);</code> | Finds an official_5g_nidd completed run with at least one evaluated label. |
| 41 | <code>    expect(official).toBeDefined();</code> | Requires such a run to exist before selecting it. |
| 42 | <code>    render(&lt;App /&gt;);</code> | Mounts the real App against the server adapter. |
| 43 | <code>    const select = await screen.findByLabelText(&#39;Selected run&#39;, {}, { timeout: 10000 });</code> | Waits up to 10 seconds for the accessible run selector. |
| 44 | <code>    fireEvent.change(select, { target: { value: official!.run_id } });</code> | Selects the official run; ! is a compile-time non-null assertion after the prior expectation. |
| 45 | <code>    await waitFor(() =&gt; expect(screen.getByText(&#39;Official 5G-NIDD&#39;)).toBeInTheDocument(), { timeout: 10000 });</code> | Retries up to 10 seconds until the official source badge is visible. |
| 46 | <code>    expect(await screen.findByRole(&#39;img&#39;, { name: /Prediction timeline/ })).toBeInTheDocument();</code> | Waits for the accessible prediction-timeline SVG and asserts it exists. |
| 47 | <code>    expect(screen.getByText(&#39;Dataset and feature provenance&#39;)).toBeInTheDocument();</code> | Requires the expandable dataset/feature-provenance panel. |
| 48 | <code>    expect(screen.getAllByText(official!.provenance!.sha256!, { exact: false }).length).toBeGreaterThan(0);</code> | Requires the actual saved SHA-256 to appear somewhere in rendered content; assumes provenance contains it. |
| 49 | <code>    expect(screen.queryByText(&#39;This run is labeled&#39;, { exact: false })).not.toBeInTheDocument();</code> | Checks that an official run is not given the nonofficial-source notice. |
| 50 | <code>  }, 20000);</code> | Closes the official-render test with a 20-second limit. |
| 51 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 52 | <code>  it(&#39;renders actual live collection with a distinct source and no official-data claim&#39;, async () =&gt; {</code> | Begins checking a real live-sFlow run is presented with appropriate provenance. |
| 53 | <code>    connect();</code> | Installs the server adapter. |
| 54 | <code>    const runs = await getRuns();</code> | Loads the real saved run list. |
| 55 | <code>    const live = runs.find(run =&gt; run.source === &#39;live_sflow&#39; &amp;&amp; run.mode === &#39;live_sflow&#39;);</code> | Finds a run whose source and mode both identify live_sflow. |
| 56 | <code>    expect(live).toBeDefined();</code> | Requires such a run to exist. |
| 57 | <code>    render(&lt;App /&gt;);</code> | Mounts the real dashboard. |
| 58 | <code>    const select = await screen.findByLabelText(&#39;Selected run&#39;, {}, { timeout: 10000 });</code> | Waits up to 10 seconds for run selection. |
| 59 | <code>    fireEvent.change(select, { target: { value: live!.run_id } });</code> | Simulates selecting the live run ID. |
| 60 | <code>    await waitFor(() =&gt; expect(screen.getAllByText(&#39;Live telemetry&#39;).length).toBeGreaterThan(0), { timeout: 10000 });</code> | Retries until at least one Live telemetry source label appears. |
| 61 | <code>    expect(screen.getByText(&#39;Live sFlow&#39;)).toBeInTheDocument();</code> | Requires the Live sFlow execution-mode label. |
| 62 | <code>    expect(screen.getByText(/Its results do not establish performance on official/)).toBeInTheDocument();</code> | Requires the warning that this live run does not establish official dataset performance. |
| 63 | <code>    expect(screen.queryByText(&#39;Official 5G-NIDD&#39;)).not.toBeInTheDocument();</code> | Requires no Official 5G-NIDD source label in the selected-run presentation. |
| 64 | <code>  }, 20000);</code> | Closes the live-render test with a 20-second timeout. |
| 65 | <code>});</code> | Closes the current callback/object and its surrounding call. |

## frontend/package.json

Package identity, commands, runtime dependencies, and development tools.

### Complete source

```json
{
  "name": "m3-observatory",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite --host 127.0.0.1",
    "build": "tsc -b && vite build",
    "preview": "vite preview --host 127.0.0.1",
    "test": "vitest run"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@testing-library/react": "^16.1.0",
    "@testing-library/jest-dom": "^6.6.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^4.3.4",
    "jsdom": "^26.0.0",
    "typescript": "^5.7.3",
    "vite": "^6.1.0",
    "vitest": "^3.0.0"
  }
}
```

### Every physical line

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>{</code> | Starts the npm package manifest JSON object. |
| 2 | <code>  &quot;name&quot;: &quot;m3-observatory&quot;,</code> | Names the frontend package m3-observatory. |
| 3 | <code>  &quot;version&quot;: &quot;1.0.0&quot;,</code> | Declares this package's version as 1.0.0. |
| 4 | <code>  &quot;private&quot;: true,</code> | Marks the package private, preventing accidental publication through normal npm publish. |
| 5 | <code>  &quot;type&quot;: &quot;module&quot;,</code> | Uses JavaScript ES-module semantics for package files. |
| 6 | <code>  &quot;scripts&quot;: {</code> | Starts named commands available via npm run. |
| 7 | <code>    &quot;dev&quot;: &quot;vite --host 127.0.0.1&quot;,</code> | Runs Vite's development server bound to local loopback only. |
| 8 | <code>    &quot;build&quot;: &quot;tsc -b &amp;&amp; vite build&quot;,</code> | Runs TypeScript project build/check first and only if it succeeds creates the Vite production bundle; && enforces that dependency. |
| 9 | <code>    &quot;preview&quot;: &quot;vite preview --host 127.0.0.1&quot;,</code> | Serves the existing production bundle locally for preview; it does not itself build the bundle. |
| 10 | <code>    &quot;test&quot;: &quot;vitest run&quot;</code> | Runs Vitest once and exits, rather than watch mode. |
| 11 | <code>  },</code> | Closes scripts. |
| 12 | <code>  &quot;dependencies&quot;: {</code> | Starts runtime library dependencies. |
| 13 | <code>    &quot;react&quot;: &quot;^19.0.0&quot;,</code> | Requests React compatible with major version 19 beginning at 19.0.0; the caret permits compatible newer releases, while the lockfile pins resolution. |
| 14 | <code>    &quot;react-dom&quot;: &quot;^19.0.0&quot;</code> | Requests matching React DOM for browser rendering. |
| 15 | <code>  },</code> | Closes runtime dependencies. |
| 16 | <code>  &quot;devDependencies&quot;: {</code> | Starts tools/type definitions needed during development, builds, and tests. |
| 17 | <code>    &quot;@testing-library/react&quot;: &quot;^16.1.0&quot;,</code> | Adds React Testing Library for DOM-oriented component tests. |
| 18 | <code>    &quot;@testing-library/jest-dom&quot;: &quot;^6.6.0&quot;,</code> | Adds DOM-specific assertion matchers. |
| 19 | <code>    &quot;@types/react&quot;: &quot;^19.0.0&quot;,</code> | Adds TypeScript declarations for React 19. |
| 20 | <code>    &quot;@types/react-dom&quot;: &quot;^19.0.0&quot;,</code> | Adds TypeScript declarations for ReactDOM 19. |
| 21 | <code>    &quot;@vitejs/plugin-react&quot;: &quot;^4.3.4&quot;,</code> | Adds Vite's React plugin for JSX/React development transformations. |
| 22 | <code>    &quot;jsdom&quot;: &quot;^26.0.0&quot;,</code> | Adds jsdom, a simulated DOM used by Vitest instead of a full browser. |
| 23 | <code>    &quot;typescript&quot;: &quot;^5.7.3&quot;,</code> | Adds the TypeScript compiler. |
| 24 | <code>    &quot;vite&quot;: &quot;^6.1.0&quot;,</code> | Adds Vite development/bundling tooling. |
| 25 | <code>    &quot;vitest&quot;: &quot;^3.0.0&quot;</code> | Adds the Vitest test runner. |
| 26 | <code>  }</code> | Closes development dependencies. |
| 27 | <code>}</code> | Closes the package manifest. |

## frontend/tsconfig.json

TypeScript rules for application, tests, and Vite config.

### Complete source

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "Bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "types": ["vitest/globals", "@testing-library/jest-dom"]
  },
  "include": ["src", "vite.config.ts"]
}
```

### Every physical line

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>{</code> | Starts the TypeScript configuration object. |
| 2 | <code>  &quot;compilerOptions&quot;: {</code> | Starts compiler options. |
| 3 | <code>    &quot;target&quot;: &quot;ES2022&quot;,</code> | Targets ES2022 language semantics for compilation/checking. |
| 4 | <code>    &quot;useDefineForClassFields&quot;: true,</code> | Uses standard define semantics for class-field initialization. |
| 5 | <code>    &quot;lib&quot;: [&quot;ES2022&quot;, &quot;DOM&quot;, &quot;DOM.Iterable&quot;],</code> | Makes ES2022 and browser DOM/iterable APIs available to the type checker. |
| 6 | <code>    &quot;module&quot;: &quot;ESNext&quot;,</code> | Preserves modern ES-module syntax for Vite to bundle. |
| 7 | <code>    &quot;skipLibCheck&quot;: true,</code> | Skips full checking of declaration-file internals to reduce build work; application code is still checked. |
| 8 | <code>    &quot;moduleResolution&quot;: &quot;Bundler&quot;,</code> | Resolves imports using bundler-oriented rules appropriate for Vite. |
| 9 | <code>    &quot;allowImportingTsExtensions&quot;: true,</code> | Allows imports whose paths end in TypeScript extensions when used with this nonemitting configuration. |
| 10 | <code>    &quot;resolveJsonModule&quot;: true,</code> | Allows importing JSON modules with inferred types. |
| 11 | <code>    &quot;isolatedModules&quot;: true,</code> | Requires source to be compatible with compiling files independently, matching Vite's transform model. |
| 12 | <code>    &quot;noEmit&quot;: true,</code> | Makes TypeScript check without emitting JavaScript; Vite performs actual production code generation. |
| 13 | <code>    &quot;jsx&quot;: &quot;react-jsx&quot;,</code> | Uses React's automatic JSX runtime, so JSX files do not need a React default import just for JSX. |
| 14 | <code>    &quot;strict&quot;: true,</code> | Enables strict type checking, including strict null handling and implicit-any checks. |
| 15 | <code>    &quot;types&quot;: [&quot;vitest/globals&quot;, &quot;@testing-library/jest-dom&quot;]</code> | Includes Vitest globals and jest-dom matcher type declarations. |
| 16 | <code>  },</code> | Closes compiler options. |
| 17 | <code>  &quot;include&quot;: [&quot;src&quot;, &quot;vite.config.ts&quot;]</code> | Includes src and the Vite configuration in the TypeScript project. |
| 18 | <code>}</code> | Closes the TypeScript configuration. |

## frontend/vite.config.ts

Development proxy, React plugin, and test runtime settings.

### Complete source

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy: { '/api': 'http://127.0.0.1:8000' } },
  test: { environment: 'jsdom', setupFiles: ['./src/test-setup.ts'], restoreMocks: true },
});
```

### Every physical line

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>import { defineConfig } from &#39;vitest/config&#39;;</code> | Imports typed configuration helpers from Vitest, allowing both Vite and test settings in this config. |
| 2 | <code>import react from &#39;@vitejs/plugin-react&#39;;</code> | Imports the React integration plugin. |
| 3 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 4 | <code>export default defineConfig({</code> | Exports the tool configuration through defineConfig for type support. |
| 5 | <code>  plugins: [react()],</code> | Enables React transformations and development integration. |
| 6 | <code>  server: { port: 5173, proxy: { &#39;/api&#39;: &#39;http://127.0.0.1:8000&#39; } },</code> | Uses development port 5173 and proxies relative /api requests to the local FastAPI server on 8000; this proxy setting concerns the development server. |
| 7 | <code>  test: { environment: &#39;jsdom&#39;, setupFiles: [&#39;./src/test-setup.ts&#39;], restoreMocks: true },</code> | Runs tests in jsdom, loads shared matcher/cleanup setup, and restores mock implementations/spies after tests. |
| 8 | <code>});</code> | Closes and exports the configuration object. |

## frontend/README.md

Human setup instructions and evidence interpretation summary.

### Complete source

````markdown
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
````

### Every physical line

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code># M3 Observatory</code> | Markdown title identifying the frontend application. |
| 2 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 3 | <code>React + TypeScript dashboard for the M3 FastAPI experiment server. It reads saved evidence and polls every three seconds. The application contains no demonstration data or fabricated experiment values.</code> | Summarizes the real application: React/TypeScript reads FastAPI evidence every three seconds without runtime fake runs. |
| 4 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 5 | <code>## Run</code> | Starts developer run instructions. |
| 6 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 7 | <code>```sh</code> | Opens a shell-command code fence; Markdown formatting only. |
| 8 | <code>npm install</code> | Documents installation of frontend dependencies. |
| 9 | <code>npm run dev</code> | Documents starting the local development server. |
| 10 | <code>```</code> | Closes that command fence. |
| 11 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 12 | <code>Open http://127.0.0.1:5173 with the FastAPI server on http://127.0.0.1:8000. Vite proxies `/api` to the backend. For a packaged deployment, serve `dist/` from FastAPI or configure the reverse proxy to route `/api` to that server.</code> | Documents frontend/backend addresses, development API proxy, and the need to serve dist and route /api appropriately in a packaged deployment. |
| 13 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 14 | <code>```sh</code> | Opens a second shell-command fence. |
| 15 | <code>npm test</code> | Documents running frontend tests. |
| 16 | <code>npm run build</code> | Documents type checking and production bundling through the build script. |
| 17 | <code>```</code> | Closes that command fence. |
| 18 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 19 | <code>Optional read-only integration checks against a running API with official CSV and live collector results:</code> | Introduces optional real-server integration testing; these tests require existing official CSV and live collector runs. |
| 20 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 21 | <code>```powershell</code> | Opens a PowerShell command fence. |
| 22 | <code>$env:M3_API_URL = &#39;http://127.0.0.1:8000&#39;</code> | Documents setting the M3_API_URL environment variable so the optional integration suite is enabled. |
| 23 | <code>npm test -- --run src/integration.test.tsx</code> | Documents executing the integration-test file using the npm test script and forwarded runner arguments. |
| 24 | <code>```</code> | Closes the PowerShell fence. |
| 25 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 26 | <code>These checks read existing experiments and never create runs or write synthetic evidence.</code> | States the read-only nature of integration tests; execution writes no synthetic results. |
| 27 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 28 | <code>## Evidence interpretation</code> | Starts explanation of evidence interpretation. |
| 29 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 30 | <code>- Source and execution mode appear on every selected experiment.</code> | Requires source and mode labels in selected experiment presentation; implemented by the App badges. |
| 31 | <code>- Unavailable measurements display their reason, never a replacement zero.</code> | Describes unavailable-metric reason display and preservation of meaningful measured zero. |
| 32 | <code>- Comparison is restricted to completed runs matching source, mode, scenario, observation unit, feature schema, dataset checksum, and model/window/warm-up/record-limit settings.</code> | Summarizes the compatibility-grouping rules implemented in compatibleRuns. |
| 33 | <code>- Each comparison row is an individual trial. The Pareto plot uses measured F1 and measured overhead only; it does not automatically select a knee point.</code> | Explains each row is an individual trial and measured Pareto points do not automatically establish a knee. |
| 34 | <code>- Timelines request up to 1,000 predictions and show the returned series without inventing missing observations.</code> | Explains the limited series request and no fabricated interpolation of missing observations. |
| 35 | <code>- Live runs and saved runs share the same read-only result contract. Execution is controlled by the experiment runner.</code> | States the dashboard reads a common result contract while the separate experiment runner controls execution. |
| 36 | <em>blank</em> | Blank line separates logical sections; no runtime effect. |
| 37 | <code>Synthetic fixtures exist exclusively in tests.</code> | Explains the synthetic fixture boundary: test code only. |

## Compressed CSS expanded into rules and declarations

CSS lines 3–9 contain many adjacent rules. A selector space means descendant, > means direct child, .name matches a class, and :hover/:focus-visible select interaction states. Comma-separated selectors share declarations. Later matching rules can override earlier ones. px is a CSS pixel, rem is root-font-relative, vw is viewport-width-relative, % depends on its context, and fr divides grid space. Eight-digit hex colors include opacity in the final two digits.

Every declaration below is reproduced in source order. var(--name) reuses a theme variable. These rules control appearance and do not alter the learning model.

### :root

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-family: 'DM Sans',system-ui,-apple-system,sans-serif` | Chooses font families in priority/fallback order: `'DM Sans',system-ui,-apple-system,sans-serif`. |
| `color: #203648` | Sets foreground text color; var(...) reuses the named root variable: `#203648`. |
| `background: #f4f7f8` | Sets the element background (a color here): `#f4f7f8`. |
| `font-synthesis: none` | Prevents browser-generated fake bold/italic where none is specified: `none`. |
| `text-rendering: optimizeLegibility` | Suggests text rendering quality/legibility choices to the browser: `optimizeLegibility`. |
| `font-size: 14px` | Sets text size; clamp(...) bounds a responsive size: `14px`. |
| `--navy: #102b3d` | Defines reusable theme variable --navy: `#102b3d`. |
| `--muted: #607787` | Defines reusable theme variable --muted: `#607787`. |
| `--teal: #087e82` | Defines reusable theme variable --teal: `#087e82`. |
| `--line: #dfE7eb` | Defines reusable theme variable --line: `#dfE7eb`. |
| `--orange: #dc8032` | Defines reusable theme variable --orange: `#dc8032`. |

### *

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `box-sizing: border-box` | Includes padding and border in declared widths/heights when border-box: `border-box`. |

### body

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `margin: 0` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `0`. |

### button,input,select

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font: inherit` | Inherits surrounding font settings into form controls: `inherit`. |

### button,select

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `cursor: pointer` | Chooses the pointer shape for interaction feedback: `pointer`. |

### button:disabled

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `cursor: default` | Chooses the pointer shape for interaction feedback: `default`. |

### a

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `color: var(--teal)` | Sets foreground text color; var(...) reuses the named root variable: `var(--teal)`. |

### button:focus-visible,select:focus-visible,input:focus-visible,summary:focus-visible,a:focus-visible

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `outline: 3px solid #e69745` | Adds a visible keyboard-focus outline that does not affect layout: `3px solid #e69745`. |
| `outline-offset: 4px` | Separates the focus outline from the element border: `4px`. |

### button

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `transition: background .15s` | Smooths changes to selected properties over time; none disables transitions: `background .15s`. |

### h1,h2,h3,p

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `margin: 0` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `0`. |

### h1,h2,h3

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-family: 'Manrope',system-ui,sans-serif` | Chooses font families in priority/fallback order: `'Manrope',system-ui,sans-serif`. |

### h2

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 19px` | Sets text size; clamp(...) bounds a responsive size: `19px`. |
| `letter-spacing: -.6px` | Adjusts spacing between letters; negative values tighten: `-.6px`. |

### h3

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 16px` | Sets text size; clamp(...) bounds a responsive size: `16px`. |

### p

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `line-height: 1.6` | Sets line spacing; unitless values multiply font size: `1.6`. |

### .topbar

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `height: 76px` | Sets element height: `76px`. |
| `background: #102334` | Sets the element background (a color here): `#102334`. |
| `color: #fff` | Sets foreground text color; var(...) reuses the named root variable: `#fff`. |
| `padding: 0 max(4vw,24px)` | Sets inner spacing in top/right/bottom/left shorthand: `0 max(4vw,24px)`. |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `align-items: center` | Aligns flex/grid children on the cross axis: `center`. |
| `gap: 34px` | Sets space between flex/grid children; two values mean row gap then column gap: `34px`. |
| `border-bottom: 1px solid #254356` | Sets only the bottom border: `1px solid #254356`. |

### .brand

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `align-items: center` | Aligns flex/grid children on the cross axis: `center`. |
| `gap: 12px` | Sets space between flex/grid children; two values mean row gap then column gap: `12px`. |
| `font-family: 'Manrope',sans-serif` | Chooses font families in priority/fallback order: `'Manrope',sans-serif`. |
| `font-size: 23px` | Sets text size; clamp(...) bounds a responsive size: `23px`. |
| `font-weight: 800` | Sets text weight: larger numbers are heavier: `800`. |
| `letter-spacing: -1px` | Adjusts spacing between letters; negative values tighten: `-1px`. |

### .brand-light

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-weight: 500` | Sets text weight: larger numbers are heavier: `500`. |
| `letter-spacing: -.7px` | Adjusts spacing between letters; negative values tighten: `-.7px`. |

### .brand-divider

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `color: #708b9b` | Sets foreground text color; var(...) reuses the named root variable: `#708b9b`. |
| `padding: 0 5px` | Sets inner spacing in top/right/bottom/left shorthand: `0 5px`. |

### .brand-icon

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `height: 29px` | Sets element height: `29px`. |
| `width: 29px` | Sets element width: `29px`. |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `gap: 4px` | Sets space between flex/grid children; two values mean row gap then column gap: `4px`. |
| `align-items: flex-end` | Aligns flex/grid children on the cross axis: `flex-end`. |

### .brand-icon i

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: block` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `block`. |
| `width: 6px` | Sets element width: `6px`. |
| `background: #66d2c7` | Sets the element background (a color here): `#66d2c7`. |
| `border-radius: 2px` | Rounds corners: `2px`. |

### .brand-icon i:nth-child(1)

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `height: 12px` | Sets element height: `12px`. |

### .brand-icon i:nth-child(2)

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `height: 22px` | Sets element height: `22px`. |

### .brand-icon i:nth-child(3)

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `height: 29px` | Sets element height: `29px`. |

### .topbar-subtitle

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `color: #a9bdca` | Sets foreground text color; var(...) reuses the named root variable: `#a9bdca`. |
| `letter-spacing: 2px` | Adjusts spacing between letters; negative values tighten: `2px`. |
| `padding-left: 30px` | Sets inner spacing on the left: `30px`. |
| `border-left: 1px solid #345060` | Sets only the left border: `1px solid #345060`. |

### .project-tag

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `margin-left: auto` | Sets outer spacing to the left; auto pushes the item toward the right in a row: `auto`. |
| `border: 1px solid #3c5869` | Sets all four border widths, styles, and colors together: `1px solid #3c5869`. |
| `border-radius: 5px` | Rounds corners: `5px`. |
| `padding: 7px 12px` | Sets inner spacing in top/right/bottom/left shorthand: `7px 12px`. |
| `font-size: 11px` | Sets text size; clamp(...) bounds a responsive size: `11px`. |
| `letter-spacing: .8px` | Adjusts spacing between letters; negative values tighten: `.8px`. |
| `color: #c9d9e1` | Sets foreground text color; var(...) reuses the named root variable: `#c9d9e1`. |

### main

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `max-width: 1390px` | Caps element width: `1390px`. |
| `margin: auto` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `auto`. |
| `padding: 40px max(3.8vw,24px) 0` | Sets inner spacing in top/right/bottom/left shorthand: `40px max(3.8vw,24px) 0`. |

### .page-heading

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `align-items: center` | Aligns flex/grid children on the cross axis: `center`. |
| `justify-content: space-between` | Distributes flex/grid children on the main axis: `space-between`. |
| `gap: 24px` | Sets space between flex/grid children; two values mean row gap then column gap: `24px`. |

### .eyebrow

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `font-weight: 700` | Sets text weight: larger numbers are heavier: `700`. |
| `letter-spacing: 1.7px` | Adjusts spacing between letters; negative values tighten: `1.7px`. |
| `color: var(--teal)` | Sets foreground text color; var(...) reuses the named root variable: `var(--teal)`. |
| `margin-bottom: 10px` | Sets outer spacing below the element: `10px`. |

### .eyebrow>span

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `color: #8699a5` | Sets foreground text color; var(...) reuses the named root variable: `#8699a5`. |
| `margin-left: 13px` | Sets outer spacing to the left; auto pushes the item toward the right in a row: `13px`. |

### h1

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: clamp(27px,2.5vw,36px)` | Sets text size; clamp(...) bounds a responsive size: `clamp(27px,2.5vw,36px)`. |
| `font-weight: 800` | Sets text weight: larger numbers are heavier: `800`. |
| `letter-spacing: -1.5px` | Adjusts spacing between letters; negative values tighten: `-1.5px`. |
| `line-height: 1.3` | Sets line spacing; unitless values multiply font size: `1.3`. |
| `color: var(--navy)` | Sets foreground text color; var(...) reuses the named root variable: `var(--navy)`. |

### h1>span

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-weight: 500` | Sets text weight: larger numbers are heavier: `500`. |
| `color: #577181` | Sets foreground text color; var(...) reuses the named root variable: `#577181`. |

### .page-heading p

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `margin-top: 9px` | Sets outer spacing above the element: `9px`. |
| `color: var(--muted)` | Sets foreground text color; var(...) reuses the named root variable: `var(--muted)`. |
| `font-size: 14px` | Sets text size; clamp(...) bounds a responsive size: `14px`. |

### .refresh-tools

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `align-items: center` | Aligns flex/grid children on the cross axis: `center`. |
| `gap: 18px` | Sets space between flex/grid children; two values mean row gap then column gap: `18px`. |

### .refresh-toggle

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `align-items: center` | Aligns flex/grid children on the cross axis: `center`. |
| `gap: 7px` | Sets space between flex/grid children; two values mean row gap then column gap: `7px`. |
| `font-size: 12px` | Sets text size; clamp(...) bounds a responsive size: `12px`. |
| `color: var(--muted)` | Sets foreground text color; var(...) reuses the named root variable: `var(--muted)`. |
| `white-space: nowrap` | Controls wrapping/space handling; nowrap keeps text on one line, normal allows wrapping: `nowrap`. |

### .refresh-toggle input

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `accent-color: var(--teal)` | Sets the native checkbox/control accent: `var(--teal)`. |
| `width: 15px` | Sets element width: `15px`. |
| `height: 15px` | Sets element height: `15px`. |

### .button

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `align-items: center` | Aligns flex/grid children on the cross axis: `center`. |
| `gap: 8px` | Sets space between flex/grid children; two values mean row gap then column gap: `8px`. |
| `background: #fff` | Sets the element background (a color here): `#fff`. |
| `border: 1px solid #cfdbE1` | Sets all four border widths, styles, and colors together: `1px solid #cfdbE1`. |
| `border-radius: 6px` | Rounds corners: `6px`. |
| `padding: 9px 14px` | Sets inner spacing in top/right/bottom/left shorthand: `9px 14px`. |
| `color: #294c5e` | Sets foreground text color; var(...) reuses the named root variable: `#294c5e`. |
| `font-weight: 600` | Sets text weight: larger numbers are heavier: `600`. |

### .button:hover

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: #eaf3f4` | Sets the element background (a color here): `#eaf3f4`. |

### .button span

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 20px` | Sets text size; clamp(...) bounds a responsive size: `20px`. |
| `line-height: 20px` | Sets line spacing; unitless values multiply font size: `20px`. |

### .connection-line

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `align-items: center` | Aligns flex/grid children on the cross axis: `center`. |
| `gap: 7px` | Sets space between flex/grid children; two values mean row gap then column gap: `7px`. |
| `color: #718590` | Sets foreground text color; var(...) reuses the named root variable: `#718590`. |
| `font-size: 11px` | Sets text size; clamp(...) bounds a responsive size: `11px`. |
| `margin: 23px 0 16px` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `23px 0 16px`. |
| `min-height: 16px` | Sets the minimum vertical space reserved by an element: `16px`. |

### .connection-dot

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `height: 6px` | Sets element height: `6px`. |
| `width: 6px` | Sets element width: `6px`. |
| `border-radius: 50%` | Rounds corners: `50%`. |
| `background: #b8c7cd` | Sets the element background (a color here): `#b8c7cd`. |

### .connection-dot.online

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: #078e77` | Sets the element background (a color here): `#078e77`. |
| `box-shadow: 0 0 0 3px #078e7712` | Adds an outer/inset visual shadow or ring without changing layout dimensions: `0 0 0 3px #078e7712`. |

### .connection-dot.offline

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: #c66a45` | Sets the element background (a color here): `#c66a45`. |

### .paused-label

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `margin-left: 8px` | Sets outer spacing to the left; auto pushes the item toward the right in a row: `8px`. |
| `color: #9a5a25` | Sets foreground text color; var(...) reuses the named root variable: `#9a5a25`. |

### .overview-strip

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `background: #fff` | Sets the element background (a color here): `#fff`. |
| `border: 1px solid var(--line)` | Sets all four border widths, styles, and colors together: `1px solid var(--line)`. |
| `border-radius: 9px` | Rounds corners: `9px`. |
| `padding: 22px 25px` | Sets inner spacing in top/right/bottom/left shorthand: `22px 25px`. |
| `margin-bottom: 24px` | Sets outer spacing below the element: `24px`. |
| `box-shadow: 0 2px 4px #10233403` | Adds an outer/inset visual shadow or ring without changing layout dimensions: `0 2px 4px #10233403`. |

### .overview-strip>div

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `min-width: 130px` | Sets minimum width; zero permits flex/grid items to shrink below content width: `130px`. |
| `padding-right: 28px` | Sets inner spacing on the right: `28px`. |
| `margin-right: 28px` | Sets outer spacing to the right: `28px`. |
| `border-right: 1px solid var(--line)` | Sets only the right border: `1px solid var(--line)`. |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `flex-direction: column` | Chooses row or column arrangement of flex children: `column`. |
| `gap: 7px` | Sets space between flex/grid children; two values mean row gap then column gap: `7px`. |

### .overview-strip span

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 11px` | Sets text size; clamp(...) bounds a responsive size: `11px`. |
| `color: #788b96` | Sets foreground text color; var(...) reuses the named root variable: `#788b96`. |

### .overview-strip strong

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 24px` | Sets text size; clamp(...) bounds a responsive size: `24px`. |
| `font-family: 'Manrope',sans-serif` | Chooses font families in priority/fallback order: `'Manrope',sans-serif`. |
| `color: var(--navy)` | Sets foreground text color; var(...) reuses the named root variable: `var(--navy)`. |

### .overview-strip>.overview-description

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `margin: 0` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `0`. |
| `padding: 0` | Sets inner spacing in top/right/bottom/left shorthand: `0`. |
| `min-width: 0` | Sets minimum width; zero permits flex/grid items to shrink below content width: `0`. |
| `border: none` | Sets all four border widths, styles, and colors together: `none`. |
| `margin-left: auto` | Sets outer spacing to the left; auto pushes the item toward the right in a row: `auto`. |
| `justify-content: center` | Distributes flex/grid children on the main axis: `center`. |

### .overview-description>span

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 9px` | Sets text size; clamp(...) bounds a responsive size: `9px`. |
| `letter-spacing: 1.5px` | Adjusts spacing between letters; negative values tighten: `1.5px`. |

### .overview-description strong

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 13px` | Sets text size; clamp(...) bounds a responsive size: `13px`. |
| `line-height: 1.5` | Sets line spacing; unitless values multiply font size: `1.5`. |

### .overview-description strong span

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: block` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `block`. |
| `font-size: 12px` | Sets text size; clamp(...) bounds a responsive size: `12px`. |
| `color: var(--teal)` | Sets foreground text color; var(...) reuses the named root variable: `var(--teal)`. |
| `font-weight: 500` | Sets text weight: larger numbers are heavier: `500`. |

### .error-banner

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `border: 1px solid #ecc9bd` | Sets all four border widths, styles, and colors together: `1px solid #ecc9bd`. |
| `border-left: 3px solid #bf5135` | Sets only the left border: `3px solid #bf5135`. |
| `background: #fff4ef` | Sets the element background (a color here): `#fff4ef`. |
| `color: #893f2a` | Sets foreground text color; var(...) reuses the named root variable: `#893f2a`. |
| `border-radius: 6px` | Rounds corners: `6px`. |
| `padding: 14px 18px` | Sets inner spacing in top/right/bottom/left shorthand: `14px 18px`. |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `flex-direction: column` | Chooses row or column arrangement of flex children: `column`. |
| `gap: 5px` | Sets space between flex/grid children; two values mean row gap then column gap: `5px`. |
| `margin-bottom: 20px` | Sets outer spacing below the element: `20px`. |
| `font-size: 12px` | Sets text size; clamp(...) bounds a responsive size: `12px`. |

### .error-banner strong

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 13px` | Sets text size; clamp(...) bounds a responsive size: `13px`. |

### .state-panel

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `min-height: 360px` | Sets the minimum vertical space reserved by an element: `360px`. |
| `background: #fff` | Sets the element background (a color here): `#fff`. |
| `border: 1px solid var(--line)` | Sets all four border widths, styles, and colors together: `1px solid var(--line)`. |
| `border-radius: 10px` | Rounds corners: `10px`. |
| `text-align: center` | Aligns inline text inside its box: `center`. |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `align-items: center` | Aligns flex/grid children on the cross axis: `center`. |
| `justify-content: center` | Distributes flex/grid children on the main axis: `center`. |
| `flex-direction: column` | Chooses row or column arrangement of flex children: `column`. |
| `padding: 45px` | Sets inner spacing in top/right/bottom/left shorthand: `45px`. |
| `gap: 15px` | Sets space between flex/grid children; two values mean row gap then column gap: `15px`. |

### .state-panel p

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `color: var(--muted)` | Sets foreground text color; var(...) reuses the named root variable: `var(--muted)`. |
| `max-width: 540px` | Caps element width: `540px`. |

### .state-panel h2

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 24px` | Sets text size; clamp(...) bounds a responsive size: `24px`. |

### .state-panel.small

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `min-height: 180px` | Sets the minimum vertical space reserved by an element: `180px`. |

### .empty-icon

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `border: 1px solid #d8e9ea` | Sets all four border widths, styles, and colors together: `1px solid #d8e9ea`. |
| `background: #edf7f6` | Sets the element background (a color here): `#edf7f6`. |
| `height: 66px` | Sets element height: `66px`. |
| `width: 66px` | Sets element width: `66px`. |
| `border-radius: 17px` | Rounds corners: `17px`. |
| `color: var(--teal)` | Sets foreground text color; var(...) reuses the named root variable: `var(--teal)`. |
| `font-size: 48px` | Sets text size; clamp(...) bounds a responsive size: `48px`. |
| `line-height: 60px` | Sets line spacing; unitless values multiply font size: `60px`. |
| `margin-bottom: 6px` | Sets outer spacing below the element: `6px`. |

### .empty-steps

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `gap: 30px` | Sets space between flex/grid children; two values mean row gap then column gap: `30px`. |
| `color: #718b99` | Sets foreground text color; var(...) reuses the named root variable: `#718b99`. |
| `font-size: 11px` | Sets text size; clamp(...) bounds a responsive size: `11px`. |
| `margin-top: 20px` | Sets outer spacing above the element: `20px`. |

### .state-panel .eyebrow

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `margin: 0` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `0`. |

### .loader

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `height: 28px` | Sets element height: `28px`. |
| `width: 28px` | Sets element width: `28px`. |
| `border: 2px solid #d8e6e8` | Sets all four border widths, styles, and colors together: `2px solid #d8e6e8`. |
| `border-top-color: var(--teal)` | Changes only the top edge color, used for the spinning loader segment: `var(--teal)`. |
| `border-radius: 50%` | Rounds corners: `50%`. |
| `animation: spin 1s linear infinite` | Sets animation name, duration, easing, and repetition; none disables it: `spin 1s linear infinite`. |

### @keyframes spin

Defines animation steps; to is the completed animation state.

### to

Context: @keyframes spin.

| Declaration | Effect |
| --- | --- |
| `transform: rotate(360deg)` | Applies a visual transformation; rotate(360deg) completes one loader rotation: `rotate(360deg)`. |

### .run-toolbar

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `align-items: center` | Aligns flex/grid children on the cross axis: `center`. |
| `gap: 24px` | Sets space between flex/grid children; two values mean row gap then column gap: `24px`. |
| `margin: 24px 0 18px` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `24px 0 18px`. |

### .run-label

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `min-width: 150px` | Sets minimum width; zero permits flex/grid items to shrink below content width: `150px`. |

### .run-label .eyebrow

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 9px` | Sets text size; clamp(...) bounds a responsive size: `9px`. |
| `margin-bottom: 5px` | Sets outer spacing below the element: `5px`. |

### .run-label label

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-weight: 600` | Sets text weight: larger numbers are heavier: `600`. |
| `font-size: 13px` | Sets text size; clamp(...) bounds a responsive size: `13px`. |

### .run-toolbar select

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `min-width: 0` | Sets minimum width; zero permits flex/grid items to shrink below content width: `0`. |
| `flex: 1` | Sets flex growth/shrink/basis; 1 lets an item share remaining space: `1`. |
| `max-width: 720px` | Caps element width: `720px`. |
| `background: #fff` | Sets the element background (a color here): `#fff`. |
| `border: 1px solid #cbdbe2` | Sets all four border widths, styles, and colors together: `1px solid #cbdbe2`. |
| `border-radius: 6px` | Rounds corners: `6px`. |
| `padding: 12px` | Sets inner spacing in top/right/bottom/left shorthand: `12px`. |
| `color: #29495b` | Sets foreground text color; var(...) reuses the named root variable: `#29495b`. |

### .selection-count

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `margin-left: auto` | Sets outer spacing to the left; auto pushes the item toward the right in a row: `auto`. |
| `font-size: 11px` | Sets text size; clamp(...) bounds a responsive size: `11px`. |
| `color: var(--muted)` | Sets foreground text color; var(...) reuses the named root variable: `var(--muted)`. |
| `white-space: nowrap` | Controls wrapping/space handling; nowrap keeps text on one line, normal allows wrapping: `nowrap`. |

### .run-context

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: var(--navy)` | Sets the element background (a color here): `var(--navy)`. |
| `color: #fff` | Sets foreground text color; var(...) reuses the named root variable: `#fff`. |
| `border-radius: 9px` | Rounds corners: `9px`. |
| `overflow: hidden` | Sets oversized-content behavior; auto enables scrolling when needed, hidden clips, visible lets it extend: `hidden`. |

### .run-context-head

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `padding: 23px 26px` | Sets inner spacing in top/right/bottom/left shorthand: `23px 26px`. |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `justify-content: space-between` | Distributes flex/grid children on the main axis: `space-between`. |
| `gap: 24px` | Sets space between flex/grid children; two values mean row gap then column gap: `24px`. |

### .run-context h2

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `text-transform: capitalize` | Transforms displayed capitalization while preserving source text: `capitalize`. |
| `font-size: 23px` | Sets text size; clamp(...) bounds a responsive size: `23px`. |
| `margin-top: 12px` | Sets outer spacing above the element: `12px`. |
| `font-weight: 600` | Sets text weight: larger numbers are heavier: `600`. |
| `letter-spacing: -.5px` | Adjusts spacing between letters; negative values tighten: `-.5px`. |

### .badge

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: inline-block` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `inline-block`. |
| `border: 1px solid #dde5ea` | Sets all four border widths, styles, and colors together: `1px solid #dde5ea`. |
| `background: #f5f8fa` | Sets the element background (a color here): `#f5f8fa`. |
| `color: #56717f` | Sets foreground text color; var(...) reuses the named root variable: `#56717f`. |
| `border-radius: 4px` | Rounds corners: `4px`. |
| `padding: 4px 8px` | Sets inner spacing in top/right/bottom/left shorthand: `4px 8px`. |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `font-weight: 600` | Sets text weight: larger numbers are heavier: `600`. |
| `line-height: 1.2` | Sets line spacing; unitless values multiply font size: `1.2`. |
| `white-space: nowrap` | Controls wrapping/space handling; nowrap keeps text on one line, normal allows wrapping: `nowrap`. |

### .run-context .badge

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: #254455` | Sets the element background (a color here): `#254455`. |
| `border-color: #395567` | Overrides border colors without changing their widths/styles: `#395567`. |
| `color: #cedee5` | Sets foreground text color; var(...) reuses the named root variable: `#cedee5`. |
| `margin-right: 7px` | Sets outer spacing to the right: `7px`. |

### .badge.completed,.run-context .badge.completed

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: #e8f6ef` | Sets the element background (a color here): `#e8f6ef`. |
| `border-color: #c8e9d8` | Overrides border colors without changing their widths/styles: `#c8e9d8`. |
| `color: #256953` | Sets foreground text color; var(...) reuses the named root variable: `#256953`. |

### .badge.running,.run-context .badge.running

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: #dff6f5` | Sets the element background (a color here): `#dff6f5`. |
| `border-color: #aee4e3` | Overrides border colors without changing their widths/styles: `#aee4e3`. |
| `color: #067a7d` | Sets foreground text color; var(...) reuses the named root variable: `#067a7d`. |

### .badge.failed,.run-context .badge.failed

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: #fff0e9` | Sets the element background (a color here): `#fff0e9`. |
| `border-color: #edcbbd` | Overrides border colors without changing their widths/styles: `#edcbbd`. |
| `color: #b7512b` | Sets foreground text color; var(...) reuses the named root variable: `#b7512b`. |

### .run-context .badge.source

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: #27495e` | Sets the element background (a color here): `#27495e`. |
| `color: #c2e6f1` | Sets foreground text color; var(...) reuses the named root variable: `#c2e6f1`. |

### .run-context .badge.fixture

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: #fff0d6` | Sets the element background (a color here): `#fff0d6`. |
| `border-color: #e5bd70` | Overrides border colors without changing their widths/styles: `#e5bd70`. |
| `color: #845721` | Sets foreground text color; var(...) reuses the named root variable: `#845721`. |

### .sampling-emblem

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `text-align: right` | Aligns inline text inside its box: `right`. |
| `min-width: 120px` | Sets minimum width; zero permits flex/grid items to shrink below content width: `120px`. |

### .sampling-emblem>span

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: block` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `block`. |
| `font-size: 9px` | Sets text size; clamp(...) bounds a responsive size: `9px`. |
| `letter-spacing: 1.5px` | Adjusts spacing between letters; negative values tighten: `1.5px`. |
| `color: #9fb8c4` | Sets foreground text color; var(...) reuses the named root variable: `#9fb8c4`. |

### .sampling-emblem strong

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 34px` | Sets text size; clamp(...) bounds a responsive size: `34px`. |
| `font-family: 'Manrope',sans-serif` | Chooses font families in priority/fallback order: `'Manrope',sans-serif`. |
| `font-weight: 700` | Sets text weight: larger numbers are heavier: `700`. |

### .sampling-emblem strong span

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 26px` | Sets text size; clamp(...) bounds a responsive size: `26px`. |
| `font-weight: 400` | Sets text weight: larger numbers are heavier: `400`. |
| `color: #6e99ab` | Sets foreground text color; var(...) reuses the named root variable: `#6e99ab`. |

### .context-bottom

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `border-top: 1px solid #365162` | Sets only the top border: `1px solid #365162`. |
| `padding: 12px 26px` | Sets inner spacing in top/right/bottom/left shorthand: `12px 26px`. |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `gap: 23px` | Sets space between flex/grid children; two values mean row gap then column gap: `23px`. |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `color: #a7c0cd` | Sets foreground text color; var(...) reuses the named root variable: `#a7c0cd`. |
| `flex-wrap: wrap` | Allows flex children to continue onto another line: `wrap`. |

### .context-bottom strong

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-weight: 500` | Sets text weight: larger numbers are heavier: `500`. |
| `color: #d5e4eb` | Sets foreground text color; var(...) reuses the named root variable: `#d5e4eb`. |

### .context-bottom code

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `color: #d4e4eb` | Sets foreground text color; var(...) reuses the named root variable: `#d4e4eb`. |
| `word-break: break-all` | Allows long run identifiers to break anywhere with break-all: `break-all`. |

### .notice

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: #eaf2f4` | Sets the element background (a color here): `#eaf2f4`. |
| `border: 1px solid #d4e4e9` | Sets all four border widths, styles, and colors together: `1px solid #d4e4e9`. |
| `color: #50717e` | Sets foreground text color; var(...) reuses the named root variable: `#50717e`. |
| `padding: 11px 17px` | Sets inner spacing in top/right/bottom/left shorthand: `11px 17px`. |
| `border-radius: 6px` | Rounds corners: `6px`. |
| `margin: 14px 0` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `14px 0`. |
| `font-size: 11px` | Sets text size; clamp(...) bounds a responsive size: `11px`. |
| `line-height: 1.6` | Sets line spacing; unitless values multiply font size: `1.6`. |

### .metric-grid

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: grid` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `grid`. |
| `grid-template-columns: repeat(4,1fr)` | Defines grid column sizes; fr divides available space proportionally: `repeat(4,1fr)`. |
| `gap: 16px` | Sets space between flex/grid children; two values mean row gap then column gap: `16px`. |
| `margin: 22px 0` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `22px 0`. |

### .metric-card

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `padding: 20px 23px` | Sets inner spacing in top/right/bottom/left shorthand: `20px 23px`. |
| `background: #fff` | Sets the element background (a color here): `#fff`. |
| `border: 1px solid var(--line)` | Sets all four border widths, styles, and colors together: `1px solid var(--line)`. |
| `border-radius: 8px` | Rounds corners: `8px`. |
| `position: relative` | Chooses normal/relative/absolute positioning; absolute offsets are relative to an appropriate containing ancestor: `relative`. |
| `min-width: 0` | Sets minimum width; zero permits flex/grid items to shrink below content width: `0`. |
| `box-shadow: 0 2px 3px #10233403` | Adds an outer/inset visual shadow or ring without changing layout dimensions: `0 2px 3px #10233403`. |

### .metric-label

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 12px` | Sets text size; clamp(...) bounds a responsive size: `12px`. |
| `color: #536d7d` | Sets foreground text color; var(...) reuses the named root variable: `#536d7d`. |
| `font-weight: 500` | Sets text weight: larger numbers are heavier: `500`. |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `justify-content: space-between` | Distributes flex/grid children on the main axis: `space-between`. |
| `align-items: center` | Aligns flex/grid children on the cross axis: `center`. |

### .metric-symbol

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `color: #acc1c9` | Sets foreground text color; var(...) reuses the named root variable: `#acc1c9`. |
| `font-size: 17px` | Sets text size; clamp(...) bounds a responsive size: `17px`. |

### .metric-value

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-family: 'Manrope',sans-serif` | Chooses font families in priority/fallback order: `'Manrope',sans-serif`. |
| `font-weight: 800` | Sets text weight: larger numbers are heavier: `800`. |
| `font-size: 32px` | Sets text size; clamp(...) bounds a responsive size: `32px`. |
| `letter-spacing: -1px` | Adjusts spacing between letters; negative values tighten: `-1px`. |
| `margin: 12px 0 6px` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `12px 0 6px`. |
| `color: var(--navy)` | Sets foreground text color; var(...) reuses the named root variable: `var(--navy)`. |

### .metric-card p

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `color: #81929d` | Sets foreground text color; var(...) reuses the named root variable: `#81929d`. |
| `min-height: 32px` | Sets the minimum vertical space reserved by an element: `32px`. |

### .metric-missing .metric-value

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 22px` | Sets text size; clamp(...) bounds a responsive size: `22px`. |
| `margin: 17px 0 13px` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `17px 0 13px`. |
| `color: #8598a3` | Sets foreground text color; var(...) reuses the named root variable: `#8598a3`. |

### .evidence-tag

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 9px` | Sets text size; clamp(...) bounds a responsive size: `9px`. |
| `text-transform: uppercase` | Transforms displayed capitalization while preserving source text: `uppercase`. |
| `letter-spacing: 1px` | Adjusts spacing between letters; negative values tighten: `1px`. |
| `color: #088071` | Sets foreground text color; var(...) reuses the named root variable: `#088071`. |
| `display: inline-block` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `inline-block`. |
| `margin-top: 10px` | Sets outer spacing above the element: `10px`. |

### .evidence-tag.estimated

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `color: #a47032` | Sets foreground text color; var(...) reuses the named root variable: `#a47032`. |

### .evidence-tag.unavailable

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `color: #83929e` | Sets foreground text color; var(...) reuses the named root variable: `#83929e`. |

### .panel

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `border: 1px solid var(--line)` | Sets all four border widths, styles, and colors together: `1px solid var(--line)`. |
| `border-radius: 9px` | Rounds corners: `9px`. |
| `background: #fff` | Sets the element background (a color here): `#fff`. |
| `padding: 23px 25px` | Sets inner spacing in top/right/bottom/left shorthand: `23px 25px`. |
| `margin-bottom: 20px` | Sets outer spacing below the element: `20px`. |
| `min-width: 0` | Sets minimum width; zero permits flex/grid items to shrink below content width: `0`. |
| `box-shadow: 0 2px 3px #10233403` | Adds an outer/inset visual shadow or ring without changing layout dimensions: `0 2px 3px #10233403`. |

### .panel-heading

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `justify-content: space-between` | Distributes flex/grid children on the main axis: `space-between`. |
| `align-items: center` | Aligns flex/grid children on the cross axis: `center`. |
| `gap: 15px` | Sets space between flex/grid children; two values mean row gap then column gap: `15px`. |
| `margin-bottom: 24px` | Sets outer spacing below the element: `24px`. |

### .panel-heading .eyebrow

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 9px` | Sets text size; clamp(...) bounds a responsive size: `9px`. |
| `margin-bottom: 6px` | Sets outer spacing below the element: `6px`. |

### .panel-heading h2

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 18px` | Sets text size; clamp(...) bounds a responsive size: `18px`. |
| `font-weight: 700` | Sets text weight: larger numbers are heavier: `700`. |

### .panel-heading>.badge

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-weight: 500` | Sets text weight: larger numbers are heavier: `500`. |

### .chart-legend

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `flex-wrap: wrap` | Allows flex children to continue onto another line: `wrap`. |
| `gap: 20px` | Sets space between flex/grid children; two values mean row gap then column gap: `20px`. |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `color: #718590` | Sets foreground text color; var(...) reuses the named root variable: `#718590`. |
| `margin: 0 0 12px` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `0 0 12px`. |

### .chart-legend>span

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `align-items: center` | Aligns flex/grid children on the cross axis: `center`. |
| `gap: 7px` | Sets space between flex/grid children; two values mean row gap then column gap: `7px`. |

### .legend-line

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `width: 17px` | Sets element width: `17px`. |
| `height: 2px` | Sets element height: `2px`. |
| `background: var(--teal)` | Sets the element background (a color here): `var(--teal)`. |
| `display: inline-block` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `inline-block`. |

### .legend-line.drift

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `height: 0` | Sets element height: `0`. |
| `border-top: 2px dashed var(--orange)` | Sets only the top border: `2px dashed var(--orange)`. |
| `background: transparent` | Sets the element background (a color here): `transparent`. |

### .legend-dot

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `height: 6px` | Sets element height: `6px`. |
| `width: 6px` | Sets element width: `6px`. |
| `border-radius: 50%` | Rounds corners: `50%`. |
| `background: #798e9d` | Sets the element background (a color here): `#798e9d`. |
| `display: inline-block` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `inline-block`. |

### .legend-dot.attack

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: #ca7647` | Sets the element background (a color here): `#ca7647`. |

### .legend-dot.benign

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: #acc5ce` | Sets the element background (a color here): `#acc5ce`. |

### .legend-dot.pareto

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: var(--teal)` | Sets the element background (a color here): `var(--teal)`. |
| `box-shadow: 0 0 0 2px #a0d9d5` | Adds an outer/inset visual shadow or ring without changing layout dimensions: `0 0 0 2px #a0d9d5`. |

### .legend-dot.comparison

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: #8d9da8` | Sets the element background (a color here): `#8d9da8`. |

### .timeline-svg,.tradeoff-svg

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: block` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `block`. |
| `width: 100%` | Sets element width: `100%`. |
| `height: auto` | Sets element height: `auto`. |
| `overflow: visible` | Sets oversized-content behavior; auto enables scrolling when needed, hidden clips, visible lets it extend: `visible`. |

### .timeline-svg

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `max-height: 300px` | Caps element height; overflow rules determine scrolling/clipping afterward: `300px`. |

### .grid-line

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `stroke: #eaf0f2` | Sets SVG line/border color: `#eaf0f2`. |
| `stroke-width: 1` | Sets SVG line thickness in coordinate units: `1`. |

### .axis-label

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `fill: #879ba7` | Sets the SVG interior/text color: `#879ba7`. |

### .axis-title

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `fill: #718895` | Sets the SVG interior/text color: `#718895`. |

### .threshold-line

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `stroke: #bdced5` | Sets SVG line/border color: `#bdced5`. |
| `stroke-dasharray: 5 5` | Alternates dash and gap lengths for SVG strokes: `5 5`. |

### .probability-line

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `fill: none` | Sets the SVG interior/text color: `none`. |
| `stroke: var(--teal)` | Sets SVG line/border color: `var(--teal)`. |
| `stroke-width: 2` | Sets SVG line thickness in coordinate units: `2`. |
| `stroke-linejoin: round` | Rounds joins between segments when round: `round`. |

### .truth-attack

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `fill: #d99a73` | Sets the SVG interior/text color: `#d99a73`. |
| `opacity: .65` | Controls whole-element transparency from 0 invisible to 1 opaque: `.65`. |

### .truth-benign

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `fill: #a4bec9` | Sets the SVG interior/text color: `#a4bec9`. |
| `opacity: .6` | Controls whole-element transparency from 0 invisible to 1 opaque: `.6`. |

### .drift-line

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `stroke: #d78a4b` | Sets SVG line/border color: `#d78a4b`. |
| `stroke-width: 1.5` | Sets SVG line thickness in coordinate units: `1.5`. |
| `stroke-dasharray: 4 4` | Alternates dash and gap lengths for SVG strokes: `4 4`. |

### .chart-note

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `color: #8698a2` | Sets foreground text color; var(...) reuses the named root variable: `#8698a2`. |
| `line-height: 1.65` | Sets line spacing; unitless values multiply font size: `1.65`. |
| `margin-top: 12px` | Sets outer spacing above the element: `12px`. |

### .chart-empty

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `min-height: 200px` | Sets the minimum vertical space reserved by an element: `200px`. |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `align-items: center` | Aligns flex/grid children on the cross axis: `center`. |
| `justify-content: center` | Distributes flex/grid children on the main axis: `center`. |
| `flex-direction: column` | Chooses row or column arrangement of flex children: `column`. |
| `gap: 9px` | Sets space between flex/grid children; two values mean row gap then column gap: `9px`. |
| `text-align: center` | Aligns inline text inside its box: `center`. |
| `padding: 25px` | Sets inner spacing in top/right/bottom/left shorthand: `25px`. |

### .chart-empty p

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 12px` | Sets text size; clamp(...) bounds a responsive size: `12px`. |
| `color: #7b909c` | Sets foreground text color; var(...) reuses the named root variable: `#7b909c`. |
| `max-width: 480px` | Caps element width: `480px`. |

### .chart-empty h3

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `color: #536e7e` | Sets foreground text color; var(...) reuses the named root variable: `#536e7e`. |
| `font-size: 15px` | Sets text size; clamp(...) bounds a responsive size: `15px`. |
| `font-weight: 600` | Sets text weight: larger numbers are heavier: `600`. |

### .chart-empty.compact

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `min-height: 180px` | Sets the minimum vertical space reserved by an element: `180px`. |

### .empty-glyph

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 42px` | Sets text size; clamp(...) bounds a responsive size: `42px`. |
| `color: #98b7c0` | Sets foreground text color; var(...) reuses the named root variable: `#98b7c0`. |

### .analysis-grid

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: grid` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `grid`. |
| `grid-template-columns: 1.15fr 1fr` | Defines grid column sizes; fr divides available space proportionally: `1.15fr 1fr`. |
| `gap: 20px` | Sets space between flex/grid children; two values mean row gap then column gap: `20px`. |

### .analysis-grid>.panel

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `margin-bottom: 20px` | Sets outer spacing below the element: `20px`. |

### .inline-control

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `justify-content: space-between` | Distributes flex/grid children on the main axis: `space-between`. |
| `align-items: center` | Aligns flex/grid children on the cross axis: `center`. |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `color: #6b8391` | Sets foreground text color; var(...) reuses the named root variable: `#6b8391`. |
| `margin-bottom: 16px` | Sets outer spacing below the element: `16px`. |
| `gap: 10px` | Sets space between flex/grid children; two values mean row gap then column gap: `10px`. |

### .inline-control select

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `border: 1px solid #dbe5e9` | Sets all four border widths, styles, and colors together: `1px solid #dbe5e9`. |
| `background: #f9fbfc` | Sets the element background (a color here): `#f9fbfc`. |
| `border-radius: 5px` | Rounds corners: `5px`. |
| `padding: 7px` | Sets inner spacing in top/right/bottom/left shorthand: `7px`. |
| `color: #486573` | Sets foreground text color; var(...) reuses the named root variable: `#486573`. |
| `font-size: 11px` | Sets text size; clamp(...) bounds a responsive size: `11px`. |

### .pareto-point

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `fill: #0e8c89` | Sets the SVG interior/text color: `#0e8c89`. |
| `stroke: #a9d9d4` | Sets SVG line/border color: `#a9d9d4`. |
| `stroke-width: 3` | Sets SVG line thickness in coordinate units: `3`. |

### .comparison-point

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `fill: #849ca9` | Sets the SVG interior/text color: `#849ca9`. |
| `stroke: white` | Sets SVG line/border color: `white`. |
| `stroke-width: 2` | Sets SVG line thickness in coordinate units: `2`. |

### .point-label

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 9px` | Sets text size; clamp(...) bounds a responsive size: `9px`. |
| `fill: #5e7988` | Sets the SVG interior/text color: `#5e7988`. |

### .count-list

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `margin: 0` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `0`. |

### .count-list>div

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `justify-content: space-between` | Distributes flex/grid children on the main axis: `space-between`. |
| `border-bottom: 1px solid #ecf1f3` | Sets only the bottom border: `1px solid #ecf1f3`. |
| `padding: 12px 0` | Sets inner spacing in top/right/bottom/left shorthand: `12px 0`. |

### .count-list>div:last-child

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `border-bottom: none` | Sets only the bottom border: `none`. |

### .count-list dt

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `text-transform: capitalize` | Transforms displayed capitalization while preserving source text: `capitalize`. |
| `color: #6b8392` | Sets foreground text color; var(...) reuses the named root variable: `#6b8392`. |
| `font-size: 12px` | Sets text size; clamp(...) bounds a responsive size: `12px`. |

### .count-list dd

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `margin: 0` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `0`. |
| `font-weight: 600` | Sets text weight: larger numbers are heavier: `600`. |
| `color: #2d4a5d` | Sets foreground text color; var(...) reuses the named root variable: `#2d4a5d`. |
| `font-variant-numeric: tabular-nums` | Uses equally wide digits with tabular-nums, aligning numeric counts: `tabular-nums`. |

### .account-note

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `color: #7f94a0` | Sets foreground text color; var(...) reuses the named root variable: `#7f94a0`. |
| `line-height: 1.7` | Sets line spacing; unitless values multiply font size: `1.7`. |
| `background: #f4f8f9` | Sets the element background (a color here): `#f4f8f9`. |
| `border-radius: 6px` | Rounds corners: `6px`. |
| `padding: 13px` | Sets inner spacing in top/right/bottom/left shorthand: `13px`. |
| `margin-top: 15px` | Sets outer spacing above the element: `15px`. |

### .table-scroll

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `overflow: auto` | Sets oversized-content behavior; auto enables scrolling when needed, hidden clips, visible lets it extend: `auto`. |

### table

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `width: 100%` | Sets element width: `100%`. |
| `border-collapse: collapse` | Controls whether adjacent table-cell borders share a single edge: `collapse`. |
| `font-size: 12px` | Sets text size; clamp(...) bounds a responsive size: `12px`. |
| `text-align: left` | Aligns inline text inside its box: `left`. |

### thead th

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-weight: 500` | Sets text weight: larger numbers are heavier: `500`. |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `color: #8496a3` | Sets foreground text color; var(...) reuses the named root variable: `#8496a3`. |
| `padding: 12px` | Sets inner spacing in top/right/bottom/left shorthand: `12px`. |
| `border-bottom: 1px solid #dce6ea` | Sets only the bottom border: `1px solid #dce6ea`. |
| `white-space: nowrap` | Controls wrapping/space handling; nowrap keeps text on one line, normal allows wrapping: `nowrap`. |

### tbody td,tbody th

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `padding: 15px 12px` | Sets inner spacing in top/right/bottom/left shorthand: `15px 12px`. |
| `border-bottom: 1px solid #edf1f3` | Sets only the bottom border: `1px solid #edf1f3`. |
| `white-space: nowrap` | Controls wrapping/space handling; nowrap keeps text on one line, normal allows wrapping: `nowrap`. |
| `font-weight: 400` | Sets text weight: larger numbers are heavier: `400`. |

### tbody tr:last-child td,tbody tr:last-child th

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `border-bottom: none` | Sets only the bottom border: `none`. |

### tbody tr:hover

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: #f8fafb` | Sets the element background (a color here): `#f8fafb`. |

### .selected-row

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: #f0f8f8` | Sets the element background (a color here): `#f0f8f8`. |

### .run-link

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `background: none` | Sets the element background (a color here): `none`. |
| `border: none` | Sets all four border widths, styles, and colors together: `none`. |
| `padding: 0` | Sets inner spacing in top/right/bottom/left shorthand: `0`. |
| `color: #087d82` | Sets foreground text color; var(...) reuses the named root variable: `#087d82`. |
| `text-align: left` | Aligns inline text inside its box: `left`. |
| `font-size: 11px` | Sets text size; clamp(...) bounds a responsive size: `11px`. |
| `max-width: 190px` | Caps element width: `190px`. |
| `overflow: hidden` | Sets oversized-content behavior; auto enables scrolling when needed, hidden clips, visible lets it extend: `hidden`. |
| `text-overflow: ellipsis` | Uses an ellipsis when clipped single-line text overflows its container: `ellipsis`. |

### .run-link:hover

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `text-decoration: underline` | Adds/removes text decoration, e.g. underline on hover: `underline`. |

### table small

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: block` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `block`. |
| `font-size: 9px` | Sets text size; clamp(...) bounds a responsive size: `9px`. |
| `color: #8398a4` | Sets foreground text color; var(...) reuses the named root variable: `#8398a4`. |
| `margin-top: 5px` | Sets outer spacing above the element: `5px`. |

### .evidence-list>div

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `align-items: flex-start` | Aligns flex/grid children on the cross axis: `flex-start`. |
| `justify-content: space-between` | Distributes flex/grid children on the main axis: `space-between`. |
| `border-bottom: 1px solid #edf1f3` | Sets only the bottom border: `1px solid #edf1f3`. |
| `padding: 10px 0` | Sets inner spacing in top/right/bottom/left shorthand: `10px 0`. |
| `gap: 16px` | Sets space between flex/grid children; two values mean row gap then column gap: `16px`. |

### .evidence-list>div:last-child

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `border-bottom: none` | Sets only the bottom border: `none`. |

### .evidence-list strong

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 11px` | Sets text size; clamp(...) bounds a responsive size: `11px`. |
| `font-weight: 500` | Sets text weight: larger numbers are heavier: `500`. |
| `color: #506d7d` | Sets foreground text color; var(...) reuses the named root variable: `#506d7d`. |

### .evidence-list small

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: block` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `block`. |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `color: #8b9da7` | Sets foreground text color; var(...) reuses the named root variable: `#8b9da7`. |
| `margin-top: 3px` | Sets outer spacing above the element: `3px`. |
| `line-height: 1.5` | Sets line spacing; unitless values multiply font size: `1.5`. |

### .evidence-list>div>span

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 11px` | Sets text size; clamp(...) bounds a responsive size: `11px`. |
| `font-weight: 500` | Sets text weight: larger numbers are heavier: `500`. |
| `color: #355568` | Sets foreground text color; var(...) reuses the named root variable: `#355568`. |
| `text-align: right` | Aligns inline text inside its box: `right`. |
| `white-space: nowrap` | Controls wrapping/space handling; nowrap keeps text on one line, normal allows wrapping: `nowrap`. |

### .details-grid

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `grid-template-columns: 1.15fr 1fr` | Defines grid column sizes; fr divides available space proportionally: `1.15fr 1fr`. |

### .drift-log

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `list-style: none` | Removes default ordered-list markers with none: `none`. |
| `padding: 0` | Sets inner spacing in top/right/bottom/left shorthand: `0`. |
| `margin: 0` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `0`. |
| `max-height: 360px` | Caps element height; overflow rules determine scrolling/clipping afterward: `360px`. |
| `overflow: auto` | Sets oversized-content behavior; auto enables scrolling when needed, hidden clips, visible lets it extend: `auto`. |

### .drift-log li

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `gap: 13px` | Sets space between flex/grid children; two values mean row gap then column gap: `13px`. |
| `border-left: 1px solid #e7edf0` | Sets only the left border: `1px solid #e7edf0`. |
| `margin-left: 4px` | Sets outer spacing to the left; auto pushes the item toward the right in a row: `4px`. |
| `padding: 0 0 22px 18px` | Sets inner spacing in top/right/bottom/left shorthand: `0 0 22px 18px`. |
| `position: relative` | Chooses normal/relative/absolute positioning; absolute offsets are relative to an appropriate containing ancestor: `relative`. |

### .event-dot

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `position: absolute` | Chooses normal/relative/absolute positioning; absolute offsets are relative to an appropriate containing ancestor: `absolute`. |
| `left: -4px` | Sets the horizontal offset of a positioned element: `-4px`. |
| `top: 4px` | Sets the vertical offset of a positioned element: `4px`. |
| `height: 7px` | Sets element height: `7px`. |
| `width: 7px` | Sets element width: `7px`. |
| `background: #d49153` | Sets the element background (a color here): `#d49153`. |
| `border: 2px solid #fff` | Sets all four border widths, styles, and colors together: `2px solid #fff`. |
| `box-shadow: 0 0 0 1px #e2bf94` | Adds an outer/inset visual shadow or ring without changing layout dimensions: `0 0 0 1px #e2bf94`. |
| `border-radius: 50%` | Rounds corners: `50%`. |

### .drift-log strong

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 12px` | Sets text size; clamp(...) bounds a responsive size: `12px`. |
| `font-weight: 500` | Sets text weight: larger numbers are heavier: `500`. |
| `color: #4b6878` | Sets foreground text color; var(...) reuses the named root variable: `#4b6878`. |
| `text-transform: capitalize` | Transforms displayed capitalization while preserving source text: `capitalize`. |

### .drift-log p

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `color: #8095a0` | Sets foreground text color; var(...) reuses the named root variable: `#8095a0`. |
| `margin: 5px 0` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `5px 0`. |

### .drift-log small

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `color: #9babb4` | Sets foreground text color; var(...) reuses the named root variable: `#9babb4`. |

### .config-details

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `border-top: 1px solid #e5edf0` | Sets only the top border: `1px solid #e5edf0`. |
| `margin-top: 20px` | Sets outer spacing above the element: `20px`. |
| `padding-top: 16px` | Sets inner spacing above content: `16px`. |

### .config-details summary

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 11px` | Sets text size; clamp(...) bounds a responsive size: `11px`. |
| `color: #597c8d` | Sets foreground text color; var(...) reuses the named root variable: `#597c8d`. |
| `cursor: pointer` | Chooses the pointer shape for interaction feedback: `pointer`. |

### .config-details pre

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `line-height: 1.8` | Sets line spacing; unitless values multiply font size: `1.8`. |
| `background: #f5f8fa` | Sets the element background (a color here): `#f5f8fa`. |
| `border-radius: 5px` | Rounds corners: `5px`. |
| `padding: 16px` | Sets inner spacing in top/right/bottom/left shorthand: `16px`. |
| `color: #5b7787` | Sets foreground text color; var(...) reuses the named root variable: `#5b7787`. |
| `overflow: auto` | Sets oversized-content behavior; auto enables scrolling when needed, hidden clips, visible lets it extend: `auto`. |
| `max-height: 350px` | Caps element height; overflow rules determine scrolling/clipping afterward: `350px`. |

### footer

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `border-top: 1px solid #dde7eb` | Sets only the top border: `1px solid #dde7eb`. |
| `display: flex` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `flex`. |
| `justify-content: space-between` | Distributes flex/grid children on the main axis: `space-between`. |
| `gap: 20px` | Sets space between flex/grid children; two values mean row gap then column gap: `20px`. |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `color: #8b9da6` | Sets foreground text color; var(...) reuses the named root variable: `#8b9da6`. |
| `padding: 24px 0` | Sets inner spacing in top/right/bottom/left shorthand: `24px 0`. |
| `margin-top: 10px` | Sets outer spacing above the element: `10px`. |
| `line-height: 1.6` | Sets line spacing; unitless values multiply font size: `1.6`. |

### .footer-dot

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `padding: 0 8px` | Sets inner spacing in top/right/bottom/left shorthand: `0 8px`. |
| `color: #a4b5bd` | Sets foreground text color; var(...) reuses the named root variable: `#a4b5bd`. |

### .sr-only

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `position: absolute` | Chooses normal/relative/absolute positioning; absolute offsets are relative to an appropriate containing ancestor: `absolute`. |
| `width: 1px` | Sets element width: `1px`. |
| `height: 1px` | Sets element height: `1px`. |
| `padding: 0` | Sets inner spacing in top/right/bottom/left shorthand: `0`. |
| `margin: -1px` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `-1px`. |
| `overflow: hidden` | Sets oversized-content behavior; auto enables scrolling when needed, hidden clips, visible lets it extend: `hidden`. |
| `clip: rect(0,0,0,0)` | Clips the positioned accessibility-only element to a tiny rectangle: `rect(0,0,0,0)`. |
| `white-space: nowrap` | Controls wrapping/space handling; nowrap keeps text on one line, normal allows wrapping: `nowrap`. |
| `border: 0` | Sets all four border widths, styles, and colors together: `0`. |

### .skip-link

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `position: absolute` | Chooses normal/relative/absolute positioning; absolute offsets are relative to an appropriate containing ancestor: `absolute`. |
| `left: 16px` | Sets the horizontal offset of a positioned element: `16px`. |
| `top: -100px` | Sets the vertical offset of a positioned element: `-100px`. |
| `background: white` | Sets the element background (a color here): `white`. |
| `padding: 10px` | Sets inner spacing in top/right/bottom/left shorthand: `10px`. |
| `z-index: 5` | Sets stacking order for a positioned element: `5`. |

### .skip-link:focus

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `top: 10px` | Sets the vertical offset of a positioned element: `10px`. |

### @media(max-width:1100px)

Applies nested rules only while this media condition matches.

### .overview-strip>div

Context: @media(max-width:1100px).

| Declaration | Effect |
| --- | --- |
| `min-width: 100px` | Sets minimum width; zero permits flex/grid items to shrink below content width: `100px`. |
| `margin-right: 20px` | Sets outer spacing to the right: `20px`. |
| `padding-right: 20px` | Sets inner spacing on the right: `20px`. |

### .topbar-subtitle

Context: @media(max-width:1100px).

| Declaration | Effect |
| --- | --- |
| `display: none` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `none`. |

### .overview-strip>.overview-description strong

Context: @media(max-width:1100px).

| Declaration | Effect |
| --- | --- |
| `font-size: 11px` | Sets text size; clamp(...) bounds a responsive size: `11px`. |

### .metric-card

Context: @media(max-width:1100px).

| Declaration | Effect |
| --- | --- |
| `padding: 18px` | Sets inner spacing in top/right/bottom/left shorthand: `18px`. |

### .metric-value

Context: @media(max-width:1100px).

| Declaration | Effect |
| --- | --- |
| `font-size: 28px` | Sets text size; clamp(...) bounds a responsive size: `28px`. |

### .refresh-tools

Context: @media(max-width:1100px).

| Declaration | Effect |
| --- | --- |
| `gap: 10px` | Sets space between flex/grid children; two values mean row gap then column gap: `10px`. |

### .refresh-toggle

Context: @media(max-width:1100px).

| Declaration | Effect |
| --- | --- |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |

### @media(max-width:850px)

Applies nested rules only while this media condition matches.

### .page-heading

Context: @media(max-width:850px).

| Declaration | Effect |
| --- | --- |
| `align-items: flex-start` | Aligns flex/grid children on the cross axis: `flex-start`. |
| `flex-direction: column` | Chooses row or column arrangement of flex children: `column`. |
| `gap: 20px` | Sets space between flex/grid children; two values mean row gap then column gap: `20px`. |

### .refresh-tools

Context: @media(max-width:850px).

| Declaration | Effect |
| --- | --- |
| `width: 100%` | Sets element width: `100%`. |
| `justify-content: flex-end` | Distributes flex/grid children on the main axis: `flex-end`. |

### .overview-strip

Context: @media(max-width:850px).

| Declaration | Effect |
| --- | --- |
| `flex-wrap: wrap` | Allows flex children to continue onto another line: `wrap`. |
| `gap: 15px` | Sets space between flex/grid children; two values mean row gap then column gap: `15px`. |
| `padding: 19px` | Sets inner spacing in top/right/bottom/left shorthand: `19px`. |

### .overview-strip>div

Context: @media(max-width:850px).

| Declaration | Effect |
| --- | --- |
| `flex: 1` | Sets flex growth/shrink/basis; 1 lets an item share remaining space: `1`. |
| `min-width: 75px` | Sets minimum width; zero permits flex/grid items to shrink below content width: `75px`. |
| `padding: 0` | Sets inner spacing in top/right/bottom/left shorthand: `0`. |
| `margin: 0` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `0`. |

### .overview-strip>.overview-description

Context: @media(max-width:850px).

| Declaration | Effect |
| --- | --- |
| `display: none` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `none`. |

### .metric-grid

Context: @media(max-width:850px).

| Declaration | Effect |
| --- | --- |
| `grid-template-columns: repeat(2,1fr)` | Defines grid column sizes; fr divides available space proportionally: `repeat(2,1fr)`. |

### .analysis-grid

Context: @media(max-width:850px).

| Declaration | Effect |
| --- | --- |
| `grid-template-columns: 1fr` | Defines grid column sizes; fr divides available space proportionally: `1fr`. |

### .run-toolbar

Context: @media(max-width:850px).

| Declaration | Effect |
| --- | --- |
| `flex-wrap: wrap` | Allows flex children to continue onto another line: `wrap`. |
| `gap: 12px` | Sets space between flex/grid children; two values mean row gap then column gap: `12px`. |

### .run-toolbar select

Context: @media(max-width:850px).

| Declaration | Effect |
| --- | --- |
| `flex-basis: 100%` | Sets the initial flex main-axis size; 100% makes the selector claim a full row: `100%`. |
| `order: 3` | Changes visual order inside flex/grid without changing document order: `3`. |
| `max-width: none` | Caps element width: `none`. |

### .selection-count

Context: @media(max-width:850px).

| Declaration | Effect |
| --- | --- |
| `margin-left: auto` | Sets outer spacing to the left; auto pushes the item toward the right in a row: `auto`. |

### .panel

Context: @media(max-width:850px).

| Declaration | Effect |
| --- | --- |
| `padding: 20px` | Sets inner spacing in top/right/bottom/left shorthand: `20px`. |

### .empty-steps

Context: @media(max-width:850px).

| Declaration | Effect |
| --- | --- |
| `flex-direction: column` | Chooses row or column arrangement of flex children: `column`. |
| `gap: 12px` | Sets space between flex/grid children; two values mean row gap then column gap: `12px`. |

### h1>span

Context: @media(max-width:850px).

| Declaration | Effect |
| --- | --- |
| `display: block` | Chooses layout behavior: flex/grid for arranging children, block/inline-block for box flow, none to hide: `block`. |

### .context-bottom

Context: @media(max-width:850px).

| Declaration | Effect |
| --- | --- |
| `gap: 12px 20px` | Sets space between flex/grid children; two values mean row gap then column gap: `12px 20px`. |

### .run-context-head

Context: @media(max-width:850px).

| Declaration | Effect |
| --- | --- |
| `padding: 20px` | Sets inner spacing in top/right/bottom/left shorthand: `20px`. |

### .context-bottom

Context: @media(max-width:850px).

| Declaration | Effect |
| --- | --- |
| `padding: 12px 20px` | Sets inner spacing in top/right/bottom/left shorthand: `12px 20px`. |

### .tradeoff-svg

Context: @media(max-width:850px).

| Declaration | Effect |
| --- | --- |
| `max-height: 300px` | Caps element height; overflow rules determine scrolling/clipping afterward: `300px`. |

### @media(max-width:480px)

Applies nested rules only while this media condition matches.

### main

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `padding: 26px 16px 0` | Sets inner spacing in top/right/bottom/left shorthand: `26px 16px 0`. |

### .topbar

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `padding: 0 16px` | Sets inner spacing in top/right/bottom/left shorthand: `0 16px`. |
| `height: 65px` | Sets element height: `65px`. |

### .brand

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `font-size: 19px` | Sets text size; clamp(...) bounds a responsive size: `19px`. |

### .project-tag

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `font-size: 9px` | Sets text size; clamp(...) bounds a responsive size: `9px`. |
| `padding: 6px` | Sets inner spacing in top/right/bottom/left shorthand: `6px`. |

### .page-heading h1

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `font-size: 27px` | Sets text size; clamp(...) bounds a responsive size: `27px`. |

### .run-context-head

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `gap: 8px` | Sets space between flex/grid children; two values mean row gap then column gap: `8px`. |

### .sampling-emblem

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `min-width: 80px` | Sets minimum width; zero permits flex/grid items to shrink below content width: `80px`. |

### .sampling-emblem strong

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `font-size: 29px` | Sets text size; clamp(...) bounds a responsive size: `29px`. |

### .sampling-emblem>span

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `font-size: 8px` | Sets text size; clamp(...) bounds a responsive size: `8px`. |

### .run-context .badge

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `margin: 0 4px 5px 0` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `0 4px 5px 0`. |
| `font-size: 9px` | Sets text size; clamp(...) bounds a responsive size: `9px`. |

### .metric-grid

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `gap: 10px` | Sets space between flex/grid children; two values mean row gap then column gap: `10px`. |

### .metric-card

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `padding: 16px 12px` | Sets inner spacing in top/right/bottom/left shorthand: `16px 12px`. |

### .metric-value

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `font-size: 25px` | Sets text size; clamp(...) bounds a responsive size: `25px`. |

### .metric-missing .metric-value

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `font-size: 18px` | Sets text size; clamp(...) bounds a responsive size: `18px`. |

### .metric-card p

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `font-size: 9px` | Sets text size; clamp(...) bounds a responsive size: `9px`. |

### .metric-label

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `font-size: 11px` | Sets text size; clamp(...) bounds a responsive size: `11px`. |

### .panel-heading h2

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `font-size: 16px` | Sets text size; clamp(...) bounds a responsive size: `16px`. |

### .chart-legend

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `gap: 12px` | Sets space between flex/grid children; two values mean row gap then column gap: `12px`. |

### .state-panel

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `padding: 25px 20px` | Sets inner spacing in top/right/bottom/left shorthand: `25px 20px`. |

### .overview-strip strong

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `font-size: 21px` | Sets text size; clamp(...) bounds a responsive size: `21px`. |

### .overview-strip span

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `font-size: 9px` | Sets text size; clamp(...) bounds a responsive size: `9px`. |

### .context-bottom code

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `font-size: 9px` | Sets text size; clamp(...) bounds a responsive size: `9px`. |

### footer

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `flex-direction: column` | Chooses row or column arrangement of flex children: `column`. |
| `gap: 6px` | Sets space between flex/grid children; two values mean row gap then column gap: `6px`. |

### .evidence-list>div>span

Context: @media(max-width:480px).

| Declaration | Effect |
| --- | --- |
| `white-space: normal` | Controls wrapping/space handling; nowrap keeps text on one line, normal allows wrapping: `normal`. |
| `min-width: 80px` | Sets minimum width; zero permits flex/grid items to shrink below content width: `80px`. |

### @media(prefers-reduced-motion:reduce)

Applies nested rules only while this media condition matches.

### .loader

Context: @media(prefers-reduced-motion:reduce).

| Declaration | Effect |
| --- | --- |
| `animation: none` | Sets animation name, duration, easing, and repetition; none disables it: `none`. |

### button

Context: @media(prefers-reduced-motion:reduce).

| Declaration | Effect |
| --- | --- |
| `transition: none` | Smooths changes to selected properties over time; none disables transitions: `none`. |

### .provenance-details

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `margin: 12px 0` | Sets outer spacing in top/right/bottom/left shorthand; auto shares available free space: `12px 0`. |
| `color: #62818f` | Sets foreground text color; var(...) reuses the named root variable: `#62818f`. |
| `font-size: 11px` | Sets text size; clamp(...) bounds a responsive size: `11px`. |

### .provenance-details summary

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `cursor: pointer` | Chooses the pointer shape for interaction feedback: `pointer`. |

### .provenance-details pre

Context: Base rules.

| Declaration | Effect |
| --- | --- |
| `padding: 15px` | Sets inner spacing in top/right/bottom/left shorthand: `15px`. |
| `background: #eaf2f4` | Sets the element background (a color here): `#eaf2f4`. |
| `border-radius: 5px` | Rounds corners: `5px`. |
| `overflow: auto` | Sets oversized-content behavior; auto enables scrolling when needed, hidden clips, visible lets it extend: `auto`. |
| `font-size: 10px` | Sets text size; clamp(...) bounds a responsive size: `10px`. |
| `line-height: 1.7` | Sets line spacing; unitless values multiply font size: `1.7`. |
| `max-height: 220px` | Caps element height; overflow rules determine scrolling/clipping afterward: `220px`. |

## frontend/package-lock.json

npm generates this file to record exact resolved dependency versions, package locations, integrity hashes, and the dependency graph. package.json declares acceptable ranges; package-lock.json pins a particular installation. npm ci uses it for a reproducible clean dependency install and fails if it disagrees with package.json. Commit intentional lockfile changes with dependency changes; let npm generate the entries instead of editing hashes/versions manually. Its repeated generated entries are package metadata, rather than custom DDoS detection code. Every physical line is explained in [Reference data and generated files](reference-data.md).

## Follow a run from click to pixels

1. Changing Selected run calls setSelectedId.
2. React starts the selected-run effect; cleanup aborts the old effect's requests and clears its timeout.
3. The effect clears old detail state, shows loading, and fetches summary and series concurrently.
4. api.ts validates responses and returns typed evidence.
5. App stores selected and series and renders context, cards, timeline, and drift log.
6. compatibleRuns creates the eligible trial group; Tradeoff retains measured F1/cost and paretoRuns finds nondominated points.
7. Changing overhead axis recalculates the browser chart; it does not run training or experiments.
8. Polling repeats reads after completion; manual Refresh restarts both request effects.

## Explain these before your demo

Be able to explain why TypeScript types do not validate JSON; why unavailable differs from measured zero; why CSV flow sampling cannot establish packet-level overhead; why effect cleanup avoids stale selection results; why missing scores create chart gaps; and why a Pareto frontier does not automatically establish the knee point.

The test sections describe the actual assertions, not a claim that tests were executed during this documentation task. Real-server integration tests depend on existing server evidence.

CSS appendix: 222 individual rules, 684 declarations. Line walkthrough: 17 files, 636 physical lines.

