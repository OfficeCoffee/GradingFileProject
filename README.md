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

If this is a first time run, you can run the following:

```bash
git clone 
```

Otherwise, you can run it with `python`. You will give it either the absolute or relative path (if in python script root) to your Pilot download zipfile.

```bash
python Grader.py
Enter the path of the zip file: /home/user/Repos/GradingFileProject/Project 4 Download Aug 1, 2025 900 AM.zip
```
