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
