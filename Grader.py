from dateutil.parser import parse
from typing import LiteralString
import zipfile
import shutil
import sys
import os
import datetime

script_log_path = ""


def log(message: str) -> None:
    global script_log_path
    """
    Logs a message to a designated log file.

    :param message: The message to be printed
    """
    with open(script_log_path, 'a') as log_file:
        _ = log_file.write(message + '\n')


def joiner(directory_path: str, *file_names: str) -> LiteralString | str:
    """
    Joins one or more path components to a given directory path.

    :param directory_path: The base directory path to which additional
        paths will be joined.
    :param file_names: Additional path components to be joined with the
        directory_path. These can be one or more path strings.
    :return: A concatenated path string based on the provided inputs. The
        returned path is constructed to be compatible with the host
        operating system's path conventions.
    """
    return os.path.join(directory_path, *file_names)


def is_dir(directory_path: str, *file_name: str) -> bool:
    """
    Determines if the provided path is a directory/folder.

    :param directory_path: The path of the directory as a string.
    :param file_name: The name of the file or directory to check
        within the provided path.
    :return: True if the combined path is a directory, False otherwise.
    """
    return os.path.isdir(joiner(directory_path, *file_name))


def prepare_directory(directory_path: str) -> None:
    """
    Ensures that the given directory is ready for use by clearing its
    contents if it exists, or creating it otherwise

    :param directory_path: Path of the directory to prepare
    """
    try:
        # If the folder exists, the contents will be deleted. Otherwise, it will be created
        if os.path.exists(directory_path):
            if not is_dir(directory_path):
                os.remove(directory_path)
            else:
                shutil.rmtree(directory_path)
        else:
            os.makedirs(directory_path)
        log(f"(+) Prepared directory '{directory_path}'")

    except PermissionError:
        log(f"(-) Permission denied: Unable to create dir '{directory_path}'")
        sys.exit(1)

    except Exception as e:
        log(f"(-) An error occurred while preparing directory '{directory_path}': {e}")


def extract_zip_file(zip_file_path: str, extraction_path: str) -> None:
    """
    Extracts all files from a zip file to a specific directory

    :param zip_file_path: The path of the zip file to be extracted
    :param extraction_path: The path of the directory to extract to
    """
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as target_zip:
            if zip_file_path.__contains__("Download") and (zip_file_path.__contains__("Project")
                                                        or zip_file_path.__contains__("Lab Problem")):
                target_zip.extractall(extraction_path)
                log(f"(+) Contents of '{zip_file_path}' was extracted to '{extraction_path}'")
            else:
                """
                Obtains the timestamp in the file's name by filtering out other information from zip_file_path

                # Replaces any "\\" characters (for Windows users) into "\" for UNIX operating systems
                -> /home/username/GradingFileProject/StudentSubmissions/LastName, FirstName/
                    123456-123456 - LastName, FirstName - TIMESTAMP - filename.zip

                # Splits the path up into its parts based on the "\".
                -> ['home', 'username', 'GradingFileProject', 'StudentSubmissions', 'LastName, FirstName',
                    '123456-123456 - LastName, FirstName - TIMESTAMP - filename.zip']

                # The [-1:] grabs the last item in the list, which is the name of the zipfile.
                # Since we are still in a list, the [0] grabs the zipfile name string.
                -> '123456-123456 - LastName, FirstName - TIMESTAMP - filename.zip'

                # Another split happens with (" - "). The [2] grabs the timestamp part of the zipfile name.
                -> ['123456-123456', 'LastName, FirstName', 'TIMESTAMP', 'filename.zip']
                """
                file_timestamp = zip_file_path.replace('\\', '/').split("/")[-1:][0].split(" - ")[2] + " #0"

                # If there are submissions with the same timestamp, increment a counter so nothing gets replaced
                while is_dir(extraction_path, file_timestamp):
                    file_timestamp_list = file_timestamp.split(" ")
                    submission_counter = file_timestamp_list[2][1]
                    file_timestamp_list[2] = "#" + str(int(submission_counter) + 1)
                    file_timestamp = " ".join(file_timestamp_list)

                # Create a new folder with the submission's timestamp and extract the submission files to this folder
                submissionDirPath = joiner(extraction_path, file_timestamp)
                os.mkdir(submissionDirPath)
                target_zip.extractall(submissionDirPath)
                log(f"(+) Contents of '{zip_file_path}' was extracted to '{submissionDirPath}'")


    except FileNotFoundError:
        log(f"(-) Could not find zip file: '{zip_file_path}'")

    except Exception as e:
        log(f"(-) An error occurred while extracting '{zip_file_path}': {e}")
        sys.exit(1)


