# QDel — Delivery simulation lab

QDel helps quick-commerce delivery-system designers explore capacity and dispatch strategies. The dashboard runs the **same Python / SimPy engine as the CLI**, inside a browser worker using Pyodide. No Python server, credentials, or database is needed for the hosted demo.

## Run locally

Requires Python 3.11 or later. The first browser load needs internet access for Pyodide 0.27.7 and optional Google Fonts. SimPy and the simulation source are bundled during the build.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/build.py
.venv/bin/python project.py --serve
```

Open http://localhost:8000. Use `--port 8080` to choose another port. The local server binds only to loopback. To publish independently, upload the contents of `dist/` to any static HTTPS host; serve `.zip` and `.js` files without rewriting them to HTML. Keep `worker.js`, `engine.zip`, and `index.html` on the same origin. Permit workers from self and scripts/WASM from https://cdn.jsdelivr.net in any custom CSP.

## Use the lab

1. Choose demand, customer count, rider fleet, packing capacity, constant rider speed, and FIFO or shortest-trip-first dispatch.
2. Apply the setup, then run, pause, or advance one simulated minute. Playback speed changes how quickly time advances; it does not change the model.
3. Inspect network movement, throughput, utilization, and the order ledger. Filter by stage or export all current orders to CSV.
4. Save a baseline, change a scenario, and compare at the same elapsed time. The baseline is stored on the current device. Use the same seed and SLA for comparable experiments. Runs are otherwise in memory and reset on reload.

## CLI and validation

```sh
.venv/bin/python project.py --duration 120 --riders 12 --processors 4 --demand 60 --seed 42 --export data/orders.csv
.venv/bin/python -m unittest discover -s tests -v
```

For other controls and strategies, use `Simulation(Config(...))` from `simulation.py`. `advance(minutes)` advances the existing run and returns a JSON-compatible snapshot. All configuration fields validate their ranges. The seed makes repeated runs reproducible, including when advanced in different step sizes.

## Model and interpretation

- Units: minutes and kilometres. One central store serves a 4 × 4 km square grid. Routes follow Manhattan distance, moving horizontally then vertically.
- Demand: exponential interarrival times at the configured **attempts/hour**. Customers are selected uniformly. Attempts by customers with an outstanding order are dropped; accepted demand can be lower than attempted demand.
- Customers share grid crossings (normally four homes per crossing). Each has at most one outstanding order.
- Packing: FIFO, one packer per order; bounded normal service time, mean 2.25 minutes, standard deviation 0.4, bounds 1–3.25 minutes. Packing capacity is released immediately after packing.
- Dispatch: ready orders queue for riders. FIFO prioritizes original order-placement time. Shortest-trip-first prioritizes route distance among waiting orders. Dispatch is nonpreemptive and may starve long trips under sustained demand.
- Riders: one order at a time, constant configured speed, 0.5-minute handoff, then a return to the store. A rider is unavailable during the entire outbound, handoff, and return trip. Packing and delivery overlap across different orders.
- The horizon stops the run with unfinished orders still present. Events exactly on the cutoff belong to the next interval and are not processed at the cutoff. There is no automatic drain period.
- Delivery duration includes queueing, packing, travel, and handoff. Average, P95, and SLA percentage use **completed orders**. The dashboard reports overdue unfinished orders separately. No completed deliveries means these metrics are unavailable, rather than zero.
- Utilization is cumulative occupied time / elapsed time / resource count, including resources still occupied at the cutoff. Rider utilization includes returns.
- Demand and service use separate seeded random generators. Changing staffing can change accepted demand because waiting customers cannot reorder. This model is a strategy sandbox, not an empirically calibrated forecast.

Not modeled: multiple stores, inventory, batching, reassignment, traffic, road networks, cancellations, payment, costs, weather, time-varying demand, or per-rider speeds. The UI’s model notes expose these assumptions to visitors.

## Project layout

- `components/`: customers, orders, city geometry, packers, riders, and fulfillment orchestration.
- `simulation.py`: configuration, seeded demand, event advancement, snapshots, metrics.
- `dashboard/`: responsive dashboard, visualization, and Python worker bridge.
- `scripts/build.py`: creates `dist/` and bundles the engine with SimPy and its license.
- `tests/`: reproducibility, capacity, lifecycle, dispatch, and input-validation checks.
- `site/.openai/hosting.json`: persistent Sites identity. The publishing checkout is isolated under `site/` to preserve this repository’s existing Git history and local edits.

Build again after Python or dashboard changes. Deployment does not require an API key; visitors’ simulations run on their own devices.
