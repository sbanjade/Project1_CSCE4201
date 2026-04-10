# Simulated Annealing for Flow-Shop Scheduling
## CSCE 4201 Project

This project implements Simulated Annealing (SA) for flow-shop scheduling optimization, with experiments on small and large instances.

---

## Files

- **scheduler.py** – Main implementation (R1–R5 experiments)
- **test_scheduler.py** – Test suite (21 assertion-based tests)
- **PartA_Pseudocode.md** – R1 and R2 pseudocode
- **PartB_Report.md** – Results and analysis
- **README.md** – This file

---

## Quick Start

### Requirements
- Python 3.8+
- Standard library only (math, random, itertools)

### Run Experiments
```bash
python scheduler.py
```

Executes R3 (known small instance), R4 (random J=50, N=3, M=5), and R5 (random J=50, N=5, M=3).

### Run Tests
```bash
python -m pytest test_scheduler.py -v
```

---

## Experiments

### R3: Small Known Instance (J=6, N=4, M=4)
- Fixed processing times
- Brute-force comparison: 6! = 720 permutations
- **Results:** Initial=43, SA=38, Optimal=38

### R4: Random Large Instance (J=50, N=3, M=5)
- Random processing times [5, 50]
- Data seed: 42
- **Results:** Initial=1625, SA=1473 (9.35% improvement)

### R5: Random Large Instance (J=50, N=5, M=3)
- Random processing times [5, 50]
- Data seed: 123
- **Results:** Initial=2894, SA=2859 (1.21% improvement)

---

## Key Components

**R1: Allocate Operations to Machines**  
Schedules jobs using round-robin machine assignment (operation_index mod M).

**R2: Compute Makespan**  
Returns maximum completion time from a schedule.

**Simulated Annealing**
- Initial temperature: 18,000
- Cooling rate: 0.99
- Iterations per temperature: 300
- Neighborhood operators: swap, insertion, 2-opt
- Metropolis acceptance criterion
- Multi-start: 5 restarts with fixed seed

---

## Test Coverage

- **Validation:** 9 tests (empty, invalid, negative values)
- **R1 Allocation:** 4 tests (correctness, machine assignment)
- **R2 Makespan:** 4 tests (edge cases, computation)
- **Brute-Force:** 3 tests (optimal verification)
- **Integration:** 1 end-to-end test

---

## Reproducibility

All experiments use fixed random seeds (data seed per experiment, SA seed = 42) for identical results across runs:

```bash
python scheduler.py  # Run multiple times, same output
```

