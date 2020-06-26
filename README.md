# SimpleSMTScheduler
A simple SMT-based schedule generator for cyclic executives real-time tasks

To quickly use the application online please visit us at: [Simple Cyclic Scheduler Online](https://simplescheduleronline.herokuapp.com/)  

# Usage
The application can run in two modes, either interactive or via command-line. 
When the application is started with no arguments it implicitly enters interactive mode.
Tasks are defined in a CSV file as shown in the [examples/simple_tasks.csv](https://github.com/egk696/SimpleSMTScheduler/blob/master/examples/simple_tasks.csv)

## Interactive Mode
In the interactive mode the application generates a schedule based on the provided task definitions and displays
a plot of the first N hyperperiods.

Start the application by running:
```python
python3 SimpleSMTScheduler.py
```
Proceed to enter the path to the desired CSV file as requested in the command prompt and hit enter.
Enter the desired number of hyperperiods to be plotted and hit enter. 
After the schedule is generated the applications will report in the command prompt the calculated activations times
as shown in the example below:

<pre><font color="#729FCF"><b>~/SimpleSMTScheduler</b></font>$ python3 SimpleSMTScheduler.py 
Welcome to this simple SMT scheduler (SSMTS)...

Enter the csv file for the tasks to be scheduled: examples/simple_tasks.csv
Enter the WCET allocation gap between activations: 50
Enter the number of hyper periods to be plotted: 2
Enable statistics (Yes/No)? No
Importing task set from file source...

Task_T1 {
  T=20000.0,
  C=1500.0,
  D=20000.0,
  O=0.0,
  J=0.0,
};
Task_T2 {
  T=5000.0,
  C=750.0,
  D=5000.0,
  O=0.0,
  J=0.0,
};
Task_T3 {
  T=10000.0,
  C=500.0,
  D=10000.0,
  O=0.0,
  J=0.0,
};
Task_T4 {
  T=100000.0,
  C=1500.0,
  D=100000.0,
  O=0.0,
  J=0.0,
};
Task_T5 {
  T=2500.0,
  C=500.0,
  D=2500.0,
  O=0.0,
  J=0.0,
};
Task_T6 {
  T=1000.0,
  C=10.0,
  D=1000.0,
  O=0.0,
  J=2000.0,
};

Utilization = 50.0 %
Schedule hyper period = 100000

Solver completed in 1475.8541584014893 ms

Schedule plotted for 2 hyper-periods

Name    Activation Instances    
T5      [0, 2500, 5000, 7500, 10000, 12500, 15000, 17500, 20000, 22500, 25000, 27500, 30000, 32500, 35000, 37500, 40000, 42500, 45000, 47500, 50000, 52500, 55000, 57500, 60000, 62500, 65000, 67500, 70000, 72500, 75000, 77500, 80000, 82500, 85000, 87500, 90000, 92500, 95000, 97500]
T4      [890]
T6      [2440, 3600, 3600, 5550, 5550, 7440, 8600, 9460, 10990, 11990, 12440, 13600, 14460, 15550, 15550, 15550, 18550, 19460, 20990, 21990, 22440, 23600, 24460, 25550, 25550, 27440, 28600, 29460, 30990, 31930, 32440, 33600, 34460, 35550, 35550, 35550, 38550, 39460, 40990, 41990, 42440, 43600, 44460, 45550, 45550, 47440, 48550, 49460, 50990, 51990, 52440, 53600, 54460, 55550, 55550, 55550, 58550, 59460, 60990, 61990, 62440, 63600, 64460, 65550, 65550, 65550, 68550, 69460, 70990, 71990, 72440, 73600, 74460, 75550, 75550, 75550, 78550, 79460, 80990, 81990, 82440, 83600, 84460, 85550, 85550, 85550, 88050, 89460, 90990, 91990, 92440, 93600, 94460, 95550, 95550, 95600, 98600, 99460, 99460, 99460]
T3      [3050, 13050, 23050, 33050, 43050, 53050, 63050, 73050, 83050, 93050]
T2      [3660, 8660, 13660, 18660, 23660, 28660, 33660, 38660, 43660, 48660, 53660, 58660, 63660, 68660, 73660, 78660, 83660, 88660, 93660, 98660]
T1      [5890, 25890, 45890, 65890, 85890]
</pre>

A window should open displaying the plotted schedule for the first N hyperperiods as shown in the example Figure below:
 
![Example Tasks Schedule](https://github.com/egk696/SimpleSMTScheduler/blob/master/examples/simple_tasks_schedule.png)

## Command-line Mode
In the command-line mode the application executes according to the provided arguments. To see the available commands
run:
```
python3 SimpleSMTScheduler.py -h
```
The available arguments are the following:

`-h (--help)` displays the available arguments

`-i (--itasks)` accepts as input the path to the tasks CSV file

`-j (--jitter)` accepts as input the jitter gap to be allocated between tasks
  
`-o (--osched)` accepts as input the path for the generated schedule plot

`-n (--nperiods)` controls the plotted number of hyper periods

`-p (--plot)` enables plotting

`-v (--verbose)` enables display of generated constraints and statistics

A typical example of six tasks with WCET inter-task allocation gap 50 is shown below:

<pre><font color="#729FCF"><b>~/SimpleSMTScheduler</b></font>$ python3 SimpleSMTScheduler.py -i examples/simple_tasks.csv -w 50

Welcome to this simple SMT scheduler (SSMTS)...
Importing task set from file source...

Task_T1 {
  T=20000.0,
  C=1500.0,
  D=20000.0,
  O=0.0,
  J=0.0,
};
Task_T2 {
  T=5000.0,
  C=750.0,
  D=5000.0,
  O=0.0,
  J=0.0,
};
Task_T3 {
  T=10000.0,
  C=500.0,
  D=10000.0,
  O=0.0,
  J=0.0,
};
Task_T4 {
  T=100000.0,
  C=1500.0,
  D=100000.0,
  O=0.0,
  J=0.0,
};
Task_T5 {
  T=2500.0,
  C=500.0,
  D=2500.0,
  O=0.0,
  J=0.0,
};
Task_T6 {
  T=1000.0,
  C=10.0,
  D=1000.0,
  O=0.0,
  J=2000.0,
};

Utilization = 50.0 %
Schedule hyper period = 100000

Solver completed in 1477.623462677002 ms

Name    Activation Instances    
T5      [0, 2500, 5000, 7500, 10000, 12500, 15000, 17500, 20000, 22500, 25000, 27500, 30000, 32500, 35000, 37500, 40000, 42500, 45000, 47500, 50000, 52500, 55000, 57500, 60000, 62500, 65000, 67500, 70000, 72500, 75000, 77500, 80000, 82500, 85000, 87500, 90000, 92500, 95000, 97500]
T4      [890]
T6      [2440, 3600, 3600, 5550, 5550, 7440, 8600, 9460, 10990, 11990, 12440, 13600, 14460, 15550, 15550, 15550, 18550, 19460, 20990, 21990, 22440, 23600, 24460, 25550, 25550, 27440, 28600, 29460, 30990, 31930, 32440, 33600, 34460, 35550, 35550, 35550, 38550, 39460, 40990, 41990, 42440, 43600, 44460, 45550, 45550, 47440, 48550, 49460, 50990, 51990, 52440, 53600, 54460, 55550, 55550, 55550, 58550, 59460, 60990, 61990, 62440, 63600, 64460, 65550, 65550, 65550, 68550, 69460, 70990, 71990, 72440, 73600, 74460, 75550, 75550, 75550, 78550, 79460, 80990, 81990, 82440, 83600, 84460, 85550, 85550, 85550, 88050, 89460, 90990, 91990, 92440, 93600, 94460, 95550, 95550, 95600, 98600, 99460, 99460, 99460]
T3      [3050, 13050, 23050, 33050, 43050, 53050, 63050, 73050, 83050, 93050]
T2      [3660, 8660, 13660, 18660, 23660, 28660, 33660, 38660, 43660, 48660, 53660, 58660, 63660, 68660, 73660, 78660, 83660, 88660, 93660, 98660]
T1      [5890, 25890, 45890, 65890, 85890]
</pre>
