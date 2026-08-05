"""
Chokepoint operator payoff model.

Each chokepoint (Hormuz, Suez, Bosporus, Malacca, Panama, Danish Straits...)
is an agent that chooses a toll/closure intensity tau in [0, 1] to maximize:

    U_i(tau) = toll_revenue(tau) - retaliation_cost(tau) - reroute_loss(tau)

The key dynamic is not the payoff function itself but how P_retaliate
(agent i's belief about the probability/severity of retaliation) updates
after observing another agent's move. A closure that is absorbed without
proportionate retaliation is a signal that lowers every other agent's
retaliation-risk prior — this is the imitation mechanism that produces
the cascade.
"""

from dataclasses import dataclass, field


@dataclass
class ChokepointAgent:
    name: str
    annual_trade_value_usd: float       # value of trade transiting this chokepoint
    reroute_elasticity: float           # fraction of trade that reroutes per unit toll (0-1)
    retaliation_cost_ceiling: float     # max plausible cost of retaliation (USD equiv)
    p_retaliate: float                  # current belief: probability retaliation is severe

    def toll_revenue(self, tau: float) -> float:
        """Revenue from tolling at intensity tau, net of trade that reroutes away."""
        reroute_fraction = min(1.0, tau * self.reroute_elasticity)
        remaining_trade = self.annual_trade_value_usd * (1 - reroute_fraction)
        return tau * remaining_trade

    def retaliation_cost(self, tau: float) -> float:
        """Expected cost of retaliation, scaling with toll intensity and current belief."""
        return self.p_retaliate * self.retaliation_cost_ceiling * tau

    def reroute_loss(self, tau: float) -> float:
        """Lost strategic/economic value from trade permanently rerouting away."""
        reroute_fraction = min(1.0, tau * self.reroute_elasticity)
        return reroute_fraction * self.annual_trade_value_usd * 0.15  # assumed margin lost

    def payoff(self, tau: float) -> float:
        return self.toll_revenue(tau) - self.retaliation_cost(tau) - self.reroute_loss(tau)

    def best_response(self, tau_grid=None) -> float:
        """Grid-search best tau (swap for closed-form/gradient method later if needed)."""
        if tau_grid is None:
            tau_grid = [i / 100 for i in range(101)]
        return max(tau_grid, key=self.payoff)

    def update_belief(self, observed_retaliation_severity: float, learning_rate: float = 0.3):
        """
        Bayesian-ish belief update after observing another agent's move.

        observed_retaliation_severity: 0 (no retaliation) to 1 (full-severity retaliation),
        as actually experienced by the agent whose move is being observed.

        If observed severity is below what was priced in, p_retaliate falls for
        every agent watching — this is the mechanism that produces imitation.
        """
        surprise = observed_retaliation_severity - self.p_retaliate
        self.p_retaliate = max(0.0, min(1.0, self.p_retaliate + learning_rate * surprise))


def run_imitation_round(agents: list[ChokepointAgent], initiator_name: str,
                         initiator_tau: float, actual_retaliation_severity: float):
    """
    One round: the initiator moves, every other agent observes the outcome
    and updates its belief, then recomputes its own best response.

    Returns dict of {agent_name: (tau_chosen, payoff)} for all non-initiator agents.
    """
    results = {}
    for agent in agents:
        if agent.name == initiator_name:
            continue
        agent.update_belief(actual_retaliation_severity)
        tau = agent.best_response()
        results[agent.name] = (tau, agent.payoff(tau))
    return results
