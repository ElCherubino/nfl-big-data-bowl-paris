import test from 'node:test';
import assert from 'node:assert/strict';
import {leagueRows, quoteFor, PERIOD, formatRate} from './broadcaster.js';

const row = (nflId, n, rank, percentile = 89) => ({nflId, displayName:`Back ${nflId}`, position:'RB', teams:['A'], counts:{evaluatedPlays:n}, eligible:n >= 20, rank, percentile, rawRate:0.4, shrunkRate:0.3});
test('excludes n=19; retains n=20 and the published ranking for ties', () => {
  const rb = {reference:{minN:20}, rows:[row('a',19,null),row('b',20,2),row('c',21,1)]};
  assert.deepEqual(leagueRows(rb).map(r => r.nflId), ['c','b']);
  assert.equal(leagueRows(rb)[0].rawRate,0.4);
  assert.equal(leagueRows(rb)[0].shrunkRate,0.3);
  assert.deepEqual(rb.rows.map(r => r.nflId), ['a','b','c']);
});
test('empty cohort is empty; incompatible data cannot become a ranking', () => {
  assert.deepEqual(leagueRows({reference:{minN:20},rows:[]}),[]);
  assert.equal(leagueRows(null),null);
  assert.equal(leagueRows({reference:{minN:20},rows:[row('a',20,null)]}),null);
});
test('top ten language requires a published percentile of at least ninety', () => {
  const below = quoteFor(row('a',20,1,89));
  assert.match(below,/percentile de 89/);
  assert.doesNotMatch(below,/top 10/);
  const boundary = quoteFor(row('a',20,1,90));
  assert.match(boundary,/top 10 %/);
  assert.match(boundary,/20 routes pressurées évaluables/);
  assert.ok(boundary.includes(PERIOD));
  assert.doesNotMatch(quoteFor(row('a',20,1,null)),/top 10|percentile de/);
});
test('null rates remain unavailable and percentage display uses fractions', () => {
  assert.equal(formatRate(null),'Indisponible');
  assert.equal(formatRate(0.3),'30 %');
});
