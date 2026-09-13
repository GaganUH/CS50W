# CS50W Project 1 — Wiki

This project is part of Harvard University's **CS50's Web Programming with Python and JavaScript (CS50W)** course.

## Overview

Wiki is a Django encyclopedia that stores each entry as a Markdown file. Visitors can browse entries, search by title, create and edit pages, and open a random page.

## Features

- Browse the index and open individual entries
- Search for an exact title or find partial title matches
- Create new entries with duplicate-title validation
- Edit existing entries in Markdown
- Open a random entry
- See an error page when an entry does not exist
- Render headings, bold text, links, unordered lists, and paragraphs from Markdown

## Technologies Used

- Python and Django
- HTML and CSS
- Markdown files for entry storage

## Run Locally

From the `Project 1` folder, install Django if needed, then start the server:

```powershell
python -m pip install django
python manage.py runserver
```

Open the local address shown in the terminal. To run the project tests:

```powershell
python manage.py test encyclopedia
```

## Project Structure

```text
Project 1/
├── encyclopedia/  # Views, routes, templates, styles, and Markdown conversion
├── entries/       # Encyclopedia entries saved as Markdown files
├── wiki/          # Django project configuration
├── manage.py
└── README.md
```
