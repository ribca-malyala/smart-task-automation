# Smart Task Automation System

A Python-based file organization and automation system that automatically sorts files into categories, detects duplicate files using SHA-256 hashing, generates automation reports, maintains activity logs, and provides a command-line dashboard for monitoring file activity.

---

## 📌 Project Overview

Managing large numbers of files manually can be time-consuming and can lead to duplicate files, disorganized folders, and difficulty tracking file activity.

The **Smart Task Automation System** solves this problem by automatically organizing files based on their file extensions and maintaining useful information about the files processed.

The system can:

- Automatically organize files into categories
- Detect duplicate files
- Move duplicate files into a separate folder
- Calculate file sizes
- Track file activity
- Maintain automation history
- Generate detailed reports
- Display a command-line dashboard
- Support new file types through configuration

---

## 🎯 Problem Statement

Manual file management becomes difficult when a folder contains files of different types such as documents, images, videos, and audio files.

This project provides an automated solution that organizes files, identifies duplicates, tracks storage usage, and generates reports without requiring the user to manually manage each file.

---

## ✨ Features

### 📂 Automatic File Organization

Files are automatically categorized based on their extensions.

Supported categories include:

- Images
- Documents
- Videos
- Audio
- Others

Example:

```text
photo.jpg       → Images
notes.txt       → Documents
movie.mp4       → Videos
song.mp3        → Audio
unknown.xyz     → Others