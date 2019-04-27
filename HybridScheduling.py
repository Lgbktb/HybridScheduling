#%% [markdown]
# # Hybrid Scheduling
# 

#%%
import datetime as dt


#%%
class task:

    def __init__(self, tID, arrivalTime, burstTime, tasksPriority, distance, areaID):
        # arrivalTime is a datetime.datetime object
        # burstTime is a datetime.timedelta object
        # All other variables are integers
        self.tID = tID
        self.arrivalTime = arrivalTime
        self.burstTime = burstTime
        self.tasksPriority = tasksPriority
        self.distance = distance
        self.areaID = areaID
        
    def __str__(self):
        return f'tID: {self.tID}; arrivalTime: ${self.arrivalTime}; burstTime: {self.burstTime}; tasksPriority: {self.tasksPriority} distance: {self.distance}; areaID: {self.areaID}'
    
    def setProcessor(self, processorID, startTime):
        # Processor ID is integer
        # startTime is a datetime.time object

        #startTime is datetime
        self.startTime = startTime
        #waitingTime is timedelta
        self.waitingTime = self.startTime - self.arrivalTime
        #turnaroundTime is timedelta
        self.turnaroundTime = self.waitingTime + self.burstTime
        #Completion Time is datetime (hopefully), this is the most suspect operation
        self.completionTime = self.arrivalTime + self.turnaroundTime
        #processorID
        self.processorID = processorID 
    
    def getProcessorInfo(self):
        return f'tID: {self.tID}; startTime: {self.startTime}; completionTime: {self.completionTime}; turnaroundTime: {self.turnaroundTime}; waitingTime: {self.waitingTime}; proc: {self.processorID}'


#%%
# mimics the default sorted functionality when used with a key
# sorted(list, key=lambda x:x.whatever)
def taskSort_helper(tasks, key):
    # Takes a list of tasks and a function key
    # Returns a Tuple of Lists of Tasks
    # Sorted into their lists based on comparison to function key
    
    less = []
    equal = []
    greater = []
    
    pivot = key(tasks[0])
    for x in tasks:
        if key(x) < pivot:
            less.append(x)
        elif key(x) == pivot:
            equal.append(x)
        elif key(x) > pivot:
            greater.append(x)
    # tuple[0] is all items less than the pivot, tuple[1] is equal (pivot/tasks[0] will always go here), tuple[2] is greater
    return (less, equal, greater)


#%%
def taskSort(tasks):
    # tasks must be a list of task objects
    # Returns list of tasks in specified sorted order 
    prioTuple = ([],[],[])
    distTuple = ([],[],[])
    burstTuple = ([],[],[])
    arrivalTuple = ([],[],[])
    trueEqual = []
    # Step 1: Sort by priority (high to low)
    if len(tasks) > 1:
        prioTuple = taskSort_helper(tasks, lambda x:x.tasksPriority)
        # Step 2: If same priority, sort by distance (low to high)
        if len(prioTuple[1]) > 1: # Length of equal priority items
            distTuple = taskSort_helper(prioTuple[1], lambda x:x.distance)
            # Step 3: if Same distance, sort by burst time (low to high)
            if len(distTuple[1]) > 1: # Length of equal Distance Items
                burstTuple = taskSort_helper(distTuple[1], lambda x:x.burstTime)
                # Step 4: If same burst time, sort by arrival time
                if len(burstTuple[1]) > 1: # Length of equal BurstTime items
                    arrivalTuple = taskSort_helper(burstTuple[1], lambda x:x.arrivalTime)
                    trueEqual = arrivalTuple[1]
                else:
                    trueEqual = burstTuple[1]
            else:
                trueEqual = distTuple[1]
        else:
            trueEqual = prioTuple[1]
        
        # return taskSort(greaterprio)+taskSort(lessdist)+equal+taskSort(greaterdist)+taskSort(lessprio)
        # For only Steps 1 and 2:
        # return taskSort(prioTuple[2])+taskSort(distTuple[0])+trueEqual+taskSort(distTuple[2])+taskSort(prioTuple[0])
        # For Steps 1,2,3
        # return taskSort(prioTuple[2])+taskSort(distTuple[0])+taskSort(burstTuple[0])+trueEqual+taskSort(burstTuple[2]+taskSort(distTuple[2])+taskSort(prioTuple[0])
        # For all steps
        return taskSort(prioTuple[2])+taskSort(distTuple[0])+taskSort(burstTuple[0])+taskSort(arrivalTuple[0])+trueEqual+taskSort(arrivalTuple[2])+taskSort(burstTuple[2])+taskSort(distTuple[2])+taskSort(prioTuple[0])

    # Note that you want equal ^^^^^ not pivot
    else:  # You need to hande the part at the end of the recursion - when you only have one element in your array, just return the array.
        return tasks


