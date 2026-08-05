import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.game_theory.payoff import ChokepointAgent, run_imitation_round
from src.insurance.threshold import InsuranceMarket


def test_belief_update_moves_toward_surprise():
    agent = ChokepointAgent("Test", 1e12, 0.3, 5e11, p_retaliate=0.7)
    agent.update_belief(observed_retaliation_severity=0.2)
    assert agent.p_retaliate < 0.7


def test_belief_update_bounded():
    agent = ChokepointAgent("Test", 1e12, 0.3, 5e11, p_retaliate=0.9)
    for _ in range(20):
        agent.update_belief(observed_retaliation_severity=0.0)
    assert 0.0 <= agent.p_retaliate <= 1.0


def test_imitation_round_excludes_initiator():
    a = ChokepointAgent("A", 1e12, 0.3, 5e11, 0.7)
    b = ChokepointAgent("B", 1e12, 0.3, 5e11, 0.7)
    results = run_imitation_round([a, b], "A", 0.5, 0.2)
    assert "A" not in results
    assert "B" in results


def test_insurance_withdrawal_past_threshold():
    market = InsuranceMarket("Test", base_premium_rate=0.0002, risk_aversion=2.0,
                              withdrawal_threshold=0.5)
    state = market.update(p_retaliate=0.9, realized_severity=0.9, imitation_count=2)
    assert state["regime"] == "WITHDRAWN"
    assert state["insurable"] is False


def test_insurance_repricing_below_threshold():
    market = InsuranceMarket("Test", base_premium_rate=0.0002, risk_aversion=2.0,
                              withdrawal_threshold=0.95)
    state = market.update(p_retaliate=0.1, realized_severity=0.1, imitation_count=0)
    assert state["regime"] == "REPRICED"
    assert state["premium_rate"] > market.base_premium_rate
