from dateutil.parser import parse
from typing import LiteralString
import zipfile
import shutil
import sys
import os
import datetime
import string


def print_message(message: str) -> None:
    """
    Logs a message to the console.

    :param message: The message to be printed
    """
    print(message)


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
    Ensures that the given directory is ready for use by clearing
    its contents if it exists, or creating it otherwise

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

    except Exception as e:
        print_message(f"(-) An error occurred while preparing directory {directory_path}: {e}")


def extract_zip_file(zip_file_path: str, extraction_path: str) -> None:
    """
    Extracts all files from a zip file to a specific directory

    :param zip_file_path: The path of the zip file to be extracted
    :param extraction_path: The path of the directory to extract to
    """
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as target_zip:
            target_zip.extractall(extraction_path)

    except FileNotFoundError:
        print_message(f"(-) Could not find zip file: {zip_file_path}")

    except Exception as e:
        print_message(f"(-) An error occurred during extraction: {e}")
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
    file_name_old_hour_format[3] = file_name_old_hour_format[3][:-2] + ":" + file_name_old_hour_format[3][-2:]

    # Parses the submission's full time value by converting it into a number and removing punctuation from it.
    # Example "Dec 7, 2024 915 PM" -> "2024-12-07 21:15:00" -> "20241207_2115"
    file_name_as_list[2] = str(parse(" ".join(file_name_old_hour_format))).translate(
        str.maketrans('', '', string.punctuation)).replace(" ", "_")[:-2]

    # Renames the current submission name with the newly formated file name
    new_file_name = " - ".join(file_name_as_list)
    os.rename(joiner(student_submission_path, submission_file_name),
              joiner(student_submission_path, new_file_name))


def create_extracted_folder() -> str:
    """
    Creates a folder for all the student submissions.

    :return: The path of the created folder.
    """
    date = datetime.datetime.now()
    directory_name = "StudentSubmissions " + date.strftime("%Y-%m-%d %H-%M-%S")

    try:
        prepare_directory(directory_name)
        print_message(f"(-) Directory '{directory_name}' created successfully.")
        return os.path.abspath(directory_name)

    except PermissionError:
        print_message(f"(-) Permission denied: Unable to create '{directory_name}'.")

    except Exception as e:
        print_message(f"(-) An error occurred: {e}")


def is_most_recent_submission(selected_submission_name: str, student_folder_path: str) -> bool:
    """
    FIXME: Implement this functionality and documentation
    :param selected_submission_name:
    :param student_folder_path:
    :return:
    """
    # for submission_name in os.listdir(student_folder_path):
    #     if submission_name.split(" ")[3] == selected_submission_name.split(" ")[3]:
    #         print_message("")


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
            if is_dir(student_submission_path, file_name) or file_name == "index.html":
                continue
            student_name = (file_name.split(" - ")[1]).split(" ")
            last_name = student_name[len(student_name) - 1]
            first_name = " ".join(student_name[:len(student_name) - 1])
            student_names.append(f"{last_name}, {first_name}")
            alter_file_name_formatting(student_submission_path, file_name, f"{last_name}, {first_name}")

        student_names = list(set(student_names)) # Removes duplicates from name list
        student_names.sort() # Sorts students names alphabetically by last name

        # Makes a named folder for each student
        for name in student_names:
            prepare_directory(joiner(student_submission_path, name))

        # Moves all submitted files to respective folders based on student name
        for file_name in os.listdir(student_submission_path):
            # Skip if file is a folder or is the index.html document
            if is_dir(student_submission_path, file_name) or file_name == "index.html":
                continue
            source_path = joiner(student_submission_path, file_name)
            destination_path = joiner(student_submission_path, file_name.split(" - ")[1])
            shutil.move(source_path, destination_path)

        # FIXME: Add a check/sorter here for multiple student submissions
        for student_folder in os.listdir(student_submission_path):
            if is_dir(student_submission_path, student_folder):
                for submission in os.listdir(joiner(student_submission_path, student_folder)):
                    if is_most_recent_submission(submission, joiner(student_submission_path, student_folder)):
                        break
                # add logic to remove other submissions here

    except IndexError:
        print_message(f"(-) An error occurred while organizing student folders")
        sys.exit(1)

    except Exception as e:
        print_message(f"(-) An error occurred while organizing student folders: {e}")
        sys.exit(1)


def extract_student_subs(student_submission_path: str) -> None:
    """
    Unzips all potential zip files in each named student folder.

    :param student_submission_path: The path of the student submission folder
    """
    try:
        for folder in os.listdir(student_submission_path):
            if folder == "index.html":
                continue
            for file in os.listdir(joiner(student_submission_path, folder)):
                if file.endswith(".zip"):
                    extract_zip_file(joiner(student_submission_path, folder, file),
                                     joiner(student_submission_path, folder))
                    os.remove(joiner(student_submission_path, folder, file))

    except Exception as e:
        print_message(f"(-) An error occurred while extracting student zip files: {e}")
        sys.exit(1)


# Main method

zip_path = input("Enter the path of the zip file: ")
zip_path = zip_path.replace('\\','/')
zip_path = zip_path.replace('"','')

#"C:\Users\roset\OneDrive\Desktop\Project 4 Download Dec 16, 2024 957 PM.zip"
extracted_path = create_extracted_folder()

extract_zip_file(zip_path, str(extracted_path))
create_student_folders(str(extracted_path))
extract_student_subs(str(extracted_path))
