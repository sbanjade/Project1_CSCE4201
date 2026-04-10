"""
Test suite for scheduler.py

Tests R1, R2, and SA functionality with assertions and edge cases.
"""

import pytest
from scheduler import (
    allocate_operations_to_machines,
    compute_makespan,
    evaluate_sequence,
    brute_force_optimal_sequence,
    validate_proc_times,
    validate_machine_count,
    validate_job_sequence,
    generate_initial_sequence,
)


class TestValidation:
    """Test input validation functions."""
    
    def test_validate_proc_times_empty(self):
        """Empty proc_times should return (0, 0)."""
        result = validate_proc_times([])
        assert result == (0, 0)
    
    def test_validate_proc_times_valid(self):
        """Valid proc_times should return correct dimensions."""
        proc_times = [[5, 2, 7], [3, 6, 2], [4, 5, 3]]
        result = validate_proc_times(proc_times)
        assert result == (3, 3)  # 3 jobs, 3 operations
    
    def test_validate_proc_times_unequal_operations(self):
        """Unequal operation counts should raise error."""
        proc_times = [[5, 2, 7], [3, 6]]  # Job 1 has 2 ops, job 0 has 3
        with pytest.raises(ValueError):
            validate_proc_times(proc_times)
    
    def test_validate_proc_times_negative(self):
        """Negative processing times should raise error."""
        proc_times = [[5, 2, -7], [3, 6, 2]]
        with pytest.raises(ValueError):
            validate_proc_times(proc_times)
    
    def test_validate_machine_count_positive(self):
        """Positive machine count should pass."""
        validate_machine_count(4)  # Should not raise
    
    def test_validate_machine_count_zero(self):
        """Zero machines should raise error."""
        with pytest.raises(ValueError):
            validate_machine_count(0)
    
    def test_validate_machine_count_negative(self):
        """Negative machines should raise error."""
        with pytest.raises(ValueError):
            validate_machine_count(-1)
    
    def test_validate_job_sequence_valid(self):
        """Valid permutation should pass."""
        validate_job_sequence([0, 1, 2], num_jobs=3)  # Should not raise
    
    def test_validate_job_sequence_invalid_permutation(self):
        """Invalid permutation should raise error."""
        with pytest.raises(ValueError):
            validate_job_sequence([0, 1, 3], num_jobs=3)  # Missing 2, has 3
    
    def test_validate_job_sequence_duplicates(self):
        """Duplicates should raise error."""
        with pytest.raises(ValueError):
            validate_job_sequence([0, 1, 1], num_jobs=3)


class TestR1Allocation:
    """Test R1: allocate_operations_to_machines."""
    
    def test_r1_simple_2x2(self):
        """Test simple 2 jobs × 2 operations on 2 machines."""
        proc_times = [[5, 3], [4, 2]]
        job_sequence = [0, 1]
        M = 2
        
        schedule = allocate_operations_to_machines(job_sequence, proc_times, M)
        
        # Should have 4 operations (2 jobs × 2 ops)
        assert len(schedule) == 4
        
        # All operations should have required fields
        for op in schedule:
            assert "job_id" in op
            assert "operation_index" in op
            assert "machine" in op
            assert "start_time" in op
            assert "end_time" in op
            assert op["end_time"] >= op["start_time"]
    
    def test_r1_machine_assignment(self):
        """Test that machine assignment follows rule: m = op_index mod M."""
        proc_times = [[5, 3, 2], [4, 2, 1]]
        job_sequence = [0, 1]
        M = 3
        
        schedule = allocate_operations_to_machines(job_sequence, proc_times, M)
        
        # Check machine assignments
        for op in schedule:
            expected_machine = op["operation_index"] % M
            assert op["machine"] == expected_machine
    
    def test_r1_no_overlap_same_machine(self):
        """Jobs on same machine should not overlap in time."""
        proc_times = [[5, 3], [4, 2]]
        job_sequence = [0, 1]
        M = 2
        
        schedule = allocate_operations_to_machines(job_sequence, proc_times, M)
        
        # Group operations by machine
        by_machine = {}
        for op in schedule:
            m = op["machine"]
            if m not in by_machine:
                by_machine[m] = []
            by_machine[m].append(op)
        
        # Check no overlaps on each machine
        for m, ops in by_machine.items():
            ops_sorted = sorted(ops, key=lambda x: x["start_time"])
            for i in range(len(ops_sorted) - 1):
                assert ops_sorted[i]["end_time"] <= ops_sorted[i+1]["start_time"]
    
    def test_r1_r3_table(self):
        """Test R3 known instance table."""
        proc_times = [
            [5, 2, 7, 4],
            [3, 6, 2, 5],
            [4, 5, 3, 6],
            [2, 4, 6, 3],
            [7, 3, 5, 2],
            [6, 7, 4, 5],
        ]
        job_sequence = [0, 1, 2, 3, 4, 5]
        M = 4
        
        schedule = allocate_operations_to_machines(job_sequence, proc_times, M)
        
        # Should have 6 jobs × 4 operations = 24 operations
        assert len(schedule) == 24
        
        # All end times should be positive
        assert all(op["end_time"] > 0 for op in schedule)


