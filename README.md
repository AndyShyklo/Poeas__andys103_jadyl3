# Scheduling Engine by Poeas

## Roster
Andy: (PM)
- Coding to specification of Mr. Dillon
- Modifying existing code to accommodate for schedule inflexibility
- Debugging and special cases

Jady:
- Coding to specification of Mr. Dillon
- Creating schedule creation and recursive functions
- Manage overall data structure


## Description

“In this project, developers will write an algorithm that places students into course sections (aka a scheduling engine) based on the students need to graduate (requirements) and want to take (electives). Students will work with Mr. Dillon using anonymized Stuyvesant data. You'll learn some of the intricacies of the Program Offices/Registrar. This is not a feature that Talos currently has and would be used to  more effectively program students.” (Dillon, April 29th via DTM Piazza)

## Install Guide

**Prerequisites**

Ensure that **Git** is installed on your machine. For help, refer to the following documentation: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

### How to clone/install
1. In terminal, clone the repository to your local machine:

HTTPS METHOD:

```
git clone https://github.com/AndyShyklo/Poeas__andys103_jadyl3.git
```

SSH METHOD (requires an SSH key):

```
git clone git@github.com:AndyShyklo/Poeas__andys103_jadyl3.git
```

## Launch Codes

**Prerequisites**

Ensure that **Git** and **Python** are installed on your machine. It is recommended that you use a virtual machine when running this project to avoid any possible conflicts. For help, refer to the following documentation:
   1. Installing Git: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
   2. Installing Python: https://www.python.org/downloads/

### Usage Directions

1. Clone repo, please see [Install Guide](#install-guide)

2. Navigate to project directory
```
cd PATH/TO/Poeas__andys103_jadyl3
```
3. Run \_\_init\_\_.py  
```
 python3 __init__.py
```
optionally with two elements
```
 python3 __init__.py <student_request_file_name> <master_schedule_file_name>
```
These files should be csvs and placed into the data/ folder.  

4. Allow program to run until "Program Complete." displays and the completed rosters and schedules will be written into the final.  

5. Check and query rosters.csv and schedules.csv
