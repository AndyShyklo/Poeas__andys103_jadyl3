import csv

STUDENT_REQUEST_FILE = "student_req.csv"
CLASSES_FILE = "classes.csv"
NUM_OF_REQUESTED_CLASSES = 9
student_requests = []
student_schedules = {}
class_list = []

# reads student request csv into a list of dictionaries
with open(STUDENT_REQUEST_FILE, newline='') as csvfile:
    document = csv.DictReader(csvfile)
    for row in document:
        student_requests.append(row)

# reads class list csv into a a list of dictionaries
with open(CLASSES_FILE, newline='') as csvfile:
    document = csv.DictReader(csvfile)
    for row in document:
        class_list.append(row)

# goes through the request and adds the possible periods for the class in course info
# returns a dictionary where student id is the key, and the list of lists is the value
# change period 10 to 0.
def returnListofAvailability(student_request, course_info):
    availability = []
    for i in range(1, NUM_OF_REQUESTED_CLASSES + 1):
        classcode = student_request["Course"+str(i)]
        availablePds = []
        for course in course_info:
            if course["CourseCode"] == classcode:
                if int(course["Remaining Capacity"]) > 0:
                    if int(course["PeriodID"]) == 10:
                        availablePds.append(0)
                    else:
                        availablePds.append(course["PeriodID"])
        availability.append(availablePds)
    return availability

def availabilitySorter(availability):
    avail_temp = []
    for item in availability:
        return("hi")
    return(avail_temp)


# goes through the request and adds the possible periods for the class in course info (dictionary)
def returnListofAvailabilityDict(student_request, course_info):
    availability = {}
    for i in range(1, NUM_OF_REQUESTED_CLASSES + 1):
        classcode = student_request["Course"+str(i)]
        availablePds = []
        for course in course_info:
            if course["CourseCode"] == classcode:
                if int(course["Remaining Capacity"]) > 0:
                    availablePds.append(course["PeriodID"])
        availability[student_request["Course"+str(i)]] = (availablePds)
    return availability

#wrapper function, starts at 1 as list starts with student id
def checkSchedule(studentid, availability):
    return checkScheduleR(studentid, availability, 0, "", False, [], [])

#recursively check available periods, and returns if successful, the furthest it got into the schedule, and the class it failed to add
def checkScheduleR(studentid, availability, current_class, schedule_so_far, working, max_sched, failed_classes):
    # print(current_class, schedule_so_far, working, max_sched, failed_classes)
    print(availability)
    print(type(availability))
    if (current_class > 0) and (schedule_so_far.find(schedule_so_far[-1]) != len(schedule_so_far) - 1) and (schedule_so_far[-1] != "-"): # if period is double booked
        return [False, max_sched, failed_classes]
    if current_class >= len(availability): # end of recursive cycle, passes scheduling
        # print(schedule_so_far)
        student_schedules[studentid] =  schedule_so_far
        return [True, max_sched, failed_classes]
    if (len(max_sched) == 0) or (len(schedule_so_far) > len(max_sched[0])): # checks for max schedule reached, for first iteration
        max_sched.clear()
        failed_classes.clear()
        max_sched.append(schedule_so_far)
        tempE = f"Course{current_class + 1}, {availability[current_class]}"
        failed_classes.append(tempE)
    elif (len(schedule_so_far) == len(max_sched[0])): # checks for max schedule reached, for all other iterations
        max_sched.append(schedule_so_far)
        tempE = f"Course{current_class + 1}, {availability[current_class]}"
        failed_classes.append(tempE)
    if len(availability[current_class]) == 0: # if no section is available
        return checkScheduleR(studentid, availability, current_class+1, schedule_so_far+"-", False, max_sched, failed_classes)
    for i in range(len(availability[current_class])): # general recursive sequence, for every case
        pd = availability[current_class][i]
        result = checkScheduleR(studentid, availability, current_class+1, schedule_so_far+str(pd), False, max_sched, failed_classes)
        if result[0]:
            return result
    return [False, max_sched, failed_classes]

# test recursion function
# print(student_schedules)

# translates the schedule into a readable
def translateSchedule(schedule, student_req):
    sched = {'1': "None", '2': "None", '3': "None", '4': "None", '5': "None", '6': "None", '7': "None", '8': "None", '9': "None", '0': "None"}
    for i in range(len(schedule)):
        if schedule[i] != "-":
            sched[schedule[i]] = student_req["Course"+str(i+1)]
    return sched

# print(translateSchedule(student_schedules[0]["100645728"], {'Course1': "geometry", 'Course2': "algebra 2", 'Course3': "precalc", 'Course4': "calc ab"}))

# prints a created schedule or none, and creates for all students
def createSchedules():
    for student in student_requests:
        osis = student['StudentID']
        availability = returnListofAvailability(student, class_list)
        # print(availability)
        # print(checkSchedule(osis, availability))
        sched = checkSchedule(osis, availability)
        if (sched[0]):
            # print(sched[1])
            print("Schedule:", translateSchedule(student_schedules[osis], student))
            print("YES schedule for " + osis)
        else:
            # print(sched)
            fails = sched[1]
            courseF = sched[2]
            totalF = {}
            for i in range(len(courseF)):
                try:
                    val = totalF[courseF[i]]
                    # print("exists")
                    val.append(fails[i])
                except:
                    # print("not exists")
                    totalF[courseF[i]] = [fails[i]]
            print("Scheduling failed at", list(totalF.keys()), ", but scheduled for", len(list(totalF.values())[0]), "iterations, with", len(list(totalF.values())[0][0]), "periods scheduled total, and with full dict:", totalF)
            print("NO schedule for " + osis)

