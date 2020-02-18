# Django One-to-One Messaging

By: Andrew Chen Wang

Date Created: 8:14:00 2020-02-18

The purpose of this setup is to test a one-to-one messaging system.

We will only use Django 3.0 ~~instead of~~ Django Channels as an experiment.
- Changed (forgot to change after writing rest of README): We will be doing both Django Channels and Django 3.0 to see performance.

This is also my first time with async code, so point out some good practices in the issues section in GitHub.

### Setup

This application was written in Python 3.7 and Django 3.0.

1. Clone or download this repository.
2. To run the native Django 3.0 application, cd into the `native` directory and pip install the requirements.
    a. Next, you need to run uvicorn with this command: `uvicorn native.asgi:application`
    b. Make sure you aren't running the wsgi server (i.e. do **NOT** do `python manage.py runserver`)
3. To run the channels application (also using Django 3.0 since it's officially supported), cd into the `dependency` directory and pip install the requirements.
4. To see how this runs on iOS, open the Xcode project, run the simulator, and run the server from either step 2 or 3. 

Setting up a chat between two users:
1. Go to your admin panel (assuming you made a superuser)
2. Create another user
3. Create a message thread and add two users
4. Start the uvicorn workers and login

### Important Notes

- This project is developed not for some Medium article but for my own test runs as Django slowly migrates (pudum, ccsiiii) to async.

Take special care knowing that to deploy the native one, you must configure ASGI and WSGI correctly. See Note 1 at the bottom.

Additionally, the chat I implement satisfies the above which is

1. Private messaging between 2 users only.
2. If a user is in an ACTIVE private messaging thread, then they cannot activate (i.e. communicate) another one.

- **NEVER USE WS** in PRODUCTION. Always use WSS ([secure and reliable](https://javascript.info/websocket)). I highly recommend you use cookiecutter-django (I'm currently working with them to implement the ASGI deployment option)
    - Remember, I am just make a local testing development, so I use ws:// all over the place. Don't in production. Use the Jinja tag templates to separate testing templates with actual production!

- I do not have any caches configured. In fact, when developing, I didn't use any except the Local Memory which is default.

- I will leave as many notes as possible so that you can incorporate your own features (such as group chats) since this code can easily be used to change up the taste very easily.

### Goals

- Register users quickly.
- Once logged in, check if you are in the middle of a chat and redirect immediately to that chat
- Have two users communicate asynchronously while 403 blocking other users.
- Add functionality to load old messages.

### TODO (w/ current implementations)

1. View old chats but not be able to communicate with that person.
    - The current MessageThread model allows for this with FKs towards users
    - It also contains a bool value making sure users can't just start communicating again.
        - That's one less transaction cost instead of looking up the entire table.
        - Although it is nice to have something like [Django cachalot](https://github.com/noripyt/django-cachalot) which makes it easier, but still... too many queries perhaps. Will consider if this bool is necessary.
2. Implement a Django Channels solution along with this to compare speeds.
3. Add iOS app to communicate with Django.
    - This means we'd have to add JWS authentication...
    
### Misc Notes / Credits

Note 1: Websocket implementation with native Django 3.0: https://dev.to/jaydenwindle/adding-websockets-to-your-django-app-with-no-extra-dependencies-2f6h
    - IMPORTANT: Andrew's note: Uvicorn is not supposed to run all WSGI and ASGI. Instead, you should run it on gunicorn mixed with uvicorn,
    which can be detailed here: https://www.uvicorn.org under the section Running with Gunicorn
    - So in deployment, use ASGI to deploy since we've setup a route for HTTP and WS.

Note 2: When using uvicorn, it isn't going to work like runserver does. When you edit some code, you must stop the uvicorn worker (ctrl + break like Django's) and start it up again.

Note 3: Debugging messages are shown in your terminal/cmd.

Note 4: If I've said anything wrong here (most likely since I'm also just learning with y'all!), please let me know in a GitHub issue and ping me. Good luck learning!

### FAQ

Where did my staticfiles go?

Since you're using a different server, you have to append them yourself during development: https://stackoverflow.com/a/12801140

I've already added them to the global urls.py in both `native` and `dependency`.

### License

LICENSE is under BSD-3-Clause, Andrew Chen Wang

Please add attributions if you use a MOST of this code; this is just to prevent some medium article from taking credit. For commercial, it MAY not be necessary to add attributions, but you **must** add this license. Thank you!