import os # for file paths
import csv # read csv
import math # math done within functions
import random # used to find random students when unscheduling

# constants used by functions only in this module
NUM_OF_REQUESTED_CLASSES = 15 #student_requests have courses from Course1 to Course15
RESET_NUM = 15
special_doubles = ["SBS22H", "SBS44QLA", "SBS44QLB", "SCS22H",
                   "SCS22QLA", "SCS22QLB", "SPS22H", "SPS22QLA", "SPS22QLB"]

# essentially global variables
student_schedules = {}
student_requests_dictionary = {}
class_list = {}
#for _check_schedule
temp_max_sched = 0
temp_failed_classes = []
#for create_schedules
last_reset = []
problem_children = []

# CSV reading ===============================================================================================================
''' parse student requests
input: filename -> String
output: (student_requests -> List of Dictionaries [{StudentID: String, Course1: String, ...}, {...}], 
        student_requests_dictionary -> Dictionary {'1': [{StudentID: String, Course1: String, ...}], ...})
'''
def get_student_requests(filename):
    student_requests = []
    student_requests_dictionary = {}
    with open(filename, newline='') as csvfile:
        document = csv.DictReader(csvfile)
        for row in document:
            row['difficulty'] = 0 
            student_requests.append(row)
            student_requests_dictionary[row['StudentID']] = row
    return(student_requests, student_requests_dictionary)

''' parse master schedule
input: filename -> String
output: class_list -> List of Dictionaries [{CourseCode: String, SectionID: String, ...}, {...}]
'''
def get_class_list(filename):
    class_list = []
    with open(filename, newline='') as csvfile:
        document = csv.DictReader(csvfile)
        for row in document:
            row['students'] = []
            class_list.append(row)
    return class_list

# Helper functions  =========================================================================================================
''' find courses with only one section
input: class_list ->  List of Dictionaries [{CourseCode: String, SectionID: String, ...}, {...}]
output: singletons -> List of Dictionaries [{CourseCode: String, SectionID: String, ...}, {...}]
'''
def get_singletons(class_list):
    courses_to_num_of_sections = {}
    for course in class_list:
        if courses_to_num_of_sections.get(course["CourseCode"]):
            courses_to_num_of_sections[course["CourseCode"]] +=1
        else:
            courses_to_num_of_sections[course["CourseCode"]] = 1
    return[x for x in courses_to_num_of_sections if courses_to_num_of_sections[x] == 1]

''' sort requests based on difficulty to schedule.
input: (class_list -> [dictionary, dictionary, ...], 
        singletons -> List of Dictionaries [{CourseCode: String, SectionID: String, ...}, {...}])
output: student_requests -> List of Dictionaries [{StudentID: String, Course1: String, ...}, {...}]
'''
def sort_requests(student_requests, singletons):
    for request in student_requests:
        num_requests = 0
        counter = 0
        for i in range(1, NUM_OF_REQUESTED_CLASSES + 1):
            classcode = request["Course"+str(i)]
            if classcode:
                num_requests += 1
            if classcode in singletons:
                counter += 1
        request['difficulty'] = counter + (num_requests / 10 * 2)
    student_requests.sort(key=lambda L: L['difficulty'], reverse=True)
    return student_requests

''' return list of courses with a course_code
input: (coursecode -> String, 
        class_list ->  List of Dictionaries [{CourseCode: String, SectionID: String, ...}, {...}])
output: found_courses ->  List of Lists [(SectionID, PeriodID, Cycle -> String, AvailableSeats), ...]
'''
def _sections_from_coursecode(coursecode, course_info):
    found_courses = []
    for course in course_info:
        if course["CourseCode"] == coursecode:
            if (int(course["Remaining Capacity"]) > 0) or (coursecode[0:2] == "ZQ"):
                found_courses.append([course["SectionID"], course["PeriodID"],
                                    course["Cycle Day"], int(course["Remaining Capacity"])])
    return found_courses

''' return integer from a 'Cycle Day' from MasterSchedule. also checks for invalid classes
input: cycle -> String
output: cycle -> Integer (translation: 0 means all days, 1 means a days, 2 means b days)
'''
def _cycle_to_number(cycle):
    if cycle in ["11111", "00110", "11000"]:
        return 0
    elif cycle == "10101":
        return 1
    elif cycle == "01010":
        return 2
    else:
        return cycle
    
