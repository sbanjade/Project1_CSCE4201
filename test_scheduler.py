from scheduler import (
    allocate_operations_to_machines,
    brute_force_optimal_sequence,
    evaluate_sequence,
    generate_initial_sequence,
)


def main() -> None:
    """Test R1/R2 functionality with a small instance."""
    proc_times = [
        [5, 2, 7, 4],
        [3, 6, 2, 5],
        [4, 5, 3, 6],
        [2, 4, 6, 3],
        [7, 3, 5, 2],
        [6, 7, 4, 5],
    ]
    M = 4

    print("Test R1: Allocation and Evaluation")
    print("="*60)
    
    job_sequence = generate_initial_sequence(len(proc_times))
    schedule = allocate_operations_to_machines(job_sequence, proc_times, M)
    
    # Compute makespan from schedule (max end_time)
    makespan_from_schedule = max(op["end_time"] for op in schedule) if schedule else 0
    makespan_from_evaluate = evaluate_sequence(job_sequence, proc_times, M)
    
    print(f"Sequence: {job_sequence}")
    print(f"Makespan from schedule: {makespan_from_schedule}")
    print(f"Makespan from evaluate_sequence: {makespan_from_evaluate}")
    print(f"Match: {makespan_from_schedule == makespan_from_evaluate}")
    
    print("\nTest R2: Brute-Force Optimal")
    print("="*60)
    
    best_sequence, best_makespan = brute_force_optimal_sequence(proc_times, M)
    print(f"Optimal sequence: {best_sequence}")
    print(f"Optimal makespan: {best_makespan}")
    
    # Verify the optimal is at least as good as our initial sequence
    initial_makespan = evaluate_sequence(job_sequence, proc_times, M)
    print(f"Initial sequence makespan: {initial_makespan}")
    print(f"Improvement: {initial_makespan - best_makespan}")
    print(f"Optimal is better: {best_makespan <= initial_makespan}")


if __name__ == "__main__":
    main()
