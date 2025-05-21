import csv
import math

# StudentRequest-Sample2.csv     student_test.csv
STUDENT_REQUEST_FILE = "student_test.csv"
# 02M475,2024,2,799,,,,,EES88,FFS62,MPS22X,PPS88QA,SCS22,ZQ03,ZQ04,ZQ05,ZQ06,ZQ07,ZQ08,,,,
# 02M475,2024,2,527,,,,,EES82QFC,FJS64,HGS42,MPS22XH,PHS11,PPS82QB,SBS22H,SBS44QLA,UZS32,ZLUN,,,,,
CLASSES_FILE = "MasterSchedule.csv"
NUM_OF_REQUESTED_CLASSES = 15
student_requests = []
student_schedules = {}
class_list = []
special_doubles = ["SBS22H", "SBS44QLA", "SBS44QLB", "SCS22H",
                   "SCS22QLA", "SCS22QLB", "SPS22H", "SPS22QLA", "SPS22QLB"]

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

# goes through the request and adds the section-ids for available classes in course info
# returns a dictionary where student id is the key, and the list of lists is the value
# if a course id and section id are the same, add a second list of same section/course id to the availability ex. calc bc double with same id


def returnListofAvailability(student_request, course_info):
    biology = False
    chemistry = False
    physics = False

    availability = []
    for i in range(1, NUM_OF_REQUESTED_CLASSES + 1):
        classcode = student_request["Course"+str(i)]
        availablePds = []
        found_courses = []
        if classcode != None:
            if len(classcode) > 0:
                found_courses = sectionsFromCourseCode(classcode, course_info)
        
        found_courses.sort(key=lambda L: L[0], reverse=True)# check for doubles
        if (classcode in special_doubles):  # messed up special case
            ind = special_doubles.index(classcode)
            if (ind == 0 and not biology):
                biology = True
                found_courses.append(sectionsFromCourseCode[special_doubles[1]])
                found_courses.append(sectionsFromCourseCode[special_doubles[2]])
            elif (ind == 3 and not chemistry):
                chemistry = True
                found_courses.append(sectionsFromCourseCode[special_doubles[4]])
                found_courses.append(sectionsFromCourseCode[special_doubles[5]])
            elif (ind == 6 and not physics):
                physics = True
                found_courses.append(sectionsFromCourseCode[special_doubles[7]])
                found_courses.append(sectionsFromCourseCode[special_doubles[8]])
            if (ind in [0, 3, 6]):
                found_courses.sort(key=lambda L: L[0], reverse=True)
                for i in range(int(len(found_courses) / 2)):
                    avail1 = found_courses[2 * i]
                    avail2 = found_courses[2 * i + 1]
                    cycle1 = cycleToNumber(avail1[2])
                    cycle2 = cycleToNumber(avail2[2])
                    # adds section id, periods, cycles for the periods, and the lesser availability of the courses(which shouldn't be a problem but could be).
                    if type(cycle1) is int and type(cycle2) is int:
                        availablePds.append(
                            (avail1[0], (avail1[1], avail2[1]), (cycle1, cycle2), min(avail1[3], avail2[3])))
        # double case
        elif (len(found_courses) > 1 and found_courses[0][0] == found_courses[1][0]):
            for i in range(int(len(found_courses) / 2)):
                avail1 = found_courses[2 * i]
                avail2 = found_courses[2 * i + 1]
                cycle1 = cycleToNumber(avail1[2])
                cycle2 = cycleToNumber(avail2[2])
                # adds section id, periods, cycles for the periods, and the lesser availability of the courses(which shouldn't be a problem but could be).
                if type(cycle1) is int and type(cycle2) is int:
                    availablePds.append(
                        (avail1[0], (avail1[1], avail2[1]), (cycle1, cycle2), min(avail1[3], avail2[3])))
        else:  # normal case
            for avail in found_courses:
                cycle = cycleToNumber(avail[2])
                if cycle != "00000" and type(cycle) is int:
                    availablePds.append((avail[0], avail[1], cycle, avail[3]))
        # sort by availability
        availablePds.sort(key=lambda L: L[3], reverse=True)

        if len(found_courses) > 0 and len(availablePds) > 1:  # add sublist to full list
            availablePds.insert(0, classcode)
            print(availablePds)
            availability.append(availablePds)
    availability.sort(key=len)
    return availability


def sectionsFromCourseCode(coursecode, course_info):
    found_courses = []
    for course in course_info:
        if course["CourseCode"] == coursecode:
            if int(course["Remaining Capacity"]) > 0:
                found_courses.append([course["SectionID"], course["PeriodID"],
                                    course["Cycle Day"], int(course["Remaining Capacity"])])
    return found_courses


