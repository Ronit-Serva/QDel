"""In-memory order records, exported explicitly rather than writing global CSVs."""
from dataclasses import dataclass, asdict


@dataclass
class Order:
    order_key: str
    customer_id: str
    customer_loc: tuple
    timestamp: float
    status: str = "queued"
    packing_at: float | None = None
    ready_at: float | None = None
    dispatched_at: float | None = None
    delivered_at: float | None = None
    rider_id: str | None = None
    processor_id: str | None = None
    distance_km: float = 0

    def read_order(self):
        return asdict(self)