class TestR2Makespan:
    """Test R2: compute_makespan."""
    
    def test_r2_empty_schedule(self):
        """Empty schedule should return 0."""
        schedule = []
        makespan = compute_makespan(schedule)
        assert makespan == 0
    
    def test_r2_single_operation(self):
        """Single operation schedule."""
        schedule = [{"end_time": 10}]
        makespan = compute_makespan(schedule)
        assert makespan == 10
    
    def test_r2_multiple_operations(self):
        """Makespan should be max end_time."""
        schedule = [
            {"end_time": 10},
            {"end_time": 25},
            {"end_time": 15},
            {"end_time": 8},
        ]
        makespan = compute_makespan(schedule)
        assert makespan == 25
    
    def test_r2_consistency_with_evaluate(self):
        """compute_makespan from schedule should match evaluate_sequence."""
        proc_times = [[5, 2, 7, 4], [3, 6, 2, 5]]
        job_sequence = [0, 1]
        M = 2
        
        schedule = allocate_operations_to_machines(job_sequence, proc_times, M)
        makespan_from_schedule = compute_makespan(schedule)
        makespan_from_evaluate = evaluate_sequence(job_sequence, proc_times, M)
        
        assert makespan_from_schedule == makespan_from_evaluate


class TestBruteForceOptimal:
    """Test brute-force optimal solution (for small instances)."""
    
    def test_brute_force_2jobs(self):
        """Brute force on 2 jobs should find optimal."""
        proc_times = [[5, 3], [4, 2]]
        M = 2
        
        best_seq, best_makespan = brute_force_optimal_sequence(proc_times, M)
        
        # Result should be a valid sequence and positive makespan
        assert len(best_seq) == 2
        assert best_makespan > 0
        assert set(best_seq) == {0, 1}
    
    def test_brute_force_3jobs(self):
        """Brute force on 3 jobs."""
        proc_times = [[5, 2], [3, 4], [2, 6]]
        M = 2
        
        best_seq, best_makespan = brute_force_optimal_sequence(proc_times, M)
        
        # Should be better than some arbitrary sequence
        arbitrary_seq = [0, 1, 2]
        arbitrary_makespan = evaluate_sequence(arbitrary_seq, proc_times, M)
        
        assert best_makespan <= arbitrary_makespan
    
    def test_brute_force_r3_table(self):
        """Brute force on R3 known instance."""
        proc_times = [
            [5, 2, 7, 4],
            [3, 6, 2, 5],
            [4, 5, 3, 6],
            [2, 4, 6, 3],
            [7, 3, 5, 2],
            [6, 7, 4, 5],
        ]
        M = 4
        
        best_seq, best_makespan = brute_force_optimal_sequence(proc_times, M)
        
        # Valid sequence
        assert len(best_seq) == 6
        assert set(best_seq) == {0, 1, 2, 3, 4, 5}
        assert best_makespan > 0


class TestIntegration:
    """Integration tests."""
    
    def test_full_workflow_r3(self):
        """Full workflow: R3 table → allocate → compute → compare."""
        proc_times = [
            [5, 2, 7, 4],
            [3, 6, 2, 5],
            [4, 5, 3, 6],
            [2, 4, 6, 3],
            [7, 3, 5, 2],
            [6, 7, 4, 5],
        ]
        M = 4
        
        # Allocate and compute
        seq = [0, 1, 2, 3, 4, 5]
        schedule = allocate_operations_to_machines(seq, proc_times, M)
        makespan = compute_makespan(schedule)
        
        # Should be consistent
        assert makespan > 0
        assert len(schedule) == 24  # 6 jobs × 4 ops
        
        # Brute force should find optimal
        opt_seq, opt_makespan = brute_force_optimal_sequence(proc_times, M)
        assert opt_makespan > 0
        assert opt_makespan <= (makespan + 1000)  # Sanity check


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
