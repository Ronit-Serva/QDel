"""Run a reproducible simulation or serve the built dashboard."""
import argparse
import csv
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true", help="Serve dashboard at localhost:8000")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--duration", type=int, default=120)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--riders", type=int, default=12)
    parser.add_argument("--processors", type=int, default=4)
    parser.add_argument("--demand", type=int, default=60, help="Order attempts per hour")
    parser.add_argument("--export", type=Path, help="Write final orders to CSV")
    args = parser.parse_args()
    if args.serve:
        from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
        from functools import partial
        root = Path(__file__).parent / "dist"
        if not (root / "index.html").exists():
            parser.error("Build first: python scripts/build.py")
        print(f"QDel: http://localhost:{args.port}", flush=True)
        ThreadingHTTPServer(("127.0.0.1", args.port), partial(SimpleHTTPRequestHandler, directory=str(root))).serve_forever()
        return
    from simulation import Config, Simulation
    try:
        sim = Simulation(Config(duration=args.duration, seed=args.seed, riders=args.riders,
                                processors=args.processors, orders_per_hour=args.demand))
    except ValueError as error:
        parser.error(str(error))
    result = sim.advance(args.duration)
    print(json.dumps(result["metrics"], indent=2))
    if args.export:
        args.export.parent.mkdir(parents=True, exist_ok=True)
        from components.order import Order
        with args.export.open("w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(Order.__dataclass_fields__))
            writer.writeheader()
            writer.writerows(result["orders"])


if __name__ == "__main__":
    main()
