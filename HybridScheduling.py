#%% [markdown]
# # Hybrid Scheduling
# 
# 

#%%
import datetime as dt
import threading
import copy


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
        
        self.lock = threading.Lock()
        
    def __str__(self):
        return f'tID: {self.tID}; arrivalTime: ${self.arrivalTime}; burstTime: {self.burstTime}; tasksPriority: {self.tasksPriority} distance: {self.distance}; areaID: {self.areaID}'
    
    def setProcessor(self, processorID, startTime):
        # Processor ID is integer
        # startTime is a datetime.time object

        #startTime is datetime
        self.startTime = startTime
        #Completion Time is datetime
        self.completionTime = self.startTime + self.burstTime
        #waitingTime is timedelta
        self.waitingTime = self.startTime - self.arrivalTime
        #turnaroundTime is timedelta
        self.turnaroundTime = self.completionTime - self.arrivalTime
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
    
class Processor:
    def __init__(self, pID, name, startTime, medic=False, water=False):
        self.thread = threading.Thread(name=name) 
        self.time = startTime
        self.medic = medic
        self.water = water
        self.id = pID


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
    #print("helper: ")
    #print(tasks)
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
                if len(burstTuple[1]) > 1: # Length of equal BurstTime items
                    burstTuple = taskSort_helper(burstTuple[1], lambda x:x.tasks[0].arrivalTime)
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
def prioritySort(tasks):
    # areas must be a 2d list of tasks objects; where 1 taskk is a list of tasks
    # Returns list of tasks in specified sorted order 
    prioTuple = ([],[],[])
    arrivalTuple = ([],[],[])
    trueEqual = []
    # Step 1: Sort by priority (high to low)
    if len(tasks) > 1:
        prioTuple = taskSort_helper(tasks, lambda x:x.tasksPriority)
        # Step 2: If same priority, sort by arrivalTime (low to high)
        if len(prioTuple[1]) > 1: # Length of equal priority items
            arrivalTuple = taskSort_helper(prioTuple[1], lambda x:x.arrivalTime) # Assumes Equal distances, or at least that distances are closer to each other than to other tasks
            trueEqual = arrivalTuple[1]
        else:
            trueEqual = prioTuple[1]
    
        return prioritySort(prioTuple[2])+prioritySort(arrivalTuple[0])+trueEqual+prioritySort(arrivalTuple[2])+prioritySort(prioTuple[0])

    # Note that you want equal ^^^^^ not pivot
    else:  # You need to hande the part at the end of the recursion - when you only have one element in your array, just return the array.
        return tasks


#%%
def arrivalTimeSort(tasks):
    # tasks must be a list of task objects
    # Returns list of tasks in specified sorted order 
    arrivalTuple = ([],[],[])
    trueEqual = []
    
    # Step 1: sort by arrival Time
    if len(tasks) > 1:
        arrivalTuple = taskSort_helper(tasks, lambda x:x.arrivalTime)
        trueEqual = arrivalTuple[1]
        
        return arrivalTimeSort(arrivalTuple[0])+trueEqual+arrivalTimeSort(arrivalTuple[2])
    # Note that you want equal ^^^^^ not pivot
    else:  # You need to hande the part at the end of the recursion - when you only have one element in your array, just return the array.
        return tasks


#%%
def soonestTime(processors):
    # Used once in code, so doeen't need to be a function, but is a useful abstraction
    # Returns key of dict processorTime that is the soonest time 
    soonest = processors[0]
    for proc in processors:
        if proc.time < soonest.time:
            soonest = proc
    return soonest
def isAvailable(task, processor):
    #Determines if a task can be completed by processor
    if task.arrivalTime > processor.time:
        return False
    return True


