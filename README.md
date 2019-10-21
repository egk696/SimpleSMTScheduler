# SimpleSMTScheduler
A simple SMT-based monotonic rate scheduler for real-time tasks

# Usage
The application can run in two modes, either interactive or via command-line.
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
 SYN _pit = 0]

Solver completed in 77.06785202026367 ms
</pre>

A window should open displaying the plotted schedule for the first N hyperperiods as shown in the example Figure below: 
![Example Tasks Schedule](https://github.com/egk696/SimpleSMTScheduler/blob/master/examples/simple_tasks_schedule.png)

