# Student Planner

Student Planner is a desktop productivity application built for students who want one focused place to manage study life.  
It combines tasks, exams, timetable planning, a Pomodoro study timer, habit tracking, and notes inside a clean `Dark Academic` interface built with pure Python.

## Overview

This project was developed using `Python` and `tkinter` with local `JSON` storage.  
The goal is to provide an offline, lightweight, and visually polished planner that helps students stay organized without needing external services or third-party packages.

## Features

### Dashboard
- View pending tasks and completion rate
- Track weekly habit consistency
- See the next upcoming exam with countdown
- Display a motivational daily quote

### To-Do List
- Add and delete tasks
- Set priority levels: `Urgent`, `High`, `Medium`, `Low`
- Mark tasks as completed
- Monitor progress with a progress bar

### Exam Schedule
- Add exams with subject, date, time, and hall
- View live countdowns for upcoming exams
- Highlight urgent exams automatically

### Timetable
- Organize a full weekly study schedule
- Display subjects in color-coded cards
- Add and remove timetable slots easily

### Study Timer
- Built-in `Pomodoro` timer
- Work and break session settings
- Start, pause, reset, and switch mode controls
- Circular animated timer display

### Habit Tracker
- Track daily habits across the week
- Mark progress with one click
- View overall weekly consistency

### Notes
- Free writing area for reminders and study notes
- Local autosave support

## Tech Stack

- `Python 3`
- `tkinter` for the graphical user interface
- `JSON` for local persistent data storage

## Project Structure

```text
.
|-- StudentPlanner.py
|-- StudentPlanner.exe
|-- README.md
`-- data/
    `-- student_dashboard_data.json
```

## How To Run

### Option 1: Run with Python

```bash
python StudentPlanner.py
```

### Option 2: Run the Windows executable

Open:

```text
StudentPlanner.exe
```

## Data Storage

All planner data is stored locally in:

```text
data/student_dashboard_data.json
```

Saved data includes:
- tasks
- exams
- timetable entries
- timer settings
- habits
- notes

## Why This Project Stands Out

- Clean and elegant `Dark Academic` visual style
- Fully offline and lightweight
- No external Python packages required
- Designed around real student workflows
- Packaged as both source code and executable

## Use Cases

- Managing assignments and deadlines
- Tracking upcoming exams
- Building a weekly class timetable
- Running focused study sessions with Pomodoro
- Monitoring personal study habits
- Keeping quick notes in one place

## Requirements

- `Python 3.11+` if running from source
- Windows environment for the included `.exe`


