// Run a copy from tmp/research-deck with node_modules linked to Codex's bundled runtime.
// This builder refuses incomplete evidence and never substitutes illustrative numbers.
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const root = process.cwd();
const runtime = process.env.M3_ARTIFACT_RUNTIME || 'C:/Users/NITHIS/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES ||= path.join(runtime, 'node/node_modules');
const skill = process.env.M3_PRESENTATION_SKILL || 'C:/Users/NITHIS/.codex/plugins/cache/openai-primary-runtime/presentations/26.1015.12040/skills/presentations';
const analysis = path.join(root, 'output/research/analysis');
const staging = path.join(root, 'tmp/research-deck');
const finalPath = path.join(root, 'output/presentations/M3_Research_Presentation_Reviewed.pptx');
const { finalizePresentation, applyPresentationChartFont, resolvePresentationFont } = await import(
  pathToFileURL(path.join(skill, 'container_tools/artifact_tool_utils.mjs')).href);
const read = async name => JSON.parse(await fs.readFile(path.join(analysis, name), 'utf8'));
const readiness = await read('research_readiness.json');
if (!readiness.ready || readiness.accepted_trials !== 54) {
  throw new Error('The final presentation requires 54 accepted trials and all analysis gates');
}
const aggregated = await read('aggregated_metrics.json');
if (aggregated.groups.length !== 18 || aggregated.groups.some(group => !group.complete_three_trials)) {
  throw new Error('Incompatible or incomplete comparison groups');
}
const groups = new Map(aggregated.groups.map(group => [`${group.scenario}:${group.sampling_rate}`, group]));
const scenarios = ['baseline', 'drift', 'unseen'];
const rates = [1, 2, 5, 10, 20, 50];
const palette = ['#17446B', '#AD5823', '#287755'];
const font = resolvePresentationFont({ fontFamily: 'Arial' });
const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });
const metric = (scenario, rate, key) => groups.get(`${scenario}:${rate}`).metrics[key];
const fmt = (value, decimals = 3) => value == null ? 'Unavailable' : value.toFixed(decimals);
// Preserve scientific values in the analysis; round only the presentation's
// literal chart snapshots to a precision Excel can store without truncation.
const chartValue = value => value == null ? null : Number(value.toPrecision(12));
const totalCost = (scenario, rate) => metric(scenario, rate, 'sflow_bandwidth_kbit_s').mean + metric(scenario, rate, 'openflow_bandwidth_kbit_s').mean;

function text(slide, value, left, top, width, height, size = 28, bold = false, color = '#253544') {
  const shape = slide.shapes.add({ geometry: 'textbox', position: { left, top, width, height },
    fill: 'none', line: { fill: 'none', width: 0, style: 'solid' } });
  shape.text = value;
  shape.text.style = { typeface: font, fontSize: size, bold, color };
  return shape;
}
function slide(title, notes) {
  const result = deck.slides.add();
  result.background.fill = '#FFFFFF';
  text(result, title, 64, 44, 1148, 100, 44, true, '#17324D');
  text(result, `M3 controlled replay study    ${deck.slides.items.length}`, 64, 674, 1100, 24, 18, false, '#64717E');
  result.speakerNotes.text = notes || 'Source: research/results/aggregated_metrics.json and linked primary run evidence. Three repeats per cell; fixed traffic, limited generalization.';
  return result;
}
function body(slide, paragraphs, top = 175) {
  let y = top;
  for (const paragraph of paragraphs) {
    text(slide, paragraph, 72, y, 1128, 104, 28);
    y += 112;
  }
}
function chart(slide, key, label, options = {}) {
  const result = slide.charts.add('line', {
    position: { left: 64, top: 160, width: 1150, height: 430 },
    lineOptions: { smooth: false },
    categories: rates.map(String),
    series: scenarios.map((scenario, index) => ({ name: scenario[0].toUpperCase() + scenario.slice(1),
      values: rates.map(rate => chartValue(metric(scenario, rate, key).mean)),
      smooth: false,
      line: { fill: palette[index], width: 3, style: 'solid' },
      marker: { symbol: 'circle', size: 7, fill: palette[index] } })),
    hasLegend: true, legend: { position: 'bottom', textStyle: { fontSize: 23 } },
    xAxis: { title: 'Switch sampling denominator N', textStyle: { fontSize: 23 }, majorGridlines: null },
    yAxis: { title: label, textStyle: { fontSize: 23 }, numberFormatCode: '0.00',
      majorGridlines: { fill: '#DDE4EA', width: 1, style: 'solid' }, ...options },
  });
  applyPresentationChartFont(result, { fontFamily: font });
  text(slide, 'Trial means. Sample SD and unbounded 95% Student-t intervals are in the report.', 80, 616, 1110, 34, 20, false, '#596875');
}

