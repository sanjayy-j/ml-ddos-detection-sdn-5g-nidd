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
