#!/usr/bin/python

import getopt

from simplesmtscheduler.schedulers import *
from simplesmtscheduler.utilities import *

taskSet = []
tasksFileName = ""
plotFileName = ""
schedulePlotPeriods = 1
plot = True
verbose = True
interactive = False
optimize = False

if __name__ == "__main__":
    print("Welcome to this simple SMT scheduler (SSMTS)...\n")

    if len(sys.argv) > 1:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hi:w:p:n:ovc",
                                       ["help", "itasks=", "wcet=", "plot=", "nperiods=", "optimize", "verbose",
                                        "code"])
        except getopt.GetoptError:
            print('Try : SimpleSMTScheduler.py -i <inputtasks> -w 35713 -p <outputplot> -n <plotperiods> -v -c')
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
                print('SimpleSMTScheduler.py -i <inputtasks> -w 35713 -p <outputplot> -n <plotperiods> -v -c')
                print("-h\t--help")
                print("-i\t--itasks")
                print("-w\t--wcet")
                print("-p\t--plot")
                print("-n\t--nperiods")
                print("-o\t--optimize")
                print("-v\t--verbose")
                print("-c\t--code")
                sys.exit()
            elif opt in ("-i", "--itasks"):
                tasksFileName = arg
            elif opt in ("-w", "--wcet"):
                wcet_offset = int(arg)
            elif opt in ("-p", "--plot"):
                plotFileName = arg
                plot = True
            elif opt in ("-n", "--nperiods"):
                schedulePlotPeriods = int(arg)
            elif opt in ("-o", "--optimize"):
                optimize = True
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

    print("Importing task set from file source...\n")
    parse_csv_taskset(tasksFileName, taskSet)
    baseFileName = os.path.basename(tasksFileName)

    taskSet.sort(key=lambda x: x.coreid, reverse=True)

    if [t for t in taskSet if t.execution > t.deadline]:
        sys.exit("\nTask set is not valid.\nExecution time violate period and deadline constraints")
    elif [t for t in taskSet if t.deadline > t.period]:
        sys.exit("\nTask set is not valid.\nDeadline times violate period constraints")
    elif [t for t in taskSet if t.offset > t.period]:
        sys.exit("\nTask set is not valid.\nOffset times violate period constraints")
    else:
        nr_cores = max([t.coreid for t in taskSet])
        for core_id in range(1, nr_cores + 1):
            core_tasks = [t for t in taskSet if t.coreid == core_id]
            hyper_period = find_lcm([t.period for t in core_tasks])
            utilization = sum(t.execution / t.period for t in core_tasks) * 100
            print(f"\nScheduling CPU ID {str(core_id)} started...")
            print("\tUtilization = %s %%" % str(utilization))
            print("\tSchedule hyper period = %s" % str(hyper_period))
            print("\tUsing optimization is", str(optimize))
            print("\tAllocated WCET RTS=", str(wcet_offset))

            schedule, utilization, hyperPeriod, elapsedTime = gen_cyclic_schedule_model(core_tasks, wcet_offset,
                                                                                        optimize,
                                                                                        verbose)
            print("\n\tSolver completed in %s ms" % (elapsedTime * SEC_TO_MS))
            if schedule is not None:
                gen_schedule_activations(schedule, core_tasks)

                print("\tName\tActivation Instances\t")
                for i in range(len(core_tasks)):
                    print("\tschedtime_t %s_sched_insts[%s] = %s;" % (
                    core_tasks[i].name, len(core_tasks[i].getStartPIT()),
                    str(core_tasks[i].getStartPIT()).replace("[", "{").replace(
                        "]", "}")))
            else:
                print(f"\tA schedule for CPU ID {core_id} could not be generated")

        if interactive:
            schedulePlot = plot_cyclic_schedule(os.path.splitext(baseFileName)[0], taskSet, hyperPeriod,
                                                schedulePlotPeriods)
            schedulePlot.show()
        elif plot:
            schedulePlot = plot_cyclic_schedule(os.path.splitext(baseFileName)[0], taskSet, hyperPeriod,
                                                schedulePlotPeriods)
            schedulePlot.savefig(plotFileName, dpi=MY_DPI)
            schedulePlot.show()

        if code:
            gen_schedule_code(os.path.splitext(baseFileName).replace(".csv", "_schedule.h"), tasksFileName, taskSet,
                              hyperPeriod,
                              utilization, True)
            sys.exit()