# createSchedules()

# returns if a schedule works and that schedule, or if it fails, it returns where and what failed
def createSchedule(student):
    osis = student['StudentID']
    availability = returnListofAvailability(student, class_list)
    # print(availability)
    # print(checkSchedule(osis, availability))
    sched = checkSchedule(osis, availability)
    if (sched[0]):
        # print(sched[1])
        translated = translateSchedule(student_schedules[osis], student)
        print("Schedule:", translated)
        print("YES schedule for " + osis)
        return([True, translated])
    else:
        # print(sched)
        fails = sched[1]
        courseF = sched[2]
        totalF = {}
        for i in range(len(courseF)):
            try:
                val = totalF[courseF[i]]
                # print("exists")
                val.append(fails[i])
            except:
                # print("not exists")
                totalF[courseF[i]] = [fails[i]]
        print("Scheduling failed at", list(totalF.keys()), ", but scheduled for", len(list(totalF.values())[0]), "iterations, with", len(list(totalF.values())[0][0]), "periods scheduled total, and with full dict:", totalF)
        print("NO schedule for " + osis)
        return ([False, sched])

# prints an array of one student with schedules, or blank without schedules. courses are CourseID-SectionID
def formatList(osis):
    student = None
    for stude in student_requests:
        if stude['StudentID'] == osis:
            student = stude
            break
    if student == None:
        return("Unknown osis")
    sched = createSchedule(student)
    if sched[0]:
        studentC = [osis, student['FirstName'], student['LastName'], student['OffClass'], True]
        for val in list(sched[1].keys()):
            classS = None
            for classR in class_list:
                if classR["CourseCode"] == sched[1][val]:
                    classS = classR["SectionID"]
            if classS == None:
                tempF = ""
            else:
                tempF = f"{sched[1][val]}-{classS}"
            studentC.append(tempF)
    else:
        studentC = [osis, student['FirstName'], student['LastName'], student['OffClass'], False, "", "", "", "", "", "", "", "", "", ""]
    return(studentC)

# prints a 2d array of each student with schedules, or blank without schedules. courses are CourseID-SectionID. fulfills task 2
def formatListTotal():
    studentsTotal = [["OSIS", "FIRSTNAME", "LASTNAME", "OFFICIALCLASS", "VALID", "PERIOD1", "PERIOD2", "PERIOD2", "PERIOD3", "PERIOD4", "PERIOD5", "PERIOD6", "PERIOD7", "PERIOD8", "PERIOD9", "PERIOD10"]]
    for student in student_requests:
        studentC = formatList(student['StudentID'])
        studentsTotal.append(studentC)
    return(studentsTotal)

# prints array of strings each with one class, with the section and id, and the student assigned to it. fulfills task 1
def formatListTotalClass():
    classArr = []
    twoArr = formatListTotal()
    if len(twoArr) == 0 or len(twoArr) == 1:
        return("No items in 2D array")
    for a in twoArr[1:]:
        for b in a[5:]:
            if b != "":
                str = ",".join(a[0:4]) + ","
                c = b.split("-")
                str += c[0] + "," + c[1]
                classArr.append(str)
    return(classArr)

print("\n", "Task 1:", formatListTotalClass(), "\n")
print("\n", "Task 2:", formatListTotal(), "\n")

# finds list of all classes and periods
def findImpossibleSchedulesStudent(student_id):
    for student in student_requests:
        if student_id == student['StudentID']:
            availability = returnListofAvailabilityDict(student, class_list)
            print(availability)
            # checkSchedule(availability)

# findImpossibleSchedulesStudent('100635729')

# finds a potential schedule using existing period availability. framework for future algorithm, NOT IN USE
def findPossibleSchedule(student_id):
    for student in student_requests:
        if student_id == student['StudentID']:
            classes = {'1': "None", '2': "None", '3': "None", '4': "None", '5': "None", '6': "None", '7': "None", '8': "None", '9': "None", '10': "None"}
            avail_dict = returnListofAvailabilityDict(student, class_list)
            print(avail_dict)
            availability = sorted(avail_dict, key=lambda k: len(avail_dict[k]), reverse = False)
            print(availability)
            for item in availability:
                # print(item)
                for pd in avail_dict[item]:
                    # print(pd, classes[pd])
                    if classes[pd] == "None":
                        classes[pd] = item
                        # print(pd, classes[pd])
                        break
                    if (pd == availability[-1]):
                        return ("Error, cannot be scheduled. Current Schedule", classes, "   Current class and period:", item, pd, "   Current pd list: ", avail_dict[item])
            return(classes)

# print("Class schedule: ", findPossibleSchedule('100635729'))
