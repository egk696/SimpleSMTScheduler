from math import ceil


class PeriodicTask:

    def __init__(self, period: float, execution: float, deadline: float, offset: float,
                 jitter: float, coreid: int = 0, fixed_pit: int = None, name: str = "a_task",
                 cfunc: str = "void"):

        self.name = name
        self.period = ceil(period)
        self.deadline = ceil(deadline)
        self.execution = ceil(execution)
        self.offset = ceil(offset)
        self.jitter = ceil(jitter)
        self.coreid = coreid
        self.mapped_coreid = None
        self.release_instances = []  # constraint
        self.releas_itr = None
        self.cfunc = cfunc
        self.active_itr = None
        self.activation_instances = []  # result

        if fixed_pit is not None:
            self.fixed_pit = fixed_pit

        print(name + " {")
        print("  T=%s," % period)
        print("  C=%s," % execution)
        print("  D=%s," % deadline)
        print("  O=%s," % offset)
        print("  J=%s," % jitter)
        print("  CPU=%s," % coreid)
        if fixed_pit is not None:
            print("  S=%s μs" % fixed_pit)
        print("};")

    def addStartPIT(self, pit: float):
        self.activation_instances.append(pit)

    def setActivationInstancePIT(self, i: int, activation_pit: float):
        self.activation_instances[i] = activation_pit

    def getStartPIT(self):
        return self.activation_instances

    def toActualDict(self):
        return {k: v for k, v in self.__dict__ if not k.contains('release_instances')}
