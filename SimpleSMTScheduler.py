#!/usr/bin/python

import csv
import getopt

from simplesmtscheduler.PeriodicTask import *
from simplesmtscheduler.schedulers import *
from simplesmtscheduler.utilities import *

taskSet = []
tasksFileName = ""
scheduleFileName = ""
schedulePlotPeriods = 1
plot = True
verbose = True
interactive = False

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
                    coreid = float(row[6])
                except ValueError:
                    coreid = None
                try:
                    name = str(row[7]).strip()
                except ValueError:
                    name = "Task %s" % rowIndex
                try:
                    func = str(row[8])
                except ValueError:
                    func = "void"

                taskSet.append(PeriodicTask(period, execution, deadline, offset, jitter, coreid, name, fixed, func))
                rowIndex = rowIndex + 1

    # Show Utilization
    utilization = sum(t.execution / t.period for t in taskSet) * 100
    print("\nUtilization = %s %%" % utilization)

    if [t for t in taskSet if t.execution > t.deadline]:
        sys.exit("\nTask set is not valid.\nExecution time violate period and deadline constraints")
    elif [t for t in taskSet if t.deadline > t.period]:
        sys.exit("\nTask set is not valid.\nDeadline times violate period constraints")
    elif [t for t in taskSet if t.offset > t.period]:
        sys.exit("\nTask set is not valid.\nOffset times violate period constraints")
    else:
        schedule, hyperPeriod = gen_cyclic_schedule(taskSet, wcet_offset, verbose)
        if schedule is not None:
            for task in taskSet:
                for pit in task.release_instances:
                    task.addStartPIT(schedule[pit].as_long())

            taskSet.sort(reverse=True, key=lambda x: x.getStartPIT()[0])

            if interactive:
                schedulePlot = plot_cyclic_schedule(taskSet, hyperPeriod, schedulePlotPeriods)
                schedulePlot.show()
            elif plot:
                schedulePlot = plot_cyclic_schedule(taskSet, hyperPeriod, schedulePlotPeriods)
                schedulePlot.savefig(scheduleFileName, dpi=MY_DPI)

            print("Name\tActivation Instances\t")
            for i in range(len(taskSet)):
                print("schedtime_t %s_sched_insts[%s] = %s;" % (taskSet[i].name, len(taskSet[i].getStartPIT()),
                                                                str(taskSet[i].getStartPIT()).replace("[", "{").replace(
                                                                    "]", "}")))

            if code:
                gen_schedule_code("simplesmtschedule.h", tasksFileName, taskSet, hyperPeriod, utilization)

            sys.exit()
        else:
            sys.exit("\nA schedule could not be generated")
