export const PERIOD = '2021 · weeks 1–8';
export const formatNumber = value => value.toLocaleString('en-US', { maximumFractionDigits: 1 });
export const formatRate = value => value == null ? 'Unavailable' : `${formatNumber(value * 100)}%`;

// Eligibility and ranks are published by the pipeline; display order follows those ranks.
export function leagueRows(rb) {
  if (!rb || !Array.isArray(rb.rows) || !Number.isInteger(rb.reference?.minN)) return null;
  const rows = rb.rows.filter(row => row.eligible && row.counts?.evaluatedPlays >= rb.reference.minN);
  if (rows.some(row => !Number.isInteger(row.rank) || row.rank < 1 ||
    !Number.isFinite(row.shrunkRate) || !Number.isFinite(row.rawRate) ||
    !Array.isArray(row.teams) || !row.displayName ||
    (row.percentile != null && (!Number.isFinite(row.percentile) || row.percentile < 0 || row.percentile > 100)))) return null;
  return [...rows].sort((a, b) => a.rank - b.rank);
}

export function quoteFor(row) {
  const standing = row.percentile == null ? 'ranks among eligible backs' :
    row.percentile >= 90 ? 'ranks in the top 10% of eligible backs' :
      `sits at the ${formatNumber(row.percentile)} percentile among eligible backs`;
  return `${row.displayName} ${standing} for availability under pressure, over ${formatNumber(row.counts.evaluatedPlays)} evaluable pressured routes (${PERIOD}).`;
}
