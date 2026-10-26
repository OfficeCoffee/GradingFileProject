import argparse
import datetime
import logging
import os
import shutil
import sys
import zipfile
from pathlib import Path

from dateutil.parser import parse

logger = logging.getLogger(__name__)


def relativize(path: Path) -> Path:
    return Path(str(path.relative_to(os.getcwd())).replace(" ", r"\ "))


def prepare_directory(directory_path: Path) -> None:
    """
    Ensures that the given directory is ready for use by clearing its
    contents if it exists, or creating it otherwise

    :param directory_path: Path of the directory to prepare
    """
    try:
        # If the folder exists, the contents will be deleted. Otherwise, it will be created
        if os.path.exists(directory_path):
            if not os.path.isdir(directory_path):
                os.remove(directory_path)
            else:
                shutil.rmtree(directory_path)
        else:
            os.makedirs(directory_path)
        logger.debug(f"Prepared directory '{relativize(directory_path)}'")

    except PermissionError:
        logger.error(
            f"Permission denied: Unable to create dir '{relativize(directory_path)}'"
        )
        sys.exit(-1)

    except Exception as e:
        logger.error(
            f"An error occurred while preparing directory '{relativize(directory_path)}': {e}"
        )


def extract_zip_file(zip_file_path: Path, extraction_path: Path) -> None:
    """
    Extracts all files from a zip file to a specific directory

    :param zip_file_path: The path of the zip file to be extracted
    :param extraction_path: The path of the directory to extract to
    """
    zip_file_name = str(zip_file_path)
    try:
        with zipfile.ZipFile(zip_file_path, "r") as target_zip:
            if "Download" in zip_file_name and (
                "Project" in zip_file_name or "Lab Problem" in zip_file_name
            ):
                target_zip.extractall(extraction_path)
                logger.debug(
                    f"Contents of '{relativize(zip_file_path)}' was extracted to '{relativize(extraction_path)}'"
                )
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
                file_timestamp = (
                    zip_file_name.replace("\\", "/").split("/")[-1:][0].split(" - ")[2]
                    + " #0"
                )

                # If there are submissions with the same timestamp, increment a counter so nothing gets replaced
                while os.path.isdir(extraction_path / file_timestamp):
                    file_timestamp_list = file_timestamp.split(" ")
                    submission_counter = file_timestamp_list[2][1]
                    file_timestamp_list[2] = "#" + str(int(submission_counter) + 1)
                    file_timestamp = " ".join(file_timestamp_list)

                # Create a new folder with the submission's timestamp and extract the submission files to this folder
                submissionDirPath = extraction_path / file_timestamp
                os.mkdir(submissionDirPath)
                target_zip.extractall(submissionDirPath)
                logger.debug(
                    f"Contents of '{relativize(zip_file_path)}' was extracted to '{relativize(submissionDirPath)}'"
                )

    except FileNotFoundError:
        logger.error(f"Could not find zip file: '{relativize(zip_file_path)}'")

    except Exception as e:
        logger.error(
            f"An error occurred while extracting '{relativize(zip_file_path)}': {e}"
        )
        sys.exit(-1)


def create_extracted_folder(master_zip_path: Path) -> Path:
    """
    Creates a folder for all the student submissions in the master zip file.

    :param: The path to the master Pilot zip file containing all submissions.
    :return: The path of the created folder.
    """
    now = datetime.datetime.now().strftime("%m-%d-%Y %H-%M-%S")
    master_zip_name = str(master_zip_path)

    # If the zip file name has standard Pilot formatting, add the assignment name to the directory
    # Standard Pilot Formatting Example: "Project 3 Download Mar 30, 2025 507 PM.zip"
    if "Download" in master_zip_name and (
        "Project" in master_zip_name or "Lab Problem" in master_zip_name
    ):
        # Extracts the assignment name from the file name by using "Download" as a delimiter
        assignment_name = (
            master_zip_name.split("/")[-1:][0].strip().split("Download")[0].strip()
        )
        directory_name = Path(f"Student Submissions {assignment_name} {now}")
    else:
        # If non-standard formatting is used, a folder with a default name will be created
        directory_name = Path(f"Student Submissions {now}")
    try:
        prepare_directory(directory_name)
        return Path.resolve(directory_name)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(-1)


