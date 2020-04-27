#!/usr/bin/python
# Author: Eleftherios Kyriakakis

import csv
import getopt
from math import *
from time import *

import matplotlib.pyplot as plt
from z3 import *

MY_DPI = 480
SEC_TO_MS = 1000
US_TO_MS = 0.001
NS_TO_US = 1 / 1000

taskSet = []
tasksFileName = ""
scheduleFileName = ""
schedulePlotPeriods = 1
plot = True
verbose = True
interactive = False


class Task:

    def __init__(self, period: float, execution: float, deadline: float, offset: int, jitter: int,
                 name: str, fixed_pit: int = None, cfunc: str = "void"):
        self.name = name
        self.period = ceil(period)
        self.deadline = ceil(deadline)
        self.execution = ceil(execution)
        self.offset = offset
        self.jitter = ceil(jitter)
        self.release_instances = []
        self.cfunc = cfunc
        self.activation_instances = []

        if fixed_pit is not None:
            self.fixed_pit = fixed_pit

        print("Task_" + name + " {")
        print("  T=%s," % period)
        print("  C=%s," % execution)
        print("  D=%s," % deadline)
        print("  O=%s," % offset)
        print("  J=%s," % jitter)
        print("};")
        if fixed_pit is not None:
            print("\tS=%s μs" % fixed_pit)

    def addStartPIT(self, pit: float):
        self.activation_instances.append(pit)

    def setActivationInstancePIT(self, i: int, activation_pit: float):
        self.activation_instances[i] = activation_pit

    def getStartPIT(self):
        return self.activation_instances


def find_lcm(numbers):
    lcm = numbers[0]
    for ii in numbers[1:]:
        lcm = int(lcm * ii / gcd(lcm, ii))
    return lcm


def z3_abs(x):
    return If(x >= 0, x, -x)


def gen_schedule(task_set, wcet_gap):
    # Test utilization
    utilization = sum(t.execution / t.period for t in taskSet) * 100
    print("\nUtilization = %s %%" % utilization)
    # Find the hyper period
    hyper_period = find_lcm([o.period for o in task_set])
    print("Schedule hyper period = %s" % hyper_period)
    # Define constraints
    smt = Solver()
    for test_task in taskSet:
        for nn in range(floor(hyper_period / test_task.period)):
            test_task.release_instances.append(Int(test_task.name + "_" + "inst_" + str(nn)))
    # Search for task specific
    for test_task in task_set:
        for nn in range(len(test_task.release_instances)):
            smt.add(test_task.release_instances[nn] + test_task.execution <= hyper_period)
            # If a task has a user fixed start PIT define it
            if hasattr(test_task, 'fixed_pit'):
                smt.add(test_task.release_instances[nn] == nn * test_task.period + test_task.fixed_pit)
            else:
                smt.add(test_task.release_instances[nn] >= nn * test_task.period + test_task.offset)
            # Period constraint including jitter
            if nn > 0:
                smt.add(And(
                    test_task.release_instances[nn] - test_task.release_instances[
                        nn - 1] >= test_task.period - test_task.jitter,
                    test_task.release_instances[nn] - test_task.release_instances[
                        nn - 1] <= test_task.period + test_task.jitter
                )
                )
            # Each task should finish within the deadline with jitter
            smt.add(test_task.release_instances[
                        nn] + test_task.execution <= nn * test_task.period + test_task.deadline + test_task.jitter)
            # The start PIT should not fall within the execution of another task including a BAG
            for other_task in [o for o in task_set if o != test_task]:
                for kk in range(len(other_task.release_instances)):
                    smt.add(Or(
                        test_task.release_instances[nn] + test_task.execution + wcet_gap <=
                        other_task.release_instances[kk],
                        test_task.release_instances[nn] >= other_task.release_instances[
                            kk] + other_task.execution + wcet_gap
                    )
                    )
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


def plot_schedule(task_set, hyper_period, iterations):
    # Declaring a figure "gnt"
    fig, axis = plt.subplots()

    # Setting Y-axis limits
    axis.set_ylim(0, len(task_set) * 10)

    # Setting X-axis limits
    axis.set_xlim(0, hyperPeriod * iterations)

    # Setting labels for x-axis and y-axis
    axis.set_xlabel('Schedule Timeline')
    axis.set_ylabel('Tasks')

    # axis.set_xticks(range(0, periods*Sum([t.getStartPIT()+t.execution for t in taskSet]), 5000))
    axis.set_xticks(range(0, hyper_period * iterations, int(hyper_period * iterations / 10)))

    # Setting ticks on y-axis
    axis.set_yticks(range(5, len(task_set) * 10 + 5, 10))

    # Labelling tickes of y-axis
    axis.set_yticklabels([t.name for t in task_set])

    # Show the major grid lines with dark grey lines
    plt.grid(b=True, which='major', color='#666666', linestyle='-')

    # Show the minor grid lines with very faint and almost transparent grey lines
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

    # Color map
    cmap = plt.cm.get_cmap('jet', len(task_set))

    print("Schedule plotted for %s hyper-periods\n" % iterations)

    for i in range(len(task_set)):
        taskExecutionBars = []
        for hyper_iter in range(0, iterations):
            for jj in range(len(task_set[i].getStartPIT())):
                taskExecutionBars.append(
                    (hyper_iter * hyper_period + task_set[i].getStartPIT()[jj], task_set[i].execution))
        axis.broken_barh(taskExecutionBars, (i * 10, 10), label=task_set[i].name, linewidth=0.3, edgecolors='black',
                         facecolors=cmap(i))

    # Rotate labels to fit nicely
    fig.autofmt_xdate()

    return plt


