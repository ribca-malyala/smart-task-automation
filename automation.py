from pathlib import Path
from datetime import datetime
import hashlib
import shutil

from config import (
    TEST_FOLDER,
    LOG_FILE,
    REPORT_FILE,
    FILE_CATEGORIES,
    DUPLICATES_FOLDER
)


# --------------------------------------------------
# GET FILE CATEGORY
# --------------------------------------------------

def get_category(file):

    extension = file.suffix.lower()

    for category, extensions in FILE_CATEGORIES.items():

        if extension in extensions:
            return category

    return "Others"


# --------------------------------------------------
# CALCULATE FILE HASH
# --------------------------------------------------

def calculate_hash(file):

    sha256 = hashlib.sha256()

    try:

        with open(file, "rb") as f:

            while chunk := f.read(4096):
                sha256.update(chunk)

        return sha256.hexdigest()

    except Exception:

        return None


# --------------------------------------------------
# FORMAT FILE SIZE
# --------------------------------------------------

def format_size(size_bytes):

    if size_bytes < 1024:

        return f"{size_bytes} B"

    elif size_bytes < 1024 ** 2:

        return f"{size_bytes / 1024:.2f} KB"

    elif size_bytes < 1024 ** 3:

        return f"{size_bytes / (1024 ** 2):.2f} MB"

    else:

        return f"{size_bytes / (1024 ** 3):.2f} GB"


# --------------------------------------------------
# WRITE LOG
# --------------------------------------------------

def write_log(message):

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as log:

        log.write(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"{message}\n"
        )


# --------------------------------------------------
# WRITE AUTOMATION SUMMARY TO LOG
# --------------------------------------------------

def write_run_summary(
    organized_count,
    duplicate_count,
    duplicates_moved,
    total_storage
):

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as log:

        log.write("\n")
        log.write("=" * 50 + "\n")
        log.write("AUTOMATION RUN SUMMARY\n")
        log.write("=" * 50 + "\n")

        log.write(
            f"Date: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        log.write(
            f"Files organized: "
            f"{organized_count}\n"
        )

        log.write(
            f"Duplicates found: "
            f"{duplicate_count}\n"
        )

        log.write(
            f"Duplicates moved: "
            f"{duplicates_moved}\n"
        )

        log.write(
            f"Total storage: "
            f"{format_size(total_storage)}\n"
        )

        log.write("Status: SUCCESS\n")

        log.write("=" * 50 + "\n")


# --------------------------------------------------
# GET CURRENT DASHBOARD DATA
# --------------------------------------------------

def get_dashboard_data():

    categories = (
        list(FILE_CATEGORIES.keys())
        + ["Others"]
    )

    category_counts = {}
    category_sizes = {}

    for category in categories:

        folder = TEST_FOLDER / category

        if not folder.exists():

            category_counts[category] = 0
            category_sizes[category] = 0

            continue

        files = [
            file
            for file in folder.iterdir()
            if file.is_file()
        ]

        category_counts[category] = len(files)

        total_size = 0

        for file in files:

            try:

                total_size += file.stat().st_size

            except OSError:

                pass

        category_sizes[category] = total_size

    # --------------------------------------------------
    # COUNT DUPLICATE FILES
    # --------------------------------------------------

    duplicate_count = 0

    if DUPLICATES_FOLDER.exists():

        duplicate_count = sum(
            1
            for file in DUPLICATES_FOLDER.iterdir()
            if file.is_file()
        )

    total_files = sum(
        category_counts.values()
    )

    total_storage = sum(
        category_sizes.values()
    )

    return (
        category_counts,
        category_sizes,
        duplicate_count,
        total_files,
        total_storage
    )


# --------------------------------------------------
# GET FILE TYPE SUMMARY
# --------------------------------------------------

def get_file_type_summary():

    file_type_counts = {}

    categories = (
        list(FILE_CATEGORIES.keys())
        + ["Others"]
    )

    for category in categories:

        folder = TEST_FOLDER / category

        if not folder.exists():
            continue

        for file in folder.iterdir():

            if not file.is_file():
                continue

            extension = file.suffix.lower()

            if extension:

                if extension in file_type_counts:

                    file_type_counts[extension] += 1

                else:

                    file_type_counts[extension] = 1

            else:

                if "No Extension" in file_type_counts:

                    file_type_counts["No Extension"] += 1

                else:

                    file_type_counts["No Extension"] = 1

    return file_type_counts


# --------------------------------------------------
# GET RECENT AUTOMATION ACTIVITY
# --------------------------------------------------