def create_folders_with_student_subs(student_submission_folder_path: Path) -> None:
    """
    Creates a named folder for each student who submitted. Moves
    all student submissions to their respective named folder.

    :param student_submission_path: The path of the student submission folder
    """

    def sanitize_submission_file_name(
        submission_file_path: Path,
        last_first_name_order: str,
    ) -> None:
        """
        Changes the name order of students' name and the format of the timestamp in their submission files.

        Transforms the given `submission_file_name`:

        >>> "123456-654321 - FirstName, LastName - Dec 7, 2024 915 PM - Main.java",

        Into the following for further processing:

        >>> "123456-654321 - LastName, FirstName - 2024-12-07 21:15:00 - Main.java",

        :param submission_file_name: The current file's name should be formatted
        :param student_submission_path: Path to the directory containing student submissions
        :param last_first_name_order: The new name order that the submission files should be changed to
        """
        # Changes students name to last/first order from first/last order
        file_name_as_list = str(submission_file_path).split(" - ")
        file_name_as_list[1] = last_first_name_order

        # Extracts the numerical time value and add a colon to separate the hour from the minute (915 -> 9:15)
        pilot_timestamp: list[str] = file_name_as_list[2].split(" ")
        pilot_timestamp[3] = pilot_timestamp[3][:-2] + ":" + pilot_timestamp[3][-2:]

        # Parses the submission's full time value by converting it into a number and removing punctuation from it.
        # Example "Dec 7, 2024 915 PM" -> "2024-12-07 21:15:00"
        parsed_timestamp = str(parse(" ".join(pilot_timestamp)))
        file_name_as_list[2] = parsed_timestamp

        # Renames the current submission name with the newly formatted file name
        old_file_name_path = student_submission_folder_path / submission_file_path
        new_file_name_path = student_submission_folder_path / " - ".join(
            file_name_as_list
        )
        os.rename(old_file_name_path, new_file_name_path)
        logger.debug(
            f"Renamed '{relativize(old_file_name_path)}' to '{relativize(new_file_name_path)}'"
        )

    def student_submissions_file_paths_list() -> list[Path]:
        student_submission_file_names = []
        for file in os.listdir(student_submission_folder_path):
            # Skip if file_name is a folder or is the index.html document
            if file == "index.html" or (student_submission_folder_path / file).is_dir():
                continue

        return [Path(file) for file in student_submission_file_names]

    try:
        student_names = []

        # Generates a list of names of the students who made at least one submission
        for submission_file_path in student_submissions_file_paths_list():
            first_last_name_list: list[str] = (
                str(submission_file_path).split(" - ")[1].split(" ")
            )
            last_name = first_last_name_list[len(first_last_name_list) - 1]
            first_name = " ".join(first_last_name_list[: len(first_last_name_list) - 1])
            last_first_name_order = f"{last_name}, {first_name}"
            student_names.append(last_first_name_order)

            sanitize_submission_file_name(submission_file_path, last_first_name_order)

        # Removes duplicates from name list and sort alphabetically by last name
        student_names = list(set(student_names))
        student_names.sort()

        # Make a named folder for each student
        for name in student_names:
            prepare_directory(student_submission_folder_path / name)

        # Moves all submitted files to respective folders based on student name
        for submission_file_path in student_submissions_file_paths_list():
            source_path = student_submission_folder_path / submission_file_path
            destination_path = (
                student_submission_folder_path
                / str(submission_file_path).split(" - ")[1]
            )
            _ = shutil.move(source_path, destination_path)
            logger.debug(
                f"Moved '{relativize(source_path)}' to '{relativize(destination_path)}'"
            )

    except IndexError:
        logger.error("An error occurred while organizing student folders")
        sys.exit(-1)

    except Exception as e:
        logger.error(f"An error occurred while organizing student folders: {e}")
        sys.exit(-1)


