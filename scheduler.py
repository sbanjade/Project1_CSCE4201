"""
R3, R4, R5: SIMULATED ANNEALING SCHEDULING EXPERIMENTS

This file implements Simulated Annealing for permutation flow-shop scheduling:
- R3: Simulated Annealing algorithm with neighbor operators
- R4: Large instance experiment (J=50, N=3, M=5)
- R5: Large instance experiment (J=50, N=5, M=3)

Core scheduling functions (from R1/R2) are included as helpers.
"""

from __future__ import annotations

import math
import random
from typing import Callable, List, Sequence, Tuple


# ============================================================================
# CORE SCHEDULING HELPERS (from R1/R2)
# ============================================================================


def evaluate_sequence(
    job_sequence: Sequence[int],
    proc_times: Sequence[Sequence[int]],
    M: int,
) -> int:
    """Evaluate a sequence and return makespan.
    
    Algorithm:
    1. For each operation, schedule jobs in sequence order
    2. Each job starts when both machine and previous job are ready
    3. Return maximum completion time across all operations
    """
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

    return compute_makespan(job_ready)


def compute_makespan(completion_times: Sequence[int]) -> int:
    """Return the maximum completion time across all jobs."""
    return max(completion_times) if completion_times else 0


def generate_initial_sequence(num_jobs: int) -> List[int]:
    """Return the default initial sequence [0, 1, ..., num_jobs-1]."""
    return list(range(num_jobs))


def generate_greedy_sequence(proc_times: Sequence[Sequence[int]]) -> List[int]:
    """Build a simple priority order using total job processing time."""
    return sorted(range(len(proc_times)), key=lambda job_id: -sum(proc_times[job_id]))



def swap_neighbor(sequence: Sequence[int]) -> List[int]:
    """Generate a neighbor by swapping two random jobs in the sequence."""
    neighbor = list(sequence)
    if len(neighbor) < 2:
        return neighbor
    i, j = random.sample(range(len(neighbor)), 2)
    neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
    return neighbor


def insertion_neighbor(sequence: Sequence[int]) -> List[int]:
    """Generate a neighbor by removing a random job and inserting it elsewhere."""
    neighbor = list(sequence)
    if len(neighbor) < 2:
        return neighbor
    remove_idx = random.randint(0, len(neighbor) - 1)
    job = neighbor.pop(remove_idx)
    insert_idx = random.randint(0, len(neighbor))
    neighbor.insert(insert_idx, job)
    return neighbor


def two_opt_neighbor(sequence: Sequence[int]) -> List[int]:
    """Generate a neighbor using 2-opt: reverse a random segment."""
    neighbor = list(sequence)
    if len(neighbor) < 2:
        return neighbor
    i, j = sorted(random.sample(range(len(neighbor)), 2))
    neighbor[i:j + 1] = reversed(neighbor[i:j + 1])
    return neighbor


def generate_neighbor(sequence: Sequence[int]) -> List[int]:
    """Randomly choose one of the supported neighborhood moves."""
    neighbor_strategies: List[Callable[[Sequence[int]], List[int]]] = [
        swap_neighbor,
        insertion_neighbor,
        two_opt_neighbor,
    ]
    strategy = random.choice(neighbor_strategies)
    return strategy(sequence)


