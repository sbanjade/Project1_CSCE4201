import itertools


def allocate_ops_to_machines(job_sequence, proc_times, M):
    """
    Build the full schedule for a given job order.
    Each operation goes to machine = op_index % M
    """

    num_jobs = len(proc_times)
    num_ops = len(proc_times[0])

    # stores when each machine becomes free
    machine_time = [0] * M

    # stores when each job is ready for its next operation
    job_time = [0] * num_jobs

    schedule = []

    # go job by job based on the chosen sequence
    for job in job_sequence:
        for op in range(num_ops):
            machine = op % M

            # operation can only start when:
            # 1. the machine is free
            # 2. the previous op of the same job is done
            start = max(machine_time[machine], job_time[job])
            end = start + proc_times[job][op]

            schedule.append({
                "job": job,
                "op": op,
                "machine": machine,
                "start": start,
                "end": end
            })

            # update machine and job availability
            machine_time[machine] = end
            job_time[job] = end

    return schedule


def compute_makespan(schedule):
    """
    Makespan = finishing time of the last completed operation
    """
    if len(schedule) == 0:
        return 0

    max_end = 0
    for item in schedule:
        if item["end"] > max_end:
            max_end = item["end"]

    return max_end


def sequence_makespan(job_sequence, proc_times, M):
    """
    Shortcut function:
    directly get makespan from a job sequence
    """
    schedule = allocate_ops_to_machines(job_sequence, proc_times, M)
    return compute_makespan(schedule)


def brute_force_optimal(proc_times, M):
    """
    Try all possible job orders.
    This is only realistic for the small case (R3).
    """

    num_jobs = len(proc_times)
    all_jobs = list(range(num_jobs))

    best_seq = None
    best_makespan = float("inf")

    for perm in itertools.permutations(all_jobs):
        current_seq = list(perm)
        current_cost = sequence_makespan(current_seq, proc_times, M)

        if current_cost < best_makespan:
            best_makespan = current_cost
            best_seq = current_seq

    return best_seq, best_makespan