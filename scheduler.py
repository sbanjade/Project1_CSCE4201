"""
CSCE 4201 Project: Simulated Annealing for Flow-Shop Scheduling

Implements R1-R5 experiments:
- R1: Allocate operations to machines
- R2: Compute makespan from schedule
- R3: SA on known small instance (J=6, N=4, M=4)
- R4: SA on random large instance (J=50, N=3, M=5)
- R5: SA on random large instance (J=50, N=5, M=3)
"""

from __future__ import annotations

import math
import random
from itertools import permutations
from typing import Callable, List, Sequence, Tuple


# R1: ALLOCATION AND VALIDATION


def validate_proc_times(proc_times: Sequence[Sequence[int]]) -> Tuple[int, int]:
    """Validate processing times and return (num_jobs, num_operations)."""
    if not proc_times:
        return (0, 0)
    
    num_jobs = len(proc_times)
    num_operations = len(proc_times[0])
    
    for job_id, job_times in enumerate(proc_times):
        if len(job_times) != num_operations:
            raise ValueError(
                f"Job {job_id} has {len(job_times)} operations "
                f"but expected {num_operations}"
            )
        for op_idx, proc_time in enumerate(job_times):
            if proc_time < 0:
                raise ValueError(
                    f"Job {job_id}, operation {op_idx} has negative time: {proc_time}"
                )
    
    return (num_jobs, num_operations)


def validate_machine_count(M: int) -> None:
    """Validate that machine count is positive."""
    if M <= 0:
        raise ValueError(f"Machine count must be positive, got M={M}")


def validate_job_sequence(job_sequence: Sequence[int], num_jobs: int) -> None:
    """Validate that job_sequence is a valid permutation."""
    expected_jobs = set(range(num_jobs))
    actual_jobs = set(job_sequence)
    
    if actual_jobs != expected_jobs:
        raise ValueError(f"Job sequence is not a valid permutation")
    
    if len(job_sequence) != len(set(job_sequence)):
        raise ValueError("Job sequence contains duplicates")


def allocate_operations_to_machines(
    job_sequence: Sequence[int],
    proc_times: Sequence[Sequence[int]],
    M: int,
) -> List[dict]:
    """
    R1: Allocate operations to machines and return detailed schedule.
    
    Algorithm:
      For each operation, schedule jobs in sequence order to machines.
      Each job starts when both machine and previous job are ready.
      Machine assignment rule: machine = operation_index mod M
    
    Returns:
      List of scheduled operations with job, operation, machine, start_time, end_time
    """
    # Validate inputs
    num_jobs, num_operations = validate_proc_times(proc_times)
    validate_machine_count(M)
    validate_job_sequence(job_sequence, num_jobs)
    
    # Initialize availability tracking
    machine_available = [0] * M
    job_ready = [0] * num_jobs
    schedule = []
    
    # Schedule each operation
    for op_idx in range(num_operations):
        machine = op_idx % M  # Round-robin machine assignment
        
        for job_id in job_sequence:
            start_time = max(machine_available[machine], job_ready[job_id])
            end_time = start_time + proc_times[job_id][op_idx]
            
            operation = {
                "job_id": job_id,
                "operation_index": op_idx,
                "machine": machine,
                "start_time": start_time,
                "end_time": end_time,
            }
            schedule.append(operation)
            
            machine_available[machine] = end_time
            job_ready[job_id] = end_time
    
    return schedule



# R2: MAKESPAN COMPUTATION


def compute_makespan(schedule: List[dict]) -> int:
    """
    R2: Compute makespan (total completion time) from a schedule.
    
    Returns the maximum end_time across all operations.
    """
    if not schedule:
        return 0
    return max(op["end_time"] for op in schedule)


def evaluate_sequence(
    job_sequence: Sequence[int],
    proc_times: Sequence[Sequence[int]],
    M: int,
) -> int:
    """Evaluate a job sequence and return its makespan."""
    if not proc_times:
        return 0

    num_jobs = len(proc_times)
    num_operations = len(proc_times[0])

    machine_available = [0] * M
    job_ready = [0] * num_jobs

    for op_idx in range(num_operations):
        machine = op_idx % M
        for job_id in job_sequence:
            start = max(machine_available[machine], job_ready[job_id])
            end = start + proc_times[job_id][op_idx]
            machine_available[machine] = end
            job_ready[job_id] = end

    return max(job_ready) if job_ready else 0



