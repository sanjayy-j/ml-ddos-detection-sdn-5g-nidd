import { fireEvent, render, screen, waitFor } from '@testing-library/react';
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
});
