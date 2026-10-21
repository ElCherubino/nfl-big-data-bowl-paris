import React from 'react';
import './replay.css';

const number = (value, suffix = '') => typeof value === 'number' ? `${value.toFixed(1)}${suffix}` : 'Non renseigné';

/** Published checks at the first pressure; each row is coloured by whether its threshold was met. */
export default function PressurePanel({ observation, parameters = {}, pressure }) {
  const checks = [
    ['routeRunner', 'En route', 'Oui', ''],
    ['open', 'Défenseur le plus proche du back', `> ${parameters.openDistanceYd ?? '—'} yd`, ' yd'],
    ['inRange', 'Distance back–QB', `< ${parameters.maxQbDistanceYd ?? '—'} yd`, ' yd'],
    ['pastLine', 'Progression depuis la ligne', `≥ ${parameters.minLosProgressYd ?? '—'} yd`, ' yd'],
    ['facingQb', 'Écart d’orientation vers le QB', `< ${parameters.maxFacingAngleDeg ?? '—'}°`, '°'],
  ];
  return <section className="replay-pressure" aria-label="Mesures publiées à la pression">
    <h3>Mesures à la pression</h3>
    {pressure?.status === 'none' ? <p>Aucune pression détectée sur cette action.</p> :
      <div className="replay-table-scroll"><table className="replay-checks"><thead><tr><th>Condition</th><th>Valeur</th><th>Seuil</th><th>Seuil atteint</th></tr></thead><tbody>
        {checks.map(([key, label, threshold, unit]) => {
          const check = observation?.checks?.[key];
          const met = check?.passed === true ? 'met' : check?.passed === false ? 'missed' : 'unknown';
          return <tr key={key} className={`check-${met}`}><th scope="row">{label}</th><td>{typeof check?.value === 'boolean' ? (check.value ? 'Oui' : 'Non') : number(check?.value, unit)}</td><td>{threshold}</td><td><span className="check-result">{{ met: '✓ Oui', missed: '✗ Non', unknown: '? Indéterminé' }[met]}</span></td></tr>;
        })}
      </tbody></table></div>}
  </section>;
}
