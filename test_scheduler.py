from scheduler import (
    allocate_ops_to_machines,
    brute_force_optimal_sequence,
    compute_makespan,
    evaluate_sequence,
    generate_initial_sequence,
)


def main() -> None:
    proc_times = [
        [5, 2, 7, 4],
        [3, 6, 2, 5],
        [4, 5, 3, 6],
        [2, 4, 6, 3],
        [7, 3, 5, 2],
        [6, 7, 4, 5],
    ]
    M = 4

    job_sequence = generate_initial_sequence(len(proc_times))
    schedule = allocate_ops_to_machines(job_sequence, proc_times, M)
    makespan = compute_makespan(schedule)

    print("Sequence:", job_sequence)
    print("Makespan from compute_makespan:", makespan)
    print("Makespan from evaluate_sequence:", evaluate_sequence(job_sequence, proc_times, M))

    best_sequence, best_makespan = brute_force_optimal_sequence(proc_times, M)
    print("Best sequence:", best_sequence)
    print("Optimal makespan:", best_makespan)


if __name__ == "__main__":
    main()