def cycleToNumber(cycle):
    if cycle == "11111":
        return 0
    elif cycle == "10101":
        return 1
    elif cycle == "01010":
        return 2
    else:
        return cycle

# old availability function. works but not with doubles, just single 11111 classes
# works with updated recursive functions


def returnListofAvailabilityOld(student_request, course_info):
    availability = []
    for i in range(1, NUM_OF_REQUESTED_CLASSES + 1):
        classcode = student_request["Course"+str(i)]
        # print(classcode, type(classcode), len(classcode), availability)
        availablePds = []
        if classcode != None:
            if len(classcode) > 0:
                for course in course_info:
                    if course["CourseCode"] == classcode:
                        if int(course["Capacity"]) > 0:
                            if int(course["PeriodID"]) == 10:
                                availablePds.append('0')
                            else:
                                availablePds.append(course["PeriodID"])
                availability.append(availablePds)
    # print(availability)
    return availability

# print(returnListofAvailabilityOld(student_requests[0], class_list))
# print(returnListofAvailability(student_requests[0], class_list))


def selectionSorter(availability):
    avail_temp = []
    count = 0
    for item in availability:
        if count < len(item):
            count = len(item)
    for i in range(0, count):
        for item in availability:
            if i == len(item):
                avail_temp.append(item)
    return (avail_temp)


def availabilitySorter(availability):
    avail_temp = []

# wrapper function, calls R with osis#, availability list, starting index, schedule array, the WIP schedule, the empty failed classes, and an empty assigned classes


def checkSchedule(studentid, availability):
    return checkScheduleR(studentid, availability, 0, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [], [], [])

# new recursive function that works for doubles and half periods, returning both scheduled classes and periods
# currently error with class code ZQPD1, which has cycle 00110???


def checkScheduleR(studentid, availability, current_class, schedule_so_far, max_sched, failed_classes, class_courses):
    # print(current_class, schedule_so_far, working, max_sched, failed_classes)
    # end of recursive cycle, passes scheduling
    if current_class >= len(availability):
        pd = class_courses[-1]
        student_schedules[studentid] = schedule_so_far
        # organizeSchedule(schedule_so_far, class_courses)
        return [True, max_sched, failed_classes, class_courses]
    # checks for max schedule reached, for first iteration
    if (len(max_sched) == 0) or (len(schedule_so_far) > len(max_sched[0]) - 1):
        max_sched.clear()
        # erase later, seems to work decently, but can schedule last class and print valid max schedule
        failed_classes.clear()
        max_sched.append(schedule_so_far)
        tempE = f"Course{current_class + 1}, {availability[current_class]}"
        failed_classes.append(tempE)
    # checks for max schedule reached, for all other iterations
    elif (len(schedule_so_far) == len(max_sched[0])):
        max_sched.append(schedule_so_far)
        tempE = f"Course{current_class + 1}, {availability[current_class]}"
        failed_classes.append(tempE)
    # general recursive sequence, for every case
    for i in range(1, len(availability[current_class])):
        pd = availability[current_class][i]
        comp = schedule_so_far.copy()
        if (type(pd[1]) is not str) and len(pd[1]) > 1:  # double case
            print(pd)
            pd1 = pd[1][0]
            pd1cycle = pd[2][0]
            pd2 = pd[1][1]
            pd2cycle = pd[2][1]
            comp[int(pd1)-1] += cycleToDouble(pd1cycle)
            comp[int(pd2)-1] += cycleToDouble(pd2cycle)
            if max(comp) > 1:  # if 2 b days or a or b on full period
                comp = schedule_so_far
            elif 0.2 in comp:  # if 2 a days
                comp = schedule_so_far
            if comp == schedule_so_far:
                result = [False, max_sched, failed_classes, class_courses]
            else:
                class_courses_copy = class_courses.copy()
                class_courses_copy.append([availability[current_class][0], pd])
                result = checkScheduleR(studentid, availability, current_class+1,
                                        comp, max_sched, failed_classes.copy(), class_courses_copy)

        else:  # non double case
            # print(pd, availability[current_class][0])
            # print(availability[current_class])
            if comp[int(pd[1])-1] == 0.0:
                # print("trace1")
                # print(comp[int(pd[1])-1])
                if pd[2] == 0:
                    # print("trace4")
                    comp[int(pd[1])-1] += 1.0
                elif pd[2] == 1:
                    comp[int(pd[1])-1] += 0.1
                elif pd[2] == 2:
                    comp[int(pd[1])-1] += 0.9
            elif comp[int(pd[1])-1] == 0.1:
                # print("trace2")
                # print(comp[int(pd[1])-1])
                if pd[2] == 2:
                    comp[int(pd[1])-1] += 0.9
            elif comp[int(pd[1])-1] == 0.9:
                # print("trace3")
                # print(comp[int(pd[1])-1])
                if pd[2] == 1:
                    comp[int(pd[1])-1] += 0.1
            if comp == schedule_so_far:
                result = [False, max_sched, failed_classes, class_courses]
            else:
                class_courses_copy = class_courses.copy()
                class_courses_copy.append([availability[current_class][0], pd])
                result = checkScheduleR(studentid, availability, current_class+1,
                                        comp, max_sched, failed_classes.copy(), class_courses_copy)
        # print(comp)
        # print(result)
        # print(pd)
        if result != None and result[0]:
            return result
    return [False, max_sched, failed_classes, class_courses]


