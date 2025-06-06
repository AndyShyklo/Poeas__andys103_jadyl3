import sys # used to handle command line arguments and unix/windows differences
import os # Handle file path differences.

#Custom Modules:
from helper import *
from formatter import *

# default files for unix/windows
STUDENT_REQUEST_FILE = os.path.normpath("data/StudentRequest-Sample2.csv")
CLASSES_FILE = os.path.normpath("data/MasterSchedule.csv")

# output file paths for unix/windows
SCHEDULES_OUTPUT_FILE = os.path.normpath("final/schedules.csv")
ROSTER_OUTPUT_FILE = os.path.normpath("final/rosters.csv")
SEATS_OUTPUT_FILE = os.path.normpath("final/seats.csv")

# command line inputs
if len(sys.argv) == 2:
    STUDENT_REQUEST_FILE = os.path.normpath(f"data/{sys.argv[0]}")
    CLASSES_FILE = os.path.normpath(f"data/{sys.argv[1]}")

'''main function
input: No args
output: (csvTextOfSchedules -> String, csvTextOfRoster -> String, csvTextOfSeats -> String)
'''
def main():
    # using internal functions from module to parse csv files
    student_requests = get_student_requests(STUDENT_REQUEST_FILE)
    class_list = get_class_list(CLASSES_FILE)

    # find courses with only one section to sort the student_request_list which acts as the initial queue of requests
    singletons = get_singletons(class_list)
    student_request_list = sort_requests(student_requests[0], singletons)
    student_request_dictionary = student_requests[1]

    result = create_schedules(student_request_list, class_list, student_request_dictionary)
    
    formatted_schedules = format_schedules(result[0], student_request_list)
    formatted_class_roster = format_classes(result[1])
    formatted_seats = format_seats(result[0], student_request_list)
    return(formatted_schedules, formatted_class_roster, formatted_seats)

# run function
result = main()

# Generated schedules and class rosters are written to files.
# Fulfills task 2 of formatting
with open(SCHEDULES_OUTPUT_FILE, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for arr in result[0]:
        writer.writerow(arr)
with open(ROSTER_OUTPUT_FILE, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for arr in result[1]:
        writer.writerow(arr)
# Fulfills task 1 of formatting
with open(SEATS_OUTPUT_FILE, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for arr in result[2]:
        writer.writerow(arr)

# Notify user of program completion
print("Program Complete.")