''' return double from cycle integer for use in _check_schedule_r
input: cycle -> Integer
output: cycle -> Integer (translation: 1.0 means all days, 0.1 means a days, 0.9 means b days)
'''
def cycleToDouble(cycle):
    if cycle == 0:
        return 1.0
    elif cycle == 1:
        return 0.1
    elif cycle == 2:
        return 0.9

''' return integer from a 'Cycle Day' from MasterSchedule. also checks for invalid classes
input: (coursecode -> String,
        class_list ->  List of Dictionaries [{CourseCode: String, SectionID: String, ...}, {...}])
output: cycle -> Integer (translation: 0 means all days, 1 means a days, 2 means b days)
'''   
def _list_all_class(coursecode):
    studentsC = []
    for dictClass in class_list:
        if dictClass.get('CourseCode') == coursecode:
            for student in dictClass['students']:
                if student not in studentsC:
                    studentsC.append(student)
    return(studentsC)

''' returns sorted/filtered list of courses and their sections that need to be scheduled.
input: (student_request -> Dictionary {StudentID: String, Course1: String, ...}, 
        course_info -> List of Dictionaries [{CourseCode: String, SectionID: String, ...}, {...}])
output: availability -> ~4D List [[CourseCode, (SectionID, PeriodID, ScheduleID, AvailableSeats), ...], 
                                [CourseCode, ((first_SectionID, second_SectionID), (first_PeriodID, second_PeriodID), 
                                              (first_ScheduleID, second_ScheduleID), AvailableSeats)], 
                                ...]
'''
def _return_list_of_availability(student_request, course_info):
    availability = []
    for i in range(1, NUM_OF_REQUESTED_CLASSES + 1):
        classcode = student_request["Course"+str(i)]
        availablePds = []
        found_courses = []
        if classcode != None:
            found_courses = _sections_from_coursecode(classcode, course_info)
        found_courses.sort(key=lambda L: L[0], reverse=True)# check for doubles
        if (classcode in special_doubles):  # messed up special case
            ind = special_doubles.index(classcode)
            initial_length=len(found_courses)
            extra_courses=[]
            if (ind == 0): # bio class
                extra_courses.extend(_sections_from_coursecode(special_doubles[1], course_info))
                extra_courses.extend(_sections_from_coursecode(special_doubles[2], course_info))
            elif (ind == 3): # chem class
                extra_courses.extend(_sections_from_coursecode(special_doubles[4], course_info))
                extra_courses.extend(_sections_from_coursecode(special_doubles[5], course_info))
            elif (ind == 6): # physics class
                extra_courses.extend(_sections_from_coursecode(special_doubles[7], course_info))
                extra_courses.extend(_sections_from_coursecode(special_doubles[8], course_info))
            if (ind in [0, 3, 6]):
                for i in range(initial_length):
                    avail1 = found_courses[i]
                    avail2 = [x for x in extra_courses if x[0] == avail1[0]][0]
                    cycle1 = _cycle_to_number(avail1[2])
                    cycle2 = _cycle_to_number(avail2[2])
                    # adds section id, periods, cycles for the periods, and the lesser availability of the courses.
                    if type(cycle1) is int and type(cycle2) is int:
                        availablePds.append(
                            (avail1[0], (avail1[1], avail2[1]), (cycle1, cycle2), min(avail1[3], avail2[3])))
        # double case
        elif (len(found_courses) > 1 and found_courses[0][0] == found_courses[1][0]):
            for i in range(int(len(found_courses) / 2)):
                avail1 = found_courses[2 * i]
                avail2 = found_courses[2 * i + 1]
                cycle1 = _cycle_to_number(avail1[2])
                cycle2 = _cycle_to_number(avail2[2])
                # adds section id, periods, cycles for the periods, and the lesser availability of the courses.
                if type(cycle1) is int and type(cycle2) is int:
                    availablePds.append(
                        (avail1[0], (avail1[1], avail2[1]), (cycle1, cycle2), min(avail1[3], avail2[3])))
        else:  # normal case
            for avail in found_courses:
                cycle = _cycle_to_number(avail[2])
                if cycle != "00000" and type(cycle) is int:
                    availablePds.append((avail[0], avail[1], cycle, avail[3]))
        # sort by availability
        availablePds.sort(key=lambda L: L[3], reverse=True)
        if classcode and (classcode[0:2] != "ZQ") and classcode not in ["SBS44QLA", "SBS44QLB", "SCS22QLA", "SCS22QLB", "SPS22QLA", "SPS22QLB", "EES88", "FFS62", "SCS22"]:
            if len(availablePds) == 0:
                print("EMPTY SECTION ", classcode)
            availablePds.insert(0, classcode)
            availability.append(availablePds)
    availability.sort(key=len)
    return availability

