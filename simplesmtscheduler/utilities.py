import csv
import ast
import shutil
from io import StringIO
from math import *

import matplotlib.pyplot as plt
from z3 import *

from simplesmtscheduler.taskdefs import *

# set_param('parallel.enable', True)

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
    if isinstance(csv_file, StringIO):
        f = csv_file
    else:
        f = open(csv_file, 'r')
    reader = csv.reader(f)
    is_first_row = True
    row_index = 0
    for row in reader:
        if is_first_row:
            is_first_row = False
        elif not str(row[0]).startswith("#"):
            try:
                period = eval(compile(ast.parse(row[0], mode='eval'), '<string>', 'eval'))
            except ValueError:
                period = 0
            try:
                execution = eval(compile(ast.parse(row[1], mode='eval'), '<string>', 'eval'))
            except ValueError:
                execution = 0
            try:
                deadline = eval(compile(ast.parse(row[2], mode='eval'), '<string>', 'eval'))
            except ValueError:
                deadline = 0
            try:
                offset = eval(compile(ast.parse(row[3], mode='eval'), '<string>', 'eval'))
            except ValueError:
                offset = 0
            try:
                jitter = eval(compile(ast.parse(row[4], mode='eval'), '<string>', 'eval'))
            except ValueError:
                jitter = 0
            try:
                coreid = int(row[5])
            except ValueError:
                coreid = None
            try:
                fixed_pit = eval(compile(ast.parse(row[6], mode='eval'), '<string>', 'eval'))
            except ValueError:
                fixed_pit = None
            try:
                name = str(row[7]).strip()
            except ValueError:
                name = "Task %s" % row_index
            try:
                func = str(row[8])
            except ValueError:
                func = "void"

            task_set.append(PeriodicTask(period, execution, deadline, offset, jitter, coreid, fixed_pit, name, func))
            row_index = row_index + 1
    f.close()


