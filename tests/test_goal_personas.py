"""Ten fictional, end-to-end goal workflows with an independent cash-flow oracle."""

import calendar
from datetime import date
from decimal import Decimal, localcontext
import json
import os
from pathlib import Path
import sys
import unittest

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from goal_planning import goal_cashflow_check, project_goal

CASES = json.loads((ROOT / "data/goal_validation_cases.json").read_text())["cases"]
RESULTS = []


def deadline_after(months):
    today = date.today()
    year, month = divmod(today.year * 12 + today.month - 1 + months, 12)
    return date(year, month + 1, min(today.day, calendar.monthrange(year, month + 1)[1]))


def reference_projection(case):
    with localcontext() as context:
        context.prec = 40
        annual = (Decimal(str(case["annual_return"])) - Decimal(str(case["annual_drag"]))) / 100
        rate = (1 + annual) ** (Decimal(1) / 12) - 1
        principal = Decimal(str(case["current"]))
        unit_contribution = Decimal(0)
        for _ in range(case["months"]):
            principal *= 1 + rate
            unit_contribution = unit_contribution * (1 + rate) + 1
        projected = principal + Decimal(str(case["monthly"])) * unit_contribution
        required = max(Decimal(0), (Decimal(str(case["target"])) - principal) / unit_contribution)
        return float(projected), float(required)


class GoalPersonaTests(unittest.TestCase):
    def assert_healthy(self, app):
        self.assertFalse(list(app.exception), [item.message for item in app.exception])

    def run_persona(self, case):
        app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30)
        app.query_params.update(lang="ko", view="finance", mode="dashboard")
        app.run()
        app.selectbox(key="pf_display_currency").select(case["finance_currency"])
        values = {
            "monthly_income":case["income"], "fixed_expenses":case["fixed"],
            "variable_expenses":case["variable"], "monthly_debt_payment":case["debt_payment"],
            "cash_savings":case["current"], "monthly_savings_goal":case["monthly"],
            "target_goal_amount":case["target"], "current_goal_savings":case["current"],
            "taxable_investments":0, "retirement_accounts":0, "real_estate_value":0,
            "credit_card_debt":0, "student_loan":0, "auto_loan":0, "mortgage":0,
        }
        # Cross-currency fixtures never pretend their goal balance is a USD balance.
        if case["currency"] != case["finance_currency"]:
            values.update(cash_savings=30000, monthly_savings_goal=1000,
                          target_goal_amount=50000, current_goal_savings=30000)
        for key, value in values.items():
            app.number_input(key=f"pf_{key}").set_value(float(value))
        app.button(key="apply_situation_calculation").click().run()
        self.assert_healthy(app)
        surplus = case["income"] - case["fixed"] - case["variable"] - case["debt_payment"]
        self.assertEqual(app.session_state["last_personal_finance_result"]["monthly_surplus"], surplus)
        assets_before = app.session_state["last_personal_finance_result"]["total_assets"]
        app.button(key="v2_nav_life").click().run()
        goal_name = f"{case['id']} {case['name']} - {case['goal']}"
        app.text_input(key="goal_name").set_value(goal_name)
        app.selectbox(key="goal_currency").select(case["currency"])
        for key in ("target", "current", "monthly", "return", "drag"):
            value = case[f"annual_{key}"] if key in ("return", "drag") else case[key]
            app.number_input(key=f"goal_{key}").set_value(float(value))
        app.date_input(key="goal_deadline").set_value(deadline_after(case["months"]))
        next(button for button in app.button if button.label == "목표 달성 전망 계산").click().run()
        self.assert_healthy(app)
        plan = app.session_state["goal_plan"]
        expected, required = reference_projection(case)
        self.assertAlmostEqual(plan["result"]["projected"], expected, delta=0.01)
        self.assertAlmostEqual(plan["result"]["required_monthly"], required, delta=0.01)
        self.assertEqual(plan["result"]["months"], case["months"])
        self.assertEqual(app.session_state["last_personal_finance_result"]["total_assets"], assets_before)
        # These assertions reproduce misleading goal feasibility in the old screen.
        if case["currency"] != case["finance_currency"]:
            self.assertTrue(any("통화가 달라" in msg.value for msg in app.info))
        elif case["monthly"] > max(0, surplus):
            self.assertTrue(any("잉여 현금" in msg.value for msg in app.warning))
        elif required > max(0, surplus):
            self.assertTrue(any("필요한 월 적립액" in msg.value for msg in app.warning))
        for language in ("en", "ko"):
            app.button(key=f"v2_language_{language}").click().run()
            self.assertEqual(app.number_input(key="goal_target").value, case["target"])
            self.assertEqual(app.number_input(key="goal_monthly").value, case["monthly"])
        app.button(key="goal_open_grow_capital").click().run()
        self.assert_healthy(app)
        self.assertEqual(app.number_input(key="fx_rate_input").value, 1350)
        app.button(key="v2_nav_scenario").click().run()
        app.slider(key="scenario_income").set_value(-20).run()
        self.assert_healthy(app)
        app.button(key="v2_nav_diary").click().run()
        self.assert_healthy(app)
        report = app.text_area(key="diary_current_report").value
        self.assertIn(goal_name, report)
        symbol = "₩" if case["currency"] == "KRW" else "$"
        amount = f"{case['target']:,.0f}" if case["currency"] == "KRW" else f"{case['target']:,.2f}"
        self.assertIn(f"목표 금액: {symbol}{amount}", report)
        if case["currency"] != case["finance_currency"]:
            self.assertIn("통화가 달라", report)
        elif case["monthly"] > max(0, surplus):
            self.assertIn("재원이 부족", report)
        next(button for button in app.button if button.label == "보고서 임시 저장").click().run()
        self.assertEqual(len(app.session_state["financial_diary"]), 1)
        app.button(key="v2_nav_life").click().run()
        self.assertEqual(app.text_input(key="goal_name").value, goal_name)
        self.assertEqual(app.number_input(key="goal_current").value, case["current"])
        self.assert_healthy(app)
        RESULTS.append({**case, "projected":expected, "gap":expected-case["target"],
                        "required_monthly":required, "monthly_surplus":surplus,
                        "status":"passed", "checks":"math, finance, currency, navigation, languages, scenario, report, diary, no double count"})


