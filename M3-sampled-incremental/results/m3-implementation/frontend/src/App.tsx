import { useCallback, useEffect, useMemo, useState } from 'react';
import { getOverview, getRun, getRuns, getSeries } from './api';
import { compatibleRuns, formatMetric, metricValue, modeName, overheadMetric, paretoRuns, sourceName } from './evidence';
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
    overheadMetric(run, 'combined_ip_bandwidth_kbit_s')?.status === 'measured')
    ? 'combined_ip_bandwidth_kbit_s' : runs.some(run =>
    run.metrics.telemetry_bandwidth_kbps?.status === 'measured' && metricValue(run.metrics.telemetry_bandwidth_kbps) !== null)
    ? 'telemetry_bandwidth_kbps' : 'cpu_percent_mean');
  const frontier = useMemo(() => paretoRuns(runs, costKey), [runs, costKey]);
  const available = runs.filter(run => run.metrics.f1?.status === 'measured' && overheadMetric(run, costKey)?.status === 'measured' && metricValue(run.metrics.f1) !== null && metricValue(overheadMetric(run, costKey)) !== null);
  const costName = costKey === 'combined_ip_bandwidth_kbit_s' ? 'Combined IP bandwidth (kbit/s)' : costKey === 'telemetry_bandwidth_kbps' ? 'Legacy payload bandwidth (kbit/s)' : 'Detector CPU (%)';
  const w = 480, h = 240, left = 55, right = 30, top = 20, bottom = 45;
  const maxCost = Math.max(1, ...available.map(run => metricValue(overheadMetric(run, costKey))!)) * 1.1;
  const x = (c: number) => left + c / maxCost * (w - left - right);
  const y = (q: number) => top + (1 - q) * (h - top - bottom);
  return <>
    <label className="inline-control" htmlFor="cost-axis">Overhead measure<select id="cost-axis" value={costKey} onChange={e => setCostKey(e.target.value)}><option value="combined_ip_bandwidth_kbit_s">Combined IP bandwidth</option><option value="telemetry_bandwidth_kbps">Legacy payload bandwidth</option><option value="cpu_percent_mean">Detector CPU</option></select></label>
    {available.length ? <>
      <svg className="tradeoff-svg" viewBox={`0 0 ${w} ${h}`} role="img" aria-label={`${available.length} compatible measured trials comparing F1 and ${costName}. ${frontier.size} Pareto-efficient trials.`}>
        {[0, .25, .5, .75, 1].map(q => <g key={q}><line className="grid-line" x1={left} y1={y(q)} x2={w - right} y2={y(q)} /><text className="axis-label" x={left - 10} y={y(q) + 4} textAnchor="end">{Math.round(q * 100)}%</text></g>)}
        {[0, .5, 1].map(c => <text key={c} className="axis-label" x={x(c * maxCost)} y={h - bottom + 20} textAnchor="middle">{(c * maxCost).toFixed(1)}</text>)}
        {available.map(run => <g key={run.run_id}><circle cx={x(metricValue(overheadMetric(run, costKey))!)} cy={y(metricValue(run.metrics.f1)!)} r={run.run_id === selectedId ? 7 : 5} className={frontier.has(run.run_id) ? 'pareto-point' : 'comparison-point'}><title>{`${run.run_id}: N=${run.sampling_rate}, F1 ${formatMetric('f1', run.metrics.f1)}, cost ${formatMetric(costKey, overheadMetric(run, costKey))}${frontier.has(run.run_id) ? ', Pareto efficient' : ''}`}</title></circle><text className="point-label" x={x(metricValue(overheadMetric(run, costKey))!) + 9} y={y(metricValue(run.metrics.f1)!) - 7}>N={run.sampling_rate}</text></g>)}
        <text className="axis-title" x={w / 2} y={h - 4} textAnchor="middle">{costName} · lower is better</text>
      </svg>
      <div className="chart-legend"><span><i className="legend-dot pareto" />Pareto efficient</span><span><i className="legend-dot comparison" />Other measured trials</span></div>
    </> : <div className="chart-empty compact"><h3>Trade-off evidence pending</h3><p>At least one completed trial with measured F1 and {costName.toLowerCase()} is required.</p></div>}
    <p className="chart-note">Only compatible completed trials with measured costs are compared. Combined IP bandwidth sums measured sFlow and OpenFlow IP-layer bytes in kbit/s. Dots are individual trials; the report's frontier uses three-trial cell means.</p>
  </>;
}

