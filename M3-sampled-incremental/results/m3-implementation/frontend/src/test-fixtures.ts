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
