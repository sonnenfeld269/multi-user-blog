# Multi User Blog

## Introduction

A backend webapplication with a secure authentication system and where users can post, delete and update their blog posts.
The main parts of the app are:
  * **main.py**: A main class to initialize the app and communicate between browser and app.
  * **user.py**: A class specifing a user
  * **post.py**: A class specifing a blog post
  * **templates**: Inside you will find html template, which will be rendered using the jinja2 template engine

## Requirements

* Python: Make sure you have python installed. Use can use folowing command: `python --version`
* Google App Engine SDK
* Browser: Make sure you have a browser installed

## Installation

1. Clone the github project with `git clone https://github.com/sonnenfeld269/multi-user-blog.git`
2. Go inside the folder with `cd multi-user-blog.git`
3. Start the programm by running `dev_appserver.py app.yaml`
