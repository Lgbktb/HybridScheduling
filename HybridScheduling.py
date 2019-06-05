#%% [markdown]
# # Hybrid Scheduling
# 
# 

#%%
import datetime as dt


#%%
class Task:
    
    
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
        #Completion Time is datetime
        self.completionTime = self.arrivalTime + self.turnaroundTime
        #processorID
        self.processorID = processorID 
    
    def getProcessorInfo(self):
        return f'tID: {self.tID}; startTime: {self.startTime}; completionTime: {self.completionTime}; turnaroundTime: {self.turnaroundTime}; waitingTime: {self.waitingTime}; proc: {self.processorID}'


#%%
class Area:
    def __init__(self, tasks, avgPriority, totalBurstTime):
        self.tasks = tasks
        self.avgPriority = avgPriority
        self.totalBurstTime = totalBurstTime
        self.id = tasks[0].areaID
    def __str__(self):
        return str(self.tasks)


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
def areaSort(areas):
    # areas must be a 2d list of area objects; where 1 area is a list of tasks
    # Returns list of tasks in specified sorted order 
    prioTuple = ([],[],[])
    distTuple = ([],[],[])
    tasksTuple = ([],[],[])
    burstTuple = ([],[],[])
    #arrivalTuple = ([],[],[])
    trueEqual = []
    # Step 4: Sort by priority (high to low)
    if len(areas) > 1:
        prioTuple = taskSort_helper(areas, lambda x:x.avgPriority)
        # Step 5: If same priority, sort by distance (low to high)
        if len(prioTuple[1]) > 1: # Length of equal priority items
            distTuple = taskSort_helper(prioTuple[1], lambda x:x.tasks[0].distance) # Assumes Equal distances, or at least that distances are closer to each other than to other tasks
            # Step 6: if Same distance, sort by number of tasks (high to low)
            if len(distTuple[1]) > 1: # Length of equal Distance Items
                tasksTuple = taskSort_helper(distTuple[1], lambda x:len(x.tasks))
                # Step 7: If same number of tasks, sort by total burst time (low to high)
                if len(distTuple[1]) > 1: # Length of equal BurstTime items
                    burstTuple = taskSort_helper(burstTuple[1], lambda x:x.arrivalTime)
                    trueEqual = burstTuple[1]
                else:
                    trueEqual = tasksTuple[1]
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
        return areaSort(prioTuple[2])+areaSort(distTuple[0])+areaSort(tasksTuple[2])+areaSort(burstTuple[0])+trueEqual+areaSort(burstTuple[2])+areaSort(tasksTuple[0])+areaSort(distTuple[2])+areaSort(prioTuple[0])

    # Note that you want equal ^^^^^ not pivot
    else:  # You need to hande the part at the end of the recursion - when you only have one element in your array, just return the array.
        return areas


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
def hybridScheduleNoGroup(taskList, rescueStartTime, processorCount):
    # taskList is a list of task objects needed to be sorted
    # rescueStartTime is a datetime.time object meaning the time 
    # processorCount is an integer
    # ProcessorResetTime represents ProcessorPrepTime, but I don't entirely understand what it's purpose is.
    # My best guess and how I am impementing it is that each processor needs 30 minutes(defualt) to 'prep'
    # As that preptime is unrelated to the acutal processes completing, the task object doesnt have knowledge of it, and only the processorTime dict sees its effects
    
    # Sort Tasks in  based by Priority
    sortedTaskList = taskSort(taskList)
    # Schedule processors
    sortedTaskList = schedule(sortedTaskList, rescueStartTime, processorCount )
    return sortedTaskList
    


#%%

def schedule(sortedTaskList, rescueStartTime, processorCount, processorResetTime=dt.timedelta(minutes=30), grouping=False):
    
    # Assign each task to a processor
    # First Come First Serve (now that tasks are sorted)
    # ProcessorTime is a dictionary mapping each processor (labeled 0 to processorcount-1) to it's earliest free time
    processorTime = {}
    for i in range(processorCount):
        processorTime[i] = rescueStartTime 
    
    totalWaitingTime = dt.timedelta(0)
    totalTurnaroundTime = dt.timedelta(0)
    prevTask = ''
    for task in sortedTaskList:
        # i represents the processor that will act the soonest
        i = soonestTime(processorTime)
        
        # Warning: Terrible code practice ahead
        if grouping and prevTask != '':
            if prevTask.areaID == task.areaID:
                # If there is grouping, and the previous task was in the same group, we don't need prep/reset time
                processorTime[i] -= processorResetTime 
                i = prevTask.areaID
                
        # Determines start time, either as soon as possible or as soon as task arrives
        #timeUsed = processorTime[i] if processorTime[i] > task.arrivalTime else task.arrivalTime
        task.setProcessor(i, processorTime[i])
        
        processorTime[i] = task.completionTime+processorResetTime
       
        print("task: "+str(task.tID) + "; proc: " + str(i))
        print(processorTime)
    
        # Calculate totalWaitingTime
        totalWaitingTime += task.waitingTime 
        # Calculate totalTurnaroundTime
        totalTurnaroundTime += task.turnaroundTime
        
        prevTask = task
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



