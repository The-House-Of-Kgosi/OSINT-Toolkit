# The Extortion Cascade

**How a single maritime chokepoint closure propagates into a global food,
energy, and market security crisis — via strategic imitation and the
collapse of marine insurability.**

## Thesis

Maritime chokepoints (Hormuz, Bab-el-Mandeb, Suez, Bosporus, Malacca,
Panama, the Danish Straits) are natural monopolies: each is a narrow
channel through which a disproportionate share of global energy, grain,
and containerized trade must pass, with no viable substitute route at
comparable cost. This gives whoever controls a chokepoint a latent
extortion option — toll, threaten, or close it — that is normally
restrained by the expectation of retaliation and reputational cost.

This project models what happens when that restraint breaks down once,
using a hypothetical Iranian toll/closure of the Strait of Hormuz as the
initiating event. The core claim is that the primary transmission
mechanism is not physical (cargo can usually be rerouted at a cost) —
it is **financial**: marine War Risk and P&I insurance repricing, and at
the extreme, insurer withdrawal of cover altogether. A chokepoint doesn't
have to be blocked to stop functioning; it just has to become
uninsurable.

Three coupled effects follow:

1. **Strategic imitation** — other chokepoint operators observe that a
   closure/toll was absorbed without catastrophic retaliation, which
   revises every other operator's payoff calculation in favor of doing
   the same.
2. **Insurance cascade** — premiums for the affected route spike
   (Lloyd's Joint War Committee listed-areas mechanism is the real-world
   analogue), and insurer risk-aversion determines whether this is a
   smooth cost increase or a discrete withdrawal of cover past a
   threshold.
3. **Sector propagation** — food security (Black Sea/Bosporus grain
   corridors), energy security (Hormuz/Bab-el-Mandeb crude and LNG), and
   market security (freight rates, commodity vol, sovereign credit
   spreads for import-dependent economies) absorb the shock through the
   insurance layer, not directly from the physical event.

## Architecture

```
src/
├── game_theory/     agent payoff functions, belief-updating, imitation dynamics
├── insurance/        premium repricing model, discrete withdrawal threshold
├── propagation/      network graph, DebtRank-style shock propagation across chokepoints/sectors
└── validation/       historical calibration: Ever Given (2021), Red Sea/Houthi (2023-24), Hormuz rhetoric episodes
```

### Why insurance sits in the middle, not the shock layer

Naive chokepoint models treat insurance as a cost that scales with
physical risk. This model treats it as a **discrete-state variable**:
insurers either reprice incrementally (raising premiums, trade
continues at higher cost) or withdraw cover past a risk threshold
(trade *stops* regardless of shipper risk tolerance, because cargo
without cover is uninsurable for financing, ports, and counterparties).
The second regime is what produces a cascade cliff-edge rather than a
smooth cost curve, and it's the mechanism that makes "existential
threat" a falsifiable claim rather than rhetoric — the difference
between goods getting more expensive and goods not moving at all.

## Data sources (planned)

- Lloyd's Market Association Joint War Committee listed areas (premium calibration signal)
- UNCTAD Review of Maritime Transport (chokepoint trade volumes)
- EIA World Oil Transit Chokepoints reports
- Baltic Exchange freight indices
- Historical event windows: Ever Given (Mar 2021), Houthi Red Sea attacks (Nov 2023–), Hormuz tension episodes

## Status

Scaffolding stage — payoff function and insurance threshold model in
progress.
