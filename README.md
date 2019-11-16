# Carafe (Flask Test Project)

## Summary:

Carafe is an online message board written in Python. Carafe utilizes the Flask framework and PostgreSQL. 

## Features:

#### Implemented
- Users, Boards, Posts, Comments
- Markdown Support

## Deployment (Heroku)

1. Download the project from Github.
2. Edit ```config.py``` in the carafe folder.
3. Upload the project to a Heroku free tier dyno.
4. Attach the PostgreSQL database plugin from Heroku.
5. Create a ```SECRET_KEY``` environment variable on the Heroku dashboard.
6. Restart the dyno and enjoy.


[Heroku Example](https://carafeboard.herokuapp.com)
