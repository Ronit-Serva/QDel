import unittest
from simulation import Config, Simulation


class SimulationTests(unittest.TestCase):
    def test_seed_and_incremental_advancement_are_reproducible(self):
        one, two = Simulation(), Simulation()
        a = one.advance(120)
        for _ in range(120):
            b = two.advance(1)
        self.assertEqual(a, b)
        self.assertGreater(a['metrics']['delivered'], 0)

    def test_lifecycle_and_capacity(self):
        sim = Simulation(Config(orders_per_hour=120, riders=3, processors=1))
        result = sim.advance(120)
        metrics = result['metrics']
        self.assertEqual(metrics['placed'], metrics['active'] + metrics['delivered'])
        self.assertGreater(metrics['queued'], 0)
        for key in ('rider_utilization', 'packer_utilization'):
            self.assertTrue(0 <= metrics[key] <= 100)
        for order in result['orders']:
            times = [order[key] for key in ('timestamp', 'packing_at', 'ready_at', 'dispatched_at', 'delivered_at') if order[key] is not None]
            self.assertEqual(times, sorted(times))
            if order['delivered_at'] is not None:
                expected = order['distance_km'] / sim.config.speed_kmh * 60 + .5
                self.assertAlmostEqual(order['delivered_at'] - order['dispatched_at'], expected)
        # No rider can begin a subsequent outbound trip before the preceding return is complete.
        for rider in sim.platform.riders:
            jobs = [o for o in sim.platform.orders if o.rider_id == rider.id]
            for previous, current in zip(jobs, jobs[1:]):
                self.assertGreaterEqual(current.dispatched_at + 1e-9,
                    previous.delivered_at + previous.distance_km / sim.config.speed_kmh * 60)

    def test_more_riders_relieve_backlog(self):
        lean = Simulation(Config(riders=2)).advance(120)['metrics']
        staffed = Simulation(Config(riders=30)).advance(120)['metrics']
        self.assertGreater(staffed['delivered'], lean['delivered'])
        self.assertLess(staffed['overdue'], lean['overdue'])

    def test_shortest_trip_policy_prioritizes_waiting_shorter_trip(self):
        sim = Simulation(Config(riders=1, processors=4, dispatch='shortest_trip', duration=10, orders_per_hour=1))
        customers = sim.platform.customers[:3]
        customers[0].loc = (2, 2)
        customers[1].loc = (2, 1.5)
        customers[2].loc = (.5, 0)
        first = customers[0].order()
        sim.env.run(until=4)
        far = customers[1].order()
        near = customers[2].order()
        sim.env.run(until=70)
        self.assertLess(first.dispatched_at, near.dispatched_at)
        self.assertLess(near.dispatched_at, far.dispatched_at)

    def test_horizon_and_invalid_inputs(self):
        sim = Simulation(Config(duration=10))
        self.assertEqual(sim.advance(100)['time'], 10)
        self.assertTrue(sim.advance(1)['finished'])
        for config in ({'riders':0}, {'duration':True}, {'dispatch':'unknown'}, {'seed':-1}):
            with self.assertRaises(ValueError):
                Config(**config)
        for step in (0, -1, float('nan'), float('inf'), True):
            with self.assertRaises(ValueError):
                sim.advance(step)

    def test_resources_are_released_after_demand_ends(self):
        sim = Simulation(Config(duration=10, orders_per_hour=120, riders=2))
        sim.advance(10)
        sim.env.run()
        self.assertTrue(all(o.status == 'delivered' for o in sim.platform.orders))
        self.assertEqual(len(sim.platform.available_riders.items), 2)
        self.assertEqual(len(sim.platform.available_processors.items), 4)
        self.assertEqual(sim.platform.dispatch_slots.count, 0)


if __name__ == '__main__':
    unittest.main()
