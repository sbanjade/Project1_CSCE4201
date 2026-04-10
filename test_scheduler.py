"""Test suite for scheduler.py functions (R1 and R2)."""
from scheduler import (
    allocate_operations_to_machines,  # R1: Generate detailed schedule
    brute_force_optimal_sequence,      # R2: Find optimal permutation
    evaluate_sequence,                 # R3: Compute makespan from sequence
    generate_initial_sequence,         # Generate [0, 1, ..., J-1]
)


def main() -> None:
    """Test R1/R2 functionality with a small instance.
    
    Tests:
    - R1: Schedule allocation produces correct makespan
    - R2: Brute-force finds optimal job sequence
    """
    # Small test instance: 6 jobs, 4 operations each, 4 machines
    proc_times = [
        [5, 2, 7, 4],
        [3, 6, 2, 5],
        [4, 5, 3, 6],
        [2, 4, 6, 3],
        [7, 3, 5, 2],
        [6, 7, 4, 5],
    ]
    M = 4  # Number of machines

    print("Test R1: Allocation and Evaluation")
    print("="*60)
    
    # Generate initial sequence [0, 1, 2, 3, 4, 5]
    job_sequence = generate_initial_sequence(len(proc_times))
    # Allocate operations to machines and get detailed schedule
    schedule = allocate_operations_to_machines(job_sequence, proc_times, M)
    
    # Verify consistency: schedule's max end_time should equal makespan
    makespan_from_schedule = max(op["end_time"] for op in schedule) if schedule else 0
    makespan_from_evaluate = evaluate_sequence(job_sequence, proc_times, M)
    
    print(f"Sequence: {job_sequence}")
    print(f"Makespan from schedule: {makespan_from_schedule}")
    print(f"Makespan from evaluate_sequence: {makespan_from_evaluate}")
    print(f"Match: {makespan_from_schedule == makespan_from_evaluate}")
    
    print("\nTest R2: Brute-Force Optimal")
    print("="*60)
    
    # Find the best job sequence by exhaustive search
    best_sequence, best_makespan = brute_force_optimal_sequence(proc_times, M)
    print(f"Optimal sequence: {best_sequence}")
    print(f"Optimal makespan: {best_makespan}")
    
    # Compare optimal to initial sequence to show improvement
    initial_makespan = evaluate_sequence(job_sequence, proc_times, M)
    print(f"Initial sequence makespan: {initial_makespan}")
    print(f"Improvement: {initial_makespan - best_makespan}")
    print(f"Optimal is better: {best_makespan <= initial_makespan}")

if __name__ == "__main__":
    # Run all tests
    main()