def alter_file_name_formatting(student_submission_path: str, submission_file_name: str, last_first_order: str) -> None:
    """
    Changes the name order of students' name and the format of the timestamp in their submission files.

    :param submission_file_name: The current file's name should be formatted
    :param student_submission_path: Path to the directory containing student submissions
    :param last_first_order: The new name order that the submission files should be changed to
    """
    # Changes students name to last/first order from first/last order
    file_name_as_list = submission_file_name.split(" - ")
    file_name_as_list[1] = last_first_order

    # Extracts the numerical time value and add a colon to separate the hour from the minute (915 -> 9:15)
    file_name_old_hour_format = file_name_as_list[2].split(" ")
    file_name_old_hour_format[3] = (
        file_name_old_hour_format[3][:-2] + ":" + file_name_old_hour_format[3][-2:]
    )

    # Parses the submission's full time value by converting it into a number and removing punctuation from it.
    # Example "Dec 7, 2024 915 PM" -> "2024-12-07 21:15:00"
    file_name_as_list[2] = str(parse(" ".join(file_name_old_hour_format)))
    # .translate(str.maketrans('', '', string.punctuation)).replace(" ", "_")[:-2] TODO: move this elsewhere

    # Renames the current submission name with the newly formated file name
    old_file_name_path = joiner(student_submission_path, submission_file_name)
    new_file_name_path = joiner(student_submission_path, " - ".join(file_name_as_list))
    os.rename(old_file_name_path, new_file_name_path)
    log(f"(+) Renamed '{old_file_name_path}' to '{new_file_name_path}'")


def create_extracted_folder(master_zip_name: str) -> str:
    """
    Creates a folder for all the student submissions.

    :return: The path of the created folder.
    """
    date = datetime.datetime.now()

    # If the zip file name has standard Pilot formatting, add the assignment name to the directory
    # Standard Pilot Formatting Example: "Project 3 Download Mar 30, 2025 507 PM.zip"
    if master_zip_name.__contains__("Download") and (master_zip_name.__contains__("Project")
                                                           or master_zip_name.__contains__("Lab Problem")):
        # Extracts the assignment name from the file name by using "Download" as a delimiter
        assignment_name = master_zip_name.split("/")[-1:][0].strip().split("Download")[0]
        directory_name = f"StudentSubmissions {assignment_name}" + date.strftime("%m-%d-%Y %H-%M-%S")
    else :
        # If non-standard formatting is used, a folder with a default name will be created
        directory_name = "StudentSubmissions " + date.strftime("%m-%d-%Y %H-%M-%S")
    try:
        prepare_directory(directory_name)
        return os.path.abspath(directory_name)

    except Exception as e:
        log(f"(-) An error occurred: {e}")
        sys.exit(1)


def create_student_folders(student_submission_path: str) -> None:
    """
    Creates a named folder for each student who submitted. Moves
    all student submissions to their respective named folder.

    :param student_submission_path: The path of the student submission folder
    """
    try:
        student_names = []

        # Generates a list of names of the students who made at least one submission
        for file_name in os.listdir(student_submission_path):
            # Skip if file_name is a folder or is the index.html document
            if is_dir(student_submission_path, file_name) or file_name == "index.html":
                continue
            student_name = (file_name.split(" - ")[1]).split(" ")
            last_name = student_name[len(student_name) - 1]
            first_name = " ".join(student_name[:len(student_name) - 1])
            student_names.append(f"{last_name}, {first_name}")
            alter_file_name_formatting(student_submission_path, file_name, f"{last_name}, {first_name}")

        student_names = list(set(student_names)) # Removes duplicates from name list
        student_names.sort() # Sorts students names alphabetically by last name

        # Make a named folder for each student
        for name in student_names:
            named_dir_path = joiner(student_submission_path, name)
            prepare_directory(named_dir_path)

        # Moves all submitted files to respective folders based on student name
        for file_name in os.listdir(student_submission_path):
            # Skip if file_name is a folder or is the index.html document
            if is_dir(student_submission_path, file_name) or file_name == "index.html":
                continue
            source_path = joiner(student_submission_path, file_name)
            destination_path = joiner(student_submission_path, file_name.split(" - ")[1])
            _ = shutil.move(source_path, destination_path)
            log(f"(+) Moved '{source_path}' to '{destination_path}'")

    except IndexError:
        log("(-) An error occurred while organizing student folders")
        sys.exit(1)

    except Exception as e:
        log(f"(-) An error occurred while organizing student folders: {e}")
        sys.exit(1)


