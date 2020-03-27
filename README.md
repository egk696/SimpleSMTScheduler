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
Enter the jitter allocation to be accounted for: 50
Enter the number of hyper periods to be plotted: 2
Enable statistics (Yes/No)? No


--Task_T1()
        T=20000.0 μs
        D=20000.0 μs
        C=1500.0 μs
--Task_T2()
        T=5000.0 μs
        D=5000.0 μs
        C=750.0 μs
--Task_T3()
        T=10000.0 μs
        D=10000.0 μs
        C=500.0 μs
--Task_T4()
        T=100000.0 μs
        D=100000.0 μs
        C=1500.0 μs
--Task_T5()
        T=2500.0 μs
        D=2500.0 μs
        C=500.0 μs

Utilization = 0.49

Schedule hyper period = 100000

Satisfied by the following activation times:
[T4_pit = 0,
 T5_pit = 1551,
 T2_pit = 2102,
 T1_pit = 4602,
 T3_pit = 7903]

Schedule printout for 2 periods
T4[0,100000,]

T5[1551,4051,6551,9051,11551,14051,16551,19051,21551,24051,26551,29051,31551,34051,36551,39051,41551,44051,46551,49051,51551,54051,56551,59051,61551,64051,66551,69051,71551,74051,76551,79051,81551,84051,86551,89051,91551,94051,96551,99051,101551,104051,106551,109051,111551,114051,116551,119051,121551,124051,126551,129051,131551,134051,136551,139051,141551,144051,146551,149051,151551,154051,156551,159051,161551,164051,166551,169051,171551,174051,176551,179051,181551,184051,186551,189051,191551,194051,196551,199051,]

T2[2102,7102,12102,17102,22102,27102,32102,37102,42102,47102,52102,57102,62102,67102,72102,77102,82102,87102,92102,97102,102102,107102,112102,117102,122102,127102,132102,137102,142102,147102,152102,157102,162102,167102,172102,177102,182102,187102,192102,197102,]

T1[4602,24602,44602,64602,84602,104602,124602,144602,164602,184602,]

T3[7903,17903,27903,37903,47903,57903,67903,77903,87903,97903,107903,117903,127903,137903,147903,157903,167903,177903,187903,197903,]
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

A minimal example is shown below:

<pre><font color="#729FCF"><b>~/SimpleSMTScheduler</b></font>$ python3 SimpleSMTScheduler.py -i examples/simple_tasks.csv -j 50

Welcome to this simple SMT scheduler (SSMTS)...
--Task_T1()
        T=20000.0 μs
        D=20000.0 μs
        C=1500.0 μs
--Task_T2()
        T=5000.0 μs
        D=5000.0 μs
        C=750.0 μs
--Task_T3()
        T=10000.0 μs
        D=10000.0 μs
        C=500.0 μs
--Task_T4()
        T=100000.0 μs
        D=100000.0 μs
        C=1500.0 μs
--Task_T5()
        T=2500.0 μs
        D=2500.0 μs
        C=500.0 μs

Utilization = 0.49

Schedule hyper period = 100000

Satisfied by the following activation times:
[T4_pit = 0,
 T5_pit = 1551,
 T2_pit = 2102,
 T1_pit = 4602,
 T3_pit = 7903]
</pre>
