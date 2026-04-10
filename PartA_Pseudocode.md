# R1 & R2: CORE SCHEDULING PSEUDOCODE

## R1: `allocate_ops_to_machines(job_sequence, proc_times, M)`

**Purpose:** Convert a job sequence into a detailed operation schedule with start/end times.

**Input:**
- `job_sequence` - Permutation of job indices [0, 1, ..., J-1]
- `proc_times` - 2D table: proc_times[j][o] = processing time of job j on operation o
- `M` - Number of machines

**Output:**
- `schedule` - List of operations, each with: job, operation, machine, start_time, end_time

**Algorithm:**

```
1. Validate inputs (job sequence, proc_times dimensions, M > 0)

2. Initialize:
   machine_available[0...M-1]  ← 0  (each machine is free at time 0)
   job_ready[0...J-1]          ← 0  (each job is ready at time 0)
   schedule                    ← empty list

3. For each operation o from 0 to N-1:
     machine ← o mod M
     
     For each job j in job_sequence:
       start_time ← max(machine_available[machine], job_ready[j])
       end_time   ← start_time + proc_times[j][o]
       
       Add to schedule: {job: j, operation: o, machine: machine,
                         start_time: start_time, end_time: end_time}
       
       machine_available[machine] ← end_time
       job_ready[j]               ← end_time

4. Return schedule
```

**Key Properties:**
- **General:** Works for any J (jobs), N (operations), M (machines)
- **Deterministic:** Same sequence always produces same schedule
- **Time Complexity:** O(J × N)
- **Makespan = max(end_time)** of all operations

**Example (J=2, N=3, M=2):**

Input: 
- proc_times = [[5, 3, 2], [4, 2, 6]]
- job_sequence = [0, 1]
- M = 2

Execution:
```
Operation 0 → Machine 0:
  Job 0: start 0, end 5    → machine_available[0] = 5
  Job 1: start 5, end 9    → machine_available[0] = 9

Operation 1 → Machine 1:
  Job 0: start 3, end 6    → machine_available[1] = 6
  Job 1: start 9, end 11   → machine_available[1] = 11

Operation 2 → Machine 0:
  Job 0: start 9, end 11   → machine_available[0] = 11
  Job 1: start 11, end 17  → machine_available[0] = 17

Makespan = 17
```

---

## R2: `compute_makespan(schedule)`

**Purpose:** Extract the total makespan (project completion time) from a schedule.

**Input:**
- `schedule` - List of operations, each with end_time

**Output:**
- `makespan` - Integer: maximum end_time across all operations

**Algorithm:**

```
1. If schedule is empty:
     Return 0

2. makespan ← 0

3. For each operation in schedule:
     makespan ← max(makespan, operation.end_time)

4. Return makespan
```

**Complexity:**
- **Time:** O(number of operations) = O(J × N)
- **Space:** O(1)

**Properties:**
- Handles empty schedule gracefully
- Always returns non-negative integer
- Works for any schedule size
