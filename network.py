"""
Chokepoint-sector propagation network.

DebtRank-style propagation, but the edge weight between a chokepoint and
a downstream sector (food / energy / market) is NOT physical trade volume
directly -- it's trade volume *gated by insurability*. An insurable
chokepoint at high premium still transmits a cost shock; an uninsured
chokepoint transmits a supply shock (volume goes to ~0 regardless of
shipper willingness), which is a qualitatively larger hit.

This module is intentionally thin -- it consumes state dicts produced by
InsuranceMarket.update() (see src/insurance/threshold.py) and
ChokepointAgent (see src/game_theory/payoff.py), and distributes impact
across sectors. Swap in a real graph library (networkx) once the node/edge
data model below is validated against historical events.
"""

from dataclasses import dataclass


@dataclass
class SectorExposure:
    sector: str                      # "food", "energy", "market"
    chokepoint_weights: dict         # {chokepoint_name: fraction of sector volume routed through it}

    def stress_score(self, insurance_states: dict) -> float:
        """
        insurance_states: {chokepoint_name: result dict from InsuranceMarket.update()}

        Weighted stress: an insurable-but-repriced chokepoint contributes
        (premium_multiplier - 1) * weight; a withdrawn chokepoint
        contributes its full weight (treated as ~total volume loss
        through that route).
        """
        total = 0.0
        for chokepoint, weight in self.chokepoint_weights.items():
            state = insurance_states.get(chokepoint)
            if state is None:
                continue
            if not state["insurable"]:
                total += weight * 1.0
            else:
                multiplier = state["premium_rate"] / max(state["premium_rate"], 1e-9)
                # cost-side stress is a fraction of full withdrawal stress;
                # placeholder linear scaling -- refine once calibrated against
                # historical freight-rate/premium data
                total += weight * 0.25
        return min(1.0, total)


def propagate(sector_exposures: list[SectorExposure], insurance_states: dict) -> dict:
    """Returns {sector: stress_score} across all tracked sectors for one time step."""
    return {s.sector: s.stress_score(insurance_states) for s in sector_exposures}