''' function to sort requests based on difficulty to schedule.
input: (osis -> String
        sched -> [[course_code, (section_id -> String, period_id -> String, schedule -> integer, available_seats -> String)], ...]
        change -> Integer:-1/1)
output: class_list ->  List of Dictionaries [{CourseCode: String, SectionID: String, ...}, {...}]
'''
def _update_class_list(osis, sched, change):
    global student_schedules
    global class_list
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
                if course['CourseCode'][0:2] != "ZQ":
                    course['Remaining Capacity'] = str(int(course['Remaining Capacity']) + change)
    if change == 1:
        student_schedules[osis] = []
    # return class_list

# Create/Check Schedule functions ===========================================================================================
''' wrapper function for recursive function _check_schedule_r
input: (student_request -> Dictionary {StudentID: String, Course1: String, ...},
        availability -> ~4D List [[CourseCode, (SectionID, PeriodID, ScheduleID, AvailableSeats), ...], ...])
output: _check_schedule_r
'''
def _check_schedule(studentid, availability):
    global temp_max_sched
    global temp_failed_classes
    temp_max_sched = 0
    temp_failed_classes = []
    return _check_schedule_r(studentid, availability, 0, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [])

''' recursive function _check_schedule_r
input: (student_request -> Dictionary {StudentID: String, Course1: String, ...},
        availability -> ~4D List [[CourseCode, (SectionID, PeriodID, ScheduleID, AvailableSeats), ...], ...],
        current_class -> Integer
        schedule_so_far -> IntegerArray, tracks how full a schedule is based on assigned courses
        class_courses -> [[classcode, [CourseCode, (SectionID, PeriodID, ScheduleID, AvailableSeats)]], ...]
        temp_max_sched -> integer
        temp_failed_classes -> [CourseCode, (SectionID, PeriodID, ScheduleID, AvailableSeats), ...]
        )
output: [True/False, temp_max_sched, temp_failed_classes, class_courses]
'''
def _check_schedule_r(studentid, availability, current_class, schedule_so_far, class_courses):
    global temp_max_sched
    global temp_failed_classes
    # end of recursive cycle, passes scheduling
    if current_class >= len(availability):
        pd = class_courses[-1]
        student_schedules[studentid] = class_courses
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
                    result = _check_schedule_r(studentid, availability, current_class+1, comp, class_courses_copy)

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
                    result = _check_schedule_r(studentid, availability, current_class+1, comp, class_courses_copy)
            if result != None and result[0]:
                return result
    else:
        print("student couldnt be scheduled since no classes for availability")
        return [False, temp_max_sched, temp_failed_classes, class_courses]
    return [False, temp_max_sched, temp_failed_classes, class_courses]


''' wrapper function to call checkSchedule functions and format result for create_schedules based on difficulty to schedule.
input: (student -> Dictionary {StudentID: String, Course1: String, ...},)
output: List [True, StudentID -> String, result -> List] or [False, StudentID -> String, result -> List, temp_failed_classes -> List]
'''
def _create_schedule(student):
    global class_list
    osis = student['StudentID']
    availability = _return_list_of_availability(student, class_list)
    result = _check_schedule(osis, availability)
    if (result[0]):
        _update_class_list(osis, result[3], -1)
        return ([True, osis, result])
    else:
        temp_failed_classes = result[2]
        totalF = []
        for i in range(len(temp_failed_classes)):
            totalF.append(temp_failed_classes[i][0])
        return ([False, osis, result, totalF])