#%%
def singleProcessorSchedule(processor, unscheduledTasks, processorResetTime, grouping=False):
    # Find First Task that each processor can acomplish
        mytask = None
        for task in unscheduledTasks:
            if isAvailable(task, processor):
                mytask = task
                break
        #Update Task Times, processors, etc
        if mytask is not None:
            unscheduledTasks.remove(mytask)
            mytask.setProcessor(processor.id, processor.time)
            print('Processor {} Took task {} at startTime{}'.format(processor.id, task.tID, task.startTime))
            if grouping==False:
                processor.time = mytask.completionTime+processorResetTime # only for single, not for grouping
            else:
                processor.time = mytask.completionTime
        else:
            print('Processor {} has no tasks to do at {}'.format(processor.id,processor.time))
            processor.time += dt.timedelta(minutes=5)
            
def scheduleGroup(processor, unscheduledTaskGroups, processorResetTime):
    # Find First Task that each processor can acomplish
        mytasks = None
        for group in unscheduledTaskGroups:
            if isAvailable(group.tasks[0], processor):
                mytasks = group
                break
        #Update Task Times, processors, etc
        if mytasks is not None:
            unscheduledTaskGroups.remove(mytasks)
            
            while(mytasks.tasks):
                if mytasks.tasks:
                    singleProcessorSchedule(processor, mytasks.tasks, processorResetTime, True)
            processor.time += processorResetTime
#             for task in mytasks.tasks:
#                 if isAvailable(task, processor) : 
#                     task.setProcessor(processor.id, processor.time)
#                     print('Processor {} took task {} at startTime {}'.format(processor.id, task.tID, task.startTime))
#                     processor.time = task.completionTime
#                 else:
#                     print('Processor {} cannot take task {}. This error is fatal. '.format(processor.id, task.tID))
            #processor.time += processorResetTime
        else:
            print('Processor {} has no tasks to do at {}'.format(processor.id,processor.time))
            processor.time += dt.timedelta(minutes=5)


#%%
def schedule(sortedTaskList, rescueStartTime, processorCount, processorResetTime=dt.timedelta(minutes=30), grouping=False):
    
    # Assign each task to a processor
    # First Come First Serve (now that tasks are sorted)
    # Processors is a list of processor objects 
    processors = []
    for i in range(processorCount):
        processors.append(Processor(i, 'p'+str(i), rescueStartTime))
        
    unscheduledTasks = copy.copy(sortedTaskList)
    if not grouping :
        while(unscheduledTasks):
            processor = soonestTime(processors)
            if unscheduledTasks:
                singleProcessorSchedule(processor, unscheduledTasks, processorResetTime)
    else: #if grouping:
        # Go from sorting based on areas to based on tasks
        taskList = []
        for area in sortedTaskList:
            for task in area.tasks:
                taskList.append(task)
        print(taskList)
        
        # Sorted Task List and unscheduled Tasks are now groups, not tasks
        while(unscheduledTasks):
            processor = soonestTime(processors)
            if unscheduledTasks:
                scheduleGroup(processor, unscheduledTasks, processorResetTime)
        

        
    
    totalWaitingTime = dt.timedelta()
    totalTurnaroundTime = dt.timedelta()
    for task in taskList:
        totalWaitingTime += task.waitingTime
        totalTurnaroundTime += task.turnaroundTime
        
    print("totalWaitingTime: "+str(totalWaitingTime))
    # Calculate AverageWaitingTime
    averageWaitingTime = totalWaitingTime / len(taskList)
    print("averageWaitingTime: "+str(averageWaitingTime))
    print("totalTurnaroundTime: "+str(totalTurnaroundTime))
    # Calculate averageTurnaroundTime
    averageTurnaroundTime = totalTurnaroundTime / len(taskList)
    print("averageTurnaroundTime: "+str(averageTurnaroundTime))
    return taskList


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
    # Schedule processors
    sortedTaskList = schedule(sortedTaskList, rescueStartTime, processorCount, processorResetTime )
    return sortedTaskList
    


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
            #print("Sorting tasks")
            sortedAreas.append(Area(taskSort(areas[aID]), avgPrio, burstTime))
        sortedAreas.append(Area(areas[aID], avgPrio, burstTime))

    # Sort Areas
    sortedAreas = areaSort(sortedAreas)
    sortedTaskList = schedule(sortedAreas, rescueStartTime, processorCount, processorResetTime, grouping=True )