const detailMetrics: [string, string][] = [
  ['roc_auc', 'ROC-AUC'], ['false_positive_rate', 'False-positive rate'], ['detection_time_seconds', 'Detection time'],
  ['packets_to_detect', 'Packets to detect'], ['unseen_attack_recall', 'Unseen-attack recall'], ['post_drift_recovery_seconds', 'Post-drift recovery'],
  ['cpu_percent_mean', 'Detector CPU · mean'], ['cpu_percent_p95', 'Detector CPU · p95'], ['controller_cpu_percent_mean', 'Controller CPU · mean'],
  ['controller_cpu_percent_p95', 'Controller CPU · p95'], ['sflow_bandwidth_kbit_s', 'sFlow IP-layer bandwidth'],
  ['openflow_bandwidth_kbit_s', 'OpenFlow IP-layer bandwidth'], ['telemetry_bandwidth_kbps', 'Legacy telemetry payload bandwidth'],
  ['openflow_bandwidth_kbps', 'Legacy OpenFlow frame bandwidth'], ['flow_table_entries', 'Flow-table entries'],
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

  const comparisonCostKey = selected?.source === 'official_realtime_verified' ? 'combined_ip_bandwidth_kbit_s' : 'telemetry_bandwidth_kbps';
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
          {selected.source === 'official_realtime_verified' && selected.validation?.accepted ? <div className="notice">Independently validated live trial using controlled official 5G-NIDD packets. Oracle labels are revealed after prediction. This is not a physical 5G deployment or a claim of generalization to all attacks.</div> : selected.source !== 'official_5g_nidd' && <div className="notice">This run is labeled <strong>{sourceName(selected.source)}</strong>. Its results do not establish performance on official 5G-NIDD.</div>}
          <details className="provenance-details"><summary>Dataset and feature provenance</summary><pre>{JSON.stringify({ feature_schema: selected.feature_schema ?? 'Not recorded', provenance: selected.provenance ?? 'Not recorded' }, null, 2)}</pre></details>
          {selected.mode === 'csv_replay' && <div className="notice">This run samples flow records. Packet sampling and live SDN overhead require capture replay or live sFlow measurements.</div>}
          {selected.status === 'failed' && <div className="error-banner" role="alert"><strong>This run failed.</strong><span>{selected.error || 'No error detail was saved.'}</span></div>}
          <section className="metric-grid" aria-label="Detection metrics"><MetricCard name="Precision" metricKey="precision" metric={selected.metrics.precision} caption="How often attack predictions are correct" /><MetricCard name="Recall" metricKey="recall" metric={selected.metrics.recall} caption="Share of labeled attacks detected" /><MetricCard name="F1 score" metricKey="f1" metric={selected.metrics.f1} caption="Balance of precision and recall" /><MetricCard name="Inference latency" metricKey="inference_latency_ms" metric={selected.metrics.inference_latency_ms} caption="Average time per prediction" /></section>
          <section className="panel timeline-panel"><div className="panel-heading"><div><span className="eyebrow">DETECTION THROUGH TIME</span><h2>Adaptive learning timeline</h2></div><Badge>{number(selected.drift_count)} drift {selected.drift_count === 1 ? 'alarm' : 'alarms'}</Badge></div><Timeline series={series} unit={selected.unit} threshold={typeof selected.config.threshold === 'number' ? selected.config.threshold : .5} /></section>
          <div className="analysis-grid"><section className="panel"><div className="panel-heading"><div><span className="eyebrow">ACCURACY × OVERHEAD</span><h2>Sampling trade-off</h2></div></div><Tradeoff key={[selected.source, selected.mode, selected.scenario, selected.feature_schema].join(':')} runs={comparisons} selectedId={selected.run_id} /></section><section className="panel"><div className="panel-heading"><div><span className="eyebrow">STREAM ACCOUNTING</span><h2>Every observation accounted for</h2></div></div><dl className="count-list">{Object.entries(selected.counts).map(([key, value]) => <div key={key}><dt>{key.replaceAll('_', ' ')}</dt><dd>{number(value)}</dd></div>)}</dl><div className="account-note">Input and sampling counts are recorded independently from evaluated labels. Warm-up, exclusions, and unlabeled records are retained in the evidence.</div></section></div>
          <section className="panel"><div className="panel-heading"><div><span className="eyebrow">COMPATIBLE COMPLETED TRIALS</span><h2>Sampling comparison</h2></div><Badge>{comparisons.length} trials</Badge></div><div className="table-scroll"><table><caption className="sr-only">Individual compatible trials; no implicit averaging of repeated trials.</caption><thead><tr><th scope="col">Run / seed</th><th scope="col">Sampling</th><th scope="col">F1</th><th scope="col">Recall</th><th scope="col">CPU mean</th><th scope="col">{comparisonCostKey === 'combined_ip_bandwidth_kbit_s' ? 'IP channel total' : 'Legacy payload'}</th><th scope="col">Drift alarms</th></tr></thead><tbody>{comparisons.map(run => <tr key={run.run_id} className={run.run_id === selected.run_id ? 'selected-row' : ''}><th scope="row"><button className="run-link" onClick={() => setSelectedId(run.run_id)}>{run.run_id}</button><small>Seed {run.seed}</small></th><td><Badge>1 / {run.sampling_rate}</Badge></td>{['f1', 'recall', 'cpu_percent_mean', comparisonCostKey].map(key => <td key={key}>{formatMetric(key, overheadMetric(run, key))}{overheadMetric(run, key)?.status === 'estimated' && <small>estimated</small>}</td>)}<td>{run.drift_count}</td></tr>)}{!comparisons.length && <tr><td colSpan={7}>No compatible completed trials yet.</td></tr>}</tbody></table></div></section>
          <div className="analysis-grid details-grid"><section className="panel"><div className="panel-heading"><div><span className="eyebrow">METRIC EVIDENCE</span><h2>Measurements & limitations</h2></div></div><div className="evidence-list">{detailMetrics.map(([key, label]) => <div key={key}><div><strong>{label}</strong><small>{metricValue(selected.metrics[key]) === null ? selected.metrics[key]?.reason || 'No measurement saved.' : selected.metrics[key]?.reason || selected.metrics[key]?.status}</small></div><span>{formatMetric(key, selected.metrics[key])}</span></div>)}</div></section><section className="panel"><div className="panel-heading"><div><span className="eyebrow">ADWIN / HAT</span><h2>Drift event log</h2></div></div>{series.drift.length ? <ol className="drift-log">{series.drift.map((event, i) => <li key={`${event.index}-${i}`}><span className="event-dot" /><div><strong>{event.event.replaceAll('_', ' ')}</strong><p>{event.detector} · observation {event.index}</p><small>{timeLabel(event.time)}</small></div></li>)}</ol> : <div className="chart-empty compact"><h3>No drift events saved</h3><p>Absence of an alarm does not establish absence of a distribution change.</p></div>}<details className="config-details"><summary>Run configuration and provenance</summary><pre>{JSON.stringify(selected.config, null, 2)}</pre></details></section></div>
        </>}
      </>}
      <footer><span>M3 Observatory <span className="footer-dot">·</span> 5G-NIDD sampled telemetry</span><span>Evidence first. Every number traces to a saved run.</span></footer>
    </main>
  </>;
}
