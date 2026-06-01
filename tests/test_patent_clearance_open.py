import json
import unittest

from tools.patent_clearance_open.server import (
    build_official_patent_number_links,
    build_parallel_open_search_workflow,
    build_patent_clearance_search_plan,
    evaluate_patent_clearance_candidates,
    handle_request,
    validate_open_sources_policy,
)


class PatentClearanceOpenTests(unittest.TestCase):
    def test_direct_fips_links_for_known_patent_numbers(self):
        result = build_official_patent_number_links({"patent_numbers": ["RU2838158C1", "2838158"]})

        self.assertEqual(result["lookups"][0]["normalized_number"], "2838158")
        self.assertIn("DocNumber=2838158", result["lookups"][0]["official_links"][0]["url"])
        self.assertIn("docid=2838158", result["lookups"][0]["official_links"][1]["url"])

    def test_search_plan_includes_known_number_lookup_links(self):
        result = build_patent_clearance_search_plan(
            {
                "product_name": "Known patent check",
                "technical_features": ["маршрутизация трафика"],
                "known_patent_numbers": ["2838158"],
            }
        )

        self.assertEqual(result["known_patent_numbers"], ["2838158"])
        self.assertEqual(result["number_lookup_links"][0]["normalized_number"], "2838158")

    def test_parallel_open_search_workflow_combines_fips_and_web(self):
        result = build_parallel_open_search_workflow(
            {
                "product_name": "Operator VPN",
                "technical_features": ["маршрутизация трафика абонента", "VPN туннель"],
                "keywords_en": ["mobile operator VPN routing"],
                "ipc_codes": ["H04W"],
                "known_patent_numbers": ["RU2838158C1"],
            }
        )

        official_tasks = result["run_in_parallel"]["official_register_tasks"]
        web_tasks = result["run_in_parallel"]["web_discovery_tasks"]

        self.assertEqual(official_tasks[0]["task"], "direct_fips_number_lookup")
        self.assertIn("DocNumber=2838158", official_tasks[0]["lookups"][0]["official_links"][0]["url"])
        self.assertTrue(any(task["task"] == "fips_keyword_search" for task in official_tasks))
        self.assertTrue(any(task["task"] == "google_patents_discovery" for task in web_tasks))
        self.assertIn("H04W", result["queries"]["ru"])

    def test_mcp_tools_list_includes_parallel_workflow(self):
        response = handle_request({"jsonrpc": "2.0", "id": 10, "method": "tools/list"})

        tool_names = {tool["name"] for tool in response["result"]["tools"]}
        self.assertIn("build_parallel_open_search_workflow", tool_names)

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
