import csv
import math
import random

# StudentRequest-Sample2.csv     student_test.csv
STUDENT_REQUEST_FILE = "StudentRequest-Sample2.csv"
# 02M475,2024,2,799,,,,,EES88,FFS62,MPS22X,PPS88QA,SCS22,ZQ03,ZQ04,ZQ05,ZQ06,ZQ07,ZQ08,,,,
# 02M475,2024,2,527,,,,,EES82QFC,FJS64,HGS42,MPS22XH,PHS11,PPS82QB,SBS22H,SBS44QLA,UZS32,ZLUN,,,,,
CLASSES_FILE = "MasterSchedule.csv"
NUM_OF_REQUESTED_CLASSES = 15
student_requests = []
student_requests_dictionary = {}
student_schedules = {}
class_list = []
special_doubles = ["SBS22H", "SBS44QLA", "SBS44QLB", "SCS22H",
                   "SCS22QLA", "SCS22QLB", "SPS22H", "SPS22QLA", "SPS22QLB"]

special_frees = ['ZQ01', 'ZQ02', 'ZQ03', 'ZQ04', 'ZQ05', 'ZQ06', 'ZQ07', 'ZQ08', 'ZQ09', 'ZQ10', 
                 'ZQFA1', 'ZQFA2', 'ZQFA3', 'ZQFA4', 'ZQFA5', 'ZQFA6', 'ZQFA7', 'ZQFA8', 'ZQFA9',
                 'ZQFB1', 'ZQFB2', 'ZQFB3', 'ZQFB4', 'ZQFB5', 'ZQFB6', 'ZQFB7', 'ZQFB8', 'ZQFB9',
                 'ZQHALL', 'ZQT10', 'ZT10']

totalClassList = {}
temp_max_sched = 0
temp_failed_classes = []
classArr = []
temp_requests = []

# reads student request csv into a list of dictionaries
with open(STUDENT_REQUEST_FILE, newline='') as csvfile:
    document = csv.DictReader(csvfile)
    for row in document:
        student_requests.append(row)
        student_requests_dictionary[row['StudentID']] = row

# reads class list csv into a a list of dictionaries
with open(CLASSES_FILE, newline='') as csvfile:
    document = csv.DictReader(csvfile)
    for row in document:
        row['students'] = []
        class_list.append(row)

# goes through the request and adds the course-code, section-ids, periods, cycle, and availaibilities of each class in order of availability
# if a course id and section id are the same, add a second list of same section/course id to the availability ex. calc bc double with same id
# same for special cases like normal bio, chem, and physics,
def returnListofAvailability(student_request, course_info):
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
            initial_length=len(found_courses)
            extra_courses=[]
            if (ind == 0): # bio class
                extra_courses.extend(sectionsFromCourseCode(special_doubles[1], course_info))
                extra_courses.extend(sectionsFromCourseCode(special_doubles[2], course_info))
            elif (ind == 3): # chem class
                extra_courses.extend(sectionsFromCourseCode(special_doubles[4], course_info))
                extra_courses.extend(sectionsFromCourseCode(special_doubles[5], course_info))
            elif (ind == 6): # physics class
                extra_courses.extend(sectionsFromCourseCode(special_doubles[7], course_info))
                extra_courses.extend(sectionsFromCourseCode(special_doubles[8], course_info))
            if (ind in [0, 3, 6]):
                for i in range(initial_length):
                    avail1 = found_courses[i]
                    avail2 = [x for x in extra_courses if x[0] == avail1[0]][0]
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

        print(classcode)
        print(availablePds, "\n", found_courses, "\n \n")

        if len(found_courses) > 0 and len(availablePds) > 0:  # add sublist to full list
            availablePds.insert(0, classcode)
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

# wrapper function, calls R with osis#, availability list, starting index, schedule array, the WIP schedule, the empty failed classes, and an empty assigned classes
def checkSchedule(studentid, availability):
    global temp_max_sched
    global temp_failed_classes
    temp_max_sched = 0
    temp_failed_classes = []
    return checkScheduleR(studentid, availability, 0, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [])