#%%
def soonestTime(processorTime):
    # Used once in code, so doeen't need to be a function, but is a useful abstraction
    # Returns key of dict processorTime that is the soonest time 
    soonest = 0
    for key in processorTime:
        if processorTime[key] < processorTime[soonest]:
            soonest = key
    return soonest


#%%
def hybridScheduleNoGroup(taskList, rescueStartTime, processorCount, processorResetTime=dt.timedelta(minutes=30)):
    # taskList is a list of task objects needed to be sorted
    # rescueStartTime is a datetime.time object meaning the time 
    # processorCount is an integer
    # ProcessorResetTime represents ProcessorPrepTime, but I don't entirely understand what it's purpose is.
    # My best guess and how I am impementing it is that each processor needs 30 minutes(defualt) to 'prep'
    # As that preptime is unrelated to the acutal processes completing, the task object doesnt have knowledge of it, and only the processorTime dict sees its effects
    
    # Sort Tasks in  based by Priority
    sortedTaskList = taskSort(taskList)
    
    # Assign each task to a processor
    # First Come First Serve (now that tasks are sorted)
    # ProcessorTime is a dictionary mapping each processor (labeled 0 to processorcount-1) to it's earliest free time
    processorTime = {}
    for i in range(processorCount):
        processorTime[i] = rescueStartTime        
    
    totalWaitingTime = dt.timedelta(0)
    totalTurnaroundTime = dt.timedelta(0)
    for task in sortedTaskList:
        # i represents the processor that will act the soonest
        i = soonestTime(processorTime)
        task.setProcessor(i, processorTime[i])
        processorTime[i] = task.completionTime+processorResetTime
        #print("task: "+str(task.tID) + "; proc: " + str(i))
        #print(processorTime)
    
        # Calculate totalWaitingTime
        totalWaitingTime += task.waitingTime 
        # Calculate totalTurnaroundTime
        totalTurnaroundTime += task.turnaroundTime
    print("totalWaitingTime: "+str(totalWaitingTime))
    # Calculate AverageWaitingTime
    averageWaitingTime = totalWaitingTime / len(sortedTaskList)
    print("averageWaitingTime: "+str(averageWaitingTime))
    print("totalTurnaroundTime: "+str(totalTurnaroundTime))
    # Calculate averageTurnaroundTime
    averageTurnaroundTime = totalTurnaroundTime / len(sortedTaskList)
    print("averageTurnaroundTime: "+str(averageTurnaroundTime))
    return sortedTaskList


#%%
def sample():
    # 'main' funciton for this file
    # Runs the sample code given in paper (with date of jan 1, 2000)
    # Define sample input
    rescueStartTime = dt.datetime(2000,1,1,10,40)
    numberOfProcessors = 3
    tasks =     [task(1, dt.datetime(2000,1,1,10,00), dt.timedelta(minutes=30), 7, 5, 1)]
    tasks.append(task(2, dt.datetime(2000,1,1,10,00), dt.timedelta(minutes=15), 7, 3, 2))
    tasks.append(task(3, dt.datetime(2000,1,1,10,00), dt.timedelta(minutes=40), 5, 7, 3))
    tasks.append(task(4, dt.datetime(2000,1,1,10,15), dt.timedelta(minutes=35), 8, 2, 4))
    tasks.append(task(5, dt.datetime(2000,1,1,10,30), dt.timedelta(minutes=10), 4, 3, 2))

    sortedTasks = hybridScheduleNoGroup(tasks, rescueStartTime, numberOfProcessors)
    for i in sortedTasks:
        print(i)
        print(i.getProcessorInfo())


#%%
sample()


