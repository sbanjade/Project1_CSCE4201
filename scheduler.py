"""Core scheduling utilities for permutation flow-shop style evaluation.

This file intentionally stops at the handoff marker at the bottom so a second
teammate can continue from there.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from typing import Iterable, List, Sequence, Tuple


@dataclass(frozen=True)
class ScheduledOperation:
    """Represents one scheduled operation for one job on one machine."""

    job_id: int
    operation_index: int
    machine: int
    start_time: int
    end_time: int


Schedule = List[ScheduledOperation]


def _validate_proc_times(proc_times: Sequence[Sequence[int]]) -> Tuple[int, int]:
    """Validate the processing-time table and return (num_jobs, num_operations)."""
    if not proc_times:
        return 0, 0

    num_operations = len(proc_times[0])
    for job_index, job_times in enumerate(proc_times):
        if len(job_times) != num_operations:
            raise ValueError(
                f"Job {job_index} has {len(job_times)} operations; "
                f"expected {num_operations}."
            )
        for operation_index, duration in enumerate(job_times):
            if duration < 0:
                raise ValueError(
                    f"Processing time must be non-negative: "
                    f"job {job_index}, operation {operation_index}."
                )

    return len(proc_times), num_operations


def _validate_machine_count(machine_count: int) -> None:
    """Ensure the number of machines is valid."""
    if machine_count <= 0:
        raise ValueError("M must be a positive integer.")


def _validate_job_sequence(
    job_sequence: Sequence[int],
    num_jobs: int,
) -> None:
    """Ensure the sequence is a permutation of all job ids."""
    expected_jobs = list(range(num_jobs))
    if sorted(job_sequence) != expected_jobs:
        raise ValueError(
            "job_sequence must be a permutation of all job ids "
            f"0 through {num_jobs - 1}."
        )


def generate_initial_sequence(num_jobs: int) -> List[int]:
    """Return the default initial sequence [0, 1, ..., J-1]."""
    if num_jobs < 0:
        raise ValueError("Number of jobs cannot be negative.")
    return list(range(num_jobs))


def allocate_ops_to_machines(
    job_sequence: Sequence[int],
    proc_times: Sequence[Sequence[int]],
    M: int,
) -> Schedule:
    """Build a valid schedule for the given common job permutation.

    PSEUDO-CODE
    1. Validate the machine count, processing-time table, and job permutation.
    2. Track the next available time for every machine.
    3. Track the completion time of the last scheduled operation for every job.
    4. For each operation index from 0 to N-1:
    5.   Determine which machine performs that operation using machine = o mod M.
    6.   Visit jobs in the shared job_sequence order for that machine.
    7.   Start each operation at the later of:
    8.     a) when its machine becomes available
    9.     b) when the previous operation of the same job has completed
    10.  Compute end time = start time + processing time.
    11.  Save a structured schedule record.
    12.  Update that machine's availability and the job's latest completion time.
    13. Return the full schedule.
    """
    _validate_machine_count(M)
    num_jobs, num_operations = _validate_proc_times(proc_times)
    _validate_job_sequence(job_sequence, num_jobs)

    machine_available_times = [0] * M
    job_ready_times = [0] * num_jobs
    schedule: Schedule = []

    # Each operation index defines the machine used by all jobs for that stage.
    for operation_index in range(num_operations):
        machine = operation_index % M

        # The same job order is followed on every machine.
        for job_id in job_sequence:
            start_time = max(
                machine_available_times[machine],
                job_ready_times[job_id],
            )
            end_time = start_time + proc_times[job_id][operation_index]

            schedule.append(
                ScheduledOperation(
                    job_id=job_id,
                    operation_index=operation_index,
                    machine=machine,
                    start_time=start_time,
                    end_time=end_time,
                )
            )

            machine_available_times[machine] = end_time
            job_ready_times[job_id] = end_time

    return schedule


def compute_makespan(schedule: Sequence[ScheduledOperation]) -> int:
    """Return the maximum completion time in the schedule.

    PSEUDO-CODE
    1. If the schedule is empty, return 0.
    2. Initialize the best completion time seen so far.
    3. Scan every scheduled operation.
    4. If an operation ends later than the current best time, update the best.
    5. Return the final maximum end time.
    """
    if not schedule:
        return 0
    return max(operation.end_time for operation in schedule)


def evaluate_sequence(
    job_sequence: Sequence[int],
    proc_times: Sequence[Sequence[int]],
    M: int,
) -> int:
    """Build the schedule for a sequence and return its makespan."""
    schedule = allocate_ops_to_machines(job_sequence, proc_times, M)
    return compute_makespan(schedule)


def brute_force_optimal_sequence(
    proc_times: Sequence[Sequence[int]],
    M: int,
) -> Tuple[List[int], int]:
    """Evaluate all job permutations and return the best one and its makespan."""
    num_jobs, _ = _validate_proc_times(proc_times)
    _validate_machine_count(M)

    best_sequence: List[int] | None = None
    best_makespan = float("inf")

    for candidate in permutations(range(num_jobs)):
        candidate_list = list(candidate)
        candidate_makespan = evaluate_sequence(candidate_list, proc_times, M)

        if candidate_makespan < best_makespan:
            best_sequence = candidate_list
            best_makespan = candidate_makespan

    if best_sequence is None:
        return [], 0

    return best_sequence, int(best_makespan)


def pretty_print_schedule(schedule: Sequence[ScheduledOperation]) -> None:
    """Print the schedule in a compact readable format."""
    if not schedule:
        print("Schedule is empty.")
        return

    header = f"{'Job':>3} {'Op':>3} {'Mach':>4} {'Start':>5} {'End':>5}"
    print(header)
    print("-" * len(header))
    for operation in schedule:
        print(
            f"{operation.job_id:>3} "
            f"{operation.operation_index:>3} "
            f"{operation.machine:>4} "
            f"{operation.start_time:>5} "
            f"{operation.end_time:>5}"
        )


def main() -> None:
    """Run the required R3 brute-force demonstration."""
    proc_times = [
        [5, 2, 7, 4],
        [3, 6, 2, 5],
        [4, 5, 3, 6],
        [2, 4, 6, 3],
        [7, 3, 5, 2],
        [6, 7, 4, 5],
    ]
    M = 4

    initial_sequence = generate_initial_sequence(len(proc_times))
    initial_makespan = evaluate_sequence(initial_sequence, proc_times, M)
    best_sequence, best_makespan = brute_force_optimal_sequence(proc_times, M)

    print("Initial sequence:", initial_sequence)
    print("Initial makespan:", initial_makespan)
    print("Optimal sequence:", best_sequence)
    print("Optimal makespan:", best_makespan)


if __name__ == "__main__":
    main()

# =========================
# PERSON B STARTS HERE
# =========================