def extract_student_subs(student_submission_path: str) -> None:
    """
    Unzips all potential zip files in each named student folder.

    :param student_submission_path: The path of the student submission folder
    """
    try:
        # Iterate through all student folders containing each of their submissions
        for folder in os.listdir(student_submission_path):
            if folder == "index.html": continue

            # Handle each file submitted by the student from Pilot
            for file in os.listdir(joiner(student_submission_path, folder)):
                currentFile = joiner(student_submission_path, folder, file);

                if file.endswith(".zip"):
                    # Extract all submitted zip files and move extractions to
                    # each student's individual timed submission folder
                    currentStudentDir = joiner(student_submission_path, folder)
                    extract_zip_file(currentFile, currentStudentDir)
                    os.remove(currentFile)
                    log(f"(+) Contents of '{currentFile}' was extracted to '{currentStudentDir}'")

                elif file.endswith(".java") or file.endswith(".md"):
                    # Clean single file submission from Pilot format to regular:
                    # "123-123 - Last, First - TIMESTAMP - Main.java" -> "Main.java"
                    isolated_file_name_path = (
                        joiner(student_submission_path, folder, file.split(" - ")[3]))
                    os.rename(currentFile, isolated_file_name_path)
                    log(
                        f"(+) Submission file '{currentFile}' was renamed to '{isolated_file_name_path}'")

                else:
                    # If not .zip, .java, or .md, then it is not a valid submission
                    log(f"(!) '{currentFile}' is not a valid submission")
                    continue

    except Exception as e:
        log(f"(-) An error occurred while extracting student zip files: {e}")
        sys.exit(1)


def clean_student_subs(student_submission_path: str) -> None:
    """
    Cleans all student submission in each named student folder by removing
    unwanted/unneeded files and directories.

    :param student_submission_path: The path of the student submission folder
    """
    try:
        dir_names_to_delete = ("__MACOSX", "out", "bin", "lib", ".idea", ".vscode", ".DS_Store")

        for dir_path, dir_names, file_names in os.walk(joiner(student_submission_path)):
            # Delete .gitignore files and any files ending in `.iml`
            for file_name in file_names:
                if file_name == ".gitignore" or file_name.endswith(".iml"):
                    try:
                        os.remove(joiner(dir_path, file_name))
                        log(f"(+) Deleted file '{dir_path}/{file_name}'")
                    except Exception as e:
                        log(f"(-) Error deleting file '{dir_path}/{file_name}': {e}")

            # Delete any dirs if they have the name of any dir in dir_names_to_delete
            for dir_name in dir_names:
                if dir_name in dir_names_to_delete:
                    try:
                        shutil.rmtree(joiner(dir_path, dir_name))
                        log(f"(+) Deleted dir '{dir_path}/{dir_name}'")
                    except Exception as e:
                        log(f"(-) Error deleting dir '{dir_path}/{dir_name}': {e}")

    except Exception as e:
        log(f"(-) An error occurred while cleaning student zip files: {e}")
        sys.exit(1)


def main():
    global script_log_path

    zip_path = input("Enter the path of the zip file: ")
    zip_path = zip_path.replace('\\', '').replace('"', '').replace("'", '')

    script_log_path = f"Log {datetime.datetime.now().strftime("%m-%d-%Y %H-%M-%S")}.log"
    open(script_log_path, 'a').close()
    log(f"(+) Log file '{script_log_path}' created successfully")

    try:
        extracted_path = create_extracted_folder(zip_path)
        extract_zip_file(zip_path, str(extracted_path))
        create_student_folders(str(extracted_path))
        extract_student_subs(str(extracted_path))
        clean_student_subs(str(extracted_path))

    except Exception:
        print(f"An error has occured. Please check log file: {script_log_path}")


# Start program
if __name__ == "__main__":
    main()
