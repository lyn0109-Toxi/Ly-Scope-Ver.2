"""Public fictional cases must not overwrite an active financial plan."""

from copy import deepcopy
from pathlib import Path
import sys
import unittest

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from goal_case_studies import load_goal_cases, validate_goal_cases
from goal_planning import project_goal


class GoalCaseStudyTests(unittest.TestCase):
    def app(self):
        app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30)
        app.query_params.update(view="advisor", lang="ko", mode="dashboard")
        return app.run()

    def test_all_cases_render_without_mutating_user_inputs(self):
        app = self.app()
        plan = {"name": "My existing goal", "target": 80000, "currency": "USD",
                "current": 25000, "monthly": 600, "deadline": "2031-09-29",
                "result": project_goal(25000, 600, 80000, 60, 6, 1)}
        app.session_state["goal_plan"] = deepcopy(plan)
        app.session_state["pf_monthly_income"] = 8765.0
        for case in load_goal_cases():
            app.selectbox(key="validation_case_id").select(case["id"]).run()
            self.assertFalse(list(app.exception))
            self.assertEqual(app.session_state["goal_plan"], plan)
            self.assertEqual(app.session_state["pf_monthly_income"], 8765.0)
            self.assertIn(case["id"], app.subheader[-1].value)
            self.assertEqual(len(app.metric), 3)
        app.button(key="verify_goal_cases").click().run()
        self.assertTrue(any("10/10" in item.value for item in app.success))
        app.button(key="v2_language_en").click().run()
        self.assertEqual(app.selectbox(key="validation_case_id").value, "G10")
        self.assertEqual(app.header[-1].value, "10 goals, 10 case studies")
        self.assertEqual(app.session_state["goal_plan"], plan)
        app.button(key="v2_nav_finance").click().run()
        self.assertEqual(app.number_input(key="pf_monthly_income").value, 8765.0)

    def test_funding_warning_and_profile_mode_remain_available(self):
        app = self.app()
        app.selectbox(key="validation_case_id").select("G06").run()
        self.assertTrue(any("재원이 부족" in item.value for item in app.warning))
        app.selectbox(key="validation_case_id").select("G09").run()
        self.assertTrue(any("통화가 달라" in item.value for item in app.info))
        app.segmented_control(key="case_study_mode").set_value("profiles").run()
        self.assertFalse(list(app.exception))
        self.assertNotIn("validation_case_id", [item.key for item in app.selectbox])

    def test_independent_checks_cover_all_cases(self):
        checks = validate_goal_cases(load_goal_cases())
        self.assertEqual(len(checks), 10)
        self.assertTrue(all(item["passed"] for item in checks))


if __name__ == "__main__":
    unittest.main()
