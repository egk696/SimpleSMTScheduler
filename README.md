# SimpleSMTScheduler
A simple SMT-based schedule generator for cyclic executives real-time tasks

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

Enter the number of hyper periods to be plotted: 2

Enable statistics (Yes/No)? No


--Task_ACT ()
	T=20000.0 μs
	D=20000.0 μs
	C=2304.0 μs
--Task_RCV ()
	T=5000.0 μs
	D=5000.0 μs
	C=300.0 μs
--Task_SND ()
	T=10000.0 μs
	D=10000.0 μs
	C=238.0 μs
--Task_MON ()
	T=100000.0 μs
	D=100000.0 μs
	C=204.0 μs
--Task_SYN ()
	T=5000.0 μs
	D=5000.0 μs
	C=475.0 μs

Utilization = 0.29603999999999997

Schedule hyper period = 100000

Satisfied by the following activation times in μs:
[SYN _pit = 3050,
 ACT _pit = 0,
 RCV _pit = 2305,
 MON _pit = 2845,
 SND _pit = 2606]

Schedule printout for 2 periods
ACT [0,20000,40000,60000,80000,100000,120000,140000,160000,180000,]

RCV [2305,7305,12305,17305,22305,27305,32305,37305,42305,47305,52305,57305,62305,67305,72305,77305,82305,87305,92305,97305,102305,107305,112305,117305,122305,127305,132305,137305,142305,147305,152305,157305,162305,167305,172305,177305,182305,187305,192305,197305,]

SND [2606,12606,22606,32606,42606,52606,62606,72606,82606,92606,102606,112606,122606,132606,142606,152606,162606,172606,182606,192606,]

MON [2845,102845,]

SYN [3050,8050,13050,18050,23050,28050,33050,38050,43050,48050,53050,58050,63050,68050,73050,78050,83050,88050,93050,98050,103050,108050,113050,118050,123050,128050,133050,138050,143050,148050,153050,158050,163050,168050,173050,178050,183050,188050,193050,198050,]
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
  
`-o (--osched)` accepts as input the path for the generated schedule plot

`-n (--nperiods)` controls the plotted number of hyper periods

`-p (--plot)` enables plotting

`-v (--verbose)` enables display of generated constraints and statistics

A minimal example is shown below:

<pre><font color="#729FCF"><b>~/SimpleSMTScheduler</b></font>$ python3 SimpleSMTScheduler.py -i examples/simple_tasks.csv

Welcome to this simple SMT scheduler (SSMTS)...
--Task_ACT ()
	T=20000.0 μs
	D=20000.0 μs
	C=2304.0 μs
--Task_RCV ()
	T=5000.0 μs
	D=5000.0 μs
	C=200.0 μs
--Task_SND ()
	T=10000.0 μs
	D=10000.0 μs
	C=138.0 μs
--Task_MON ()
	T=100000.0 μs
	D=100000.0 μs
	C=4.0 μs
--Task_SYN ()
	T=5000.0 μs
	D=5000.0 μs
	C=375.0 μs
	S=0.0 μs

Schedule hyper period = 100000

Satisfied by the following activation times in μs:
[ACT _pit = 376,
 RCV _pit = 2681,
 MON _pit = 90376,
 SND _pit = 2882,
 SYN _pit = 0]</pre>
