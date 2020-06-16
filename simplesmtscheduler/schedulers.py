from time import *

from simplesmtscheduler.utilities import *


def gen_cyclic_schedule(task_set, wcet_gap, plot=True, verbose=True, interactive=False):
    # Find the hyper period
    hyper_period = find_lcm([o.period for o in task_set])
    print("Schedule hyper period = %s" % hyper_period)
    # Define constraints
    smt = Solver()
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
            # If a task has a user fixed start PIT define it
            if hasattr(test_task, 'fixed_pit'):
                smt.add(test_release_inst == nn * test_task.period + test_task.fixed_pit)
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
            prev_test_release_inst = test_release_inst
    # Try to solve
    elapsed_time = 0
    start_time = time()
    if smt.check() in (sat, unknown):
        solution_model = smt.model()
        elapsed_time = time() - start_time
    else:
        solution_model = None
        time() - start_time
        print("\nCould not be solved: ", str(smt.check()))

    if verbose:
        print("\nModel Solution:")
        print(solution_model)
        print("\nAsserted constraints...")
        for c in smt.assertions():
            print(c)
        print("\nZ3 statistics...")
        for k, v in smt.statistics():
            print("%s : %s" % (k, v))

    print("\nSolver completed in %s ms\n" % (elapsed_time * SEC_TO_MS))

    return solution_model, hyper_period
