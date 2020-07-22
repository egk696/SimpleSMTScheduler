from time import *

from simplesmtscheduler.utilities import *


def gen_cyclic_schedule_model(task_set, wcet_gap, optimize=False, verbose=False):
    # Find the hyper period
    hyper_period = find_lcm([o.period for o in task_set])
    utilization = sum(t.execution / t.period for t in task_set) * 100
    # Define solver
    if optimize:
        smt = Optimize()
        smt.set('priority', 'pareto')
    else:
        smt = Solver()
        smt.set('arith.solver', 3)
        smt.set('arith.auto_config_simplex', True)
    # Define constraints
    opt_bounds = []
    for task in task_set:
        for nn in range(floor(hyper_period / task.period)):
            task.release_instances.append(Int(task.name + "_" + "inst_" + str(nn)))
        task.releas_itr = iter(task.release_instances)
    # Search for task specific
    for test_task in task_set:
        prev_test_release_inst = None
        for nn in range(len(test_task.release_instances)):
            test_release_inst = next(test_task.releas_itr)
            # We only check release instances that fit within a hyperperiod
            smt.add(test_release_inst + test_task.execution <= hyper_period - wcet_gap)
            # If a task has a user fixed start PIT define it otherwise use offset
            if hasattr(test_task, 'fixed_pit'):
                smt.add(And(
                    test_release_inst <= nn * test_task.period + test_task.fixed_pit + test_task.jitter,
                    test_release_inst >= nn * test_task.period + test_task.fixed_pit - test_task.jitter
                ))
            else:
                smt.add(test_release_inst >= nn * test_task.period + test_task.offset)
            # Period constraint including jitter
            if prev_test_release_inst is not None:
                smt.add(And(
                    test_release_inst - prev_test_release_inst >= test_task.period - test_task.jitter,
                    test_release_inst - prev_test_release_inst <= test_task.period + test_task.jitter
                ))
            # Each task should finish within the deadline with jitter
            smt.add(test_task.release_instances[
                        nn] + test_task.execution <= nn * test_task.period + test_task.deadline + test_task.jitter)
            # The start PIT should not fall within the execution of another task including a BAG
            for other_task in [o for o in task_set if o != test_task]:
                if test_task.coreid == other_task.coreid:
                    for other_release_inst in other_task.release_instances:
                        smt.add(Or(
                            test_release_inst + test_task.execution + wcet_gap <= other_release_inst,
                            test_release_inst >= other_release_inst + other_task.execution + wcet_gap
                        ))
            if optimize:
                opt_bounds.append((test_release_inst, smt.minimize(test_release_inst)))
            prev_test_release_inst = test_release_inst
        # if optimize:
        #     opt_bounds.append((test_task, smt.minimize(Sum(test_task.release_instances))))

    # Try to solve
    elapsed_time = 0
    start_time = time()
    if smt.check() in (sat, unknown):
        solution_model = smt.model()
        elapsed_time = time() - start_time
    else:
        solution_model = None
        elapsed_time = time() - start_time

    if verbose:
        print("\nAsserted constraints...")
        for c in smt.assertions():
            print(c)
        print("\nModel Solution:")
        print(solution_model)
        if optimize:
            print("\nOptimization bounds:")
            for o_bound in opt_bounds:
                print(f"\t{o_bound[0]}: (lower = {o_bound[1].lower()}, upper = {o_bound[1].upper()})")
        print("\nZ3 statistics...")
        for k, v in smt.statistics():
            print("%s : %s" % (k, v))

    return solution_model, utilization, hyper_period, elapsed_time


def gen_schedule_activations(schedule, task_set):
    for task in task_set:
        for pit in task.release_instances:
            task.addStartPIT(schedule[pit].as_long())