if __name__ == "__main__":
    print("Welcome to this simple SMT scheduler (SSMTS)...\n")

    if len(sys.argv) > 1:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hi:o:w:n:pvc",
                                       ["help", "itasks=", "osched=", "wcet=", "nperiods=", "plot", "verbose",
                                        "code"])
        except getopt.GetoptError:
            print('Try : SimpleSMTScheduler.py -i <inputtasks> -o <outputschedule> -w 35713 -n <plotperiods> -p -v')
            print("Or : SimpleSMTScheduler.py --help")
            sys.exit(2)
        plot = False
        verbose = False
        code = False
        schedulePlotPeriods = 1
        wcet_offset = 0
        jitter = 0
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print('SimpleSMTScheduler.py -i <inputtasks> -o <outputschedule> -w 35713 -n <plotperiods> -p -v')
                print("-h\t--help")
                print("-i\t--itasks")
                print("-o\t--osched")
                print("-w\t--wcet")
                print("-n\t--nperiods")
                print("-p\t--plot")
                print("-v\t--verbose")
                print("-c\t--code")
                sys.exit()
            elif opt in ("-i", "--itasks"):
                tasksFileName = arg
            elif opt in ("-o", "--osched"):
                scheduleFileName = arg
            elif opt in ("-w", "--wcet"):
                wcet_offset = int(arg)
            elif opt in ("-n", "--nperiods"):
                schedulePlotPeriods = int(arg)
            elif opt in ("-p", "--plot"):
                plot = True
            elif opt in ("-v", "--verbose"):
                verbose = True
            elif opt in ("-c", "--code"):
                code = True
    else:
        code = False
        interactive = True
        wcet_offset = 0
        jitter = 0

    if interactive:
        tasksFileName = input("Enter the csv file for the tasks to be scheduled: ")
        wcet_offset = int(input("Enter the WCET allocation gap between activations: "))
        schedulePlotPeriods = int(input("Enter the number of hyper periods to be plotted: "))
        verbose = input("Enable statistics (Yes/No)? ") == "Yes"

    with open(tasksFileName, 'r') as f:
        print("Importing task set from file source...\n")
        reader = csv.reader(f)
        isFirstRow = True
        rowIndex = 0
        for row in reader:
            if isFirstRow:
                isFirstRow = False
            elif not str(row[0]).startswith("#"):
                try:
                    period = float(row[0])
                except ValueError:
                    period = 0
                try:
                    execution = float(row[1])
                except ValueError:
                    execution = 0
                try:
                    deadline = float(row[2])
                except ValueError:
                    deadline = 0
                try:
                    offset = float(row[3])
                except ValueError:
                    offset = 0
                try:
                    jitter = float(row[4])
                except ValueError:
                    jitter = 0
                try:
                    fixed = float(row[5])
                except ValueError:
                    fixed = None
                try:
                    name = str(row[6]).strip()
                except ValueError:
                    name = "Task %s" % rowIndex
                try:
                    func = str(row[7])
                except ValueError:
                    func = "void"

                taskSet.append(Task(period, execution, deadline, offset, jitter, name, fixed, func))
                rowIndex = rowIndex + 1

    if [t for t in taskSet if t.execution > t.deadline]:
        sys.exit("\nTask set is not valid.\nExecution times violate period and deadline constraints")
    else:
        schedule, hyperPeriod = gen_schedule(taskSet, wcet_offset)
        if schedule is not None:
            for task in taskSet:
                for pit in task.release_instances:
                    task.addStartPIT(schedule[pit].as_long())

            # taskSet.sort(key=lambda x: x.getStartPIT()[0])

            if interactive:
                schedulePlot = plot_schedule(taskSet, hyperPeriod, schedulePlotPeriods)
                schedulePlot.show()
            elif plot:
                schedulePlot = plot_schedule(taskSet, hyperPeriod, schedulePlotPeriods)
                schedulePlot.savefig(scheduleFileName, dpi=MY_DPI)

            print("Name\tActivation Instances\t")
            for i in range(len(taskSet)):
                print("%s_sched_insts[%s] = %s;" % (taskSet[i].name, len(taskSet[i].getStartPIT()),
                                                    str(taskSet[i].getStartPIT()).replace("[", "{").replace("]", "}")))

            sys.exit()
        else:
            sys.exit("\nA schedule could not be generated")