def process_submissions_in_student_folders(student_submission_path: Path) -> None:
    """
    Unzips all potential zip files in each named student folder.

    :param student_submission_path: The path of the student submission folder
    """
    try:
        # Iterate through all student folders containing each of their submissions
        for folder in [
            entry
            for entry in os.listdir(student_submission_path)
            if Path(entry).is_dir()
        ]:
            # Handle each file submitted by the student from Pilot
            for file in os.listdir(student_submission_path / folder):
                student_submission_file = student_submission_path / folder / file

                if file.endswith(".zip"):
                    # Extract all submitted zip files and move extractions to
                    # each student's individual timed submission folder
                    current_student_dir = student_submission_path / folder
                    extract_zip_file(student_submission_file, current_student_dir)
                    os.remove(student_submission_file)
                    logger.debug(
                        f"Contents of '{relativize(student_submission_file)}' was extracted to '{relativize(current_student_dir)}'"
                    )

                elif file.endswith((".java", ".md")):
                    # Clean single file submission from Pilot format to regular:
                    # "123456-654321 - LastName, FirstName - TIMESTAMP - Main.java" -> "Main.java"
                    actual_file_name = (
                        student_submission_path / folder / file.split(" - ")[3]
                    )
                    os.rename(student_submission_file, actual_file_name)
                    logger.debug(
                        f"Submission file '{relativize(student_submission_file)}' was renamed to '{relativize(actual_file_name)}'"
                    )

                else:
                    # If not .zip, .java, or .md, then it is not a valid submission
                    logger.warning(
                        f"'{relativize(student_submission_file)}' is not a valid submission"
                    )
                    continue

    except Exception as e:
        logger.error(f"An error occurred while extracting student zip files: {e}")
        sys.exit(-1)


def clean_student_subs(student_submission_path: Path) -> None:
    """
    Cleans all student submission in each named student folder by removing
    unwanted/unneeded files and directories.

    :param student_submission_path: The path of the student submission folder
    """
    try:
        dir_names_to_delete = (
            "__MACOSX",
            "out",
            "bin",
            "lib",
            ".idea",
            ".vscode",
            ".DS_Store",
        )

        for dir_path, dir_names, file_names in os.walk(student_submission_path):
            # Delete .gitignore files and any files ending in `.iml`
            for file_name in file_names:
                if file_name == ".gitignore" or file_name.endswith(".iml"):
                    try:
                        file_path_to_delete = Path(dir_path, file_name)
                        os.remove(file_path_to_delete)
                        logger.debug(
                            f"Deleted file '{relativize(file_path_to_delete)}'"
                        )
                    except Exception as e:
                        logger.error(
                            f"Error deleting file '{relativize(file_path_to_delete)}': {e}"
                        )

            # Delete any dirs if they have the name of any dir in dir_names_to_delete
            for dir_name in dir_names:
                if dir_name in dir_names_to_delete:
                    try:
                        dir_path_to_delete = Path(dir_path, dir_name)
                        shutil.rmtree(dir_path_to_delete)
                        logger.debug(f"Deleted dir '{relativize(dir_path_to_delete)}'")
                    except Exception as e:
                        logger.error(
                            f"Error deleting dir '{relativize(dir_path_to_delete)}': {e}"
                        )

    except Exception as e:
        logger.error(f"An error occurred while cleaning student zip files: {e}")
        sys.exit(-1)


def extract_all_from_zip(zip_path: Path) -> None:
    extracted_path = create_extracted_folder(zip_path)
    extract_zip_file(zip_path, extracted_path)
    create_folders_with_student_subs(extracted_path)
    process_submissions_in_student_folders(extracted_path)
    clean_student_subs(extracted_path)
    logger.info(
        f"Master zip file: '{relativize(extracted_path)}' organized successfully"
    )


def main():
    parser = argparse.ArgumentParser(
        prog="GradingScript",
        description="Script to help automate grading process",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument(
        "zip_file_path", type=Path, help="Did you wrap the path in quotes?"
    )
    args = parser.parse_args()

    log_file_path = f"{datetime.datetime.now().strftime('%H:%M:%S_%m-%d-%y')}.log"
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.ERROR,
        format='[%(levelname)s] %(funcName)s(): "%(message)s"',
        filename=log_file_path if args.verbose else None,
    )

    if not Path.exists(args.zip_file_path) or args.zip_file_path.suffix != ".zip":
        logger.error(f"Given path is not a valid zip file: {args.zip_file_path}")
        sys.exit(-1)

    try:
        extract_all_from_zip(args.zip_file_path)
    except Exception:
        print(f"An error has occurred. Please check log file: {log_file_path}")
