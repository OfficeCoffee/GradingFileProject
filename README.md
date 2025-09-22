# Grading Optimizier Script 

### What does it do? 

1. Takes in master zip file from Pilot and unzips it to a master dir
2. Creates a folder for each student who made a submission for that assignment
3. Moves all student submissions to their named folder. Changes naming from Pilot's formatting of first/last name to last/first name
4. Unzips their zips (if applicable) and scrubs file names of any Pilot formatting 
5. Removes junk files/dirs from student folders (`out`, `__MACOSX`, `.idea`, etc.)

### Who is this for? 

TAs and faculity. Mainly used to take out the manual labor unzipping, moving, and renaming files. 

### How do I run this? 

If this is a first time run, you can download the script or clone the repo:

```bash
git clone https://github.com/OfficeCoffee/GradingFileProject.git && cd GradingFileProject
```

The script can be run in the terminal with `python`. 

```bash
python Grader.py
```

You can give it either the absolute or relative path (if in python script root) to your Pilot download zipfile. If you change the name of the zip from how Pilot formats it, you may run into an error. 

```bash
Enter the path of the zip file: /home/user/Repos/GradingFileProject/Project 4 Download Aug 1, 2025 900 AM.zip
```

### I got an error, what do I do? 

1. Check to make sure that the name of the master zip file was unchanged from when you downloaded it from Pilot.
```bash
// This will not work
Enter the path of the zip file: /home/user/Repos/GradingFileProject/Submissions.zip

// This will work
Enter the path of the zip file: /home/user/Repos/GradingFileProject/Project 4 Download Aug 1, 2025 900 AM.zip
```

2. Reach out to us. Try to include as much information as possible in your message/email (screenshot of current directory, contents of student submissions folder, log file contents, error message(s), and anything else you think would be useful for us to know).

> [!CAUTION]
> DO NOT MAKE ANY STUDENT INFORMATION PUBLIC ON GITHUB OR ELSEWHERE. 


