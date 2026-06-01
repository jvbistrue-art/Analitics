#!/usr/bin/env python3
"""MCP tools for open-source Russia patent clearance checks.

The server intentionally avoids paid databases and authenticated APIs. It helps
an agent build an auditable search plan, collect source links, and create a
preliminary risk register from documents verified in open registers.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import date
from typing import Any
from urllib.parse import quote_plus


DISCLAIMER = (
    "Preliminary research aid only. Patent clearance / freedom-to-operate "
    "requires claim construction, legal-status verification in official "
    "registers, and review by a qualified patent professional."
)

PAID_SOURCE_NAMES = {
    "derwent",
    "clarivate",
    "patsnap",
    "patseer",
    "questel",
    "orbit",
    "lexisnexis",
    "patent sight",
    "patentsight",
    "stn",
    "cas",
}


@dataclass(frozen=True)
class OpenSource:
    key: str
    name: str
    url: str
    role: str
    official: bool
    query_template: str | None = None
    notes: str = ""

    def search_url(self, query: str) -> str:
        if not self.query_template:
            return self.url
        return self.query_template.format(query=quote_plus(query))


OPEN_SOURCES: tuple[OpenSource, ...] = (
    OpenSource(
        key="fips_search",
        name="FIPS information retrieval system",
        url="https://www.fips.ru/elektronnye-servisy/informatsionno-poiskovaya-sistema/",
        role="Search Russian patent documents and applications by keywords, IPC, names, and numbers.",
        official=True,
        notes="Use for RU inventions, utility models, industrial designs, and applications. Full-text depth may depend on free/paid FIPS access.",
    ),
    OpenSource(
        key="fips_registers",
        name="FIPS open registers",
        url="https://www1.fips.ru/registers-web/",
        role="Verify official legal status and prosecution data for known Russian patent/application numbers.",
        official=True,
        notes="Primary source for RU legal status. Record status must be cited in the final report.",
    ),
    OpenSource(
        key="rospatent_platform",
        name="Rospatent search platform",
        url="https://searchplatform.rospatent.gov.ru/",
        role="Search Russian and international patent information, including AI-assisted similarity search where available.",
        official=True,
        notes="Open public platform; use results as discovery and verify legal status in official registers.",
    ),
    OpenSource(
        key="eapo_register",
        name="EAPO Eurasian patent register",
        url="https://www.eapo.org/ru/?patents=reestr",
        role="Check Eurasian patents and whether they are in force for the Russian Federation.",
        official=True,
        notes="EA patents may create blocking rights in Russia; verify country-by-country maintenance status.",
    ),
    OpenSource(
        key="espacenet",
        name="Espacenet",
        url="https://worldwide.espacenet.com/",
        role="Discover patent families, classifications, citations, and foreign equivalents.",
        official=False,
        query_template="https://worldwide.espacenet.com/patent/search?q={query}",
        notes="Use for broad discovery. Verify RU/EA status in FIPS/EAPO before drawing conclusions.",
    ),
    OpenSource(
        key="patentscope",
        name="WIPO PATENTSCOPE",
        url="https://patentscope.wipo.int/search/en/search.jsf",
        role="Search PCT publications and national-phase clues.",
        official=False,
        notes="Use to identify WO applications that may have entered RU or EA phase; verify in official RU/EA registers.",
    ),
    OpenSource(
        key="google_patents",
        name="Google Patents",
        url="https://patents.google.com/",
        role="Fast discovery search across patent families and machine translations.",
        official=False,
        query_template="https://patents.google.com/?q={query}",
        notes="Discovery only; not an official legal-status source.",
    ),
    OpenSource(
        key="lens",
        name="The Lens",
        url="https://www.lens.org/lens/search/patent/list",
        role="Open patent search, family exploration, and calculated legal-status hints.",
        official=False,
        query_template="https://www.lens.org/lens/search/patent/list?q={query}",
        notes="Legal status is derived from available data and must not replace official registers.",
    ),
)


def compact_list(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        return [values.strip()] if values.strip() else []
    if not isinstance(values, list):
        return []
    return [str(value).strip() for value in values if str(value).strip()]


def source_to_dict(source: OpenSource) -> dict[str, Any]:
    return {
        "key": source.key,
        "name": source.name,
        "url": source.url,
        "role": source.role,
        "official": source.official,
        "notes": source.notes,
    }


def validate_open_sources_policy(sources: list[str] | None = None) -> dict[str, Any]:
    """Check a proposed source list against the open-source-only policy."""

    proposed = compact_list(sources)
    blocked = []
    for item in proposed:
        normalized = item.casefold()
        if any(name in normalized for name in PAID_SOURCE_NAMES):
            blocked.append(item)

    allowed_keys = [source.key for source in OPEN_SOURCES]
    return {
        "compliant": not blocked,
        "blocked_sources": blocked,
        "allowed_open_sources": [source_to_dict(source) for source in OPEN_SOURCES],
        "allowed_source_keys": allowed_keys,
        "policy": (
            "Use public web sources and official open registers only. Do not use paid databases, "
            "private APIs, accounts, or scraped content behind access controls."
        ),
    }


def make_boolean_query(terms: list[str], ipc_codes: list[str] | None = None) -> str:
    quoted_terms = []
    for term in terms:
        normalized = " ".join(term.split())
        if not normalized:
            continue
        quoted_terms.append(f'"{normalized}"' if " " in normalized else normalized)

    query = " OR ".join(quoted_terms)
    ipc_parts = [f'IPC={code}' for code in compact_list(ipc_codes)]
    if query and ipc_parts:
        return f"({query}) AND ({' OR '.join(ipc_parts)})"
    if ipc_parts:
        return " OR ".join(ipc_parts)
    return query


def build_patent_clearance_search_plan(arguments: dict[str, Any]) -> dict[str, Any]:
    product_name = str(arguments.get("product_name", "")).strip() or "Unnamed product"
    description = str(arguments.get("product_description", "")).strip()
    technical_features = compact_list(arguments.get("technical_features"))
    keywords_ru = compact_list(arguments.get("keywords_ru"))
    keywords_en = compact_list(arguments.get("keywords_en"))
    ipc_codes = compact_list(arguments.get("ipc_codes"))
    assignees = compact_list(arguments.get("assignees"))

    ru_terms = keywords_ru + technical_features
    en_terms = keywords_en
    ru_query = make_boolean_query(ru_terms, ipc_codes)
    en_query = make_boolean_query(en_terms or ru_terms, ipc_codes)

    jurisdiction_filters = {
        "russia": "RU patents, RU utility models, RU patent applications, and PCT applications in RU national phase",
        "eurasian": "EA patents/applications with validity or potential validity in the Russian Federation",
        "pending": "Published applications are not blocking rights yet, but should be monitored until grant/refusal/withdrawal",
    }

    source_searches = []
    for source in OPEN_SOURCES:
        query = ru_query if source.key in {"fips_search", "fips_registers", "rospatent_platform", "eapo_register"} else en_query
        source_searches.append(
            {
                **source_to_dict(source),
                "suggested_query": query,
                "search_url": source.search_url(query) if query else source.url,
            }
        )

    search_steps = [
        "Define the product/process and split it into essential technical features.",
        "Search RU official sources first: FIPS search, Rospatent platform, and FIPS open registers for known numbers.",
        "Search EA sources because Eurasian patents may be enforceable in Russia.",
        "Use Espacenet, PATENTSCOPE, Google Patents, and Lens only for discovery and family expansion.",
        "For every potentially relevant RU/EA document, capture the independent claims and official legal-status evidence.",
        "Build a claim chart: each independent-claim limitation versus product feature evidence.",
        "Classify risks and list design-around, invalidity, licensing, or monitoring actions.",
    ]

    report_outline = [
        "# Patent clearance research report",
        f"Product: {product_name}",
        "",
        "## Scope",
        "- Territory: Russian Federation",
        "- Objects: inventions, utility models, industrial designs if relevant, and Eurasian patents valid in Russia",
        "- Sources: open sources only",
        "",
        "## Product features",
        *[f"- {feature}" for feature in technical_features],
        "",
        "## Search strategy",
        f"- RU query: `{ru_query}`",
        f"- EN/global query: `{en_query}`",
        f"- IPC/CPC: {', '.join(ipc_codes) if ipc_codes else 'not provided'}",
        f"- Assignees/competitors: {', '.join(assignees) if assignees else 'not provided'}",
        "",
        "## Candidate documents",
        "- Patent/application number, title, owner, source URL, official legal status, independent claim text.",
        "",
        "## Claim charts",
        "- Map every relevant independent claim to product features.",
        "",
        "## Preliminary conclusion",
        f"- {DISCLAIMER}",
    ]

    return {
        "product_name": product_name,
        "product_description": description,
        "technical_features": technical_features,
        "keywords_ru": keywords_ru,
        "keywords_en": keywords_en,
        "ipc_codes": ipc_codes,
        "assignees": assignees,
        "jurisdiction_filters": jurisdiction_filters,
        "queries": {"ru": ru_query, "en_or_global": en_query},
        "source_searches": source_searches,
        "workflow": search_steps,
        "report_outline_markdown": "\n".join(report_outline),
        "disclaimer": DISCLAIMER,
    }


ACTIVE_STATUS_MARKERS = (
    "active",
    "in force",
    "действ",
    "granted",
    "patented",
    "выдан",
    "поддерживается",
)
PENDING_STATUS_MARKERS = ("pending", "application", "заявк", "экспертиз", "published")
INACTIVE_STATUS_MARKERS = (
    "expired",
    "lapsed",
    "terminated",
    "ceased",
    "withdrawn",
    "rejected",
    "abandoned",
    "не действует",
    "прекрат",
    "истек",
    "аннулир",
    "отозван",
)


def classify_status(status: str) -> str:
    normalized = status.casefold()
    if any(marker in normalized for marker in INACTIVE_STATUS_MARKERS):
        return "inactive_or_expired"
    if any(marker in normalized for marker in PENDING_STATUS_MARKERS):
        return "pending_or_application"
    if any(marker in normalized for marker in ACTIVE_STATUS_MARKERS):
        return "active_or_potentially_active"
    return "unknown"


def score_candidate(product_features: list[str], candidate: dict[str, Any]) -> dict[str, Any]:
    matched_features = compact_list(candidate.get("matched_features"))
    status = str(candidate.get("legal_status", "")).strip()
    status_class = classify_status(status)
    feature_count = max(len(product_features), 1)
    coverage = len(matched_features) / feature_count

    missing = []
    if not status:
        missing.append("official legal status")
    if not candidate.get("source_urls"):
        missing.append("source URL")
    if not candidate.get("independent_claim"):
        missing.append("independent claim text")

    if status_class == "active_or_potentially_active" and coverage >= 0.8:
        risk = "high"
        rationale = "Active/potentially active right and most product features are mapped."
    elif status_class == "active_or_potentially_active" and coverage >= 0.5:
        risk = "medium"
        rationale = "Active/potentially active right with partial feature overlap."
    elif status_class == "pending_or_application" and coverage >= 0.5:
        risk = "monitor"
        rationale = "Published/pending application with meaningful overlap; monitor for grant and claim changes."
    elif status_class == "inactive_or_expired":
        risk = "low_verify"
        rationale = "Document appears inactive/expired, but reinstatement, extensions, and related rights must be checked."
    elif coverage > 0:
        risk = "unknown"
        rationale = "Some overlap found, but official status or claim evidence is incomplete."
    else:
        risk = "low"
        rationale = "No mapped product features were provided for this document."

    return {
        "number": candidate.get("number", ""),
        "title": candidate.get("title", ""),
        "jurisdiction": candidate.get("jurisdiction", ""),
        "kind": candidate.get("kind", ""),
        "legal_status": status,
        "status_class": status_class,
        "matched_features": matched_features,
        "feature_coverage": round(coverage, 3),
        "risk": risk,
        "rationale": rationale,
        "missing_evidence": missing,
        "source_urls": candidate.get("source_urls", []),
        "notes": candidate.get("notes", ""),
    }


def evaluate_patent_clearance_candidates(arguments: dict[str, Any]) -> dict[str, Any]:
    product_features = compact_list(arguments.get("product_features"))
    candidates = arguments.get("candidate_documents") or []
    if not isinstance(candidates, list):
        candidates = []

    scored = [score_candidate(product_features, candidate) for candidate in candidates if isinstance(candidate, dict)]
    risk_order = {"high": 0, "medium": 1, "monitor": 2, "unknown": 3, "low_verify": 4, "low": 5}
    scored.sort(key=lambda item: risk_order.get(item["risk"], 99))

    lines = [
        "# Preliminary patent clearance risk register",
        "",
        f"Generated: {date.today().isoformat()}",
        f"Scope: Russian Federation; open sources only.",
        "",
        "## Risk summary",
    ]
    if not scored:
        lines.append("- No candidate documents were provided for evaluation.")
    for item in scored:
        lines.extend(
            [
                f"- **{item['risk'].upper()}** `{item['number'] or 'no number'}` {item['title']}".strip(),
                f"  - Status: {item['legal_status'] or 'not provided'} ({item['status_class']})",
                f"  - Feature coverage: {item['feature_coverage']}",
                f"  - Rationale: {item['rationale']}",
            ]
        )
        if item["missing_evidence"]:
            lines.append(f"  - Missing evidence: {', '.join(item['missing_evidence'])}")
        for url in item["source_urls"]:
            lines.append(f"  - Source: {url}")
    lines.extend(["", f"Note: {DISCLAIMER}"])

    return {
        "product_features": product_features,
        "candidate_count": len(scored),
        "risk_register": scored,
        "risk_register_markdown": "\n".join(lines),
        "disclaimer": DISCLAIMER,
    }


def generate_open_fto_report(arguments: dict[str, Any]) -> dict[str, Any]:
    plan = build_patent_clearance_search_plan(arguments)
    evaluation = evaluate_patent_clearance_candidates(
        {
            "product_features": arguments.get("technical_features") or arguments.get("product_features"),
            "candidate_documents": arguments.get("candidate_documents", []),
        }
    )

    source_lines = []
    for source in plan["source_searches"]:
        source_lines.append(f"- {source['name']}: {source['search_url']}")

    report = "\n".join(
        [
            plan["report_outline_markdown"],
            "",
            "## Open source search links",
            *source_lines,
            "",
            evaluation["risk_register_markdown"],
        ]
    )
    return {"report_markdown": report, "plan": plan, "evaluation": evaluation, "disclaimer": DISCLAIMER}


TOOLS: dict[str, dict[str, Any]] = {
    "validate_open_sources_policy": {
        "description": "Validate that proposed patent research sources comply with the open-sources-only policy.",
        "inputSchema": {
            "type": "object",
            "properties": {"sources": {"type": "array", "items": {"type": "string"}}},
        },
        "handler": validate_open_sources_policy,
    },
    "build_patent_clearance_search_plan": {
        "description": "Build an open-source Russia patent-clearance search plan with source links and report outline.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_name": {"type": "string"},
                "product_description": {"type": "string"},
                "technical_features": {"type": "array", "items": {"type": "string"}},
                "keywords_ru": {"type": "array", "items": {"type": "string"}},
                "keywords_en": {"type": "array", "items": {"type": "string"}},
                "ipc_codes": {"type": "array", "items": {"type": "string"}},
                "assignees": {"type": "array", "items": {"type": "string"}},
            },
        },
        "handler": build_patent_clearance_search_plan,
    },
    "evaluate_patent_clearance_candidates": {
        "description": "Evaluate manually collected RU/EA patent candidates into a preliminary FTO risk register.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_features": {"type": "array", "items": {"type": "string"}},
                "candidate_documents": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "number": {"type": "string"},
                            "title": {"type": "string"},
                            "jurisdiction": {"type": "string"},
                            "kind": {"type": "string"},
                            "legal_status": {"type": "string"},
                            "independent_claim": {"type": "string"},
                            "matched_features": {"type": "array", "items": {"type": "string"}},
                            "source_urls": {"type": "array", "items": {"type": "string"}},
                            "notes": {"type": "string"},
                        },
                    },
                },
            },
        },
        "handler": evaluate_patent_clearance_candidates,
    },
    "generate_open_fto_report": {
        "description": "Generate a markdown patent-clearance report scaffold from open-source search inputs and candidates.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_name": {"type": "string"},
                "product_description": {"type": "string"},
                "technical_features": {"type": "array", "items": {"type": "string"}},
                "keywords_ru": {"type": "array", "items": {"type": "string"}},
                "keywords_en": {"type": "array", "items": {"type": "string"}},
                "ipc_codes": {"type": "array", "items": {"type": "string"}},
                "assignees": {"type": "array", "items": {"type": "string"}},
                "candidate_documents": {"type": "array", "items": {"type": "object"}},
            },
        },
        "handler": generate_open_fto_report,
    },
}


def as_text_content(payload: Any) -> list[dict[str, str]]:
    return [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=2)}]


def handle_request(request: dict[str, Any]) -> dict[str, Any] | None:
    method = request.get("method")
    request_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "patent-clearance-open", "version": "0.1.0"},
            },
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": name,
                        "description": definition["description"],
                        "inputSchema": definition["inputSchema"],
                    }
                    for name, definition in TOOLS.items()
                ]
            },
        }

    if method == "tools/call":
        params = request.get("params") or {}
        tool_name = params.get("name")
        arguments = params.get("arguments") or {}
        if tool_name not in TOOLS:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
            }
        try:
            handler = TOOLS[tool_name]["handler"]
            if tool_name == "validate_open_sources_policy":
                result = handler(arguments.get("sources"))
            else:
                result = handler(arguments)
            return {"jsonrpc": "2.0", "id": request_id, "result": {"content": as_text_content(result)}}
        except Exception as exc:  # pragma: no cover - defensive MCP boundary
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32000, "message": str(exc)},
            }

    if request_id is None:
        return None

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"Unsupported method: {method}"},
    }


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
        except json.JSONDecodeError as exc:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