def cycleToDouble(cycle):
    if cycle == 0:
        return 1.0
    elif cycle == 1:
        return 0.1
    elif cycle == 2:
        return 0.9

# [1.0, 0.1, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

# ["StudentID" ["CourseCode", "SectionID", "Period"]]

# test recursion function
# print(student_schedules)


# def organizeSchedule(schedule_so_far, class_courses):
#     class_courses.sort(key=lambda L: int(L[1][1]), reverse=False)
#     print(class_courses)
#     for class in class_courses:
#         if

# translates the schedule into a readable
def translateSchedule(schedule, student_req):
    sched = {'1': "None", '2': "None", '3': "None", '4': "None", '5': "None",
             '6': "None", '7': "None", '8': "None", '9': "None", '0': "None"}
    # print(student_req["StudentID"])
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
            print("hi")
            # print(sched[1])
            # print("Schedule:", translateSchedule(student_schedules[osis], student))
            # print("YES schedule for " + osis)
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
            print("Scheduling failed at", list(totalF.keys()), ", but scheduled for", len(list(totalF.values())[
                  0]), "iterations, with", len(list(totalF.values())[0][0]), "periods scheduled total, and with full dict:", totalF)
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
        print("Schedule:", sched[1])
        print("Total List:", sched[3])
        print("YES schedule for " + osis)
        return ([True, osis, sched])
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
        print("Scheduling failed at", list(totalF.keys()), ", but scheduled for", len(list(totalF.values())[0]), "iterations, with", len(list(totalF.values())[
              0][0]), "periods scheduled total, and with full dict:", totalF, "\n \n Total class sections: ", sched[3], "\n \n Availability:", availability)
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
        return ("Unknown osis")
    sched = createSchedule(student)
    if sched[0]:
        studentC = [osis, student['FirstName'],
                    student['LastName'], student['OffClass'], True]
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
        studentC = [osis, student['FirstName'], student['LastName'],
                    student['OffClass'], False, "", "", "", "", "", "", "", "", "", ""]
    return (studentC)

# prints a 2d array of each student with schedules, or blank without schedules. courses are CourseID-SectionID. fulfills task 2


def formatListTotal():
    studentsTotal = [["OSIS", "FIRSTNAME", "LASTNAME", "OFFICIALCLASS", "VALID", "PERIOD1", "PERIOD2",
                      "PERIOD2", "PERIOD3", "PERIOD4", "PERIOD5", "PERIOD6", "PERIOD7", "PERIOD8", "PERIOD9", "PERIOD10"]]
    for student in student_requests:
        studentC = formatList(student['StudentID'])
        studentsTotal.append(studentC)
    return (studentsTotal)

# print(formatListTotal())

# prints array of strings each with one class, with the section and id, and the student assigned to it. fulfills task 1. OUTPUT: [[123456789,SMITH,JOHN,09,1AA,E1,1], ...]


def formatListTotalClass():
    classArr = []
    twoArr = []
    # print(student_requests)
    for student in student_requests:
        twoArr = (createSchedule(student))
        print(twoArr)
        if len(twoArr) == 0:
            return ("No items in 2D array")
        for a in twoArr[2][3]:
            print(a)
            if a != "":
                strList = [student['StudentID']]
                strList.append(student['LastName'])
                strList.append(student['FirstName'])
                strList.append(student['SchoolYear'])
                strList.append(student['OffClass'])
                strList.append(a[0] + "-" + a[1][0])
                strList.append(a[1][1])
                print(strList)
                str = ",".join(strList)
                classArr.append(str)
    return (classArr)


print("\n", "Task 1:", formatListTotalClass(), "\n")
# print("\n", "Task 2:", formatListTotal(), "\n")
