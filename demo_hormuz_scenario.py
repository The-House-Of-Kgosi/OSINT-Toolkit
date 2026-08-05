"""
End-to-end demo: Hormuz tolls -> belief updates propagate to other agents
-> insurance market reprices/withdraws -> sector stress computed.

Run: python notebooks/demo_hormuz_scenario.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.game_theory.payoff import ChokepointAgent, run_imitation_round
from src.insurance.threshold import InsuranceMarket
from src.propagation.network import SectorExposure, propagate

# --- Define agents (illustrative figures -- replace with UNCTAD/EIA data) ---
hormuz = ChokepointAgent("Hormuz", annual_trade_value_usd=1.2e12,
                          reroute_elasticity=0.3, retaliation_cost_ceiling=8e11,
                          p_retaliate=0.7)
suez = ChokepointAgent("Suez", annual_trade_value_usd=1.0e12,
                        reroute_elasticity=0.5, retaliation_cost_ceiling=3e11,
                        p_retaliate=0.6)
bosporus = ChokepointAgent("Bosporus", annual_trade_value_usd=1.5e11,
                            reroute_elasticity=0.6, retaliation_cost_ceiling=1e11,
                            p_retaliate=0.55)
malacca = ChokepointAgent("Malacca", annual_trade_value_usd=3.5e12,
                           reroute_elasticity=0.2, retaliation_cost_ceiling=1.5e12,
                           p_retaliate=0.65)

agents = [hormuz, suez, bosporus, malacca]

# --- Round 1: Hormuz tolls, retaliation turns out weaker than priced in ---
hormuz_tau = hormuz.best_response()
actual_retaliation_severity = 0.25  # lower than hormuz's own p_retaliate of 0.7 -- the "surprise"

print(f"Hormuz chosen toll intensity: {hormuz_tau:.2f}")
print(f"Actual retaliation severity observed: {actual_retaliation_severity}")
print()

results = run_imitation_round(agents, "Hormuz", hormuz_tau, actual_retaliation_severity)
for name, (tau, payoff) in results.items():
    agent = next(a for a in agents if a.name == name)
    print(f"{name}: updated p_retaliate={agent.p_retaliate:.2f}, "
          f"best-response tau={tau:.2f}, payoff=${payoff:,.0f}")

# --- Insurance layer reacts to updated beliefs ---
print("\n--- Insurance market response ---")
markets = {
    "Hormuz": InsuranceMarket("Hormuz", base_premium_rate=0.0003, risk_aversion=2.5, withdrawal_threshold=0.9),
    "Suez": InsuranceMarket("Suez", base_premium_rate=0.0002, risk_aversion=2.0, withdrawal_threshold=0.9),
    "Bosporus": InsuranceMarket("Bosporus", base_premium_rate=0.00015, risk_aversion=1.8, withdrawal_threshold=0.85),
    "Malacca": InsuranceMarket("Malacca", base_premium_rate=0.0001, risk_aversion=1.5, withdrawal_threshold=0.9),
}

imitation_count = sum(1 for name, (tau, _) in results.items() if tau > 0.3)
insurance_states = {}
insurance_states["Hormuz"] = markets["Hormuz"].update(hormuz.p_retaliate, actual_retaliation_severity, imitation_count)
for name, (tau, _) in results.items():
    agent = next(a for a in agents if a.name == name)
    insurance_states[name] = markets[name].update(agent.p_retaliate, actual_retaliation_severity, imitation_count)

for name, state in insurance_states.items():
    print(state)

# --- Sector stress ---
print("\n--- Sector stress ---")
food = SectorExposure("food", {"Bosporus": 0.5, "Suez": 0.3, "Hormuz": 0.05})
energy = SectorExposure("energy", {"Hormuz": 0.6, "Malacca": 0.25, "Suez": 0.1})
market = SectorExposure("market", {"Hormuz": 0.3, "Suez": 0.25, "Malacca": 0.25, "Bosporus": 0.1})

stress = propagate([food, energy, market], insurance_states)
for sector, score in stress.items():
    print(f"{sector}: stress={score:.2f}")
