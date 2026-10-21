# NFL Coach Lab — Frontend concept

Desktop-first, NFL-inspired coaching analytics dashboard. **Frontend visual prototype only**: all metrics, player names, team selections, play diagrams and percentages are synthetic demo content. No backend, analytics calculation, account system, or NFL tracking feed.

## Run locally

Requires Node.js >= 22.12 and npm.

```bash
npm install
npm run dev
```

Open the URL printed by Vite. To compile: `npm run build`.

## UI preview

- Dark, NFL-inspired design with red highlights, condensed display typography and dense analytical panels.
- Desktop sidebar, mobile drawer and responsive dashboard layout.
- Four illustrative KPI cards, SVG field routes, coverage bars and player table.
- Local-only demo interactions: team/timeframe/play selection, navigation labels, player search and role filtering. Buttons not yet backed by services show a notice.

## Design and licensing

Visual direction follows the public Premium Frontend Skill design workflow: brand-first hierarchy, intentional visual density, accessible focus states, reduced-motion fallback and coherent interactions. No external React Bits component code has been copied into the repository; for this dense dashboard, stable SVG visualization and lightweight native state were chosen over decorative motion. React Bits components may be integrated after validating the dashboard layout.

The NFL shield is referenced from Wikimedia's public URL, not bundled. The NFL logo and team names are third-party marks. This is an **unofficial hackathon concept, not affiliated with or endorsed by the NFL**. Confirm permitted asset use before public deployment.