# R2 (Additional): BRUTE-FORCE OPTIMAL


def brute_force_optimal_sequence(
    proc_times: Sequence[Sequence[int]],
    M: int,
) -> Tuple[List[int], int]:
    """Find optimal job sequence by exhaustive enumeration (for small J only)."""
    num_jobs = len(proc_times)
    
    if num_jobs == 0:
        return ([], 0)
    
    best_sequence: List[int] = []
    best_makespan = math.inf
    
    for permutation in permutations(range(num_jobs)):
        current_sequence = list(permutation)
        current_makespan = evaluate_sequence(current_sequence, proc_times, M)
        
        if current_makespan < best_makespan:
            best_sequence = current_sequence
            best_makespan = current_makespan
    
    return (best_sequence, int(best_makespan))



# SA: SIMULATED ANNEALING ALGORITHM


def generate_initial_sequence(num_jobs: int) -> List[int]:
    """Generate initial sequence [0, 1, ..., num_jobs-1]."""
    return list(range(num_jobs))


def generate_greedy_sequence(proc_times: Sequence[Sequence[int]]) -> List[int]:
    """Generate sequence by descending total job processing time."""
    # Order jobs by descending total processing time
    return sorted(range(len(proc_times)), key=lambda job_id: -sum(proc_times[job_id]))


def swap_neighbor(sequence: Sequence[int]) -> List[int]:
    """Generate neighbor by swapping two random jobs."""
    neighbor = list(sequence)
    if len(neighbor) < 2:
        return neighbor
    i, j = random.sample(range(len(neighbor)), 2)
    neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
    return neighbor


def insertion_neighbor(sequence: Sequence[int]) -> List[int]:
    """Generate neighbor by moving a job to a different position."""
    neighbor = list(sequence)
    if len(neighbor) < 2:
        return neighbor
    remove_idx = random.randint(0, len(neighbor) - 1)
    job = neighbor.pop(remove_idx)
    insert_idx = random.randint(0, len(neighbor))
    neighbor.insert(insert_idx, job)
    return neighbor


def two_opt_neighbor(sequence: Sequence[int]) -> List[int]:
    """Generate neighbor by reversing a segment (2-opt move)."""
    neighbor = list(sequence)
    if len(neighbor) < 2:
        return neighbor
    i, j = sorted(random.sample(range(len(neighbor)), 2))
    neighbor[i:j + 1] = reversed(neighbor[i:j + 1])
    return neighbor


def generate_neighbor(sequence: Sequence[int]) -> List[int]:
    """Randomly select one of three neighborhood operators."""
    # Three moves: swap, insertion, 2-opt
    strategies: List[Callable[[Sequence[int]], List[int]]] = [
        swap_neighbor,
        insertion_neighbor,
        two_opt_neighbor,
    ]
    strategy = random.choice(strategies)
    return strategy(sequence)


def should_accept(delta: int, temperature: float) -> bool:
    """Metropolis criterion: accept improvements always; worse moves with probability."""
    if delta <= 0:
        return True
    if temperature <= 0:
        return False
    return random.random() < math.exp(-delta / temperature)


