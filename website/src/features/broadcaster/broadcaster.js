export const PERIOD = '2021 · semaines 1–8';
export const formatNumber = value => value.toLocaleString('fr-FR', { maximumFractionDigits: 1 });
export const formatRate = value => value == null ? 'Indisponible' : `${formatNumber(value * 100)} %`;

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
  const standing = row.percentile == null ? 'figure parmi les backs éligibles' :
    row.percentile >= 90 ? 'se situe dans le top 10 % des backs éligibles' :
      `affiche un percentile de ${formatNumber(row.percentile)} parmi les backs éligibles`;
  return `${row.displayName} ${standing} pour la disponibilité sous pression, sur ${formatNumber(row.counts.evaluatedPlays)} routes pressurées évaluables (${PERIOD}).`;
}
