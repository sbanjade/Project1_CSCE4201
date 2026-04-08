from scheduler import allocate_ops_to_machines, compute_makespan, sequence_makespan, brute_force_optimal


# small test using the R3 table from the project
proc_times = [
    [5, 2, 7, 4],
    [3, 6, 2, 5],
    [4, 5, 3, 6],
    [3, 2, 4, 6],
    [7, 3, 5, 2],
    [5, 6, 7, 4]
]

M = 4
job_sequence = [0, 1, 2, 3, 4, 5]

schedule = allocate_ops_to_machines(job_sequence, proc_times, M)
makespan = compute_makespan(schedule)

print("Schedule:")
for item in schedule:
    print(item)

print("\nMakespan for this sequence:", makespan)

best_seq, best_cost = brute_force_optimal(proc_times, M)
print("\nBest sequence found by brute force:", best_seq)
print("Optimal makespan:", best_cost)