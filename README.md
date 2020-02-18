# Django One-to-One Messaging

By: Andrew Chen Wang

8:14:00 2020-02-18

The purpose of this setup is to test a one-to-one messaging system.

We will only use Django 3.0 instead of Django Channels as an experiment.

### Setup

This application was written in Python 3.7 and Django 3.0.

1. Clone or download this repository.
2. To run the native Django 3.0 application, cd into the `native` directory and pip install the requirements.
3. To run the channels application (also using Django 3.0 since it's officially supported), cd into the `dependency` directory and pip install the requirements.
4. To see how this runs on iOS, open the Xcode project, run the simulator, and run the server from either step 2 or 3. 

### Important Notes

This project is developed not for some Medium article but for my own test runs as Django slowly migrates (pudum, ccsiiii) to async.

Additionally, the chat I implement satisfies the above which is

1. Private messaging between 2 users only.
2. If a user is in an ACTIVE private messaging thread, then they cannot activate (i.e. communicate) another one.

I will leave as many notes as possible so that you can incorporate your own features (such as group chats) since this code can easily be used to change up the taste very easily.

Finally, I do not have any caches available. In fact, when developing, I didn't use any except the LocMem which is default.

### Goals

- Register users quickly.
- Once logged in, check if you are in the middle of a chat and redirect immediately to that chat
- Have two users communicate asynchronously while 403 blocking other users.

### TODO (w/ current implementations)

1. View old chats but not be able to communicate with that person.
    - The current MessageThread model allows for this with FKs towards users
    - It also contains a bool value making sure users can't just start communicating again.
        - That's one less transaction cost instead of looking up the entire table.
        - Although it is nice to have something like [Django cachalot](https://github.com/noripyt/django-cachalot) which makes it easier, but still... too many queries perhaps. Will consider if this bool is necessary.
2. Implement a Django Channels solution along with this to compare speeds.
3. Add iOS app to communicate with Django.
    - This means we'd have to add JWS authentication...