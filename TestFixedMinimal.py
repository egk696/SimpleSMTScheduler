#!/usr/bin/python

from simplesmtscheduler.schedulers import gen_cyclic_schedule_model, gen_schedule_activations, plot_cyclic_schedule
from simplesmtscheduler.utilities import parse_csv_taskset

tasksFileName = "examples/demo_tasks.csv"
taskSet = []
wcet_offset = 0
verbose = False
schedulePlotPeriods = 1

parse_csv_taskset(tasksFileName, taskSet)
schedule, utilization, hyperPeriod, elapsedTime = gen_cyclic_schedule_model(taskSet, wcet_offset, verbose)
if schedule is not None:
    gen_schedule_activations(schedule, taskSet)
schedulePlot = plot_cyclic_schedule(taskSet, hyperPeriod, schedulePlotPeriods)
schedulePlot.show()