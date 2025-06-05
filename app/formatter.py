''' format the schedules of each student into csv text
input: student_schedules -> Dictionary {osis: [[course_code, (section_id -> String, period_id -> String, schedule -> integer, available_seats -> String)], ...], ...}
input: student_requests -> List [{'SchoolDbn': String, 'StudentID': String (int), 'LastName': String, 'OffClass': String, 'Course1': String, 'Course2': String, ...}, ...]
output: 2D List
'''
def format_schedules(student_schedules, student_requests):
    studentsTotal = []
    studentHeader = ["LastName","FirstName","StudentId","CounselorName","ofcl","0","1","2","3","4","5","6","7","8","9","10","11","12","13","14"]
    studentsTotal.append(studentHeader)
    for student in student_schedules.keys():
        str1 = [""] * 20
        for req in student_requests: 
            if req["StudentID"] == student:
                str1[0] = req['LastName']
                str1[1] = req['FirstName']
                str1[2] = student
                str1[3] = ""
                str1[4] = req['OffClass']
                break
        for course in student_schedules[student]:
            if type(course[1][1]) == tuple:
                for val in course[1][1]:
                    if str1[int(val) + 5] == "":
                        str1[int(val) + 5] = f"{course[0]}-{course[1][0]}"
                    elif str1[int(val) + 5] == str:
                        str1[int(val) + 5] += f"/{course[0]}-{course[1][0]}"
            else:
                if str1[int(course[1][1]) + 5] == "":
                    str1[int(course[1][1]) + 5] = f"{course[0]}-{course[1][0]}"
                elif str1[int(course[1][1]) + 5] == str:
                    str1[int(course[1][1]) + 5] += f"/{course[0]}-{course[1][0]}"
        studentsTotal.append(str1)
    return (studentsTotal)

''' format the class_rosters of each student into csv text
input: class_list ->  List of Dictionaries [{CourseCode: String, SectionID: String, ...}, {...}]
output: 2D List
'''
def format_classes(class_list):
    fullArr = []
    header = list(class_list[0].keys())
    fullArr.append(header)
    for arr in class_list:
        partArr = list(arr.values())
        fullArr.append(partArr)
    return(fullArr)

''' format the course and section of each student into csv text, with each seat being a new line
input: class_list ->  List of Dictionaries [{CourseCode: String, SectionID: String, ...}, {...}]
input: student_requests -> List [{'SchoolDbn': String, 'StudentID': String (int), 'LastName': String, 'OffClass': String, 'Course1': String, 'Course2': String, ...}, ...]
output: 2D List
'''
def format_seats(student_schedules, student_requests):
    studentsTotal = []
    studentHeader = ['Student ID','Last Name','First Name','Year','Official Class','Course','Section']
    studentsTotal.append(studentHeader)
    for student in student_schedules.keys():
        for course in student_schedules[student]:
            str1 = [""] * 7
            for req in student_requests: 
                if req["StudentID"] == student:
                    str1[0] = student
                    str1[1] = req['LastName']
                    str1[2] = req['FirstName']
                    str1[3] = req['SchoolYear']
                    str1[4] = req['OffClass']
                    str1[5] = course[0]
                    str1[6] = course[1][0]
                    break
            studentsTotal.append(str1)
    return (studentsTotal)