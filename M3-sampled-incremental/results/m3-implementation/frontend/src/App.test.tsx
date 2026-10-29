import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
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
  it('groups runs by numeric sampling rate, then scenario and seed, and preserves selection on refresh', async () => {
    const makeRun = (id: string, n: number, scenario: string, seed = 42) => ({
      ...fixtureRun(id, n), scenario, seed,
    });
    const runs = [
      makeRun('n10-unseen', 10, 'unseen'), makeRun('n2-drift', 2, 'drift'),
      makeRun('n1-unseen', 1, 'unseen'), makeRun('n1-baseline-43', 1, 'baseline', 43),
      makeRun('n1-drift', 1, 'drift'), makeRun('n1-baseline-42', 1, 'baseline'),
      makeRun('n50-baseline', 50, 'baseline'), makeRun('n2-baseline', 2, 'baseline'),
      makeRun('n20-baseline', 20, 'baseline'), makeRun('n5-baseline', 5, 'baseline'),
    ];
    vi.mocked(api.getRuns).mockResolvedValueOnce(runs).mockResolvedValue([...runs].reverse());
    vi.mocked(api.getRun).mockImplementation(async id => runs.find(run => run.run_id === id)!);
    render(<App />);
    const select = await screen.findByRole('combobox', { name: 'Selected run' });
    const expected = ['n1-baseline-42', 'n1-baseline-43', 'n1-drift', 'n1-unseen',
      'n2-baseline', 'n2-drift', 'n5-baseline', 'n10-unseen', 'n20-baseline', 'n50-baseline'];
    const optionIds = () => within(select).getAllByRole('option').map(option =>
      (option as HTMLOptionElement).value);
    expect(optionIds()).toEqual(expected);
    expect(within(select).getAllByRole('group').map(group => group.getAttribute('label')))
      .toEqual(['N=1', 'N=2', 'N=5', 'N=10', 'N=20', 'N=50']);
    expect(select).toHaveValue('n1-baseline-42');
    expect(within(select).getByRole('option', { name: /N=1 · baseline · Seed 42/ })).toBeInTheDocument();
    fireEvent.change(select, { target: { value: 'n2-drift' } });
    await waitFor(() => expect(api.getRun).toHaveBeenCalledWith('n2-drift', expect.any(AbortSignal)));
    fireEvent.click(screen.getByRole('button', { name: /Refresh/ }));
    await waitFor(() => expect(api.getRuns).toHaveBeenCalledTimes(2));
    expect(select).toHaveValue('n2-drift');
    expect(optionIds()).toEqual(expected);
    expect(runs[0].run_id).toBe('n10-unseen');
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
  it('uses the paper-compatible IP cost for validated live comparisons', async () => {
    const run = fixtureRun('verified-live');
    run.source = 'official_realtime_verified'; run.mode = 'live_sflow'; run.unit = 'window';
    run.validation = { accepted: true };
    run.metrics.sflow_bandwidth_kbit_s = { value: 20, unit: 'kbit/s', status: 'measured', reason: null };
    run.metrics.openflow_bandwidth_kbit_s = { value: 2, unit: 'kbit/s', status: 'measured', reason: null };
    vi.mocked(api.getRuns).mockResolvedValue([run]);
    vi.mocked(api.getRun).mockResolvedValue(run);
    render(<App />);
    expect(await screen.findByText('sFlow IP-layer bandwidth')).toBeInTheDocument();
    expect(screen.getByLabelText('Overhead measure')).toHaveValue('combined_ip_bandwidth_kbit_s');
    expect(screen.getByRole('columnheader', { name: 'IP channel total' })).toBeInTheDocument();
    expect(within(screen.getByRole('table')).getByText('22 kbit/s')).toBeInTheDocument();
  });
  it('shows combined channel bandwidth in the card and per-trial chart', async () => {
    const run = fixtureRun('bandwidth-trial');
    run.metrics.sflow_bandwidth_kbit_s = { value: 20, unit: 'kbit/s', status: 'measured', reason: null };
    run.metrics.openflow_bandwidth_kbit_s = { value: 2, unit: 'kbit/s', status: 'measured', reason: null };
    vi.mocked(api.getRuns).mockResolvedValue([run]);
    vi.mocked(api.getRun).mockResolvedValue(run);
    render(<App />);
    const bandwidth = await screen.findByText('Bandwidth');
    expect(bandwidth.closest('article')).toHaveTextContent('22 kbit/s');
    expect(screen.queryByText('Total run time')).not.toBeInTheDocument();
    expect(screen.queryByText('Inference latency')).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Bandwidth by trial' })).toBeInTheDocument();
    expect(screen.getByRole('img', { name: /Combined sFlow and OpenFlow bandwidth for 1 trials/ })).toBeInTheDocument();
  });
});
