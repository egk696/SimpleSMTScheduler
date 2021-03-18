from time import *

from simplesmtscheduler.utilities import *


def distributed_task_mapping(task_set, nr_cores, wcet_gap=0, optimize=False, verbose=False):
    core_ids_mapping = []
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
    task_alloc = [
        [Int(task_set[t].name + "@" + str(c)) for t in range(len(task_set))] for c in range(nr_cores)
    ]

    # Each variable holds a true/false numeric value 0/1
    for c in range(nr_cores):
        for t in range(len(task_set)):
            smt.add(And(task_alloc[c][t] >= 0, task_alloc[c][t] <= 1))

    # At most each service can be active in one core
    for t in range(len(task_set)):
        smt.add(sum(task_alloc[c][t] for c in range(nr_cores)) == 1)

    # Each core assigned at least one task
    for c in range(nr_cores):
        smt.add(sum(task_alloc[c][t] for t in range(len(task_set))) >= 1)

    # Constraint utilization per core
    for c in range(nr_cores):
        smt.add(
            sum(task_alloc[c][t] * (task_set[t].execution / task_set[t].period) for t in
                range(len(task_set))) <= 0.5
        )

    # Try to solve
    start_time = time()
    if smt.check() in (sat, unknown):
        solution_model = smt.model()
        elapsed_time = time() - start_time
        print("Model success!")
    else:
        solution_model = None
        elapsed_time = time() - start_time
        print("Model failure!")

    if verbose:
        print("\nAsserted constraints...")
        for c in smt.assertions():
            print(c)
        if optimize:
            print("\nOptimization bounds:")
            for o_bound in opt_bounds:
                print(f"\t{o_bound[0]}: (lower = {o_bound[1].lower()}, upper = {o_bound[1].upper()})")
        print("\nZ3 statistics...")
        for k, v in smt.statistics():
            print("%s : %s" % (k, v))

    return solution_model, elapsed_time


def gen_rate_monotonic_schedule(task_set, wcet_gap, optimize=False, verbose=False):
    start_time = time()
    # Sorted copy
    task_set_sorted = sorted(task_set, key=lambda x: x.period, reverse=False)
    # Find hyper period
    hyper_period = find_lcm([o.period for o in task_set_sorted])
    utilization = sum(t.execution / t.period for t in task_set_sorted) * 100
    # Start scheduling
    sched_time = 0.0
    while sched_time <= hyper_period:
        for task in task_set_sorted:
            if len(task.activation_instances) > 0:
                act_pit = task.activation_instances.pop()
                if sched_time >= act_pit:
                    task.activation_instances.append(sched_time)
                    task.activation_instances.append(sched_time + task.period)
                else:
                    task.activation_instances.append(act_pit)
            else:
                task.activation_instances.append(sched_time)
                task.activation_instances.append(sched_time + task.period)
            sched_time = sched_time + task.execution + wcet_gap

    elapsed_time = time() - start_time
    return utilization, hyper_period, elapsed_time


def gen_cyclic_schedule_model(task_set, wcet_gap, optimize=False, verbose=False):
    # Sort by EDF
    task_set_sorted = sorted(task_set, key=lambda x: x.offset, reverse=False)
    # Find the hyper period
    hyper_period = find_lcm([o.period for o in task_set_sorted])
    utilization = sum(t.execution / t.period for t in task_set_sorted) * 100
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
    for task in task_set_sorted:
        for nn in range(int(floor(hyper_period / task.period))):
            task.release_instances.append(Int(task.name + "_" + "inst_" + str(nn)))
        task.releas_itr = iter(task.release_instances)
    # Search for task specific
    for task in task_set_sorted:
        prev_test_release_inst = None
        for nn in range(len(task.release_instances)):
            test_release_inst = next(task.releas_itr)
            # We only check release instances that fit within a hyperperiod
            smt.add(test_release_inst + task.execution <= hyper_period - wcet_gap)
            # If a task has a user fixed start PIT define it otherwise use offset
            if hasattr(task, 'fixed_pit'):
                smt.add(And(
                    test_release_inst <= nn * task.period + int(task.fixed_pit) + task.jitter,
                    test_release_inst >= nn * task.period + int(task.fixed_pit) - task.jitter
                ))
            else:
                smt.add(test_release_inst >= nn * task.period + task.offset)
            # Period constraint including jitter
            if prev_test_release_inst is not None:
                smt.add(And(
                    test_release_inst - prev_test_release_inst >= task.period - task.jitter,
                    test_release_inst - prev_test_release_inst <= task.period + task.jitter
                ))
                if optimize:
                    opt_bounds.append(
                        (test_release_inst, smt.minimize(test_release_inst - prev_test_release_inst - task.period)))
            # Each task should finish within the deadline with jitter
            smt.add(test_release_inst + task.execution + wcet_gap <= nn * task.period + task.deadline + task.jitter)
            # The start PIT should not fall within the execution of another task including a BAG
            for other_task in [o for o in task_set_sorted if o.name != task.name and o.coreid == task.coreid]:
                for other_release_inst in other_task.release_instances:
                    smt.add(Or(
                        test_release_inst + task.execution + wcet_gap <= other_release_inst,
                        test_release_inst >= other_release_inst + other_task.execution + wcet_gap
                    ))
            prev_test_release_inst = test_release_inst
        # if optimize:
        #     opt_bounds.append((test_task, smt.minimize(Sum(test_task.release_instances))))

    # Try to solve
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
