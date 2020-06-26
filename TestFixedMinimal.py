#!/usr/bin/python
import csv
import io

from simplesmtscheduler.schedulers import gen_cyclic_schedule_model, gen_schedule_activations, plot_cyclic_schedule
from simplesmtscheduler.utilities import parse_csv_taskset

tasksFileName = "examples/demo_tasks.csv"
taskSet = []
wcet_offset = 0
verbose = False
schedulePlotPeriods = 1

tasks_data = "Period,Execution,Deadline,Offset,Jitter,Fixed Start,CPU ID,Name,Function\n5 ,2 ,5 ,0 ,2 ,None ,0 ,T1 ,&task_1\n7 ,4 ,7 ,0 ,2 ,None ,0 ,T2 ,&task_2"
file = io.StringIO(tasks_data)
csv.writer(file)

parse_csv_taskset(file, taskSet)
schedule, utilization, hyperPeriod, elapsedTime = gen_cyclic_schedule_model(taskSet, wcet_offset, verbose)
if schedule is not None:
    gen_schedule_activations(schedule, taskSet)
schedulePlot = plot_cyclic_schedule(taskSet, hyperPeriod, schedulePlotPeriods)
schedulePlot.show()