{
  const first = deck.slides.add();
  first.background.fill = '#F2F5F8';
  text(first, 'Sampled telemetry and\nadaptive flood detection', 80, 145, 1120, 180, 60, true, '#17324D');
  text(first, 'A controlled 5G-NIDD replay study in an SDN emulator', 84, 365, 1080, 90, 32);
  text(first, '54 accepted live trials\nIndependent packet truth and reproducible measurements', 84, 500, 1080, 100, 26, false, '#596875');
  first.speakerNotes.text = 'Official dataset: https://arxiv.org/abs/2212.01298 and https://doi.org/10.23729/e80ac9df-d9fb-47e7-8d0d-01384a415361. Existing HAT/ADWIN and sFlow methods; no new algorithm or physical 5G claim.';
}
body(slide('Study design', 'Source: configs/research_protocol.json, frozen before primary outcomes. Local protocol, not an external preregistration registry.'), [
  'Six switch sampling values: N = 1, 2, 5, 10, 20 and 50. Three repeats for each scenario and N.',
  'Baseline, held-out SYN introduction, and a constructed family/cadence shift. Every selected class replays at 100 packets/s.',
  'Primary windows: 0.1 seconds. A separate one-second sensitivity rebuilds features from saved raw exports.',
  'N = 1 is the unsampled M3 reference. M1/M2 and automatic mitigation are outside this study.',
]);
body(slide('Independent truth and causal prediction', 'Sources: docs/research-methods.md; sdn/live_ground_truth.py; src/m3/causal_live.py. sFlow specification https://sflow.org/sflow_version_5.txt. Labels derive from authoritative original flow matches, not filenames or sampled predictions.'), [
  'Sender and receiver captures agree on every original frame. Kernel receive timestamps define physical attack onset.',
  'The detector predicts before reading that window’s independent label. Scoring precedes learning.',
  'The 0.5-second parameter holds a completed window before prediction. The oracle label is then read immediately.',
  'Empty sampled windows remain scored when original-packet truth exists. Unknown original truth stays unscored.',
]);
chart(slide('Mean attack F1 by sampling rate'), 'f1', 'Attack F1', { min: 0, max: 1 });
{
  const page = slide('Measured control-channel cost');
  chart(page, 'sflow_bandwidth_kbit_s', 'sFlow IP-layer kbit/s');
  page.speakerNotes.text += '\nCost basis: sFlow IPv4+UDP+payload; OpenFlow captured IP bytes. Full combined-channel Pareto analysis is in the report. No physical wire/FCS or switch-CPU claim.';
}
chart(slide('False positives remain visible'), 'false_positive_rate', 'False-positive rate', { min: 0, max: 1 });
{
  const page = slide('Physical detection and recovery');
  const lines = scenarios.map(scenario => {
    const delays = [1, 50].map(rate => {
      const item = metric(scenario, rate, 'detection_time_seconds');
      return `N=${rate}: ${fmt(item.mean)} s, ${item.n}/3 detected`;
    });
    return `${scenario[0].toUpperCase() + scenario.slice(1)}\n${delays.join('     ')}`;
  });
  body(page, lines, 155);
  const recovery = metric('drift', 2, 'post_drift_recovery_seconds');
  text(page, `Drift recovery at N=2: ${fmt(recovery.mean)} s, ${recovery.n}/3 recovered with the fixed criterion.`, 72, 510, 1128, 45, 25);
  text(page, 'First post-warm-up attack episode. Means include detections only; misses are censored, never zero.', 72, 565, 1128, 62, 25, false, '#596875');
}
{
  const page = slide('Previously held-out SYN family');
  const result = page.charts.add('bar', {
    position: { left: 70, top: 165, width: 1130, height: 410 }, categories: rates.map(String),
    series: [{ name: 'SYN recall', values: rates.map(rate => chartValue(metric('unseen', rate, 'unseen_attack_recall').mean)), fill: palette[2] }],
    barOptions: { direction: 'column', grouping: 'clustered' }, hasLegend: false,
    yAxis: { title: 'Held-out family recall', min: 0, max: 1, numberFormatCode: '0%', textStyle: { fontSize: 23 } },
    xAxis: { title: 'Switch sampling denominator N', textStyle: { fontSize: 23 } },
  });
  applyPresentationChartFont(result, { fontFamily: font });
  text(page, 'SYN is absent during warm-up. Subsequent oracle labels allow adaptation, so this is not a broad zero-day guarantee.', 72, 606, 1128, 62, 24, false, '#596875');
}
{
  const page = slide('Descriptive sampling recommendations');
  const fronts = await read('pareto_recommendations.json');
  const lines = fronts.filter(front => front.recommendation).map(front => {
    const selected = front.recommendation;
    const scenario = JSON.parse(front.comparison_group).scenario;
    return `${scenario[0].toUpperCase() + scenario.slice(1)}: N=${selected.sampling_rate}\nMean F1 ${fmt(selected.f1)} and combined IP cost ${fmt(selected.combined_bandwidth_kbit_s)} kbit/s`;
  });
  body(page, lines, 155);
  text(page, 'Fixed equal-weight distance to the normalized ideal. These are in-study suggestions, not universal optima.', 72, 565, 1128, 62, 24, false, '#596875');
}
body(slide('Evidence, limits and demonstration', 'Source files: research/M3_Research_Report.md, docs/research-methods.md, docs/research-related-work.md, research/results/derived_trial_evidence.zip. HAT: https://doi.org/10.1007/978-3-642-03915-7_22. ADWIN: https://doi.org/10.1137/1.9781611972771.42. Prior sampling study: https://doi.org/10.1016/j.future.2019.10.015.'), [
  'Reproduce from the official dataset, frozen protocol, source mappings and trial configurations. Failed attempts remain recorded.',
  'The report includes paired uncertainty, nonadaptive-tree and majority ablations, and one-second sensitivity.',
  'Constructed timing, flow correlations, oracle labels and one shared-host emulator limit generalization. No physical 5G deployment claim.',
  'Demo: open the local dashboard, choose a validated live trial, inspect predictions and cost, then compare compatible N values.',
]);