# Main functions =========================================================================================================
''' wrapper function to sort requests based on difficulty to schedule.
input: (student_requests -> List of Dictionaries [{StudentID: String, Course1: String, ...}, {...}],
        class_list_in ->  List of Dictionaries [{CourseCode: String, SectionID: String, ...}, {...}], 
        student_requests_dictionary -> Dictionary {'1': [{StudentID: String, Course1: String, ...}], ...})
output: _create_schedules_r
'''
def create_schedules(student_requests, class_list_in, student_requests_dictionary_in):
    global class_list
    class_list = class_list_in
    global last_reset
    last_reset = student_requests.copy()
    global student_requests_dictionary
    student_requests_dictionary = student_requests_dictionary_in
    return _create_schedules_r(student_requests)

''' function to sort requests based on difficulty to schedule.
input: (student_requests -> List of Dictionaries [{StudentID: String, Course1: String, ...}, {...}],
        student_requests_dictionary -> Dictionary {'1': [{StudentID: String, Course1: String, ...}], ...},
        problem_children -> List of Dictionaries [{StudentID: String, Course1: String, ...}, {...}],
        failed_students -> List of Dictionaries [{StudentID: String, Course1: String, ...}, {...}],
        minimum -> integer, least amount of failed students, 
        last_reset -> List of Dictionaries [{StudentID: String, Course1: String, ...}, {...}]
        )
output: (student_schedules -> Dictionary {osis: [[course_code, (section_id -> String, period_id -> String, schedule -> integer, available_seats -> String)], ...], ...}, 
        class_list ->  List of Dictionaries [{CourseCode: String, SectionID: String, ...}, {...}])
'''
def _create_schedules_r(student_requests):
    minimum = len(student_requests)
    failed_students = []
    for student in student_requests:
        twoArr = (_create_schedule(student))
        counter = 0 # track number of unscheduled kids per problematic request
        while (not twoArr[0]) and (counter < RESET_NUM): # if schedule couldn't be created based on request
            test_students = _list_all_class(twoArr[3][0]) # find students in contested class that should be unscheduled
            if (len(test_students) <= 1): # if no students left to unschedule
                counter = RESET_NUM + 2
                break
            random_student = random.randint(0, len(test_students) - 1) # get random student request to unschedule
            while test_students[random_student] in problem_children: # make sure not to reschedule a schedule known to cause problems
                test_students.pop(random_student)
                if (len(test_students) <= 1):
                    counter = RESET_NUM + 2
                    break
                random_student = random.randint(0, len(test_students) - 1)
            _update_class_list(test_students[random_student], student_schedules[test_students[random_student]], 1) # officialize unschedule by editing class list
            failed_students.append(student_requests_dictionary[test_students[random_student]]) # append unscheduled request to list to reschedule
            twoArr = _create_schedule(student) # retry problematic request
            counter += 1
        if counter >= RESET_NUM and not twoArr[0]: # reset case if a request had more than RESET_NUM requests be unscheduled and still isn't scheduled
            # global problem_children
            problem_children.append(student["StudentID"]) # add unscheduled request's osis to super problematic request list 
            global last_reset
            restart = last_reset.copy()  
            restart.remove(student)
            restart.insert(0, student) # put problematic request at front with the rest of them. 
            last_reset = restart
            for id in student_schedules: # empty student_schedules
                if student_schedules[id]:
                    _update_class_list(id, student_schedules[id], 1)
            for course in class_list: # empty class_list
                if course['students']:
                    course['students'] = []
            return _create_schedules_r(restart)
        # update student_schedules since check_schedule came back correctly
    # recursive case
    if failed_students:
        # in case of (near)impossible request lists, the dictionaries are written to files when a minimum number of failed students is reached 
        if len(failed_students) < minimum:
            minimum = len(failed_students)
            with open(os.path.normpath("temp/schedules.txt"), "w") as f:
                f.write(str(student_schedules))
            with open(os.path.normpath("temp/classes.txt"), "w") as f:
                f.write(str(class_list))
        # recursive call to reschedule unscheduled requests 
        _create_schedules_r(failed_students)
    # recursion complete and schedules and rosters have been generated
    with open(os.path.normpath("temp/schedules.txt"), "w") as f:
        f.write(str(student_schedules))
    with open(os.path.normpath("temp/classes.txt"), "w") as f:
        f.write(str(class_list))
    return(student_schedules, class_list)