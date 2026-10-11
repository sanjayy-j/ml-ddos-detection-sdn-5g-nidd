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