def get_recent_activity():

    activity = {
        "Last Run": "No previous run",
        "Files Organized": "0",
        "Duplicates Found": "0",
        "Duplicates Moved": "0",
        "Status": "NOT RUN"
    }

    if not LOG_FILE.exists():

        return activity

    try:

        with open(
            LOG_FILE,
            "r",
            encoding="utf-8"
        ) as log:

            content = log.read()

        summaries = content.split(
            "AUTOMATION RUN SUMMARY"
        )

        if len(summaries) <= 1:

            return activity

        latest_summary = summaries[-1]

        lines = latest_summary.splitlines()

        for line in lines:

            if line.startswith("Date:"):

                activity["Last Run"] = (
                    line.replace(
                        "Date:",
                        ""
                    ).strip()
                )

            elif line.startswith(
                "Files organized:"
            ):

                activity["Files Organized"] = (
                    line.replace(
                        "Files organized:",
                        ""
                    ).strip()
                )

            elif line.startswith(
                "Duplicates found:"
            ):

                activity["Duplicates Found"] = (
                    line.replace(
                        "Duplicates found:",
                        ""
                    ).strip()
                )

            elif line.startswith(
                "Duplicates moved:"
            ):

                activity["Duplicates Moved"] = (
                    line.replace(
                        "Duplicates moved:",
                        ""
                    ).strip()
                )

            elif line.startswith("Status:"):

                activity["Status"] = (
                    line.replace(
                        "Status:",
                        ""
                    ).strip()
                )

    except Exception:

        pass

    return activity


# --------------------------------------------------
# GET AUTOMATION HISTORY
# --------------------------------------------------

def get_automation_history():

    history = []

    if not LOG_FILE.exists():

        return history

    try:

        with open(
            LOG_FILE,
            "r",
            encoding="utf-8"
        ) as log:

            content = log.read()

        summaries = content.split(
            "AUTOMATION RUN SUMMARY"
        )

        for summary in summaries[1:]:

            date = "Unknown"
            organized = "0"
            duplicates = "0"

            lines = summary.splitlines()

            for line in lines:

                if line.startswith("Date:"):

                    date = line.replace(
                        "Date:",
                        ""
                    ).strip()

                elif line.startswith(
                    "Files organized:"
                ):

                    organized = line.replace(
                        "Files organized:",
                        ""
                    ).strip()

                elif line.startswith(
                    "Duplicates found:"
                ):

                    duplicates = line.replace(
                        "Duplicates found:",
                        ""
                    ).strip()

            history.append({
                "Date": date,
                "Organized": organized,
                "Duplicates": duplicates
            })

    except Exception:

        pass

    return history


# --------------------------------------------------
# VIEW AUTOMATION DASHBOARD
# --------------------------------------------------

def show_dashboard():

    print("\n" + "=" * 50)
    print("        AUTOMATION DASHBOARD")
    print("=" * 50)

    if not TEST_FOLDER.exists():

        print("\nTest folder does not exist.")

        return

    (
        category_counts,
        category_sizes,
        duplicate_count,
        total_files,
        total_storage
    ) = get_dashboard_data()

    # --------------------------------------------------
    # FILE SUMMARY
    # --------------------------------------------------

    print("\nFILE SUMMARY")
    print("-" * 50)

    for category, count in category_counts.items():

        print(
            f"{category:<20}: "
            f"{count}"
        )

    print(
        f"{'Duplicates':<20}: "
        f"{duplicate_count}"
    )

    print(
        f"{'Total Active Files':<20}: "
        f"{total_files}"
    )

    # --------------------------------------------------
    # FILE TYPE SUMMARY
    # --------------------------------------------------

    file_type_counts = get_file_type_summary()

    print("\nFILE TYPE SUMMARY")
    print("-" * 50)

    if file_type_counts:

        for extension, count in sorted(
            file_type_counts.items()
        ):

            print(
                f"{extension:<20}: "
                f"{count}"
            )

        print("-" * 50)

        print(
            f"{'Total File Types':<20}: "
            f"{len(file_type_counts)}"
        )

    else:

        print("No active files found.")

    # --------------------------------------------------
    # STORAGE SUMMARY
    # --------------------------------------------------

    print("\nSTORAGE SUMMARY")
    print("-" * 50)

    for category, size in category_sizes.items():

        print(
            f"{category:<20}: "
            f"{format_size(size)}"
        )

    print("-" * 50)

    print(
        f"{'Total Storage':<20}: "
        f"{format_size(total_storage)}"
    )

    # --------------------------------------------------
    # RECENT ACTIVITY
    # --------------------------------------------------

    recent_activity = get_recent_activity()

    print("\nRECENT ACTIVITY")
    print("-" * 50)

    print(
        f"{'Last Run':<20}: "
        f"{recent_activity['Last Run']}"
    )

    print(
        f"{'Files Organized':<20}: "
        f"{recent_activity['Files Organized']}"
    )

    print(
        f"{'Duplicates Found':<20}: "
        f"{recent_activity['Duplicates Found']}"
    )

    print(
        f"{'Duplicates Moved':<20}: "
        f"{recent_activity['Duplicates Moved']}"
    )

    print(
        f"{'Status':<20}: "
        f"{recent_activity['Status']}"
    )

    print("-" * 50)

    # --------------------------------------------------
    # AUTOMATION HISTORY
    # --------------------------------------------------

    history = get_automation_history()

    print("\nAUTOMATION HISTORY")
    print("-" * 50)

    if history:

        for index, run in enumerate(
            history,
            start=1
        ):

            print(
                f"Run {index} | "
                f"{run['Date']} | "
                f"Organized: {run['Organized']} | "
                f"Duplicates: {run['Duplicates']}"
            )

        print("-" * 50)

        print(
            f"{'Total Runs':<20}: "
            f"{len(history)}"
        )

    else:

        print("No automation history available.")

    # --------------------------------------------------
    # SYSTEM STATUS
    # --------------------------------------------------

    print("\nSYSTEM STATUS")
    print("-" * 50)

    print(
        f"{'Automation Status':<20}: "
        f"READY"
    )

    print(
        f"{'Report File':<20}: "
        f"{REPORT_FILE}"
    )

    print(
        f"{'Log File':<20}: "
        f"{LOG_FILE}"
    )

    print("\n" + "=" * 50)


