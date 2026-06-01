import json
import unittest

from tools.patent_clearance_open.server import (
    build_patent_clearance_search_plan,
    evaluate_patent_clearance_candidates,
    handle_request,
    validate_open_sources_policy,
)


class PatentClearanceOpenTests(unittest.TestCase):
    def test_policy_blocks_paid_sources(self):
        result = validate_open_sources_policy(["FIPS", "Derwent Innovation", "Questel Orbit"])

        self.assertFalse(result["compliant"])
        self.assertEqual(result["blocked_sources"], ["Derwent Innovation", "Questel Orbit"])

    def test_search_plan_uses_open_sources_and_queries(self):
        result = build_patent_clearance_search_plan(
            {
                "product_name": "Test device",
                "technical_features": ["датчик давления", "беспроводная передача"],
                "keywords_en": ["pressure sensor", "wireless transmission"],
                "ipc_codes": ["G01L"],
            }
        )

        self.assertIn("датчик давления", result["queries"]["ru"])
        self.assertIn("pressure sensor", result["queries"]["en_or_global"])
        self.assertTrue(any(source["key"] == "fips_registers" for source in result["source_searches"]))
        self.assertTrue(all("Derwent" not in source["name"] for source in result["source_searches"]))

    def test_candidate_evaluation_orders_high_risk_first(self):
        result = evaluate_patent_clearance_candidates(
            {
                "product_features": ["A", "B", "C"],
                "candidate_documents": [
                    {
                        "number": "RU000000",
                        "title": "Expired example",
                        "legal_status": "expired",
                        "matched_features": ["A", "B", "C"],
                    },
                    {
                        "number": "RU111111",
                        "title": "Active example",
                        "legal_status": "active",
                        "matched_features": ["A", "B", "C"],
                        "independent_claim": "1. A device comprising A, B, and C.",
                        "source_urls": ["https://www1.fips.ru/registers-web/"],
                    },
                ],
            }
        )

        self.assertEqual(result["risk_register"][0]["number"], "RU111111")
        self.assertEqual(result["risk_register"][0]["risk"], "high")
        self.assertEqual(result["risk_register"][1]["risk"], "low_verify")

    def test_foreign_documents_require_ru_ea_family_check(self):
        result = evaluate_patent_clearance_candidates(
            {
                "product_features": ["A", "B"],
                "candidate_documents": [
                    {
                        "number": "US123",
                        "title": "Foreign active example",
                        "jurisdiction": "US",
                        "legal_status": "active",
                        "matched_features": ["A", "B"],
                        "independent_claim": "1. A system comprising A and B.",
                        "source_urls": ["https://patents.google.com/patent/US123/en"],
                    }
                ],
            }
        )

        item = result["risk_register"][0]
        self.assertEqual(item["risk"], "family_check")
        self.assertIn("RU/EA family status", item["missing_evidence"])

    def test_mcp_tools_list(self):
        response = handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})

        tool_names = {tool["name"] for tool in response["result"]["tools"]}
        self.assertIn("build_patent_clearance_search_plan", tool_names)
        self.assertIn("generate_open_fto_report", tool_names)

    def test_mcp_tool_call_returns_text_content(self):
        response = handle_request(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "validate_open_sources_policy",
                    "arguments": {"sources": ["FIPS"]},
                },
            }
        )

        content = response["result"]["content"][0]
        payload = json.loads(content["text"])
        self.assertTrue(payload["compliant"])


if __name__ == "__main__":
    unittest.main()