class GoalFundingTests(unittest.TestCase):
    def state(self):
        return {"last_personal_finance_profile": {
            "monthly_income":4800, "fixed_expenses":2300,
            "variable_expenses":1000, "monthly_debt_payment":700},
            "last_personal_finance_currency":"USD", "pf_display_currency":"USD"}

    def test_missing_or_pending_calculation_is_not_treated_as_affordable(self):
        plan = {"monthly":1800, "currency":"USD"}
        self.assertEqual(goal_cashflow_check(plan, {})["status"], "missing")
        state = self.state()
        state["pf_monthly_income"] = 9000
        self.assertEqual(goal_cashflow_check(plan, state)["status"], "pending")
        state = self.state()
        state["pf_display_currency"] = "KRW"
        self.assertEqual(goal_cashflow_check(plan, state)["status"], "pending")

    def test_funding_shortfall_and_currency_boundary(self):
        plan = {"monthly":1800, "currency":"USD"}
        check = goal_cashflow_check(plan, self.state())
        self.assertEqual(check["surplus"], 800)
        self.assertEqual(check["contribution_gap"], 1000)
        self.assertEqual(check["status"], "shortfall")
        plan["currency"] = "KRW"
        self.assertEqual(goal_cashflow_check(plan, self.state())["status"], "currency_mismatch")
        plan.update(currency="USD", monthly=600, result={"required_monthly":900})
        self.assertEqual(goal_cashflow_check(plan, self.state())["status"], "required_shortfall")

    def test_return_scenarios_and_already_funded_goal(self):
        for case in CASES:
            values = [project_goal(case["current"], case["monthly"], case["target"],
                                  case["months"], case["annual_return"] + delta,
                                  case["annual_drag"])["projected"] for delta in (-3, 0, 3)]
            self.assertEqual(values, sorted(values))
        funded = project_goal(7000, 0, 5000, 6, -2, .5)
        self.assertEqual(funded["required_monthly"], 0)
        self.assertTrue(funded["on_track"])


for case in CASES:
    def test(self, case=case):
        self.run_persona(case)
    setattr(GoalPersonaTests, f"test_{case['id']}", test)


if __name__ == "__main__":
    result = unittest.main(exit=False)
    if os.environ.get("LY_SCOPE_PERSONA_RESULTS"):
        Path(os.environ["LY_SCOPE_PERSONA_RESULTS"]).write_text(
            json.dumps({"date":date.today().isoformat(), "fictional":True, "cases":RESULTS}, ensure_ascii=False, indent=2))
    sys.exit(not result.result.wasSuccessful())
