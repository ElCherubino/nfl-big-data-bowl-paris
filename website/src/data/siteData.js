const supportedVersion = '1.0.0';

export class DataError extends Error {
  constructor(code, message, resource) {
    super(message); this.name = 'DataError'; this.code = code; this.resource = String(resource);
  }
}

export function createSiteData({manifestUrl, fetcher = globalThis.fetch} = {}) {
  const base = typeof location === 'undefined' ? 'http://localhost/' : location.href;
  const root = new URL(manifestUrl || `${import.meta.env?.BASE_URL || '/'}data/manifest.json`, base);
  const dataRoot = new URL('.', root);
  let manifest;
  let catalog;
  const cache = new Map();
  const fail = (code, message, resource) => { throw new DataError(code, message, resource); };
  function resourceUrl(path) {
    if (typeof path !== 'string' || !path || path.includes('\\')) return fail('INVALID_DOCUMENT', 'Invalid data path.', path);
    const url = new URL(path, root);
    if (url.origin !== dataRoot.origin || !url.pathname.startsWith(dataRoot.pathname) || url.search || url.hash)
      return fail('INVALID_DOCUMENT', 'The resource leaves the data folder.', path);
    return url;
  }
  async function read(url, signal, envelope = true) {
    let response;
    try { response = await fetcher(url, {signal}); }
    catch (error) {
      if (error.name === 'AbortError') throw error;
      return fail('NETWORK_ERROR', 'Unable to load the data. Check the server, then retry.', url);
    }
    if (!response.ok) return fail(response.status === 404 ? 'NOT_FOUND' : 'NETWORK_ERROR',
      response.status === 404 ? 'Publication missing. Run ./run --build-data.' : 'The server is not responding correctly.', url);
    let doc;
    try { doc = await response.json(); }
    catch { return fail('INVALID_DOCUMENT', 'The resource is not a valid JSON document.', url); }
    if (!doc || typeof doc !== 'object' || Array.isArray(doc)) return fail('INVALID_DOCUMENT', 'Invalid data document.', url);
    if (doc.schemaVersion !== supportedVersion) return fail('UNSUPPORTED_SCHEMA', 'Data version incompatible. Regenerate the publication.', url);
    if (typeof doc.generationId !== 'string' || !doc.generationId) return fail('INVALID_DOCUMENT', 'Data generation missing.', url);
    if (envelope && doc.generationId !== manifest.generationId) return fail('GENERATION_MISMATCH', 'The data belong to different generations. Reload the publication.', url);
    if (envelope && !Object.hasOwn(doc, 'data')) return fail('INVALID_DOCUMENT', 'Resource content missing.', url);
    return envelope ? doc.data : doc;
  }
  async function loadManifest(signal) {
    if (manifest) return manifest;
    const doc = await read(root, signal, false);
    if (!doc.resources || !doc.parameters || !doc.period || !doc.counts) return fail('INVALID_DOCUMENT', 'Incomplete manifest.', root);
    for (const key of ['games', 'seasonRb', 'seasonTeam', 'analysis', 'quality']) resourceUrl(doc.resources[key]);
    manifest = doc;
    return manifest;
  }
  async function loadCatalog({signal} = {}) {
    await loadManifest(signal);
    if (!catalog) {
      const rows = await read(resourceUrl(manifest.resources.games), signal);
      if (!Array.isArray(rows) || rows.some(g => typeof g.gameId !== 'string' || !g.gameResource)) return fail('INVALID_DOCUMENT', 'Invalid game catalogue.', root);
      if (new Set(rows.map(g => g.gameId)).size !== rows.length) return fail('INVALID_DOCUMENT', 'Duplicate game IDs.', root);
      rows.forEach(g => resourceUrl(g.gameResource));
      catalog = rows;
    }
    return {manifest, games: catalog};
  }
  async function loadSeason({signal} = {}) {
    await loadManifest(signal);
    const [rb, teams, analysis] = await Promise.all(['seasonRb', 'seasonTeam', 'analysis'].map(k => read(resourceUrl(manifest.resources[k]), signal)));
    if (!Array.isArray(rb?.rows) || !Array.isArray(teams?.rows) || !Array.isArray(analysis?.comparisonRows)) return fail('INVALID_DOCUMENT', 'Invalid season tables.', root);
    return {manifest, rb, teams, analysis};
  }
  async function loadGame(gameId, {signal} = {}) {
    await loadCatalog({signal});
    const game = catalog.find(g => g.gameId === String(gameId));
    if (!game) return fail('INVALID_DOCUMENT', 'This game is not in the catalogue.', gameId);
    if (cache.has(game.gameId)) {
      const data = cache.get(game.gameId); cache.delete(game.gameId); cache.set(game.gameId, data); return data;
    }
    const data = await read(resourceUrl(game.gameResource), signal);
    if (data?.gameId !== game.gameId || !Array.isArray(data.plays) || !data.players || !Array.isArray(data.rbSummary)) return fail('INVALID_DOCUMENT', 'Invalid game bundle.', game.gameResource);
    cache.set(game.gameId, data);
    while (cache.size > 2) cache.delete(cache.keys().next().value);
    return data;
  }
  return {loadCatalog, loadSeason, loadGame};
}

export const siteData = createSiteData();
export const loadCatalog = siteData.loadCatalog;
export const loadSeason = siteData.loadSeason;
export const loadGame = siteData.loadGame;
