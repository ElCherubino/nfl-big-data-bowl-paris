import React from 'react';
import { STATUS_LABELS } from './replay.js';
import './replay.css';

const number = (value, suffix = '') => typeof value === 'number' ? `${value.toFixed(1)}${suffix}` : 'Non renseigné';

/** Fixed published observation, with current time kept separate from its verdict. */
export default function PressurePanel({ observation, parameters = {}, currentTime, currentState, pressure, pressureFrameId }) {
  const checks = [
    ['routeRunner', 'En route', 'Oui', ''],
    ['open', 'Défenseur le plus proche du back', `> ${parameters.openDistanceYd ?? '—'} yd`, ' yd'],
    ['inRange', 'Distance back–QB', `< ${parameters.maxQbDistanceYd ?? '—'} yd`, ' yd'],
    ['pastLine', 'Progression depuis la ligne', `≥ ${parameters.minLosProgressYd ?? '—'} yd`, ' yd'],
    ['facingQb', 'Écart d’orientation vers le QB', `< ${parameters.maxFacingAngleDeg ?? '—'}°`, '°'],
  ];
  return <section className="replay-pressure" aria-label="Mesures publiées à la pression">
    <div className="replay-panel-heading"><h3>Mesures à la pression</h3><span>Frame {pressureFrameId ?? observation?.pressureFrameId ?? '—'}</span></div>
    <p className="replay-current">Instant affiché : {number(currentTime, ' s')} · {STATUS_LABELS[currentState?.status] ?? '? Indéterminé'}</p>
    {pressure?.status === 'none' ? <p>Aucune pression détectée → non compté.</p> : <>
      <p>Verdict fixe : <strong>{STATUS_LABELS[observation?.status] ?? '? Indéterminé'}</strong> · {observation?.counted ? 'Compté' : 'Non compté'}</p>
      <div className="replay-table-scroll"><table className="replay-checks"><thead><tr><th>Condition</th><th>Valeur</th><th>Seuil publié</th><th>Résultat</th></tr></thead><tbody>
        {checks.map(([key, label, threshold, unit]) => {
          const check = observation?.checks?.[key];
          return <tr key={key}><th scope="row">{label}</th><td>{typeof check?.value === 'boolean' ? (check.value ? 'Oui' : 'Non') : number(check?.value, unit)}</td><td>{threshold}</td><td title={check?.reason ?? ''}>{check?.passed === true ? '✓ Oui' : check?.passed === false ? '✗ Non' : '? Indéterminé'}{check?.reason && <small>{check.reason}</small>}</td></tr>;
        })}
      </tbody></table></div>
      {pressure?.status === 'detected' && <p>Défenseur déclencheur : {pressure.defenderId ?? 'inconnu'} · distance au QB : {number(pressure.distanceYd, ' yd')} · pression à {number(pressure.timeS, ' s')}. Cette proximité ne constitue pas une attribution de couverture.</p>}
    </>}
    {(observation?.exclusionReason || pressure?.reason) && <p className="replay-note">Motif : {observation?.exclusionReason ?? pressure.reason}</p>}
    {currentState && <details className="replay-current-checks"><summary>Conditions à l’instant affiché</summary>
      <p>Mesures de la frame courante, distinctes du verdict fixé à la première pression. Elles ne modifient aucun compte publié.</p>
      <div className="replay-table-scroll"><table className="replay-checks"><caption>Conditions courantes · {number(currentTime, ' s')}</caption><thead><tr><th>Condition</th><th>Valeur</th><th>Seuil publié</th><th>Résultat</th></tr></thead><tbody>
        {checks.map(([key, label, threshold, unit]) => {
          const check = currentState.checks?.[key];
          return <tr key={key}><th scope="row">{label}</th><td>{typeof check?.value === 'boolean' ? (check.value ? 'Oui' : 'Non') : number(check?.value, unit)}</td><td>{threshold}</td><td>{check?.passed === true ? '✓ Oui' : check?.passed === false ? '✗ Non' : '? Indéterminé'}{check?.reason && <small>{check.reason}</small>}</td></tr>;
        })}
      </tbody></table></div>
    </details>}
  </section>;
}
