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
  validation?: { accepted?: boolean; [key: string]: unknown };
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
