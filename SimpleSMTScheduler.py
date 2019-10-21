# Author: Eleftherios Kyriakakis

import sys
import csv
import itertools
import matplotlib.pyplot as plt
import numpy as np
from time import *
from z3 import *
from math import *
from datetime import date

MY_DPI = 300
SEC_TO_MS = 1000
US_TO_MS = 0.001
SYS_CLK = 0.0125
WCT_PWM_US = 2200
LISTEN_WIN = 500

taskSet = []
tasksFileName = ""
show = True
verbose = True


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


def findLCM(numbers):
    lcm = numbers[0]
    for ii in numbers[1:]:
        lcm = int(lcm * ii / gcd(lcm, ii))
    return lcm


def genSchedule(taskSet):
    # Find the hyper period
    hyperperiod = findLCM([o.period for o in taskSet])
    print("\nSchedule hyper period = %s" % hyperperiod)
    # Define constraints
    s = Solver()
    # Define a set keep the constraints
    # Search for distinct values
    s.add(Distinct([t.start_pit for t in taskSet]))
    # The sum of durations should not exceed the hyper period
    s.add(Sum([t.start_pit + t.execution for t in taskSet]) <= hyperperiod)
    # Search for task specific
    for task in taskSet:
        # Each task should finish within the deadline
        s.add(task.start_pit + task.execution < task.deadline)
        # If a task has a user fixed start PIT define it
        if hasattr(task, 'fixed_pit'):
            s.add(task.start_pit == task.fixed_pit)
        else:
            s.add(task.start_pit >= 0)
        # Constraints against the other tasks
        others = [o for o in taskSet if o != task]
        for jj in range(floor(hyperperiod / task.period)):
            for ot in others:
                # The start PIT should not fall within the execution of another task
                for kk in range(floor(hyperperiod / task.period)):
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
        # print("\nAsserted constraints...")
        # for c in s.assertions():
        #     print(c)
        # print("\nZ3 statistics...")
        # for k, v in s.statistics():
        #     print("%s : %s" % (k, v))

        print("\nSolver completed in %s ms" % (elapsed_time * SEC_TO_MS))

    return m, hyperperiod


def drawSchedule(taskSet, hyperPeriod, periods):
    # Declaring a figure "gnt"
    fig, axis = plt.subplots()

    # Setting Y-axis limits
    axis.set_ylim(0, len(taskSet) * 10)

    # Setting X-axis limits
    axis.set_xlim(0, periods * Sum([t.getStartPIT() + t.execution for t in taskSet]))
    # axis.set_xlim(0, hyperPeriod * periods)
    # Setting labels for x-axis and y-axis
    axis.set_xlabel('Schedule Timeline (μs)')
    axis.set_ylabel('Tasks')

    # axis.set_xticks(range(0, periods*Sum([t.getStartPIT()+t.execution for t in taskSet]), 5000))
    axis.set_xticks(range(0, hyperPeriod * periods, int(hyperPeriod * periods / 20)))

    # Setting ticks on y-axis
    axis.set_yticks(range(5, len(taskSet) * 10 + 5, 10))
    # Labelling tickes of y-axis
    axis.set_yticklabels([t.name for t in taskSet])

    # # Setting graph attribute
    # axis.grid(True, 'both', 'both')

    # Show the major grid lines with dark grey lines
    plt.grid(b=True, which='major', color='#666666', linestyle='-')

    # Show the minor grid lines with very faint and almost transparent grey lines
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

    # Color map
    cmap = plt.cm.get_cmap('jet', len(taskSet))

    # for period in range(0, periods * hyperPeriod, hyperPeriod):

    for i in range(len(taskSet)):
        # Constructing task execution
        taskExecutionBars = []
        for jj in range(floor(hyperperiod * periods / taskSet[i].period)):
            taskExecutionBars.append((jj * taskSet[i].period + taskSet[i].getStartPIT(), taskSet[i].execution))
        # Declaring a bar in schedule
        axis.broken_barh(taskExecutionBars, (i * 10, 10), label=taskSet[i].name, linewidth=0.3, edgecolors='black',
                         facecolors=cmap(i))

    return plt


if __name__ == "__main__":
    print("\nWelcome to this simple SMT scheduler (SSMTS)...")

    if tasksFileName is None or tasksFileName == "":
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
        schedule, hyperperiod = genSchedule(taskSet)

        if schedule is not None:
            for i in range(len(taskSet)):
                taskSet[i].setStartPIT(schedule.evaluate(taskSet[i].start_pit).as_long())

            taskSet.sort(key=lambda x: x.getStartPIT())

            schedPlot = drawSchedule(taskSet, hyperperiod, 1)

            schedPlot.show()

            sys.exit()
        else:
            sys.exit("\nA schedule could not be generated")