#     sortedTaskList = []
#     # Go from sorting based on areas to based on tasks
#     for area in sortedAreas:
#         for task in area.tasks:
#             sortedTaskList.append(task)
            
    # Schedule processors 
    #sortedTaskList = schedule(sortedTaskList, rescueStartTime, processorCount, processorResetTime, grouping=True )
    
    return sortedTaskList


#%%
def firstComeSchedule(taskList, rescueStartTime, processorCount, processorResetTime=dt.timedelta(minutes=30)):
    
    sortedTaskList = arrivalTimeSort(taskList)
    sortedTaskList = schedule(sortedTaskList, rescueStartTime, processorCount, processorResetTime)
    return sortedTaskList

def prioritySchedule(taskList, rescueStartTime, processorCount, processorResetTime=dt.timedelta(minutes=30)):
    
    sortedTaskList = prioritySort(taskList)
    sortedTaskList = schedule(sortedTaskList, rescueStartTime, processorCount, processorResetTime)
    return sortedTaskList


#%%
def fcfsExample():
    rescueStartTime = dt.datetime(2000,1,1,10,5)
    numberOfProcessors = 3
    tasks =     [Task(1, dt.datetime(2000,1,1,10,00), dt.timedelta(minutes=30), 7, 5, 1)]
    tasks.append(Task(4, dt.datetime(2000,1,1,10,15), dt.timedelta(minutes=35), 8, 2, 4))
    tasks.append(Task(2, dt.datetime(2000,1,1,10,0), dt.timedelta(minutes=15), 7, 3, 2))
    tasks.append(Task(5, dt.datetime(2000,1,1,10,30), dt.timedelta(minutes=10), 4, 3, 2))
    tasks.append(Task(3, dt.datetime(2000,1,1,10,00), dt.timedelta(minutes=40), 5, 7, 3))
    
    result = firstComeSchedule(tasks, rescueStartTime, numberOfProcessors)
    for i  in result:
        print(i)
        print(i.getProcessorInfo())
fcfsExample()


#%%
def priorityExample():
    rescueStartTime = dt.datetime(2000,1,1,10,5)
    numberOfProcessors = 3
    tasks =     [Task(1, dt.datetime(2000,1,1,10,00), dt.timedelta(minutes=30), 7, 5, 1)]
    tasks.append(Task(4, dt.datetime(2000,1,1,10,15), dt.timedelta(minutes=35), 8, 2, 4))
    tasks.append(Task(2, dt.datetime(2000,1,1,10,0), dt.timedelta(minutes=15), 7, 3, 2))
    tasks.append(Task(5, dt.datetime(2000,1,1,10,30), dt.timedelta(minutes=10), 4, 3, 2))
    tasks.append(Task(3, dt.datetime(2000,1,1,10,00), dt.timedelta(minutes=40), 5, 7, 3))
    tasks.append(Task(6, dt.datetime(2000,1,1,10,00), dt.timedelta(minutes=40), 5, 7, 3))
    
    result = prioritySchedule(tasks, rescueStartTime, numberOfProcessors)
    for i  in result:
        print(i)
        print(i.getProcessorInfo())
priorityExample()


#%%
def noGroupingExample():
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
    result = hybridScheduleNoGroup(tasks, rescueStartTime, numberOfProcessors)
    for i in result:
        print(i)
        print(i.getProcessorInfo())
noGroupingExample()


#%%
def groupingExample():
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
    tasks.append(Task(6, dt.datetime(2000,1,1,11,40), dt.timedelta(minutes=10), 4, 3, 3))

    result = hybridSchedule(tasks, rescueStartTime, numberOfProcessors)
    for i in result:
        print(i)
        print(i.getProcessorInfo())
groupingExample()


#%%



