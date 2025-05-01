import csv

STUDENT_REQUEST_FILE = "student_req.csv"
CLASSES_FILE = "classes.csv"
NUM_OF_REQUESTED_CLASSES = 9
student_requests = []
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
def returnListofAvailability(student_request, course_info):
    availability = []
    for i in range(1, NUM_OF_REQUESTED_CLASSES + 1):
        classcode = student_request["Course"+str(i)]
        availablePds = []
        for course in course_info:
            if course["CourseCode"] == classcode:
                if int(course["Remaining Capacity"]) > 0:
                    availablePds.append(course["PeriodID"])
        availability.append(availablePds)
    return availability

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

#wrapper function
def checkSchedule(availability):
    return checkScheduleR(availability, 0, "", False)

#recursively check available periods
def checkScheduleR(availability, current_class, schedule_so_far, working):
    if (current_class > 0) and (schedule_so_far.find(schedule_so_far[-1]) != len(schedule_so_far) - 1):
        return False
    if current_class >= len(availability):
        # print(schedule_so_far)
        return True
    for i in range(len(availability[current_class])):
        pd = availability[current_class][i]
        working = working or checkScheduleR(availability, current_class+1, schedule_so_far+str(pd), False)
    return working

# test recursion function
# print(checkSchedule([[1], [1]]))

# prints
def findImpossibleSchedules():
    for student in student_requests:
        availability = returnListofAvailability(student, class_list)
        print(availability)
        # checkSchedule(availability)

# findImpossibleSchedules()

# finds list of all classes and periods
def findImpossibleSchedulesStudent(student_id):
    for student in student_requests:
        if student_id == student['StudentID']:
            availability = returnListofAvailabilityDict(student, class_list)
            print(availability)
            # checkSchedule(availability)

# findImpossibleSchedulesStudent('100635729')

# finds a potential schedule using existing period availability. framework for future algorithm
def findPossibleSchedule(student_id):
    for student in student_requests:
        if student_id == student['StudentID']:
            classes = {'1': "None", '2': "None", '3': "None", '4': "None", '5': "None", '6': "None", '7': "None", '8': "None", '9': "None", '10': "None"}
            availability = returnListofAvailabilityDict(student, class_list)
            for key, item in availability.items():
                for pd in item:
                    if classes[pd] == "None":
                        classes[pd] = key
                        break
            return(classes)

print(findPossibleSchedule('100635729'))
