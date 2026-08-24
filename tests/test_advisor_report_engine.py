from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from advisor_report_engine import (
    DATA_PATH,
    all_clients_pdf_bytes,
    build_all_client_reports,
    client_report_pdf_bytes,
    virtual_clients,
)


def run_tests() -> None:
    assert DATA_PATH.exists()
    clients = virtual_clients()
    assert len(clients) == 10
    assert clients[0].text("segment", "ko") == "무소득 학업 전환형"

    reports = build_all_client_reports()
    assert len(reports) == 10

    report_by_id = {report["client"].client_id: report for report in reports}
    young = report_by_id["C01"]
    assert young["result"]["no_income_mode"] is True
    assert young["result"]["planning_health_score"] > 80
    assert "runway" in young["diagnosis"].lower()

    mina = report_by_id["C04"]
    assert mina["result"]["investment_exposure_ratio"] > 0.70
    assert any("concentration" in action.lower() for action in mina["actions"])

    james = report_by_id["C05"]
    assert james["result"]["debt_to_income"] > 0.36
    assert any("debt" in action.lower() or "rate" in action.lower() for action in james["actions"])

    selected_pdf = client_report_pdf_bytes(young)
    assert selected_pdf.startswith(b"%PDF")
    assert len(selected_pdf) > 1_000

    full_pdf = all_clients_pdf_bytes(reports)
    assert full_pdf.startswith(b"%PDF")
    assert len(full_pdf) > len(selected_pdf)

    korean_reports = build_all_client_reports(language="ko")
    korean_young = {report["client"].client_id: report for report in korean_reports}["C01"]
    assert "생존기간" in korean_young["diagnosis"]
    assert "포트폴리오" in korean_young["report_text"]
    assert "가치평가" in korean_young["report_text"]
    assert "AAPL" in korean_young["report_text"]
    korean_pdf = client_report_pdf_bytes(korean_young)
    assert korean_pdf.startswith(b"%PDF")
    assert len(korean_pdf) > 1_000


if __name__ == "__main__":
    run_tests()
    print("Advisor report engine tests passed.")
