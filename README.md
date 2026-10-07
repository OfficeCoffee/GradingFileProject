# Grading Optimizer Script

## What does it do?

1. Takes in master zip file from Pilot and unzips it to a master dir
2. Creates a folder for each student who made a submission for that assignment
3. Moves all student submissions to their named folder. Changes naming from Pilot's formatting of first/last name to last/first name
4. Unzips their zips (if applicable) and scrubs file names of any Pilot formatting
5. Removes junk files/dirs from student folders (`out`, `bin`, `lib`, `__MACOSX`, `.idea`, etc.)

## Who is this for?

TAs and faculty. Mainly used to take out the manual labor unzipping, moving, and renaming files. Allows for a "bird's-eye" of all student submission for a given assignment. 

## How do I run this?

> [!NOTE]
> There is a known issue that passing in the path to your zip file on a windows machine will not work. See GH-25. Consider using WSL or a UNIX-based operating system to use this script. 

If this is a first time run, clone the repo:

```bash
$ git clone https://github.com/OfficeCoffee/GradingFileProject.git && cd GradingFileProject
```

The script can be run in the terminal with `python` or `python3`.

## Path given after script execution

```bash
$ python -m grading_script
Enter the path of the zip file: /home/user/Repos/GradingFileProject/Project 4 Download Aug 1, 2025 900 AM.zip
```

## Path given before script execution

```bash
$ python -m grading_script <path-to-master-zip-file>
```

You can give it either the absolute or relative path (if current working directory is root of project) to your Pilot download zip file. If you change the name of the zip from how Pilot formats it, you may run into an error.

## I got an error, what do I do?

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
