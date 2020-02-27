# Carafe (2017)

## Summary:

Carafe is an online message board written in Python. Carafe utilizes the Flask framework and PostgreSQL. 

## Features:

#### Implemented
- Users, Boards, Posts, Comments
- Markdown Support
- Registration
- Basic Post/Comment administration

#### Planned (no longer in active development as of 2017)
- User Management
- Admin Panel
- REST API
- Verification Email
- Password Reset

## Deployment (Heroku)

1. Clone repo
2. Edit ```config.py``` in the carafe folder.
3. Link repo to Heroku project and utilize Heroku free tier dyno.
4. Attach the PostgreSQL database plugin from Heroku.
5. Create a ```SECRET_KEY``` environment variable on the Heroku dashboard.
6. Restart the dyno and enjoy.

[Heroku Example](https://carafeboard.herokuapp.com)

![demo](https://github.com/haydenmcfarland/assets/blob/master/images/carafe.gif?raw=true)

