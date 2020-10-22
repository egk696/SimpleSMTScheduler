#!/usr/bin/python
from statistics import stdev

from simplesmtscheduler.schedulers import gen_cyclic_schedule_model, gen_schedule_activations, plot_cyclic_schedule, \
    gen_rate_monotonic_schedule
from simplesmtscheduler.utilities import parse_csv_taskset, calc_jitter_pertask

tasksFileName = "examples/task_set_rms.csv"
taskSet = []
wcet_offset = 0
verbose = False
optimize = False
schedulePlotPeriods = 1
rate_monotonic_mode = True
schedule = None

# tasks_data = "Period,Execution,Deadline,Offset,Jitter,CPU ID,Fixed Start,Name,Function\n" \
#              "5 ,2 ,5 ,0 ,2 ,0 ,None ,T1 ,&task_1\n" \
#              "7 ,4 ,7 ,0 ,2 ,0 ,None ,T2 ,&task_2"

# tasks_data = "Period,Execution,Deadline,Offset,Jitter,CPU ID,Fixed Start,Name,Function\n" \
#              "100 ,20 ,100 ,0 ,0 ,0 ,None ,T1 ,&task_1"

# tasks_data = "Period,Execution,Deadline,Offset,Jitter,CPU ID,Fixed Start,Name,Function\n" \
# "10,2,10,0,1,1,None,t1,t1\n" \
# "20,2,20,0,2,1,None,t2,t2\n" \
# "100,2,100,0,10,1,None,t3,t3\n" \
# "15,2,15,0,1.5,1,None,t4,t4\n" \
# "14,2,14,0,1.4,1,None,t5,t5\n" \
# "50,2,50,0,5,1,None,t6,t6\n" \
# "40,2,40,0,4,1,None,t7,t7"

# file = io.StringIO(tasks_data)
# csv.writer(file)

parse_csv_taskset(tasksFileName, taskSet)
if rate_monotonic_mode:
    utilization, hyperPeriod, elapsedTime = gen_rate_monotonic_schedule(taskSet, wcet_offset, optimize, verbose)
else:
    schedule, utilization, hyperPeriod, elapsedTime = gen_cyclic_schedule_model(taskSet, wcet_offset, optimize, verbose)

print("Utilization = " + str(utilization))
print("Hyperperiod = " + str(hyperPeriod))

if schedule is not None or rate_monotonic_mode:
    gen_schedule_activations(schedule, taskSet)
    schedulePlot = plot_cyclic_schedule('Fixed Demo', taskSet, hyperPeriod, schedulePlotPeriods)
    schedulePlot.show()
    print("\nEstimated release jitter per task:")
    tasks_jitter = calc_jitter_pertask(taskSet)
    for t in taskSet:
        print(
            f"\t{t.name} (std.dev = {round(stdev(tasks_jitter[t.name]), 2)}, "
            f"min = {min(tasks_jitter[t.name])}, max={max(tasks_jitter[t.name])}):")
        print("\t\t" + str(tasks_jitter[t.name]))
