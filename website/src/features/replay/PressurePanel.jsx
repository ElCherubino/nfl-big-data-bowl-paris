import React from 'react';
import './replay.css';

const number = (value, suffix = '') => typeof value === 'number' ? `${value.toFixed(1)}${suffix}` : 'Not available';

/** Published checks at the first pressure; each row is coloured by whether its threshold was met. */
export default function PressurePanel({ observation, parameters = {}, pressure }) {
  const checks = [
    ['routeRunner', 'Running a route', 'Yes', ''],
    ['open', 'Nearest defender to the back', `> ${parameters.openDistanceYd ?? '—'} yd`, ' yd'],
    ['inRange', 'Back–QB distance', `< ${parameters.maxQbDistanceYd ?? '—'} yd`, ' yd'],
    ['pastLine', 'Progress from the line', `≥ ${parameters.minLosProgressYd ?? '—'} yd`, ' yd'],
    ['facingQb', 'Orientation gap to the QB', `< ${parameters.maxFacingAngleDeg ?? '—'}°`, '°'],
  ];
  return <section className="replay-pressure" aria-label="Published measurements at pressure">
    <h3>Measurements at pressure</h3>
    {pressure?.status === 'none' ? <p>No pressure detected on this play.</p> :
      <div className="replay-table-scroll"><table className="replay-checks"><thead><tr><th>Condition</th><th>Value</th><th>Threshold</th><th>Threshold met</th></tr></thead><tbody>
        {checks.map(([key, label, threshold, unit]) => {
          const check = observation?.checks?.[key];
          const met = check?.passed === true ? 'met' : check?.passed === false ? 'missed' : 'unknown';
          return <tr key={key} className={`check-${met}`}><th scope="row">{label}</th><td>{typeof check?.value === 'boolean' ? (check.value ? 'Yes' : 'No') : number(check?.value, unit)}</td><td>{threshold}</td><td><span className="check-result">{{ met: '✓ Yes', missed: '✗ No', unknown: '? Undetermined' }[met]}</span></td></tr>;
        })}
      </tbody></table></div>}
  </section>;
}