await fs.mkdir(staging, { recursive: true });
await fs.mkdir(path.dirname(finalPath), { recursive: true });
for (const [index, page] of deck.slides.items.entries()) {
  const png = await deck.export({ slide: page, format: 'png', scale: 1 });
  await fs.writeFile(path.join(staging, `slide-${String(index + 1).padStart(2, '0')}.png`), new Uint8Array(await png.arrayBuffer()));
}
const candidatePath = path.join(staging, 'candidate-reviewed-v6.pptx');
await (await PresentationFile.exportPptx(deck)).save(candidatePath);
const result = await finalizePresentation({
  workspaceDir: root, candidatePath, finalPath,
  pythonExecutable: path.join(runtime, 'python/python.exe'),
  integrityValidatorPath: path.join(skill, 'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath: path.join(skill, 'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs: ['--expected-slide-size-emu', '12192000,6858000', '--validate-bullet-geometry', '--validate-heading-fit'],
  requiredNativeChartOwnerSlides: [4, 5, 6, 8], requiredNativeTableOwnerSlides: [],
  fontPolicy: { basis: 'design', families: [font] },
  materializeLiteralChartWorkbooks: true,
  verifyArtifactToolImport: true,
  receiptPath: path.join(staging, 'validation-reviewed.json'),
});
console.log(JSON.stringify({ slides: deck.slides.items.length, finalPath, result }));
