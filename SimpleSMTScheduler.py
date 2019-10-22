#!/usr/bin/python

import csv
# Author: Eleftherios Kyriakakis (egk696@hotmail.com)
import getopt
from math import *
from time import *

import matplotlib.pyplot as plt
from z3 import *

MY_DPI = 480
SEC_TO_MS = 1000
US_TO_MS = 0.001
SYS_CLK = 0.0125
WCT_PWM_US = 2200
LISTEN_WIN = 500

taskSet = []
tasksFileName = ""
scheduleFileName = ""
schedulePlotPeriods = 1
plot = True
verbose = True
interactive = False


class Task:
    def __init__(self, period: float, deadline: float, execution: float, name: str, fixed_pit: int = None,
                 elasticity: float = 0):
        self.name = name
        self.period = ceil(period)
        self.deadline = ceil(deadline)
        self.execution = ceil(execution)
        self.start_pit = Int(name + "_pit")
        self.elasticity = elasticity
        if fixed_pit is not None:
            self.fixed_pit = fixed_pit

        print("--Task_" + name + "()")
        print("\tT=%s μs" % period)
        print("\tD=%s μs" % deadline)
        print("\tC=%s μs" % execution)
        if fixed_pit is not None:
            print("\tS=%s μs" % fixed_pit)

    def setStartPIT(self, pit: float):
        self.pit = pit

    def getStartPIT(self):
        return self.pit


def find_lcm(numbers):
    lcm = numbers[0]
    for ii in numbers[1:]:
        lcm = int(lcm * ii / gcd(lcm, ii))
    return lcm


def gen_schedule(task_set):
    # Find the hyper period
    hyper_period = find_lcm([o.period for o in task_set])
    print("\nSchedule hyper period = %s" % hyper_period)
    # Define constraints
    s = Solver()
    # Define a set keep the constraints
    # Search for distinct values
    s.add(Distinct([t.start_pit for t in task_set]))
    # The sum of durations should not exceed the hyper period
    s.add(Sum([t.start_pit + t.execution for t in task_set]) <= hyper_period)
    # Search for task specific
    for task in task_set:
        # Each task should finish within the deadline
        s.add(task.start_pit + task.execution < task.deadline)
        # If a task has a user fixed start PIT define it
        if hasattr(task, 'fixed_pit'):
            s.add(task.start_pit == task.fixed_pit)
        else:
            s.add(task.start_pit >= 0)
        # Constraints against the other tasks
        others = [o for o in task_set if o != task]
        for jj in range(floor(hyper_period / task.period)):
            for ot in others:
                # The start PIT should not fall within the execution of another task
                for kk in range(floor(hyper_period / task.period)):
                    s.add(Or(jj * task.period + task.start_pit + task.execution < kk * ot.period + ot.start_pit,
                             jj * task.period + task.start_pit > kk * ot.period + ot.start_pit + ot.execution))

    # Try to solve
    elapsed_time = 0
    start_time = time()
    if s.check() == sat:
        m = s.model()
        elapsed_time = time() - start_time
        print("\nSatisfied by the following activation times in μs:")
        print(m)
    else:
        m = None
        print("\nCould not be solved")

    if verbose:
        print("\nAsserted constraints...")
        for c in s.assertions():
            print(c)
        print("\nZ3 statistics...")
        for k, v in s.statistics():
            print("%s : %s" % (k, v))

        print("\nSolver completed in %s ms" % (elapsed_time * SEC_TO_MS))

    return m, hyper_period


def plot_schedule(task_set, hyper_period, periods):
    # Declaring a figure "gnt"
    fig, axis = plt.subplots()

    # Setting Y-axis limits
    axis.set_ylim(0, len(task_set) * 10)

    # Setting X-axis limits
    axis.set_xlim(0, periods * Sum([t.getStartPIT() + t.execution for t in task_set]))
    # axis.set_xlim(0, hyperPeriod * periods)
    # Setting labels for x-axis and y-axis
    axis.set_xlabel('Schedule Timeline (μs)')
    axis.set_ylabel('Tasks')

    # axis.set_xticks(range(0, periods*Sum([t.getStartPIT()+t.execution for t in taskSet]), 5000))
    axis.set_xticks(range(0, hyper_period * periods, int(hyper_period * periods / 10)))

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

    for i in range(len(task_set)):
        # Constructing task execution
        taskExecutionBars = []
        for jj in range(floor(hyper_period * periods / task_set[i].period)):
            taskExecutionBars.append((jj * task_set[i].period + task_set[i].getStartPIT(), task_set[i].execution))
        # Declaring a bar in schedule
        axis.broken_barh(taskExecutionBars, (i * 10, 10), label=task_set[i].name, linewidth=0.3, edgecolors='black',
                         facecolors=cmap(i))

    # Rotate labels to fit nicely
    fig.autofmt_xdate()

    return plt


if __name__ == "__main__":
    print("\nWelcome to this simple SMT scheduler (SSMTS)...")

    if len(sys.argv) > 1:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hi:o:n:pv",
                                       ["help", "itasks=", "osched=", "nperiods=", "plot", "verbose"])
        except getopt.GetoptError:
            print('test.py -i <inputtasks> -o <outputschedule> -n <plotperiods> -p -v')
            sys.exit(2)
        plot = False
        verbose = False
        schedulePlotPeriods = 1
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print('test.py -i <inputtasks> -o <outputschedule> -n <plotperiods> -p -v')
                print("-h\t--help")
                print("-i\t--itasks")
                print("-o\t--osched")
                print("-n\t--nperiods")
                print("-p\t--plot")
                print("-v\t--verbose")
                sys.exit()
            elif opt in ("-i", "--itasks"):
                tasksFileName = arg
            elif opt in ("-o", "--osched"):
                scheduleFileName = arg
            elif opt in ("-n", "--nperiods"):
                schedulePlotPeriods = int(arg)
            elif opt in ("-p", "--plot"):
                plot = True
            elif opt in ("-v", "--verbose"):
                verbose = True
    else:
        interactive = True

    if interactive:
        tasksFileName = input("\nEnter the csv file for the tasks to be scheduled: ")

    with open(tasksFileName, 'r') as f:
        reader = csv.reader(f)
        isFirstRow = True
        for row in reader:
            if isFirstRow:
                isFirstRow = False
            else:
                try:
                    period = float(row[0])
                except ValueError:
                    period = 0
                try:
                    deadine = float(row[1])
                except ValueError:
                    deadine = 0
                try:
                    execution = float(row[2])
                except ValueError:
                    execution = 0
                try:
                    name = str(row[3])
                except ValueError:
                    name = "SomeTask"
                try:
                    fixed = float(row[4])
                except ValueError:
                    fixed = None
                taskSet.append(Task(period, deadine, execution, name, fixed))

    if [t for t in taskSet if t.execution > t.period or t.execution > t.deadline]:
        sys.exit("\nTask set is not valid.\nExecution times violate period and deadline constraints")
    else:
        schedule, hyperPeriod = gen_schedule(taskSet)

        if schedule is not None:
            for i in range(len(taskSet)):
                taskSet[i].setStartPIT(schedule.evaluate(taskSet[i].start_pit).as_long())

            taskSet.sort(key=lambda x: x.getStartPIT())

            schedulePlot = plot_schedule(taskSet, hyperPeriod, schedulePlotPeriods)

            if interactive:
                schedulePlot.show()
            elif plot:
                schedulePlot.savefig(scheduleFileName, dpi=MY_DPI)

            sys.exit()
        else:
            sys.exit("\nA schedule could not be generated")