#%%
def hybridPsudo(taskList, rescueStartTime, processorCount, processorResetTime=dt.timedelta(minutes=30)):
    # 1: Group base on Area ID.
    # 2: Calculate averaage priority of each area group (avgPriority = totalPriority/numberofTasks)
    # 3: combine the burstTime of each group.
    # 4-7: TaskSort(), now AreaSort
    # 8: After all sorting if there are groups iwth more than 5 tasks, schedule those also using hybridScheduleNoGroup()
    pass


#%%
def hybridSchedule(taskList, rescueStartTime, processorCount, processorResetTime=dt.timedelta(minutes=30)):
    # taskList is a list of task objects needed to be sorted
    # rescueStartTime is a datetime.time object meaning the time 
    # processorCount is an integer
    # ProcessorResetTime represents ProcessorPrepTime, but I don't entirely understand what it's purpose is.
    # My best guess and how I am impementing it is that each processor needs 30 minutes(defualt) to 'prep'
    # As that preptime is unrelated to the acutal processes completing, the task object doesnt have knowledge of it, and only the processorTime dict sees its effects
    
    # Group tasks into areas
    # areas is a dictionary where key is areaID of the area, and the value is the list of tasks
    areas = {}
    for i in taskList:
        if(i.areaID in areas):
            areas[i.areaID].append(i)
        else:
            areas[i.areaID] = [i]
    
    #SortedAreas is a list of areas, to be used with the areaSort() function
    sortedAreas = []
    for aID in areas:
        avgPrio = 0
        burstTime = dt.timedelta()
        for task in areas[aID]:
            avgPrio += task.tasksPriority
            burstTime += task.burstTime
        avgPrio = avgPrio / len(areas[aID])
        # if any area has >5 tasks, sort them using taskSort
        # Personally, I might not even want this clause, maybe just sort all of em,
        if(len(areas[aID])>5):
            print("Sorting tasks")
            sortedAreas.append(Area(taskSort(areas[aID]), avgPrio, burstTime))
        sortedAreas.append(Area(areas[aID], avgPrio, burstTime))

    # Sort Areas
    sortedAreas = areaSort(sortedAreas)
    
    sortedTaskList = []
    # Go from sorting based on areas to based on tasks
    for area in sortedAreas:
        for task in area.tasks:
            sortedTaskList.append(task)
            
    # Schedule processors 
    sortedTaskList = schedule(sortedTaskList, rescueStartTime, processorCount, grouping=True )
    
    return sortedTaskList


#%%
def foo():
    # 'main' funciton for this file
    # Runs the sample code given in paper (with date of jan 1, 2000)
    # Define sample input
    rescueStartTime = dt.datetime(2000,1,1,10,40)
    numberOfProcessors = 3
    tasks =     [Task(1, dt.datetime(2000,1,1,10,00), dt.timedelta(minutes=30), 7, 5, 1)]
    tasks.append(Task(2, dt.datetime(2000,1,1,10,00), dt.timedelta(minutes=15), 7, 3, 2))
    tasks.append(Task(3, dt.datetime(2000,1,1,10,00), dt.timedelta(minutes=40), 5, 7, 3))
    tasks.append(Task(4, dt.datetime(2000,1,1,10,15), dt.timedelta(minutes=35), 8, 2, 4))
    tasks.append(Task(5, dt.datetime(2000,1,1,10,30), dt.timedelta(minutes=10), 4, 3, 2))
    #tasks.append(Task(6, dt.datetime(2000,1,2,20,30), dt.timedelta(minutes=10), 9, 3, 2))

    result = hybridSchedule(tasks, rescueStartTime, numberOfProcessors)
    for i in result:
        print(i)
        print(i.getProcessorInfo())
foo()

#%% [markdown]
# .

