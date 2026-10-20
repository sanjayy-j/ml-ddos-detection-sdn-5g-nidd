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
  if (source === 'official_realtime_verified') return 'Validated official live trial';
  if (source === 'provisional_realtime') return 'Unvalidated live trial';
  if (source === 'official_5g_nidd_recorded_sflow') return 'Post-hoc recorded exports';
  return source === 'official_5g_nidd' ? 'Official 5G-NIDD' : source === 'fixture' ? 'Development fixture' : source === 'live_sflow' ? 'Live telemetry' : source.replaceAll('_', ' ');
}
export function modeName(mode: RunSummary['mode']) {
  return { csv_replay: 'CSV flow replay', pcap_replay: 'Packet capture replay', live_sflow: 'Live sFlow' }[mode];
}
export function compatibleRuns(runs: RunSummary[], selected: RunSummary): RunSummary[] {
  if (selected.source === 'provisional_realtime') return [];
  const settings = ['threshold', 'grace_period', 'drift_delta', 'window_seconds', 'warmup_records', 'warmup_seconds', 'max_records', 'duration_seconds', 'replay_pps', 'label_delay_seconds'];
  const signature = (run: RunSummary) => JSON.stringify(settings.map(key => [key, run.config[key] ?? null]));
  return runs.filter(run => run.status === 'completed' && run.source === selected.source && run.mode === selected.mode &&
    (run.source !== 'official_realtime_verified' || run.validation?.accepted === true) &&
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