# --------------------------------------------------
# MAIN AUTOMATION
# --------------------------------------------------

def run_automation():

    print("\n" + "=" * 50)
    print("        SMART TASK AUTOMATION")
    print("=" * 50)

    write_log(
        "Automation started."
    )

    if not TEST_FOLDER.exists():

        print(
            "\nTest folder does not exist."
        )

        write_log(
            "ERROR: Test folder does not exist."
        )

        return

    # --------------------------------------------------
    # CREATE CATEGORY FOLDERS
    # --------------------------------------------------

    for category in FILE_CATEGORIES:

        (
            TEST_FOLDER / category
        ).mkdir(
            exist_ok=True
        )

    (
        TEST_FOLDER / "Others"
    ).mkdir(
        exist_ok=True
    )

    DUPLICATES_FOLDER.mkdir(
        exist_ok=True
    )

    # --------------------------------------------------
    # ORGANIZE FILES
    # --------------------------------------------------

    organized_count = 0

    files_to_organize = [
        file
        for file in TEST_FOLDER.iterdir()
        if file.is_file()
    ]

    if not files_to_organize:

        print(
            "\nNo new files to organize."
        )

    else:

        print("\n" + "=" * 50)
        print("        FILE ORGANIZATION")
        print("=" * 50)

        for file in files_to_organize:

            category = get_category(file)

            destination_folder = (
                TEST_FOLDER / category
            )

            destination = (
                destination_folder / file.name
            )

            try:

                shutil.move(
                    str(file),
                    str(destination)
                )

                organized_count += 1

                print(
                    f"\nMoved: "
                    f"{file.name} → {category}"
                )

                write_log(
                    f"Moved {file.name} "
                    f"to {category} folder."
                )

            except Exception as e:

                print(
                    f"\nCould not move "
                    f"{file.name}: {e}"
                )

                write_log(
                    f"ERROR moving "
                    f"{file.name}: {e}"
                )

    # --------------------------------------------------
    # DUPLICATE DETECTION
    # --------------------------------------------------

    print("\n" + "=" * 50)
    print("        DUPLICATE FILE DETECTION")
    print("=" * 50)

    file_hashes = {}

    duplicate_count = 0
    duplicates_moved = 0

    duplicate_details = []

    all_files = [
        file
        for file in TEST_FOLDER.rglob("*")
        if file.is_file()
        and DUPLICATES_FOLDER not in file.parents
    ]

    for file in all_files:

        file_hash = calculate_hash(file)

        if file_hash is None:

            continue

        if file_hash in file_hashes:

            original_file = file_hashes[file_hash]

            duplicate_count += 1

            destination = (
                DUPLICATES_FOLDER /
                file.name
            )

            counter = 1

            while destination.exists():

                destination = (
                    DUPLICATES_FOLDER /
                    f"{file.stem}_{counter}"
                    f"{file.suffix}"
                )

                counter += 1

            try:

                shutil.move(
                    str(file),
                    str(destination)
                )

                duplicates_moved += 1

                duplicate_details.append(
                    f"{file.name} → "
                    f"duplicate of "
                    f"{original_file.name}"
                )

                print(
                    f"\nDuplicate moved: "
                    f"{file.name}"
                )

                write_log(
                    f"Duplicate moved: "
                    f"{file.name}"
                )

            except Exception as e:

                print(
                    f"\nCould not move "
                    f"duplicate {file.name}: {e}"
                )

                write_log(
                    f"ERROR moving duplicate "
                    f"{file.name}: {e}"
                )

        else:

            file_hashes[file_hash] = file

    if duplicate_count == 0:

        print(
            "\nNo duplicate files found."
        )

    # --------------------------------------------------
    # CATEGORY STATISTICS
    # --------------------------------------------------

    categories = (
        list(FILE_CATEGORIES.keys())
        + ["Others"]
    )

    category_counts = {}
    category_sizes = {}

    for category in categories:

        folder = TEST_FOLDER / category

        if not folder.exists():

            category_counts[category] = 0
            category_sizes[category] = 0

            continue

        files = [
            file
            for file in folder.iterdir()
            if file.is_file()
        ]

        category_counts[category] = len(files)

        total_size = 0

        for file in files:

            try:

                total_size += file.stat().st_size

            except OSError:

                pass

        category_sizes[category] = total_size

    # --------------------------------------------------
    # TOTAL STORAGE
    # --------------------------------------------------

    total_storage = sum(
        category_sizes.values()
    )

    # --------------------------------------------------
    # REMAINING FILES
    # --------------------------------------------------

    remaining_files = sum(
        category_counts.values()
    )

    # --------------------------------------------------
    # FILE TYPE SUMMARY
    # --------------------------------------------------

    file_type_counts = get_file_type_summary()

    # --------------------------------------------------
    # AUTOMATION STATISTICS
    # --------------------------------------------------

    print("\n" + "=" * 50)
    print("        AUTOMATION STATISTICS")
    print("=" * 50)

    print(
        f"\nFiles organized this run : "
        f"{organized_count}"
    )

    print(
        f"Duplicates found this run: "
        f"{duplicate_count}"
    )

    print(
        f"Duplicates moved this run: "
        f"{duplicates_moved}"
    )

    print(
        f"Active files currently   : "
        f"{remaining_files}"
    )

    # --------------------------------------------------
    # FILE CATEGORY STATISTICS
    # --------------------------------------------------

    print("\nFILE CATEGORY STATISTICS")
    print("-" * 50)

    for category in category_counts:

        print(
            f"{category:<20}: "
            f"{category_counts[category]}"
        )

    # --------------------------------------------------
    # FILE TYPE STATISTICS
    # --------------------------------------------------

    print("\nFILE TYPE STATISTICS")
    print("-" * 50)

    if file_type_counts:

        for extension, count in sorted(
            file_type_counts.items()
        ):

            print(
                f"{extension:<20}: "
                f"{count}"
            )

        print("-" * 50)

        print(
            f"{'Total File Types':<20}: "
            f"{len(file_type_counts)}"
        )

    else:

        print(
            "No active file types found."
        )

    # --------------------------------------------------
    # FILE SIZE STATISTICS
    # --------------------------------------------------

    print("\nFILE SIZE STATISTICS")
    print("-" * 50)

    for category in category_sizes:

        print(
            f"{category:<20}: "
            f"{format_size(category_sizes[category])}"
        )

    print("-" * 50)

    print(
        f"{'Total Storage':<20}: "
        f"{format_size(total_storage)}"
    )

    print("\n" + "=" * 50)

    # --------------------------------------------------
    # CREATE PROFESSIONAL REPORT
    # --------------------------------------------------

    current_duplicate_files = []

    if DUPLICATES_FOLDER.exists():

        current_duplicate_files = [
            file
            for file in DUPLICATES_FOLDER.iterdir()
            if file.is_file()
        ]

    current_duplicate_count = len(
        current_duplicate_files
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as report:

        # --------------------------------------------------
        # REPORT HEADER
        # --------------------------------------------------

        report.write(
            "=" * 60 + "\n"
        )

        report.write(
            "           SMART TASK AUTOMATION REPORT\n"
        )

        report.write(
            "=" * 60 + "\n\n"
        )

        # --------------------------------------------------
        # RUN INFORMATION
        # --------------------------------------------------

        report.write(
            "RUN INFORMATION\n"
        )

        report.write(
            "-" * 60 + "\n"
        )

        report.write(
            f"{'Generated On':<25}: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        report.write(
            f"{'Status':<25}: "
            f"SUCCESS\n\n"
        )

        # --------------------------------------------------
        # CURRENT RUN SUMMARY
        # --------------------------------------------------

        report.write(
            "CURRENT RUN SUMMARY\n"
        )

        report.write(
            "-" * 60 + "\n"
        )

        report.write(
            f"{'Files Organized':<25}: "
            f"{organized_count}\n"
        )

        report.write(
            f"{'Duplicates Found':<25}: "
            f"{duplicate_count}\n"
        )

        report.write(
            f"{'Duplicates Moved':<25}: "
            f"{duplicates_moved}\n\n"
        )

        # --------------------------------------------------
        # CURRENT FILE SUMMARY
        # --------------------------------------------------

        report.write(
            "CURRENT FILE SUMMARY\n"
        )

        report.write(
            "-" * 60 + "\n"
        )

        for category in category_counts:

            report.write(
                f"{category:<25}: "
                f"{category_counts[category]}\n"
            )

        report.write(
            f"{'Active Files':<25}: "
            f"{remaining_files}\n"
        )

        report.write(
            f"{'Stored Duplicates':<25}: "
            f"{current_duplicate_count}\n\n"
        )

        # --------------------------------------------------
        # FILE TYPE SUMMARY
        # --------------------------------------------------

        report.write(
            "FILE TYPE SUMMARY\n"
        )

        report.write(
            "-" * 60 + "\n"
        )

        if file_type_counts:

            for extension, count in sorted(
                file_type_counts.items()
            ):

                report.write(
                    f"{extension:<25}: "
                    f"{count}\n"
                )

            report.write(
                "-" * 60 + "\n"
            )

            report.write(
                f"{'Total File Types':<25}: "
                f"{len(file_type_counts)}\n"
            )

        else:

            report.write(
                "No active files found.\n"
            )

        report.write("\n")

        # --------------------------------------------------
        # FILE SIZE STATISTICS
        # --------------------------------------------------

        report.write(
            "FILE SIZE STATISTICS\n"
        )

        report.write(
            "-" * 60 + "\n"
        )

        for category in category_sizes:

            report.write(
                f"{category:<25}: "
                f"{format_size(category_sizes[category])}\n"
            )

        report.write(
            "-" * 60 + "\n"
        )

        report.write(
            f"{'Active Storage':<25}: "
            f"{format_size(total_storage)}\n\n"
        )

        # --------------------------------------------------
        # DUPLICATE FILE DETAILS
        # --------------------------------------------------

        report.write(
            "DUPLICATE FILE DETAILS\n"
        )

        report.write(
            "-" * 60 + "\n"
        )

        if duplicate_details:

            report.write(
                "Duplicates detected during this run:\n\n"
            )

            for detail in duplicate_details:

                report.write(
                    f"- {detail}\n"
                )

        else:

            report.write(
                "No duplicates detected during this run.\n"
            )

        report.write("\n")

        if current_duplicate_files:

            report.write(
                "Currently stored duplicate files:\n\n"
            )

            for file in current_duplicate_files:

                report.write(
                    f"- {file.name}\n"
                )

        else:

            report.write(
                "No duplicate files are currently stored.\n"
            )

        report.write("\n")

        # --------------------------------------------------
        # REPORT STATUS
        # --------------------------------------------------

        report.write(
            "=" * 60 + "\n"
        )

        report.write(
            "Automation completed successfully.\n"
        )

        report.write(
            "=" * 60 + "\n"
        )

    # --------------------------------------------------
    # WRITE RUN SUMMARY TO LOG
    # --------------------------------------------------

    write_run_summary(
        organized_count,
        duplicate_count,
        duplicates_moved,
        total_storage
    )

    write_log(
        "Automation completed successfully."
    )

    print(
        f"\nAutomation report created: "
        f"{REPORT_FILE}"
    )

    print(
        "\nAutomation completed successfully!"
    )


# --------------------------------------------------
# MAIN MENU
# --------------------------------------------------

while True:

    print("\n")
    print("=" * 50)
    print("        SMART TASK AUTOMATION")
    print("=" * 50)

    print("\n1. Run Complete Automation")
    print("2. View Automation Dashboard")
    print("3. Exit")

    choice = input(
        "\nEnter your choice: "
    ).strip()

    if choice == "1":

        run_automation()

    elif choice == "2":

        show_dashboard()

    elif choice == "3":

        print(
            "\nThank you for using "
            "Smart Task Automation!"
        )

        break

    else:

        print(
            "\nInvalid choice. "
            "Please enter 1, 2, or 3."
        )