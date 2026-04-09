# R1 & R2: Core Scheduling Pseudocode

## R1: Validation and Job Allocation

### 1. Validate Processing Times
**Input:** `proc_times` - 2D table of processing times [job][operation]

**Pseudocode:**
```
1. If proc_times is empty, return (0, 0)
2. Extract num_operations from first job
3. For each job in proc_times:
   a. Verify job has exactly num_operations operations
   b. Verify all processing times are non-negative
4. Return (num_jobs, num_operations)
```

---

### 2. Validate Machine Count
**Input:** `M` - number of machines

**Pseudocode:**
```
1. If M <= 0, raise ValueError
2. Validation passes
```

---

### 3. Validate Job Sequence (Permutation)
**Input:** `job_sequence`, `num_jobs`

**Pseudocode:**
```
1. Create expected_jobs = [0, 1, ..., num_jobs-1]
2. If sorted(job_sequence) != expected_jobs:
   - Raise error (not a valid permutation)
3. Validation passes
```

---

### 4. Allocate Operations to Machines
**Input:** `job_sequence`, `proc_times`, `M` (number of machines)

**Pseudocode:**
```
1. Validate inputs (machine count, proc_times, job_sequence)
2. Initialize:
   - machine_available_times = [0] * M
   - job_ready_times = [0] * num_jobs
   - schedule = empty list

3. For operation_index from 0 to num_operations-1:
   a. machine = operation_index mod M
   
   b. For each job_id in job_sequence (in this order):
      i.   start_time = max(machine_available_times[machine], 
                            job_ready_times[job_id])
      ii.  end_time = start_time + proc_times[job_id][operation_index]
      iii. Create ScheduledOperation record:
           - job_id, operation_index, machine, start_time, end_time
      iv.  Add record to schedule
      v.   Update machine_available_times[machine] = end_time
      vi.  Update job_ready_times[job_id] = end_time

4. Return schedule
```

---

### 5. Compute Makespan
**Input:** `schedule` - list of scheduled operations

**Pseudocode:**
```
1. If schedule is empty, return 0
2. makespan = 0
3. For each operation in schedule:
   - If operation.end_time > makespan:
     makespan = operation.end_time
4. Return makespan
```

---

## R2: Brute-Force Optimal Solution

### Brute-Force Optimal Sequence Finder
**Input:** `proc_times`, `M` (number of machines)

**Pseudocode:**
```
1. Validate inputs (proc_times, machine count)
2. Initialize:
   - best_sequence = None
   - best_makespan = infinity

3. For each permutation of [0, 1, ..., num_jobs-1]:
   a. candidate_sequence = current permutation
   b. candidate_makespan = evaluate_sequence(candidate_sequence, 
                                             proc_times, M)
   c. If candidate_makespan < best_makespan:
      - best_sequence = candidate_sequence
      - best_makespan = candidate_makespan

4. If best_sequence is None:
   - Return ([], 0)
5. Else:
   - Return (best_sequence, best_makespan)
```

---

## Time Complexity Analysis

| Function | Complexity | Notes |
|----------|-----------|-------|
| Validate proc_times | O(J × N) | J = jobs, N = operations |
| Allocate ops | O(J × N) | Single pass scheduling |
| Compute makespan | O(J × N) | Scan all operations |
| Brute-force | O(J! × J × N) | Factorial in jobs |

---

## Key Design Decisions

1. **Job Ordering:** Same job sequence used across all machines (common permutation)
2. **Machine Assignment:** Operation at index `o` assigned to machine `o mod M`
3. **Start Time:** Operation starts at later of:
   - Machine becomes available
   - Previous job operation completes
4. **Brute-force Approach:** Tests all J! permutations; only feasible for small J
