#!/usr/bin/python

import getopt
from statistics import stdev

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
                wcet_offset = float(arg)
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

    if [t for t in taskSet if t.execution > t.deadline]:
        sys.exit("\nTask set is not valid.\nExecution time violate period and deadline constraints")
    elif [t for t in taskSet if t.deadline > t.period]:
        sys.exit("\nTask set is not valid.\nDeadline times violate period constraints")
    elif [t for t in taskSet if t.offset > t.period]:
        sys.exit("\nTask set is not valid.\nOffset times violate period constraints")
    else:
        nr_cores = [t.coreid for t in taskSet]
        for core_id in range(min(nr_cores), max(nr_cores) + 1):
            core_tasks = [t for t in taskSet if t.coreid == core_id]
            hyper_period = find_lcm([t.period for t in core_tasks])
            utilization = sum(t.execution / t.period for t in core_tasks) * 100
            print(f"\nScheduling CPU ID {str(core_id)} started...")
            print("\t- Utilization = %s %%" % str(utilization))
            print("\t- Schedule hyper period = %s" % str(hyper_period))
            print("\t- Using optimization is", str(optimize))
            print("\t- Allocated WCET RTS =", str(wcet_offset))

            schedule, utilization, hyperPeriod, elapsedTime = gen_cyclic_schedule_model(core_tasks, wcet_offset,
                                                                                        optimize,
                                                                                        verbose)
            print("\n\t- Solver completed in %s ms" % (elapsedTime * SEC_TO_MS))
            if schedule is not None:
                gen_schedule_activations(schedule, core_tasks)

                print("\t- Activation Instances:")
                for i in range(len(core_tasks)):
                    print("\t\tschedtime_t %s_sched_insts[%s] = %s;" % (
                        core_tasks[i].name, len(core_tasks[i].getStartPIT()),
                        str(core_tasks[i].getStartPIT()).replace("[", "{").replace(
                            "]", "}")))

                print("\t- Estimated release jitter per task:")
                tasks_jitter = calc_jitter_pertask(core_tasks)
                for t in core_tasks:
                    print(f"\t\t{t.name}", end='')
                    if len(tasks_jitter[t.name]) > 1:
                        print(f"(std.dev = {round(stdev(tasks_jitter[t.name]), 2)}, "
                              f"max = {max(tasks_jitter[t.name])}, min = {min(tasks_jitter[t.name])}):", end='')
                    print("\n\t\t\t" + str(tasks_jitter[t.name]))
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

        if code:
            gen_schedule_code(tasksFileName.replace(".csv", "_schedule.h"), tasksFileName, taskSet,
                              hyperPeriod,
                              utilization, True)
            sys.exit()
