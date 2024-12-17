from typing import LiteralString
import zipfile
import shutil
import sys
import os

# better testing comment

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


def is_dir(directory_path: str, file_name: str) -> bool:
    """
    Determines if the provided path is a directory/folder.

    :param directory_path: The path of the directory as a string.
    :param file_name: The name of the file or directory to check
        within the provided path.
    :return: True if the combined path is a directory, False otherwise.
    """
    return os.path.isdir(joiner(directory_path, file_name))


def prepare_directory(directory_path: str) -> None:
    """
    Ensures that the given directory is ready for use by clearing
    its contents if it exists, or creating it otherwise

    :param directory_path: Path of the directory to prepare
    """
    # If the folder exists, the contents will be deleted. Otherwise, it will be created
    if os.path.exists(directory_path):
        for file_name in os.listdir(directory_path):
            # If a given item is a folder, its contents will be deleted. Otherwise, the file is deleted
            if is_dir(directory_path, file_name):
                for nested_file_name in os.listdir(joiner(directory_path, file_name)):
                    os.remove(joiner(directory_path, file_name, nested_file_name))
            else:
                os.remove(joiner(directory_path, file_name))
    else:
        os.makedirs(directory_path)


def extract_zip_file(zip_file_path: str, extraction_path: str) -> None:
    """
    Extracts all files from a zip file to a specific directory

    :param zip_file_path: The path of the zip file to be extracted
    :param extraction_path: The path of the directory to extract to
    """
    # Ensures directory is created or cleared of its contents
    prepare_directory(extraction_path)

    # Extracts all files to a specified folder
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as target_zip:
            target_zip.extractall(extraction_path)
        print_message(f"Files extracted to {extraction_path}")
    except FileNotFoundError:
        print_message("Zip file not found")
    except Exception as e:
        print_message(f"An error occurred during extraction: {e}")
        sys.exit(1)


def alter_name_order(student_submission_path: str, first_last_order: str, last_first_order: str) -> None:
    """
    Changes the name order of students' name in their submission files.

    :param student_submission_path: Path to the directory containing student submissions
    :param first_last_order: The old name order that needs to be changed
    :param last_first_order: The new name order that the submission files should be changed to
    """
    # Finds the target submission to change
    index_counter = 0
    all_subs = os.listdir(student_submission_path)
    for sub in all_subs:
        if sub.split(" - ")[1] == first_last_order:
            break
        index_counter += 1
    # Changes students name to last/first order from first/last order
    file_as_list = all_subs[index_counter].split(" - ")
    file_as_list[1] = last_first_order
    new_file_name = " - ".join(file_as_list)
    os.rename(joiner(student_submission_path, all_subs[index_counter]),
              joiner(student_submission_path, new_file_name))


def create_student_folders(student_submission_path: str) -> None:
    """
    Creates a named folder for each student who submitted. Moves
    all student submissions to their respective named folder.

    :param student_submission_path: The path of the student submission folder
    """
    try:
        # Generates a list of names of the students who made at least one submission
        student_names = []
        for file_name in os.listdir(student_submission_path):
            if is_dir(student_submission_path, file_name) or file_name == "index.html":
                continue
            student_name = (file_name.split(" - ")[1]).split(" ")
            last_name = student_name[len(student_name) - 1]
            first_name = " ".join(student_name[:len(student_name) - 1])
            student_names.append(f"{last_name}, {first_name}")
            alter_name_order(student_submission_path,
                             f"{first_name} {last_name}", f"{last_name}, {first_name}")

        student_names.sort()  # Sorts students names alphabetically by last name

        # Removes duplicates from name list and makes a named folder for each student
        for name in student_names:
            if student_names.count(name) > 1:
                for i in range(student_names.count(name) - 1):
                    student_names.remove(name)
            prepare_directory(joiner(student_submission_path, name))

        # Moves all submitted files to respective folders based on student name
        for file_name in os.listdir(student_submission_path):
            # Skip if file is a folder or is the index.html document
            if is_dir(student_submission_path, file_name) or file_name == "index.html":
                continue
            source_path = joiner(student_submission_path, file_name)
            destination_path = joiner(student_submission_path, file_name.split(" - ")[1])
            shutil.move(source_path, destination_path)

    except IndexError:
        print_message(f"An error occurred while organizing student folders")
        sys.exit(1)

    except Exception as e:
        print_message(f"An error occurred while organizing student folders: {e}")
        sys.exit(1)


# Main method

zip_path = ".\\Project 4 Download Dec 14, 2024 827 PM.zip"
extracted_path = ".\\Student Submissions\\"

extract_zip_file(zip_path, extracted_path)
create_student_folders(extracted_path)
