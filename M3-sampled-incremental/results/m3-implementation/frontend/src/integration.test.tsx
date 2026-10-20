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

  it('renders an accepted official realtime trial with the paper-compatible IP cost', async () => {
    connect();
    const runs = await getRuns();
    const official = runs.find(run => run.source === 'official_realtime_verified' &&
      run.status === 'completed' && run.validation?.accepted === true);
    expect(official).toBeDefined();
    render(<App />);
    const select = await screen.findByLabelText('Selected run', {}, { timeout: 10000 });
    fireEvent.change(select, { target: { value: official!.run_id } });
    await waitFor(() => expect(screen.getAllByText('Validated official live trial').length).toBeGreaterThan(0), { timeout: 10000 });
    expect(await screen.findByRole('img', { name: /Prediction timeline/ })).toBeInTheDocument();
    expect(screen.getByLabelText('Overhead measure')).toHaveValue('combined_ip_bandwidth_kbit_s');
    expect(screen.getByRole('columnheader', { name: 'IP channel total' })).toBeInTheDocument();
    expect(screen.getByText('sFlow IP-layer bandwidth')).toBeInTheDocument();
    expect(screen.getByText('OpenFlow IP-layer bandwidth')).toBeInTheDocument();
  }, 20000);
});
