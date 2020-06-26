import csv
import shutil
from math import *

import matplotlib.pyplot as plt
from z3 import *
from io import StringIO
from project.server.scheduling.simplesmtscheduler.taskdefs import PeriodicTask

MY_DPI = 480
SEC_TO_MS = 1000
US_TO_MS = 0.001
NS_TO_US = 1 / 1000


def find_lcm(numbers):
    lcm = numbers[0]
    for ii in numbers[1:]:
        lcm = int(lcm * ii / gcd(lcm, ii))
    return lcm


def z3_abs(x):
    return If(x >= 0, x, -x)


def parse_csv_taskset(csv_file, task_set):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        is_first_row = True
        row_index = 0
        for row in reader:
            if is_first_row:
                is_first_row = False
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
                    name = "Task %s" % row_index
                try:
                    func = str(row[8])
                except ValueError:
                    func = "void"

                task_set.append(PeriodicTask(period, execution, deadline, offset, jitter, coreid, name, fixed, func))
                row_index = row_index + 1


def plot_cyclic_schedule(task_set, hyper_period, iterations):
    # Declaring a figure "gnt"
    fig, axis = plt.subplots()

    # Setting Y-axis limits
    axis.set_ylim(0, len(task_set) * 10)

    # Setting X-axis limits
    axis.set_xlim(0, hyper_period * iterations)

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


def gen_schedule_code(file_name, tasks_file_name, task_set, hyper_period, utilization, isCli = False):
    wr_buf = StringIO()

    wr_buf.write("#pragma once\r\n\r\n")
    wr_buf.write("/*\r\n")
    wr_buf.write(
        " * This file was generated using SimpleSMTScheduler (https://github.com/egk696/SimpleSMTScheduler)\r\n")
    wr_buf.write(" * Generated schedule based on task set defined in %s\r\n" % tasks_file_name)
    wr_buf.write(" * Scheduled Task Set Utilization = %s %%\r\n" % utilization)
    wr_buf.write(" */\r\n\r\n")
    wr_buf.write("#define NUM_OF_TASKS %s\r\n" % len(task_set))
    wr_buf.write("#define HYPER_PERIOD %s\r\n\r\n" % hyper_period)
    for i in range(len(task_set)):
        wr_buf.write("#define %s_PERIOD %s\r\n" % (task_set[i].name, task_set[i].period))
    wr_buf.write("\r\n")
    wr_buf.write("schedtime_t tasks_periods[NUM_OF_TASKS] = {")
    for i in range(len(task_set)):
        if (i < len(task_set) - 1):
            wr_buf.write("%s_PERIOD, " % task_set[i].name)
        else:
            wr_buf.write("%s_PERIOD" % task_set[i].name)
    wr_buf.write("};\r\n")
    wr_buf.write("\r\n")
    for i in range(len(task_set)):
        wr_buf.write("#define %s_INSTS_NUM %s\r\n" % (task_set[i].name, len(task_set[i].getStartPIT())))
    wr_buf.write("\r\n")
    wr_buf.write("unsigned tasks_insts_counts[NUM_OF_TASKS] = {")
    for i in range(len(task_set)):
        if (i < len(task_set) - 1):
            wr_buf.write("%s_INSTS_NUM, " % task_set[i].name)
        else:
            wr_buf.write("%s_INSTS_NUM" % task_set[i].name)
    wr_buf.write("};\r\n")
    wr_buf.write("\r\n")
    for i in range(len(task_set)):
        wr_buf.write("schedtime_t %s_sched_insts[%s_INSTS_NUM] = %s;\r\n" % (task_set[i].name, task_set[i].name,
                                                                        str(task_set[
                                                                                i].getStartPIT()).replace(
                                                                            "[", "{").replace("]", "}")))
    wr_buf.write("\r\n")
    wr_buf.write("schedtime_t *tasks_schedules[NUM_OF_TASKS] = {")
    for i in range(len(task_set)):
        if (i < len(task_set) - 1):
            wr_buf.write("%s_sched_insts, " % task_set[i].name)
        else:
            wr_buf.write("%s_sched_insts" % task_set[i].name)
    wr_buf.write("};\r\n")

    if isCli:
        with open(file_name, 'w') as fd:
            wr_buf.seek(0)
            shutil.copyfileobj(wr_buf, fd)
        return 1
    else:
        return wr_buf

