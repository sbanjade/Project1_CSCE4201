REFLECTION ON SIMULATED ANNEALING FOR SCHEDULING:

1. When SA Helped Most:
   - SA excels when the search space is large and contains many local optima.
   - In R4/R5 with 50 jobs, exhaustive search is infeasible, so SA provides
     good solutions quickly.
   - SA can escape local optima early due to probabilistic acceptance.

2. Neighbor Operator Trade-offs:
   - Swap: Simple, explores quickly, but may miss distant good solutions.
   - Insertion: Can reorder jobs more significantly; better for escaping traps.
   - 2-opt: Reverses segments; effective for sequence problems like TSP/scheduling.
   - Best choice depends on problem structure and cooling schedule.

3. Parameter Sensitivity:
   - T0 (initial temperature): Too low → greedy behavior; too high → random walk.
   - alpha (cooling rate): Slower cooling explores more but takes longer.
   - iters_per_temp: More iterations at each T improves convergence but costs time.
   - Optimal settings depend on instance size and desired solution quality vs runtime.

4. Key Design Choices:
   - Starting from a random permutation adds diversity and consistency.
   - Tracking history enables convergence analysis and visualization.
   - Fixed seed ensures reproducibility (critical for research/debugging).
   - All parameters are printed for complete experimental documentation.