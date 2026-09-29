import ast
from datetime import date, timedelta
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from goal_planning import months_until, project_goal


class GoalMathTests(unittest.TestCase):
    def test_zero_return_and_required_contribution(self):
        result = project_goal(25000, 600, 80000, 60)
        self.assertAlmostEqual(result["projected"], 61000)
        self.assertAlmostEqual(result["gap"], -19000)
        self.assertAlmostEqual(result["required_monthly"], 55000 / 60)

    def test_compounding_matches_cash_flow_iteration(self):
        for annual in (-20, 0, 6):
            with self.subTest(annual=annual):
                result = project_goal(25000, 600, 80000, 60, annual, 1)
                self.assertAlmostEqual(result["projected"], result["path"][-1]["Projected savings"], places=6)
                funded = project_goal(25000, result["required_monthly"], 80000, 60, annual, 1)
                self.assertAlmostEqual(funded["projected"], 80000, places=6)

    def test_invalid_values_and_already_funded(self):
        for inputs in [(0, 10, 0, 12), (0, -10, 100, 12), (0, 0, 100, 0), (float("nan"), 10, 100, 12)]:
            with self.assertRaises(ValueError):
                project_goal(*inputs)
        self.assertEqual(project_goal(10000, 0, 5000, 12)["required_monthly"], 0)
        self.assertEqual(months_until(date(2026, 1, 15), date(2026, 2, 16)), 2)
        self.assertEqual(months_until(date(2026, 1, 15), date(2026, 1, 15)), 0)

    def test_dividend_units_do_not_depend_on_provider_yield(self):
        module = ast.parse((ROOT / "streamlit_app.py").read_text())
        function = next(node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == "yahoo_dividend_yield")
        namespace = {"math": math, "Any": object}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "yield_helper", "exec"), namespace)
        calculate = namespace["yahoo_dividend_yield"]
        for provider_yield in (0.0032, 0.32):
            self.assertAlmostEqual(calculate({"dividendRate": 1.08, "dividendYield": provider_yield}, 338.4), 1.08 / 338.4 * 100)
        self.assertEqual(calculate({"dividendRate": 0}, 100), 0)
        self.assertIsNone(calculate({"dividendYield": .32}, 100))


class AuditWorkflowTests(unittest.TestCase):
    def app(self, view="life"):
        app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30)
        app.query_params.update(lang="ko", view=view, mode="dashboard")
        app.run()
        self.assertFalse(list(app.exception))
        return app

    def stock(self):
        return dict(symbol="AAPL", name="Apple test fixture", price=100.0, change_pct=0,
                    industry="Technology", currency="USD", market="US", market_cap=1000,
                    pe=20, beta=1.0, eps=5, dividend=1, dividend_yield=1.0,
                    growth_rate=.05, book_value=10, peer_average_pe=20, peers=[],
                    fair_price=120, valuation_status="Undervalued", data_quality="Test fixture",
                    triangulation=dict(income_model="ECM", income_value=130, asset_value=100,
                                       market_value=130, valid_models=3))

    @patch("yfinance.download", return_value=pd.DataFrame())
    def test_search_add_compare_portfolio_and_single_edit_refresh(self, _download):
        app = self.app("search")
        app.session_state["stocks"] = {"AAPL": self.stock()}
        app.session_state["selected_detail"] = "AAPL"
        app.run()
        app.button(key="detail_compare_AAPL").click().run()
        app.button(key="detail_portfolio_AAPL").click().run()
        app.button(key="v2_nav_compare").click().run()
        self.assertIn("Apple test fixture (AAPL)", app.dataframe[-1].value.columns)
        app.button(key="v2_nav_portfolio").click().run()
        app.number_input(key="shares_AAPL").set_value(10.0).run()
        self.assertEqual(app.session_state["portfolio"]["AAPL"]["shares"], 10)
        self.assertTrue(any('총 시장가치' in item.value and '$1,000.00' in item.value for item in app.markdown))
        app.number_input(key="purchase_price_AAPL").set_value(80.0).run()
        app.number_input(key="fx_rate_input").set_value(1400.0).run()
        app.button(key="v2_nav_finance").click().run()
        app.button(key="v2_language_en").click().run()
        app.button(key="v2_nav_portfolio").click().run()
        self.assertFalse(list(app.exception))
        self.assertEqual(app.number_input(key="shares_AAPL").value, 10)
        self.assertEqual(app.number_input(key="purchase_price_AAPL").value, 80)
        self.assertEqual(app.number_input(key="fx_rate_input").value, 1400)

    def test_fx_first_render_and_navigation(self):
        app = self.app("portfolio")
        self.assertEqual(app.number_input(key="fx_rate_input").value, 1350)
        app.button(key="v2_nav_finance").click().run()
        app.button(key="v2_nav_portfolio").click().run()
        self.assertEqual(app.number_input(key="fx_rate_input").value, 1350)

    def test_goal_calculate_navigate_translate_and_report(self):
        app = self.app()
        app.text_input(key="goal_name").set_value("Home test")
        app.number_input(key="goal_target").set_value(80000)
        app.number_input(key="goal_current").set_value(25000)
        app.number_input(key="goal_monthly").set_value(600)
        app.date_input(key="goal_deadline").set_value(date.today() + timedelta(days=365))
        next(button for button in app.button if button.label == "목표 달성 전망 계산").click().run()
        self.assertFalse(list(app.exception))
        self.assertEqual(app.session_state["goal_plan"]["target"], 80000)
        app.button(key="goal_open_grow_capital").click().run()
        self.assertEqual(app.query_params["view"], ["portfolio"])
        app.button(key="goal_strip_change").click().run()
        self.assertEqual(app.number_input(key="goal_target").value, 80000)
        app.button(key="v2_language_en").click().run()
        self.assertEqual(app.number_input(key="goal_monthly").value, 600)
        app.button(key="v2_language_ko").click().run()
        app.button(key="v2_nav_diary").click().run()
        self.assertFalse(list(app.exception))
        self.assertIn("목표 금액: $80,000.00", app.text_area(key="diary_current_report").value)
        self.assertIn("현재 재무 현황 보고서", [heading.value for heading in app.subheader])
        self.assertTrue(any("임시 저장" in message.value for message in app.info))


if __name__ == "__main__":
    unittest.main()
