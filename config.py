from pathlib import Path


# ==================================================
# SMART TASK AUTOMATION - CONFIGURATION
# ==================================================


# --------------------------------------------------
# MAIN SETTINGS
# --------------------------------------------------

# Main folder containing files to organize
TEST_FOLDER = Path("test_files")

# Activity log file
LOG_FILE = Path("automation_log.txt")

# Automation report file
REPORT_FILE = Path("automation_report.txt")

# Folder where duplicate files are stored
DUPLICATES_FOLDER = TEST_FOLDER / "Duplicates"


# --------------------------------------------------
# FILE CATEGORIES
# --------------------------------------------------

FILE_CATEGORIES = {

    "Images": [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp"
    ],

    "Documents": [
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".xlsx",
        ".csv",
        ".pptx"
    ],

    "Videos": [
        ".mp4",
        ".mkv",
        ".avi",
        ".mov"
    ],

    "Audio": [
        ".mp3",
        ".wav",
        ".aac"
    ]
}