def simulated_annealing(
    proc_times: Sequence[Sequence[int]],
    M: int,
    seed: int = 42,
    T0: float = 18000,
    alpha: float = 0.99,
    iters_per_temp: int = 300,
    min_temp: float = 1,
    log_history: bool = True,
    initial_sequence: Sequence[int] | None = None,
) -> Tuple[List[int], int, List[int]]:
    """Perform Simulated Annealing to minimize makespan."""
    random.seed(seed)
    num_jobs = len(proc_times)

    # Initialize current solution
    if initial_sequence is None:
        current_sequence = generate_initial_sequence(num_jobs)
        random.shuffle(current_sequence)
    else:
        current_sequence = list(initial_sequence)
    current_makespan = evaluate_sequence(current_sequence, proc_times, M)

    # Initialize best solution tracker
    best_sequence = list(current_sequence)
    best_makespan = current_makespan
    history = [best_makespan] if log_history else []

    # Cooling loop
    temperature = T0
    while temperature >= min_temp:
        # Local search iterations at current temperature
        for _ in range(iters_per_temp):
            neighbor_sequence = generate_neighbor(current_sequence)
            neighbor_makespan = evaluate_sequence(neighbor_sequence, proc_times, M)
            delta = neighbor_makespan - current_makespan

            # Acceptance decision
            if should_accept(delta, temperature):
                current_sequence = neighbor_sequence
                current_makespan = neighbor_makespan

            # Update best if improved
            if current_makespan < best_makespan:
                best_sequence = list(current_sequence)
                best_makespan = current_makespan

            if log_history:
                history.append(best_makespan)

        # Decrease temperature
        temperature *= alpha

    return best_sequence, best_makespan, history


def multi_start_simulated_annealing(
    proc_times: Sequence[Sequence[int]],
    M: int,
    seed: int = 42,
    T0: float = 18000,
    alpha: float = 0.99,
    iters_per_temp: int = 300,
    min_temp: float = 1,
    num_restarts: int = 5,
    log_history: bool = True,
) -> Tuple[List[int], int, List[int]]:
    """Run multiple SA restarts with different initial solutions."""
    # Create diverse starting solutions: greedy + random shuffles
    seed_sequences: List[List[int]] = [generate_greedy_sequence(proc_times)]
    for restart_index in range(max(0, num_restarts - 1)):
        random.seed(seed + restart_index)
        shuffled_sequence = generate_initial_sequence(len(proc_times))
        random.shuffle(shuffled_sequence)
        seed_sequences.append(shuffled_sequence)

    best_sequence: List[int] = []
    best_makespan = math.inf
    combined_history: List[int] = []

    # Run SA from each starting solution
    for restart_index, initial_sequence in enumerate(seed_sequences):
        restart_seed = seed + restart_index
        candidate_sequence, candidate_makespan, candidate_history = simulated_annealing(
            proc_times=proc_times,
            M=M,
            seed=restart_seed,
            T0=T0,
            alpha=alpha,
            iters_per_temp=iters_per_temp,
            min_temp=min_temp,
            log_history=log_history,
            initial_sequence=initial_sequence,
        )

        # Keep global best across restarts
        if candidate_makespan < best_makespan:
            best_sequence = candidate_sequence
            best_makespan = candidate_makespan

        if log_history:
            combined_history.extend(candidate_history)

    return best_sequence, int(best_makespan), combined_history


def percent_improvement(initial: int, best: int) -> float:
    """Calculate percent improvement."""
    if initial == 0:
        return 0.0
    return ((initial - best) / initial) * 100.0



# R3: KNOWN SMALL INSTANCE (J=6, N=4, M=4)

