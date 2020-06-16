from math import *

import matplotlib.pyplot as plt
from z3 import *

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


def gen_schedule_code(file_name, tasks_file_name, task_set, hyper_period, utilization):
    f = open(file_name, "w+")
    f.write("#pragma once\r\n\r\n")
    f.write("/*\r\n")
    f.write(
        " * This file was generated using SimpleSMTScheduler (https://github.com/egk696/SimpleSMTScheduler)\r\n")
    f.write(" * Generated schedule based on task set defined in %s\r\n" % tasks_file_name)
    f.write(" * Scheduled Task Set Utilization = %s %%\r\n" % utilization)
    f.write(" */\r\n\r\n")
    f.write("#define NUM_OF_TASKS %s\r\n" % len(task_set))
    f.write("#define HYPER_PERIOD %s\r\n\r\n" % hyper_period)
    for i in range(len(task_set)):
        f.write("#define %s_PERIOD %s\r\n" % (task_set[i].name, task_set[i].period))
    f.write("\r\n")
    f.write("schedtime_t tasks_periods[NUM_OF_TASKS] = {")
    for i in range(len(task_set)):
        if (i < len(task_set) - 1):
            f.write("%s_PERIOD, " % task_set[i].name)
        else:
            f.write("%s_PERIOD" % task_set[i].name)
    f.write("};\r\n")
    f.write("\r\n")
    for i in range(len(task_set)):
        f.write("#define %s_INSTS_NUM %s\r\n" % (task_set[i].name, len(task_set[i].getStartPIT())))
    f.write("\r\n")
    f.write("unsigned tasks_insts_counts[NUM_OF_TASKS] = {")
    for i in range(len(task_set)):
        if (i < len(task_set) - 1):
            f.write("%s_INSTS_NUM, " % task_set[i].name)
        else:
            f.write("%s_INSTS_NUM" % task_set[i].name)
    f.write("};\r\n")
    f.write("\r\n")
    for i in range(len(task_set)):
        f.write("schedtime_t %s_sched_insts[%s_INSTS_NUM] = %s;\r\n" % (task_set[i].name, task_set[i].name,
                                                                        str(task_set[
                                                                                i].getStartPIT()).replace(
                                                                            "[", "{").replace("]", "}")))
    f.write("\r\n")
    f.write("schedtime_t *tasks_schedules[NUM_OF_TASKS] = {")
    for i in range(len(task_set)):
        if (i < len(task_set) - 1):
            f.write("%s_sched_insts, " % task_set[i].name)
        else:
            f.write("%s_sched_insts" % task_set[i].name)
    f.write("};\r\n")
