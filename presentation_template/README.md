# Presentation template — agents MUST read this

**Reference only — not a pre-built hackathon submission.** This directory provides an editable, data-free deck generator and presentation structure for rehearsal. The event rules recorded in the root README prohibit preparing competition-specific slides, visuals and analyses beforehand. **Do NOT put this generated deck in the judged submission or reuse its slides during the event without explicit permission from organizers.** Create the actual presentation during the permitted window. The event may not even require PowerPoint; prioritize a verified metric, working demo and required GitHub submission.

## What MUST appear if a slide deck is permitted

1. **Customer obsession:** name exactly **one primary user**, their decision, and pain before mentioning technology.
2. **Clear discovery:** one falsifiable, measured claim; definition, unit, comparison group and sample count. NEVER invent results.
3. **Why new / why now:** compare with established NFL Next Gen Stats; don't rename separation or YAC and pretend it's novel.
4. **How it works:** concrete input fields → specific calculation/algorithm → tests → output. An LLM is optional explanation, not the numeric engine.
5. **Proof and wow:** one clear annotated replay or evidence visualization using released data. No decorative 3D or fake example presented as real.
6. **User action and impact:** what does a coach, scout, reporter or commentator do differently afterward?
7. **Trust and uncertainty:** disclose missing fields, sample size, selection bias and correlation/causation boundaries.
8. **Demo + delivery:** show a working artifact and how to reproduce it. Don't replace the demo with slides.
9. **Timing:** optimize for the organizer's actual pitch/demo allowance; this deck is a *menu* of slides, not a requirement to present all eight.
10. **Compliance:** no pre-event analytics, figures or competition project materials in the submission. Do not use NFL/Amazon logos implying affiliation.

## Amazon-*inspired* storytelling, not an Amazon official template

Based on publicly stated [Amazon Leadership Principles](https://www.aboutamazon.com/about-us/leadership-principles): **Customer Obsession, Invent and Simplify, Dive Deep, Earn Trust, Bias for Action, Deliver Results and Think Big**.

Style: strong conclusion titles, navy/white, restrained orange emphasis, limited text per slide, metric first, evidence legible. Amazon often uses **written narratives** for internal decision-making; this is a student hackathon adaptation, **not** a claim that Amazon evaluates pitches with these exact slides or scoring criteria.

## Slides in the practice template

| Slide | Narrative job | Mandatory content if used |
|---|---|---|
| 1 — Claim | Lead with the discovery | Who cares and what changed |
| 2 — Customer | Work backwards | User, pain, action |
| 3 — Metric | One precise measurable insight | Metric, baseline and n |
| 4 — Evidence | Show that it happened | Verified replay/plot, correct units |
| 5 — Algorithm | Prove implementation | Data → calculation → test → output |
| 6 — Trust | Show what is known and unknown | Tests and limits |
| 7 — Benefit | Link to a buyer/user | Clear next decision |
| 8 — Demo | Finish with a working proof | Play → proof → impact |

## How to obtain the editable PowerPoint

The repository includes `generate_template.js`, using the open-source `pptxgenjs` library and ordinary editable PowerPoint shapes. A GitHub workflow also generates the binary `nfl_aws_evidence_first_template.pptx` in this directory when changes are pushed, if Actions write permissions permit.

```bash
cd presentation_template
npm install
npm run build
```

No data is downloaded, no NFL content is generated, and no Amazon/AWS logo is embedded. The deck remains editable and has placeholders only.

## Failure conditions for an AI agent

**STOP rather than filling slides** if the event rules ban prebuilt materials, official data has not been released, a metric is unverified, or source-specific images/brand usage is unlicensed. Do not automatically populate slide placeholders before the official start.
