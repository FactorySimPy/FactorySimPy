def compute_performance_metrics(stats, sim_time):
    """
    Compute cycle time, resource utilization, throughput, and % time spent in each state for each worker.

    Args:
        stats (dict): The stats dictionary from the component (key: worker id, value: stats dict).
        sim_time (float): The total simulation time.

    Returns:
        dict: A dictionary with metrics for each worker.
    """
    results = {}
    for worker_id, s in stats.items():
        total_time = sum(s["total_time_spent_in_states"].values())
        # Defensive: If sim_time is 0, avoid division by zero
        sim_time = max(sim_time, 1e-8)
        # Utilization: % time in PROCESSING_STATE
        util = s["total_time_spent_in_states"].get("PROCESSING_STATE", 0.0) / sim_time
        # Throughput: items processed per unit time
        num_processed = s.get("num_item_processed", 0) + s.get("num_pallet_processed", 0)
        throughput = num_processed / sim_time
        # Cycle time: average time per processed item
        cycle_time = (s["total_time_spent_in_states"].get("PROCESSING_STATE", 0.0) / num_processed) if num_processed > 0 else None
        # % time in each state
        pct_time_states = {state: (t / sim_time) * 100 for state, t in s["total_time_spent_in_states"].items()}
        # Discarded
        num_discarded = s.get("num_item_discarded", 0) + s.get("num_pallet_discarded", 0)

        results[worker_id] = {
            "utilization": util,
            "throughput": throughput,
            "cycle_time": cycle_time,
            "percent_time_in_states": pct_time_states,
            "num_processed": num_processed,
            "num_discarded": num_discarded,
        }
    return results






def aggregate_machine_stats(stats, sim_time):
    num_workers = len(stats)
    total_processed = sum(s["num_item_processed"] for s in stats.values())
    total_processing_time = sum(s["total_time_spent_in_states"]["PROCESSING_STATE"] for s in stats.values())
    utilization = total_processing_time / (num_workers * sim_time)
    throughput = total_processed / sim_time
    cycle_time = total_processing_time / total_processed if total_processed > 0 else None
    states = next(iter(stats.values()))["total_time_spent_in_states"].keys()
    percent_time_in_states = {
        state: sum(s["total_time_spent_in_states"][state] for s in stats.values()) / (num_workers * sim_time) * 100
        for state in states
    }
    return {
        "throughput": throughput,
        "cycle_time": cycle_time,
        "utilization": utilization,
        "percent_time_in_states": percent_time_in_states,
        "total_processed": total_processed,
    }




def aggregate_joint_stats1(stats, sim_time):
    num_workers = len(stats)
    total_item_processed = sum(s.get("num_item_processed", 0) for s in stats.values())
    total_pallet_processed = sum(s.get("num_pallet_processed", 0) for s in stats.values())
    total_processed = total_item_processed + total_pallet_processed
    total_processing_time = sum(s["total_time_spent_in_states"]["PROCESSING_STATE"] for s in stats.values())
    utilization = total_processing_time / (num_workers * sim_time)
    throughput = total_processed / sim_time
    cycle_time = total_processing_time / total_processed if total_processed > 0 else None
    states = next(iter(stats.values()))["total_time_spent_in_states"].keys()
    percent_time_in_states = {
        state: sum(s["total_time_spent_in_states"][state] for s in stats.values()) / (num_workers * sim_time) * 100
        for state in states
    }
    num_pallet_discarded = sum(s.get("num_pallet_discarded", 0) for s in stats.values())
    return {
        "throughput": throughput,
        "cycle_time": cycle_time,
        "utilization": utilization,
        "percent_time_in_states": percent_time_in_states,
        "total_item_processed": total_item_processed,
        "total_pallet_processed": total_pallet_processed,
        "num_pallet_discarded": num_pallet_discarded,
    }

