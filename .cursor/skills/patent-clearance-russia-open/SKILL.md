---
name: patent-clearance-russia-open
description: Conduct preliminary patent clearance / freedom-to-operate research for the Russian Federation using only open sources and official registers.
---

# Patent clearance research for Russia using open sources

Use this skill when a user asks to check whether a product, process, device, software-implemented technical solution, utility model, or industrial design appears free to use in the Russian Federation.

This skill is a research workflow, not a legal opinion. Patent clearance requires human review of claims, legal status, exceptions, and infringement doctrines.

## Open-source-only rule

Allowed:

- FIPS information retrieval system: <https://www.fips.ru/elektronnye-servisy/informatsionno-poiskovaya-sistema/>
- FIPS open registers: <https://www1.fips.ru/registers-web/>
- Rospatent search platform: <https://searchplatform.rospatent.gov.ru/>
- EAPO Eurasian patent register: <https://www.eapo.org/ru/?patents=reestr>
- Espacenet: <https://worldwide.espacenet.com/>
- WIPO PATENTSCOPE: <https://patentscope.wipo.int/search/en/search.jsf>
- Google Patents: <https://patents.google.com/>
- The Lens: <https://www.lens.org/lens/search/patent/list>

Not allowed unless the user explicitly changes the scope:

- Paid databases or closed APIs such as Derwent, PatSnap, PatSeer, Questel Orbit, LexisNexis PatentSight, STN/CAS.
- Sources requiring private credentials, subscriptions, or non-public scraping.
- Treating AI-generated summaries as a substitute for patent claims or official register status.

## Recommended MCP tools

If the `patent-clearance-open` MCP server is available, use:

1. `validate_open_sources_policy` before accepting a source list.
2. `build_patent_clearance_search_plan` after the product features and search terms are known.
3. `evaluate_patent_clearance_candidates` after collecting candidate RU/EA documents from open sources.
4. `generate_open_fto_report` for a structured markdown report scaffold.

## Workflow

1. Define scope.
   - Territory: Russian Federation.
   - Include RU patents, RU utility models, RU published applications, industrial designs where relevant.
   - Include EA patents/applications because Eurasian patents can be effective in Russia.
   - Define product, process, use case, launch/manufacturing/sale activities, and date of analysis.

2. Decompose the object.
   - List essential technical features.
   - Separate optional features from required features.
   - Capture alternative embodiments and equivalents.
   - Identify likely IPC/CPC classes.

3. Build search terms.
   - Russian terms first for RU sources.
   - English terms for international discovery.
   - Include synonyms, functional terms, material/process terms, and competitor names.
   - Include IPC/CPC codes and known patent numbers where available.

4. Search open sources.
   - Search FIPS and Rospatent first for RU documents.
   - Search EAPO for EA documents and status in Russia.
   - Use Espacenet, PATENTSCOPE, Google Patents, and Lens to expand patent families, identify classifications, and find foreign equivalents.
   - Keep the source URL and search query for every material result.

5. Verify legal status in official registers.
   - RU: verify in FIPS open registers.
   - EA: verify in the EAPO register and check whether the patent is maintained for Russia.
   - Pending applications: mark as monitoring items, not current blocking rights.
   - Expired/lapsed documents: verify reinstatement risk, extensions, and related active family members.

6. Analyze claims.
   - Read independent claims in the original language or official publication.
   - Make a claim chart: claim limitation -> product feature -> evidence -> match/no match/unclear.
   - A high-risk item usually requires every limitation of at least one active independent claim to be present literally or by possible equivalent.

7. Report results.
   - Identify high, medium, monitor, unknown, low-verify, and low items.
   - Cite official source URLs.
   - State assumptions and missing evidence.
   - Recommend next actions: design-around, legal opinion, invalidity search, license inquiry, or monitoring.

## Output format

Use this structure:

```markdown
# Patent clearance research report

## 1. Scope
- Territory:
- Product/process:
- Sources:
- Date:
- Limitations:

## 2. Product feature decomposition
| ID | Feature | Required? | Evidence |
| --- | --- | --- | --- |

## 3. Search strategy
| Source | Query | URL | Purpose |
| --- | --- | --- | --- |

## 4. Candidate documents
| Number | Type | Owner | Status | Source | Relevance |
| --- | --- | --- | --- | --- | --- |

## 5. Claim charts
| Patent | Claim limitation | Product feature | Match | Notes |
| --- | --- | --- | --- | --- |

## 6. Risk register
| Risk | Document | Reason | Missing checks | Next action |
| --- | --- | --- | --- | --- |

## 7. Preliminary conclusion
This is a preliminary research aid, not a legal opinion.
```

## Risk labels

- `high`: official status active or potentially active, and claim-feature mapping suggests most/all claim limitations are present.
- `medium`: active or potentially active, but mapping is partial or uncertain.
- `monitor`: pending RU/EA application or published application with relevant overlap.
- `family_check`: technically relevant foreign document; check whether an RU/EA family member exists and is in force.
- `unknown`: status or claim evidence is missing.
- `low_verify`: appears expired/lapsed/inactive, but official status, reinstatement, extension, or related rights still need verification.
- `low`: no meaningful claim-feature overlap found.
