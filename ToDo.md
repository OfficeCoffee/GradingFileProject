# Features to Implement:

- Create a new directory for all the student submissions
  - If a directory has already been made, clear the contents of it so the code won't throw errors

- Open up any zipfiles that the students create

- If a student has submitted multiple files, only take the most recent submission
    - If there are multiple submissions one or two minutes apart, batch and take them all
 
- Correct the name order from Pilot's First/Last syntax to instead be Last/First.

- Parse the file names based on what Pilot generates
  - `Ex: file_name = "271836-442356 - Blake Payne - Dec 5, 2024 1149 AM - CatacombCrawler.zip"`

- Create individual folders named after the individual student's names follwing the format `lastNam_firstName` and move them into the main grading directory

- For each `.java` file, rename the file name and class name to `lastName_firstName_originalFileName.java`

- For each student submission, locate the driver class and rename that class to follow this format `lastName_firstName`

  