# new recursive function that works for doubles and half periods, returning both scheduled classes and periods
def checkScheduleR(studentid, availability, current_class, schedule_so_far, class_courses):
    global temp_max_sched
    global temp_failed_classes
    # print(current_class, schedule_so_far, temp_max_sched, temp_failed_classes)
    # end of recursive cycle, passes scheduling
    if current_class >= len(availability):
        pd = class_courses[-1]
        student_schedules[studentid] = class_courses
        # organizeSchedule(schedule_so_far, class_courses)
        return [True, temp_max_sched, temp_failed_classes, class_courses]
    # checks for max schedule reached, for first iteration
    if (temp_max_sched == 0) or (current_class > temp_max_sched):
        # erase later, seems to work decently, but can schedule last class and print valid max schedule
        temp_max_sched = current_class
        temp_failed_classes = [availability[current_class]]
    # checks for max schedule reached, for all other iterations
    elif (current_class == temp_max_sched) and (availability[current_class] not in temp_failed_classes):
        try:
            temp_failed_classes.pop(temp_failed_classes[0].index(availability[current_class][0]))
        except:
            print("not in list", availability[current_class][0])
        temp_failed_classes.append(availability[current_class])
    # general recursive sequence, for every case
    print(availability)
    if len(availability[current_class]) > 1:
        for i in range(1, len(availability[current_class])):
            pd = availability[current_class][i]
            comp = schedule_so_far.copy()
            if (type(pd[1]) is not str) and len(pd[1]) > 1:  # double case
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
                    result = [False, temp_max_sched, temp_failed_classes, class_courses]
                else:
                    class_courses_copy = class_courses.copy()
                    class_courses_copy.append([availability[current_class][0], pd])
                    result = checkScheduleR(studentid, availability, current_class+1, comp, class_courses_copy)

            else:  # non double case
                if comp[int(pd[1])-1] == 0.0:
                    if pd[2] == 0:
                        comp[int(pd[1])-1] += 1.0
                    elif pd[2] == 1:
                        comp[int(pd[1])-1] += 0.1
                    elif pd[2] == 2:
                        comp[int(pd[1])-1] += 0.9
                elif comp[int(pd[1])-1] == 0.1:
                    if pd[2] == 2:
                        comp[int(pd[1])-1] += 0.9
                elif comp[int(pd[1])-1] == 0.9:
                    if pd[2] == 1:
                        comp[int(pd[1])-1] += 0.1
                if comp == schedule_so_far:
                    result = [False, temp_max_sched, temp_failed_classes, class_courses]
                else:
                    class_courses_copy = class_courses.copy()
                    class_courses_copy.append([availability[current_class][0], pd])
                    result = checkScheduleR(studentid, availability, current_class+1, comp, class_courses_copy)
            if result != None and result[0]:
                return result
    else:
        print("student couldnt be scheduled since no classes for availability")
        return [False, temp_max_sched, temp_failed_classes, class_courses]
    return [False, temp_max_sched, temp_failed_classes, class_courses]


def cycleToDouble(cycle):
    if cycle == 0:
        return 1.0
    elif cycle == 1:
        return 0.1
    elif cycle == 2:
        return 0.9

# updates class list based on a working schedule
def updateClassList(osis, sched, change):
    sched_codes = [x[0] for x in sched]
    sched_sections = [x[1][0] for x in sched]
    for course in class_list:
        if course['CourseCode'] in sched_codes:
            ind = sched_codes.index(course['CourseCode'])
            if course['SectionID'] == sched_sections[ind]:
                if change == -1:
                    course['students'].append(osis)
                elif change == 1:
                    course['students'].remove(osis)
                if course['CourseCode'] not in special_frees:
                    course['Remaining Capacity'] = str(int(course['Remaining Capacity']) + change)
    if change == 1:
        student_schedules[osis] = []

# returns if a schedule works and that schedule, or if it fails, it returns where and what failed
def createSchedule(student):
    osis = student['StudentID']
    availability = returnListofAvailability(student, class_list)
    sched = checkSchedule(osis, availability)
    if (sched[0]):
        print("YES schedule for " + osis)
        updateClassList(osis, sched[3], -1)
        totalClassList[osis] = sched[3]
        return ([True, osis, sched])
    else:
        fails = sched[1]
        courseF = sched[2]
        totalF = []
        for i in range(len(courseF)):
            totalF.append(courseF[i][0])
        # print("Scheduling failed at", totalF, ", but scheduled for", fails, "iterations, with", fails, "periods scheduled total, and with full dict:", courseF, "\n \n Total class sections: ", sched[3], "\n \n Availability:", availability)
        print("NO schedule for " + osis)
        # print(sched)
        return ([False, osis, sched, totalF])

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

# recursive function with student requests each time. adds all unscheduled students to failed students list and then re-runs to prioritize the failed class. OUTPUT: [[123456789,SMITH,JOHN,09,1AA,E1,1], ...]
# issue now is that when it runs, it doesnt seem to want to stop, which might mean we have an error or bad logic (both possible)
# sometimes error at user 752 again, but its not in the list, may need to always prioritize him, as he fails first
def formatListTotalClass(studentArr):
    global classArr
    counter = 0
    twoArr = []
    failed_students = []
    for student in studentArr:
        twoArr = (createSchedule(student))
        counter = 0
        if twoArr[0]:
            addClassArr(student, twoArr)
        while (not twoArr[0]) and (counter < 20):
            test_students = listAllClass(twoArr[3][0])
            if (len(test_students) <= 1):
                counter = 24
                break
            random_student = random.randint(0, len(test_students) - 1)
            updateClassList(test_students[random_student], student_schedules[test_students[random_student]], 1)
            failed_students.append(student_requests_dictionary[test_students[random_student]])
            twoArr = createSchedule(student)
            counter += 1
        if counter >= 20:
            print("restart")
            restart = student_requests.copy()
            restart.remove(student)
            restart.insert(0, student)
            for id in student_schedules:
                if student_schedules[id]:
                    updateClassList(id, student_schedules[id], 1)
            return formatListTotalClass(restart)
    if failed_students:
        formatListTotalClass(failed_students)
    return(classArr)

