# Journal verification log — Analytica Chimica Acta (ACA)

Each criterion from the brief, with the evidence actually obtained (2026-11-15). Nothing below is inferred
without being labelled as such.

| # | Criterion | Result | Evidence / source | Status |
|---|---|---|---|---|
| 1 | Indexed in JCR | Yes (Chemistry, Analytical) | Peeref listing "JCR 2024 edition, CHEMISTRY, ANALYTICAL"; continuous SCIE coverage | Secondary |
| 2 | Q1 in JCR | Q1 (JCR 2024 edition) | Peeref | Secondary; 2026 release not directly checked |
| 3 | Higher JIF preferred | 6.1 (5y 5.8) | shop.elsevier.com/journals/analytica-chimica-acta/0003-2670 | Official page (edition unlabelled) |
| 4–5 | Acceptance < 60 d preferred, ~30 d ideal | Median 60.5 d; 50.0% <= 60 d; 90.3% <= 100 d | PubMed history dates, n=300, tools/timeline_stats.py | **Measured** |
| 6–7 | Do not confuse decision vs acceptance | The 60.5 d figure is submission→acceptance (PubMed 'received'→'accepted'); first-decision (17 d) is a separate third-party figure | — | Distinguished |
| 8 | Verify actual submission-to-acceptance | Done per-article (n=300) | round3_results.jsonl | **Measured** |
| 9 | State if unverifiable | Elsevier's own insights page could not be accessed (HTTP 403) | — | Disclosed |
| 10 | No fabricated rates | No acceptance rate is claimed | — | — |
| 11–13 | Quartile / JIF / category | See 1–3 | — | Partially verified |
| 14 | Official scope | "new methodologies ... chemometric techniques ... data treatment that truly demonstrate new principles" | Elsevier shop page | Official |
| 15 | Topic fits journal | Chemometric methodology for multivariate calibration (see topic selection) | 2026 ACA papers on calibration transfer & domain-adaptive calibration | Verified |
| 16–17 | Recent comparable papers | >= 20 ACA chemometrics papers 2024–2026 retrieved (literature/tools/aca_chemometrics_2024_2026.json) | PubMed | Verified |
| 18 | Data/code/ethics requirements | Data availability section present in all inspected articles; Elsevier generative-AI declaration policy applies | Europe PMC full texts | Verified (anatomy) |
| 24–26 | Legitimacy / integrity | Elsevier flagship analytical title since 1947; no evidence found of Clarivate suspension | — | No concern found |
| — | APC | Hybrid; USD 4,620 optional OA, subscription free | Elsevier APC spreadsheet | Official |

## Unverifiable items (explicit)
- Clarivate 2026-release quartile and JIF (subscription required).
- Official Guide-for-Authors text (blocked); requirements derived from published article anatomy.
- Elsevier's published "submission to acceptance" metric (blocked); replaced by direct measurement.
