from pathlib import Path


def test_vm_launcher_is_isolated_from_scientific_campaign_queue():
    source = (Path(__file__).parents[1] / "scripts" / "gpt_oss_orchestrator.py").read_text(
        encoding="utf-8"
    )
    assert "ResearchCampaign" not in source
    assert "worker.step(task)" in source
    assert '"scientific_queue_opened": False' in source
    assert 'lane="engineering_orchestration"' in source


def test_vm_launcher_fails_closed_on_scientific_and_capital_authority():
    source = (Path(__file__).parents[1] / "scripts" / "gpt_oss_orchestrator.py").read_text(
        encoding="utf-8"
    )
    for key in (
        "real_capital_authorized",
        "live_trading_authorized",
        "scientific_unblinding_authorized",
        "frozen_protocol_redefinition_authorized",
        "irreversible_external_mutation_authorized",
    ):
        assert f'"{key}": False' in source
