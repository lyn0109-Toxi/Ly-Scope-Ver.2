from pathlib import Path
import json
import sys
import unittest

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class WorkspaceUITests(unittest.TestCase):
    def app(self, view="finance", language="ko"):
        app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30)
        app.query_params.update(lang=language, view=view, mode="dashboard")
        app.run()
        self.assertFalse(list(app.exception))
        return app

    def test_all_routes_in_both_languages(self):
        routes = ("life", "finance", "search", "compare", "portfolio", "reit", "scenario",
                  "advisor", "ai", "diary", "details", "guide", "settings")
        for language in ("en", "ko"):
            for view in routes:
                with self.subTest(language=language, view=view):
                    self.app(view, language)

    def test_market_menu_opens_and_closes(self):
        app = self.app()
        self.assertNotIn("v2_nav_search", [button.key for button in app.button])
        app.button(key="v2_market_toggle").click().run()
        self.assertIn("v2_nav_search", [button.key for button in app.button])
        app.button(key="v2_market_toggle").click().run()
        self.assertNotIn("v2_nav_search", [button.key for button in app.button])
        self.assertEqual(app.query_params["view"], ["finance"])

    def test_finance_draft_survives_navigation_and_language(self):
        app = self.app()
        app.number_input(key="pf_monthly_income").set_value(9300.0).run()
        self.assertTrue(any("아직 반영하지 않은" in item.value for item in app.warning))
        app.button(key="v2_nav_diary").click().run()
        self.assertFalse(list(app.exception))
        app.button(key="v2_language_en").click().run()
        app.button(key="v2_nav_finance").click().run()
        self.assertEqual(app.number_input(key="pf_monthly_income").value, 9300.0)
        self.assertEqual(app.number_input(key="pf_monthly_income").label, "Monthly Income")
        app.button(key="apply_situation_calculation").click().run()
        self.assertEqual(app.session_state["last_personal_finance_profile"]["monthly_income"], 9300.0)
        app.button(key="v2_language_ko").click().run()
        self.assertEqual(app.number_input(key="pf_monthly_income").value, 9300.0)
        self.assertEqual(app.number_input(key="pf_monthly_income").label, "월수입")

    def test_finance_insights_and_units_are_korean(self):
        app = self.app()
        self.assertTrue(any("비상자금" in item.value for item in app.info))
        self.assertFalse(any("Savings rate" in item.value for item in app.info))
        self.assertFalse(any(" months" in item.value for item in app.markdown))
        next(button for button in app.button if button.label == "무소득 학업 예시 적용").click().run()
        self.assertTrue(any("설정한 목표보다" in item.value for item in app.info))
        self.assertFalse(any("Cash runway" in item.value for item in app.info))

    def test_charts_keep_datasets_and_localize_titles(self):
        app = self.app()
        charts = list(app.get("vega_lite_chart"))
        self.assertEqual(len(charts), 3)
        for chart in charts:
            spec = json.loads(chart.proto.spec)
            self.assertTrue(chart.proto.datasets or chart.proto.data.data)
            self.assertNotIn('"title": "Months"', json.dumps(spec))
            self.assertNotIn('"title": "Score"', json.dumps(spec))

    def test_scenario_translation_and_inputs_survive_language(self):
        app = self.app("scenario")
        self.assertEqual(app.slider(key="scenario_income").label, "월소득 변화")
        app.slider(key="scenario_income").set_value(-35).run()
        app.button(key="v2_language_en").click().run()
        self.assertEqual(app.slider(key="scenario_income").value, -35)
        app.button(key="v2_nav_finance").click().run()
        app.button(key="v2_nav_scenario").click().run()
        self.assertEqual(app.slider(key="scenario_income").value, -35)

    def test_scenario_uses_personal_finance_currency(self):
        app = self.app()
        next(button for button in app.button if button.label == "무소득 학업 예시 적용").click().run()
        app.button(key="v2_nav_scenario").click().run()
        self.assertFalse(list(app.exception))
        money_card = next(item.value for item in app.markdown if 'class="label">월 잉여 현금' in item.value)
        self.assertIn("₩", money_card)
        self.assertNotIn("$", money_card)

    def test_default_opens_workspace_and_intro_remains_available(self):
        app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30).run()
        self.assertFalse(list(app.exception))
        self.assertIn("v2_nav_finance", [button.key for button in app.button])
        app.button(key="v2_intro").click().run()
        self.assertFalse(list(app.exception))
        self.assertEqual(app.query_params["mode"], ["intro"])


if __name__ == "__main__":
    unittest.main()
