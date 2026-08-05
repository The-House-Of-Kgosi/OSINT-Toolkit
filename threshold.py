"""
Marine insurance repricing model.

Models premium as a function of perceived risk for a given chokepoint,
with two distinct regimes:

  1. Incremental repricing: premium rises smoothly with perceived risk.
     Trade continues at higher cost.
  2. Discrete withdrawal: past a risk threshold, insurers/reinsurers pull
     capacity rather than keep pricing it (real-world analogue: Lloyd's
     Joint War Committee adding an area to its listed-areas list, or
     P&I clubs declining renewal). Trade doesn't get more expensive here
     -- it stops, because uninsured cargo can't clear financing, ports,
     or counterparty risk checks regardless of a shipper's own risk
     tolerance.

This discrete jump is what turns a chokepoint disruption into a cliff-edge
rather than a smooth cost curve, and is the mechanism that links the
game-theory layer (perceived defection risk) to the propagation layer
(trade flow collapse).
"""

from dataclasses import dataclass


@dataclass
class InsuranceMarket:
    chokepoint: str
    base_premium_rate: float          # baseline, e.g. 0.0002 (2 bps of hull+cargo value)
    risk_aversion: float              # insurer sensitivity to perceived risk (k in exp curve)
    withdrawal_threshold: float       # perceived_risk score above which capacity is pulled
    capacity_withdrawn: bool = False

    def perceived_risk(self, p_retaliate: float, realized_severity: float,
                        imitation_count: int) -> float:
        """
        Composite risk score in [0, ~1+], combining:
        - current belief about retaliation severity (from game theory layer)
        - realized severity of any actual incident
        - how many other chokepoints have already imitated (systemic contagion signal)
        """
        return min(1.5, 0.4 * p_retaliate + 0.4 * realized_severity + 0.2 * imitation_count)

    def premium_multiplier(self, risk_score: float) -> float:
        """Incremental regime: exponential repricing, capped before withdrawal threshold."""
        import math
        return math.exp(self.risk_aversion * risk_score)

    def update(self, p_retaliate: float, realized_severity: float, imitation_count: int) -> dict:
        """
        Returns current market state for this chokepoint given inputs from the
        game-theory layer. If perceived risk crosses withdrawal_threshold,
        capacity_withdrawn flips True and premium becomes moot -- the route
        is effectively uninsurable, which the propagation layer should treat
        as a hard trade-flow stop, not a cost increase.
        """
        risk_score = self.perceived_risk(p_retaliate, realized_severity, imitation_count)

        if risk_score >= self.withdrawal_threshold:
            self.capacity_withdrawn = True
            return {
                "chokepoint": self.chokepoint,
                "risk_score": risk_score,
                "regime": "WITHDRAWN",
                "premium_rate": None,
                "insurable": False,
            }

        self.capacity_withdrawn = False
        multiplier = self.premium_multiplier(risk_score)
        return {
            "chokepoint": self.chokepoint,
            "risk_score": risk_score,
            "regime": "REPRICED",
            "premium_rate": self.base_premium_rate * multiplier,
            "insurable": True,
        }