def aggregate_split_stats1(stats, sim_time):
    num_workers = len(stats)
    total_item_processed = sum(s.get("num_item_processed", 0) for s in stats.values())
    total_pallet_processed = sum(s.get("num_pallet_processed", 0) for s in stats.values())
    total_processed = total_item_processed + total_pallet_processed
    total_processing_time = sum(s["total_time_spent_in_states"]["PROCESSING_STATE"] for s in stats.values())
    utilization = total_processing_time / (num_workers * sim_time)
    throughput = total_processed / sim_time
    cycle_time = total_processing_time / total_processed if total_processed > 0 else None
    states = next(iter(stats.values()))["total_time_spent_in_states"].keys()
    percent_time_in_states = {
        state: sum(s["total_time_spent_in_states"][state] for s in stats.values()) / (num_workers * sim_time) * 100
        for state in states
    }
    num_item_discarded = sum(s.get("num_item_discarded", 0) for s in stats.values())
    num_pallet_discarded = sum(s.get("num_pallet_discarded", 0) for s in stats.values())
    return {
        "throughput": throughput,
        "cycle_time": cycle_time,
        "utilization": utilization,
        "percent_time_in_states": percent_time_in_states,
        "total_item_processed": total_item_processed,
        "total_pallet_processed": total_pallet_processed,
        "num_item_discarded": num_item_discarded,
        "num_pallet_discarded": num_pallet_discarded,
    }

def aggregate_joint_stats(stats, sim_time):
    num_workers = len(stats)
    total_item_processed = sum(s.get("num_item_processed", 0) for s in stats.values())
    total_pallet_processed = sum(s.get("num_pallet_processed", 0) for s in stats.values())
    total_processed = total_item_processed + total_pallet_processed
    total_processing_time = sum(s["total_time_spent_in_states"]["PROCESSING_STATE"] for s in stats.values())
    utilization = total_processing_time / (num_workers * sim_time)
    throughput = total_processed / sim_time
    cycle_time = total_processing_time / total_processed if total_processed > 0 else None
    states = next(iter(stats.values()))["total_time_spent_in_states"].keys()
    percent_time_in_states = {
        state: sum(s["total_time_spent_in_states"][state] for s in stats.values()) / (num_workers * sim_time) * 100
        for state in states
    }
    num_pallet_discarded = sum(s.get("num_pallet_discarded", 0) for s in stats.values())
    return {
        "throughput": throughput,
        "cycle_time": cycle_time,
        "utilization": utilization,
        "percent_time_in_states": percent_time_in_states,
        "total_item_processed": total_item_processed,
        "total_pallet_processed": total_pallet_processed,
        "num_pallet_discarded": num_pallet_discarded,
    }

def aggregate_split_stats(stats, sim_time):
    num_workers = len(stats)
    total_item_processed = sum(s.get("num_item_processed", 0) for s in stats.values())
    total_pallet_processed = sum(s.get("num_pallet_processed", 0) for s in stats.values())
    total_processed = total_item_processed + total_pallet_processed
    total_processing_time = sum(s["total_time_spent_in_states"]["PROCESSING_STATE"] for s in stats.values())
    utilization = total_processing_time / (num_workers * sim_time)
    throughput = total_processed / sim_time
    cycle_time = total_processing_time / total_processed if total_processed > 0 else None
    states = next(iter(stats.values()))["total_time_spent_in_states"].keys()
    percent_time_in_states = {
        state: sum(s["total_time_spent_in_states"][state] for s in stats.values()) / (num_workers * sim_time) * 100
        for state in states
    }
    num_item_discarded = sum(s.get("num_item_discarded", 0) for s in stats.values())
    num_pallet_discarded = sum(s.get("num_pallet_discarded", 0) for s in stats.values())
    return {
        "throughput": throughput,
        "cycle_time": cycle_time,
        "utilization": utilization,
        "percent_time_in_states": percent_time_in_states,
        "total_item_processed": total_item_processed,
        "total_pallet_processed": total_pallet_processed,
        "num_item_discarded": num_item_discarded,
        "num_pallet_discarded": num_pallet_discarded,
    }