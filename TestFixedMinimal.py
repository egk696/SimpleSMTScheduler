#!/usr/bin/python
import csv
import io
from statistics import stdev

from simplesmtscheduler.schedulers import gen_cyclic_schedule_model, gen_schedule_activations, plot_cyclic_schedule
from simplesmtscheduler.utilities import parse_csv_taskset, calc_jitter_pertask

tasksFileName = "examples/demo_tasks.csv"
taskSet = []
wcet_offset = 0
verbose = False
optimize = True
schedulePlotPeriods = 1

tasks_data = "Period,Execution,Deadline,Offset,Jitter,CPU ID,Fixed Start,Name,Function\n" \
             "5 ,2 ,5 ,0 ,2 ,0 ,None ,T1 ,&task_1\n" \
             "7 ,4 ,7 ,0 ,2 ,0 ,None ,T2 ,&task_2"

# tasks_data = "Period,Execution,Deadline,Offset,Jitter,CPU ID,Fixed Start,Name,Function\n" \
#              "100 ,20 ,100 ,0 ,0 ,0 ,None ,T1 ,&task_1"

file = io.StringIO(tasks_data)
csv.writer(file)

parse_csv_taskset(file, taskSet)
schedule, utilization, hyperPeriod, elapsedTime = gen_cyclic_schedule_model(taskSet, wcet_offset, optimize, verbose)
print("Utilization = " + str(utilization))
print("Hyperperiod = " + str(hyperPeriod))

if schedule is not None:
    gen_schedule_activations(schedule, taskSet)
    print("\nEstimated release jitter per task:")
    tasks_jitter = calc_jitter_pertask(taskSet)
    for t in taskSet:
        print(
            f"\t{t.name} (std.dev = {round(stdev(tasks_jitter[t.name]), 2)}, "
            f"min = {max(tasks_jitter[t.name])}, max={min(tasks_jitter[t.name])}):")
        print("\t\t" + str(tasks_jitter[t.name]))

schedulePlot = plot_cyclic_schedule('Fixed Demo', taskSet, hyperPeriod, schedulePlotPeriods)
schedulePlot.show()