def plot_cyclic_schedule(task_set, hyper_period, iterations=1, name=None):
    # Declaring a figure "gnt"
    fig, axis = plt.subplots()
    plt.subplots_adjust(left=0.05, bottom=0.10, right=0.97, top=0.96)

    # Sort
    try:
        srt_task_set = sorted(task_set, key=lambda x: (x.coreid, x.getStartPIT()[0]), reverse=True)
    except:
        srt_task_set = task_set

    if name is not None:
        plt.title(name + " (Hyper-period = " + str(hyper_period) + ")")

    # Setting Y-axis limits
    axis.set_ylim(0, len(srt_task_set) * 10)
    # Setting X-axis limits
    axis.set_xlim(0, hyper_period * iterations)
    # Setting labels for x-axis and y-axis
    axis.set_xlabel('Schedule Timeline')
    axis.set_ylabel('Tasks')
    # axis.set_xticks(range(0, periods*Sum([t.getStartPIT()+t.execution for t in taskSet]), 5000))
    axis.set_xticks(range(0, hyper_period * iterations, int(hyper_period * iterations / 10)))
    # Setting ticks on y-axis
    axis.set_yticks(range(5, len(srt_task_set) * 10 + 5, 10))
    # Labelling tickes of y-axis
    axis.set_yticklabels([(t.coreid, t.name) for t in srt_task_set])
    # Show the major grid lines with dark grey lines
    plt.grid(visible=True, which='major', color='#666666', linestyle='-')
    # Show the minor grid lines with very faint and almost transparent grey lines
    plt.minorticks_on()
    plt.grid(visible=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    # Color map
    cmap = plt.cm.get_cmap('viridis', len(srt_task_set))
    print("\nSchedule plotted for %s hyper-periods\n" % iterations)
    for i in range(len(srt_task_set)):
        taskExecutionBars = []
        for hyper_iter in range(0, iterations):
            for jj in range(len(srt_task_set[i].getStartPIT())):
                start = hyper_iter * hyper_period + srt_task_set[i].getStartPIT()[jj]
                end = srt_task_set[i].execution
                taskExecutionBars.append((start, end))
        task_label = f"CPU#{srt_task_set[i].coreid}_{srt_task_set[i].name}"
        axis.broken_barh(taskExecutionBars, (i * 10, 10), label=task_label, facecolors=cmap(i), edgecolor='k',
                         linestyle='dotted', linewidth=0.2)

    # Rotate labels to fit nicely
    fig.autofmt_xdate()
    fig.tight_layout()
    return plt


def gen_schedule_code(file_name, tasks_file_name, task_set, hyper_period, utilization, isCli=False):
    wr_buf = StringIO()

    time_ctype = "unsigned long long"

    srt_task_set = sorted(task_set, key=lambda x: (x.period), reverse=False)
    # srt_task_set = task_set.copy()

    wr_buf.write("#pragma once\n\n")
    wr_buf.write("/*\n")
    wr_buf.write(
        " * This file was generated using SimpleSMTScheduler (https://github.com/egk696/SimpleSMTScheduler)\n")
    wr_buf.write(" * Generated schedule based on task set defined in %s\n" % tasks_file_name)
    wr_buf.write(" * Scheduled Task Set Utilization = %s %%\n" % utilization)
    wr_buf.write(" */\n\n")
    wr_buf.write("#define NUM_OF_TASKS %s\n" % len(srt_task_set))
    wr_buf.write("#define HYPER_PERIOD %s\n\n" % hyper_period)
    wr_buf.write("#define MAPPED_CORE_COUNT %s\n\n" % max([t.coreid + 1 for t in srt_task_set]))

    for i in range(len(srt_task_set)):
        wr_buf.write("#define %s_ID %s\n" % (srt_task_set[i].name, str(i)))
        wr_buf.write("#define %s_PERIOD %s\n" % (srt_task_set[i].name, srt_task_set[i].period))
    wr_buf.write("\n")

    wr_buf.write("char* tasks_names[NUM_OF_TASKS] = {")
    for i in range(len(srt_task_set)):
        if (i < len(srt_task_set) - 1):
            wr_buf.write("\"%s\", " % srt_task_set[i].name)
        else:
            wr_buf.write("\"%s\"" % srt_task_set[i].name)
    wr_buf.write("};\n")
    wr_buf.write("\n")

    wr_buf.write("unsigned tasks_per_cores[MAPPED_CORE_COUNT] = {")
    for i in range(max([t.coreid + 1 for t in srt_task_set])):
        if i < max([t.coreid + 1 for t in srt_task_set]) - 1:
            wr_buf.write("%s, " % len([t for t in srt_task_set if t.coreid == i]))
        else:
            wr_buf.write("%s" % len([t for t in srt_task_set if t.coreid == i]))
    wr_buf.write("};\n")
    wr_buf.write("\n")

    wr_buf.write("unsigned cores_hyperperiods[MAPPED_CORE_COUNT] = {")
    for i in range(max([t.coreid + 1 for t in srt_task_set])):
        if i < max([t.coreid + 1 for t in srt_task_set]) - 1:
            wr_buf.write("%s, " % find_lcm([t.period for t in srt_task_set if t.coreid == i]))
        else:
            wr_buf.write("%s" % find_lcm([t.period for t in srt_task_set if t.coreid == i]))
    wr_buf.write("};\n")
    wr_buf.write("\n")

    wr_buf.write("unsigned tasks_coreids[NUM_OF_TASKS] = {")
    for i in range(len(srt_task_set)):
        if (i < len(srt_task_set) - 1):
            wr_buf.write("%s, " % srt_task_set[i].coreid)
        else:
            wr_buf.write("%s" % srt_task_set[i].coreid)
    wr_buf.write("};\n")
    wr_buf.write("\n")

    wr_buf.write("unsigned long long tasks_periods[NUM_OF_TASKS] = {")
    for i in range(len(srt_task_set)):
        if (i < len(srt_task_set) - 1):
            wr_buf.write("%s_PERIOD, " % srt_task_set[i].name)
        else:
            wr_buf.write("%s_PERIOD" % srt_task_set[i].name)
    wr_buf.write("};\n")
    wr_buf.write("\n")
    for i in range(len(srt_task_set)):
        wr_buf.write("#define %s_INSTS_NUM %s\n" % (srt_task_set[i].name, len(srt_task_set[i].getStartPIT())))
    wr_buf.write("\n")

    wr_buf.write("unsigned tasks_insts_counts[NUM_OF_TASKS] = {")
    for i in range(len(srt_task_set)):
        if (i < len(srt_task_set) - 1):
            wr_buf.write("%s_INSTS_NUM, " % srt_task_set[i].name)
        else:
            wr_buf.write("%s_INSTS_NUM" % srt_task_set[i].name)
    wr_buf.write("};\n")
    wr_buf.write("\n")
    for i in range(len(srt_task_set)):
        wr_buf.write(
            "unsigned long long %s_sched_insts[%s] = %s;\n" % (srt_task_set[i].name, len(srt_task_set[i].getStartPIT()),
                                                               str(srt_task_set[
                                                                       i].getStartPIT()).replace(
                                                                   "[", "{").replace("]", "}")))
    wr_buf.write("\n")

    wr_buf.write("unsigned long long *tasks_schedules[NUM_OF_TASKS] = {")
    for i in range(len(srt_task_set)):
        if (i < len(srt_task_set) - 1):
            wr_buf.write("%s_sched_insts, " % srt_task_set[i].name)
        else:
            wr_buf.write("%s_sched_insts" % srt_task_set[i].name)
    wr_buf.write("};\n")

    if isCli:
        with open(file_name, 'w') as fd:
            wr_buf.seek(0)
            shutil.copyfileobj(wr_buf, fd)
        return 1
    else:
        return wr_buf


def calc_jitter_pertask(tasks):
    tasks_jitter = dict()
    for t in tasks:
        release_jitter = []
        prev_release_inst = None
        for nn in range(len(t.getStartPIT())):
            release_inst = t.getStartPIT()[nn]
            if prev_release_inst is not None:
                release_jitter.append(release_inst - prev_release_inst - t.period)
            prev_release_inst = release_inst
        tasks_jitter[t.name] = release_jitter
    return tasks_jitter
