# What's For Dinner
A web app to help you plan your dinner menu. | Capstone I Project for Springboard Software Engineering Program

## Table of Contents
* [General Info](#general-info)
* [Stack](#stack)
* [Database Design](#database_design)
* [Setup](#setup)

## General Info
This is a fullstack project to showcase my knowledge of how to create interaction between frontend and backend.
The project uses an External API from Spoonacular and a backend database handled by PostgreSQL.

Experience the web app on heroku here: https://pbj-whats-for-dinner-app.herokuapp.com/

## Stack
#### Frontend:
* HTML
* CSS (BOOTSTRAP & SASS)
* JAVASCRIPT
#### Backend:
* PYTHON
* FLASK
* SQLALCHEMY - POSTGRESQL

## Database Design
Backend database design:
![whats-for-dinner-part1](https://user-images.githubusercontent.com/91149098/162230515-02350fd7-f277-4947-9656-634b1f501eae.png)


## Setup
To run this project, install python, pip, and postgreSQL.

Create a database in postgreSQL.
```
Replace (Line 14) SQLALCHEMY_DATABASE_URI in app.py with 'postgresql://<postgresql_username>:<postgresql_password>@localhost:<localhost_number>/<database_name>'
```

Sign up for Spoonacular (https://spoonacular.com/food-api/pricing) to get the API Key
```
Replace (Line 2) in app.js with => const apiKey = '<your_api_key_from_spoonacular>'
```

In command prompt, cd to directory, install requirements and run app.
```
$ cd ../whats-for-dinner
$ pip install -r requirements.txt
$ flask run
```