def should_accept(delta: int, temperature: float) -> bool:
    """Accept all better moves and sometimes accept worse ones."""
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

    if initial_sequence is None:
        current_sequence = generate_initial_sequence(num_jobs)
        random.shuffle(current_sequence)
    else:
        current_sequence = list(initial_sequence)
    current_makespan = evaluate_sequence(current_sequence, proc_times, M)

    best_sequence = list(current_sequence)
    best_makespan = current_makespan
    history = [best_makespan] if log_history else []

    temperature = T0
    while temperature >= min_temp:
        for _ in range(iters_per_temp):
            neighbor_sequence = generate_neighbor(current_sequence)
            neighbor_makespan = evaluate_sequence(neighbor_sequence, proc_times, M)
            delta = neighbor_makespan - current_makespan

            if should_accept(delta, temperature):
                current_sequence = neighbor_sequence
                current_makespan = neighbor_makespan

            if current_makespan < best_makespan:
                best_sequence = list(current_sequence)
                best_makespan = current_makespan

            if log_history:
                history.append(best_makespan)

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
    """Run several SA restarts and keep the best global solution."""
    seed_sequences: List[List[int]] = [generate_greedy_sequence(proc_times)]
    for restart_index in range(max(0, num_restarts - 1)):
        random.seed(seed + restart_index)
        shuffled_sequence = generate_initial_sequence(len(proc_times))
        random.shuffle(shuffled_sequence)
        seed_sequences.append(shuffled_sequence)

    best_sequence: List[int] = []
    best_makespan = math.inf
    combined_history: List[int] = []

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

        if candidate_makespan < best_makespan:
            best_sequence = candidate_sequence
            best_makespan = candidate_makespan

        if log_history:
            combined_history.extend(candidate_history)

    return best_sequence, int(best_makespan), combined_history


def percent_improvement(initial: int, best: int) -> float:
    """Calculate percent improvement from initial to best solution."""
    if initial == 0:
        return 0.0
    return ((initial - best) / initial) * 100.0


def run_r4_experiment() -> List[int]:
    """R4: SA on large instance (J=50, N=3, M=5)."""
    print("\nR4: Random Large Instance (J=50, N=3, M=5)")

    random.seed(42)
    J, N, M = 50, 3, 5
    proc_times = [[random.randint(5, 50) for _ in range(N)] for _ in range(J)]

    seed, T0, alpha, iters_per_temp, min_temp = 42, 18000, 0.99, 300, 1
    print(f"Seed: {seed}")
    print(f"SA Parameters: T0={T0}, alpha={alpha}, iterations_per_temperature={iters_per_temp}, min_temp={min_temp}")

    initial_sequence = generate_initial_sequence(J)
    initial_makespan = evaluate_sequence(initial_sequence, proc_times, M)
    print(f"Initial random sequence makespan: {initial_makespan}")

    sa_sequence, sa_makespan, history = multi_start_simulated_annealing(
        proc_times, M, seed=seed, T0=T0, alpha=alpha,
        iters_per_temp=iters_per_temp, min_temp=min_temp
    )

    print(f"Best SA makespan: {sa_makespan}")
    improvement = percent_improvement(initial_makespan, sa_makespan)
    print(f"Percent improvement: {improvement:.2f}%")
    return history


def run_r5_experiment() -> List[int]:
    """R5: SA on different large instance (J=50, N=5, M=3)."""
    print("\nR5: Random Large Instance (J=50, N=5, M=3)")

    random.seed(123)
    J, N, M = 50, 5, 3
    proc_times = [[random.randint(5, 50) for _ in range(N)] for _ in range(J)]

    seed, T0, alpha, iters_per_temp, min_temp = 42, 18000, 0.99, 300, 1
    print(f"Seed: {seed}")
    print(f"SA Parameters: T0={T0}, alpha={alpha}, iterations_per_temperature={iters_per_temp}, min_temp={min_temp}")

    initial_sequence = generate_initial_sequence(J)
    initial_makespan = evaluate_sequence(initial_sequence, proc_times, M)
    print(f"Initial random sequence makespan: {initial_makespan}")

    sa_sequence, sa_makespan, history = multi_start_simulated_annealing(
        proc_times, M, seed=seed, T0=T0, alpha=alpha,
        iters_per_temp=iters_per_temp, min_temp=min_temp
    )

    print(f"Best SA makespan: {sa_makespan}")
    improvement = percent_improvement(initial_makespan, sa_makespan)
    print(f"Percent improvement: {improvement:.2f}%")
    return history


def main() -> None:
    """Run all experiments: R4 and R5."""
    history_r4 = run_r4_experiment()
    history_r5 = run_r5_experiment()


if __name__ == "__main__":
    main()