def run_r3_experiment() -> dict:
    """
    R3: Test SA on known small instance.
    
    Table: J=6 jobs, N=4 operations, M=4 machines
    """
    print("\n" + "="*70)
    print("R3: KNOWN SMALL INSTANCE (J=6, N=4, M=4)")
    
    # Fixed processing times from requirements
    proc_times = [
        [5, 2, 7, 4],
        [3, 6, 2, 5],
        [4, 5, 3, 6],
        [2, 4, 6, 3],
        [7, 3, 5, 2],
        [6, 7, 4, 5],
    ]
    M = 4
    J, N = 6, 4
    
    print(f"\nInstance: J={J}, N={N}, M={M}")
    print("Processing times (job × operation):")
    for j, times in enumerate(proc_times):
        print(f"  Job {j}: {times}")
    
    # Compute optimal via brute force
    print("\n[Computing optimal solution via brute force...]")
    optimal_seq, optimal_makespan = brute_force_optimal_sequence(proc_times, M)
    print(f"Optimal sequence: {optimal_seq}")
    print(f"Optimal makespan: {optimal_makespan}")
    
    # Initial random sequence
    print("\n[Running SA...]")
    seed_r3_data = 42
    seed_r3_sa = 42
    
    print(f"Data seed: {seed_r3_data}")
    
    initial_sequence = generate_initial_sequence(J)
    random.seed(seed_r3_data)
    random.shuffle(initial_sequence)
    initial_makespan = evaluate_sequence(initial_sequence, proc_times, M)
    print(f"Initial (random) sequence: {initial_sequence}")
    print(f"Initial makespan: {initial_makespan}")
    
    # Run SA
    T0 = 18000
    alpha = 0.99
    iters_per_temp = 300
    min_temp = 1
    num_restarts = 5
    
    print(f"\nSA Parameters:")
    print(f"  T0 (initial temp): {T0}")
    print(f"  alpha (cooling): {alpha}")
    print(f"  iterations/temp: {iters_per_temp}")
    print(f"  min_temp: {min_temp}")
    print(f"  num_restarts: {num_restarts}")
    print(f"  SA seed: {seed_r3_sa}")
    
    sa_sequence, sa_makespan, _ = multi_start_simulated_annealing(
        proc_times, M,
        seed=seed_r3_sa,
        T0=T0,
        alpha=alpha,
        iters_per_temp=iters_per_temp,
        min_temp=min_temp,
        num_restarts=num_restarts,
    )
    
    print(f"\nSA best sequence: {sa_sequence}")
    print(f"SA best makespan: {sa_makespan}")
    
    # Compare results
    print("\n" + "-"*70)
    print("RESULTS COMPARISON:")
    print("-"*70)
    print(f"{'Method':<20} {'Makespan':<15} {'Gap to Optimal':<15}")
    print("-"*70)
    print(f"{'Optimal (BF)':<20} {optimal_makespan:<15} {0:<15}")
    print(f"{'Initial':<20} {initial_makespan:<15} {initial_makespan - optimal_makespan:<15}")
    print(f"{'SA':<20} {sa_makespan:<15} {sa_makespan - optimal_makespan:<15}")
    print("-"*70)
    
    if sa_makespan == optimal_makespan:
        print("SA found OPTIMAL solution!")
    else:
        gap_pct = 100 * (sa_makespan - optimal_makespan) / optimal_makespan
        print(f"SA within {gap_pct:.1f}% of optimal")
    
    return {
        "initial": initial_makespan,
        "sa": sa_makespan,
        "optimal": optimal_makespan,
    }



# R4: LARGE INSTANCE (J=50, N=3, M=5)


def run_r4_experiment() -> dict:
    """
    R4: SA on random large instance.
    
    J=50 jobs, N=3 operations, M=5 machines
    Processing times uniform in [5, 50]
    """
    print("\n" + "="*70)
    print("R4: RANDOM LARGE INSTANCE (J=50, N=3, M=5)")
    print("="*70)
    
    J, N, M = 50, 3, 5
    seed_data = 42
    seed_sa = 42
    
    print(f"\nInstance: J={J}, N={N}, M={M}")
    print(f"Processing times: uniform random in [5, 50]")
    print(f"Seed (data generation): {seed_data}")
    
    # Generate random instance
    random.seed(seed_data)
    proc_times = [[random.randint(5, 50) for _ in range(N)] for _ in range(J)]
    
    # Initial random sequence
    initial_sequence = generate_initial_sequence(J)
    random.seed(seed_data)
    random.shuffle(initial_sequence)
    initial_makespan = evaluate_sequence(initial_sequence, proc_times, M)
    
    print(f"\nInitial (random) sequence makespan: {initial_makespan}")
    
    # SA parameters
    T0 = 18000
    alpha = 0.99
    iters_per_temp = 300
    min_temp = 1
    num_restarts = 5
    
    print(f"\nSA Parameters:")
    print(f"  T0 (initial temp): {T0}")
    print(f"  alpha (cooling): {alpha}")
    print(f"  iterations/temp: {iters_per_temp}")
    print(f"  min_temp: {min_temp}")
    print(f"  num_restarts: {num_restarts}")
    print(f"  SA seed: {seed_sa}")
    
    print(f"\n[Running Simulated Annealing...]")
    sa_sequence, sa_makespan, _ = multi_start_simulated_annealing(
        proc_times, M,
        seed=seed_sa,
        T0=T0,
        alpha=alpha,
        iters_per_temp=iters_per_temp,
        min_temp=min_temp,
        num_restarts=num_restarts,
    )
    
    improvement = percent_improvement(initial_makespan, sa_makespan)
    
    print(f"\nResults:")
    print(f"  Initial makespan: {initial_makespan}")
    print(f"  SA best makespan: {sa_makespan}")
    print(f"  Improvement: {improvement:.2f}%")
    
    return {
        "initial": initial_makespan,
        "sa": sa_makespan,
        "improvement_pct": improvement,
    }



