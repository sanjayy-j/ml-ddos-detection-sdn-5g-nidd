import { describe, expect, it } from 'vitest';
import { compatibleRuns, formatMetric, overheadMetric, paretoRuns, sourceName } from './evidence';
import type { RunSummary } from './types';
import { fixtureRun } from './test-fixtures';

describe('scientific evidence handling', () => {
  it('keeps earlier collector trials separate from kernel timestamp collection', () => {
    const legacy = fixtureRun('legacy');
    const explicitLegacy = { ...legacy, run_id: 'explicit-legacy', config: { ...legacy.config, telemetry_clock: 'userspace' } };
    const corrected = { ...legacy, run_id: 'kernel', config: { ...legacy.config, telemetry_clock: 'kernel_receive' } };
    expect(compatibleRuns([legacy, explicitLegacy, corrected], legacy).map(run => run.run_id))
      .toEqual(['legacy', 'explicit-legacy']);
    expect(compatibleRuns([legacy, corrected], corrected).map(run => run.run_id)).toEqual(['kernel']);
  });
  it('distinguishes validated live evidence from provisional and recorded scoring', () => {
    expect(sourceName('official_realtime_verified')).toBe('Validated official 5G-NIDD trial');
    expect(sourceName('provisional_realtime')).toBe('Unvalidated live trial');
    expect(sourceName('official_5g_nidd_recorded_sflow')).toBe('Post-hoc recorded exports');
    const provisional = { ...fixtureRun(), source: 'provisional_realtime' };
    expect(compatibleRuns([provisional], provisional)).toEqual([]);
  });
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
  it('groups historical votes with explicit River but never with corrected votes', () => {
    const historical: RunSummary = { ...fixtureRun('historical'), source: 'official_realtime_verified',
      mode: 'live_sflow', unit: 'window', validation: { accepted: true } };
    const river: RunSummary = { ...historical, run_id: 'river',
      config: { ...historical.config, naive_bayes: 'river' } };
    const corrected: RunSummary = { ...historical, run_id: 'corrected',
      config: { ...historical.config, naive_bayes: 'log_space' } };
    const unaccepted: RunSummary = { ...river, run_id: 'unaccepted', validation: { accepted: false } };
    const running: RunSummary = { ...river, run_id: 'running', status: 'running' };
    const changed: RunSummary = { ...river, run_id: 'changed',
      config: { ...river.config, threshold: .8 } };
    const runs = [historical, river, corrected, unaccepted, running, changed];
    expect(compatibleRuns(runs, historical)).toEqual([historical, river]);
    expect(compatibleRuns(runs, river)).toEqual([historical, river]);
    expect(compatibleRuns(runs, corrected)).toEqual([corrected]);
  });
  it('identifies strict Pareto dominance and excludes estimated costs', () => {
    const a = fixtureRun('a', 1, .8, 10);
    const b = fixtureRun('b', 2, .85, 5);
    const c = fixtureRun('c', 5, .7, 2);
    const estimated = fixtureRun('estimate', 10, .99, .1);
    estimated.metrics.telemetry_bandwidth_kbps.status = 'estimated';
    expect([...paretoRuns([a, b, c, estimated], 'telemetry_bandwidth_kbps')]).toEqual(['b', 'c']);
  });
  it('combines only measured IP channels with matching scientific units', () => {
    const run = fixtureRun();
    run.metrics.sflow_bandwidth_kbit_s = { value: 1.5, unit: 'kbit/s', status: 'measured', reason: null };
    run.metrics.openflow_bandwidth_kbit_s = { value: .5, unit: 'kbit/s', status: 'measured', reason: null };
    expect(overheadMetric(run, 'combined_ip_bandwidth_kbit_s')?.value).toBe(2);
    run.metrics.openflow_bandwidth_kbit_s.status = 'estimated';
    expect(overheadMetric(run, 'combined_ip_bandwidth_kbit_s')?.status).toBe('unavailable');
    run.metrics.openflow_bandwidth_kbit_s.status = 'measured';
    run.metrics.openflow_bandwidth_kbit_s.unit = 'bytes/s';
    expect(overheadMetric(run, 'combined_ip_bandwidth_kbit_s')?.status).toBe('unavailable');
  });
  it('uses combined IP costs without substituting legacy payload measurements', () => {
    const a = fixtureRun('a', 1, .8, 1);
    const b = fixtureRun('b', 2, .85, 100);
    const missing = fixtureRun('missing', 5, .99, .01);
    for (const [run, value] of [[a, 99], [b, 1]] as const) {
      run.metrics.sflow_bandwidth_kbit_s = { value, unit: 'kbit/s', status: 'measured', reason: null };
      run.metrics.openflow_bandwidth_kbit_s = { value: 1, unit: 'kbit/s', status: 'measured', reason: null };
    }
    expect([...paretoRuns([a, b, missing], 'combined_ip_bandwidth_kbit_s')]).toEqual(['b']);
  });
});