# puts each response into a
def addClassArr(student, twoArr):
    if len(twoArr) == 0:
        return ("No items in 2D array")
    for a in twoArr[2][3]:
        if a != "":
            if a[0].split("-")[0] in special_doubles:
                for j in range(2):
                    strList = [student['StudentID']]
                    strList.append(student['LastName'])
                    strList.append(student['FirstName'])
                    strList.append(student['SchoolYear'])
                    strList.append(student['OffClass'])
                    i = special_doubles.index(a[0])
                    strList.append(special_doubles[i + a[1][2][j]] + "-" + a[1][0])
                    strList.append(a[1][1][j])
                    str = ",".join(strList)
                    classArr.append(str)
            elif type(a[1][2]) == tuple:
                for j in range(2):
                    strList = [student['StudentID']]
                    strList.append(student['LastName'])
                    strList.append(student['FirstName'])
                    strList.append(student['SchoolYear'])
                    strList.append(student['OffClass'])
                    strList.append(a[0] + "-" + a[1][0])
                    strList.append(a[1][1][j])
                    str = ",".join(strList)
                    classArr.append(str)
            else:
                strList = [student['StudentID']]
                strList.append(student['LastName'])
                strList.append(student['FirstName'])
                strList.append(student['SchoolYear'])
                strList.append(student['OffClass'])
                strList.append(a[0] + "-" + a[1][0])
                strList.append(a[1][1])
                str = ",".join(strList)
                classArr.append(str)

# removes all (or some) students within one course,
def removeAllClass(course):
    osiss = listAllClass(course)
    osiss2 = osiss.copy()
    # osiss2 = osiss.copy()[int((len(osiss) - len(osiss)/10)):]
    osissLen = len(osiss2)
    for i in range(0, osissLen):
        updateClassList(osiss2[i], student_schedules[osiss2[i]], 1)
    students = []
    for student in student_requests:
        if student['StudentID'] in osiss2:
            students.append(student)
    return(students)

# lists all students that are in a class. used for removing students from a course
def listAllClass(course):
    studentsC = []
    for dictClass in class_list:
        if dictClass.get('CourseCode') == course:
            for student in dictClass['students']:
                if student not in studentsC:
                    studentsC.append(student)
    return(studentsC)

formatListTotalClass(student_requests)
for i in student_schedules:
    if not student_schedules[i]:
        print(i, student_schedules[i])
    else:
        print(i)

def stdDevs():
    arr = class_list
    arr2 = []
    for classArr in arr:
        if len(classArr["students"]) > 0:
            arr2.append([classArr["CourseCode"], classArr["SectionID"], classArr["Capacity"], classArr["Remaining Capacity"]]) 
    arr2.sort(key=lambda x: x[0])
    print(arr2)
    classDict = {}
    for classArr in arr2:
        if classArr[0] not in classDict:
            classDict[classArr[0]] = []
        classDict[classArr[0]].append(float(classArr[3]))
    classDict2 = {}
    for classArr in classDict.keys():
        classDict2[classArr] = stdDev(classDict[classArr])
        print("\n")
        print("Class:", classArr, "\nStandard Dev:", classDict2[classArr])
        print("Class empty seats", classDict[classArr])
    print("\n")
    return(classDict2)

def stdDev(arr):
    if len(arr) <= 1:
        return("N/A")
    meanSum = 0.0
    for classArr in arr:
        meanSum += classArr
    mean = meanSum / len(arr)
    stDev = 0.0
    for classArr in arr:
        stDev += ((classArr - mean) ** 2)
    return(math.sqrt(stDev / (len(arr) - 1)))

print(stdDevs())

# worrysome (?) classes:
# geometry - Class: MGS22QT
# Standard Dev: 3.951491580945823
# Class empty seats [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 12.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.0, 5.0, 0.0, 0.0, 0.0]

# music app - Class: UAS11
# Standard Dev: 6.683312551921141
# Class empty seats [14.0, 13.0, 5.0, 0.0]

# swim gym - Class: PWS82QA
# Standard Dev: 4.928053803045811
# Class empty seats [7.0, 7.0, 16.0, 10.0, 19.0, 8.0, 7.0]

# phys ed - Class: PPS82QB
# Standard Dev: 4.955156044825574
# Class empty seats [0.0, 0.0, 3.0, 5.0, 4.0, 1.0, 15.0, 1.0]

# fr comp - Class: EES82QFC
# Standard Dev: 2.72621680438591
# Class empty seats [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8.0, 8.0, 8.0, 8.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]