# R5: LARGE INSTANCE (J=50, N=5, M=3)


def run_r5_experiment() -> dict:
    """
    R5: SA on random large instance.
    
    J=50 jobs, N=5 operations, M=3 machines
    Processing times uniform in [5, 50]
    """
    print("\n" + "="*70)
    print("R5: RANDOM LARGE INSTANCE (J=50, N=5, M=3)")
    print("="*70)
    
    J, N, M = 50, 5, 3
    seed_data = 123
    seed_sa = 42
    
    print(f"\nInstance: J={J}, N={N}, M={M}")
    print(f"Processing times: uniform random in [5, 50]")
    print(f"Seed (data generation): {seed_data}")
    
    # Generate random instance
    random.seed(seed_data)
    proc_times = [[random.randint(5, 50) for _ in range(N)] for _ in range(J)]
    
    # Initial random sequence
    initial_sequence = generate_initial_sequence(J)
    random.seed(seed_data)
    random.shuffle(initial_sequence)
    initial_makespan = evaluate_sequence(initial_sequence, proc_times, M)
    
    print(f"\nInitial (random) sequence makespan: {initial_makespan}")
    
    # SA parameters
    T0 = 18000
    alpha = 0.99
    iters_per_temp = 300
    min_temp = 1
    num_restarts = 5
    
    print(f"\nSA Parameters:")
    print(f"  T0 (initial temp): {T0}")
    print(f"  alpha (cooling): {alpha}")
    print(f"  iterations/temp: {iters_per_temp}")
    print(f"  min_temp: {min_temp}")
    print(f"  num_restarts: {num_restarts}")
    print(f"  SA seed: {seed_sa}")
    
    print(f"\n[Running Simulated Annealing...]")
    sa_sequence, sa_makespan, _ = multi_start_simulated_annealing(
        proc_times, M,
        seed=seed_sa,
        T0=T0,
        alpha=alpha,
        iters_per_temp=iters_per_temp,
        min_temp=min_temp,
        num_restarts=num_restarts,
    )
    
    improvement = percent_improvement(initial_makespan, sa_makespan)
    
    print(f"\nResults:")
    print(f"  Initial makespan: {initial_makespan}")
    print(f"  SA best makespan: {sa_makespan}")
    print(f"  Improvement: {improvement:.2f}%")
    
    return {
        "initial": initial_makespan,
        "sa": sa_makespan,
        "improvement_pct": improvement,
    }



# MAIN


def main() -> None:
    """Run all experiments: R3, R4, R5."""
    results_r3 = run_r3_experiment()
    results_r4 = run_r4_experiment()
    results_r5 = run_r5_experiment()
    
    # Summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print("\nR3 (Small Instance - J=6):")
    print(f"  Initial: {results_r3['initial']:>4}  |  SA: {results_r3['sa']:>4}  |  Optimal: {results_r3['optimal']:>4}")
    
    print("\nR4 (Large Instance - J=50, N=3, M=5):")
    print(f"  Initial: {results_r4['initial']:>4}  |  SA: {results_r4['sa']:>4}  |  Improvement: {results_r4['improvement_pct']:>6.2f}%")
    
    print("\nR5 (Large Instance - J=50, N=5, M=3):")
    print(f"  Initial: {results_r5['initial']:>4}  |  SA: {results_r5['sa']:>4}  |  Improvement: {results_r5['improvement_pct']:>6.2f}%")
    
    print("="*70)


if __name__ == "__main__":
    main()
