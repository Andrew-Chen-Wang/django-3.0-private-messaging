# Django 3.0 One-to-One Messaging

By: Andrew Chen Wang

Date Created: 8:14:00 2020-02-18
Date Stopped: 16:01:24 2020-02-18
Edited: 20:55:52 2020-02-29

### Better Important Edit

In wake of growing expectations, I've just created a Django 3.0 multi-chat option, as well, using just caching and the asgi.py. No Django channels. Anyways, I've implemented multi-chat using ONE WebSocket connection per user. Why? One main reason is that my iOS app's ContainerViewController which is like Android's ViewPager and Android's One-activity-multiple-fragment architecture makes using one web socket connection optimal. 1. I needed to communicate several other things between the server and the user using custom headers and 2. AWS costs a lot of money, especially with API Gateway or simply using EC2 with data transferring On-Demand... The following assumes you've set up native Django 3.0 like so to work with websockets: https://dev.to/jaydenwindle/adding-websockets-to-your-django-app-with-no-extra-dependencies-2f6h.

Anyways, how did I do it? Again, can't show any code nor say much, so bear with me. I'm now a contributor to [DRF SimpleJWT](https://github.com/SimpleJWT/django-rest-framework-simplejwt) which has an experimental feature that allows you to use a stateless TokenUser instance with Django's `cached_property` decorator. This decorator has cached a user's pk if you manually create an instance of TokenUser via SimpleJWT's authentication backend methodology. The following steps are a method for making sure there is only one socket connection per user (each `websocket_application` is essentially [ONE websocket connection](https://asgi.readthedocs.io/en/latest/specs/main.html). Docs say: 

> "The application is called once per “connection.” The definition of a connection and its lifespan are dictated by the protocol specification in question. For example, with HTTP it is one request, whereas for a WebSocket it is a single WebSocket connection."). 

First, the client needs to GET request to an APIView (remember to throttle/rate-limit these!). My `AUTH_USER_MODEL` has an attribute of BoolField called `is_ws_connected`. The APIView checks that it's false and inserts a cache into redis with the prefix `ws_checker_(USER PK)` as the key with expiration of 60 seconds (redis automatically searches for these. For me, I saved the cache keys in a local db instead of my RDS since 1. cookiecutter-django delivers with one with Docker and 2. I've had bad experiences with expiring caches that weren't automatically cleaned up in redis). The view also returns all the chat's autoincrementing pk (save these for later). The value can be anything. On `websocket.connect`, you `websocket.accept` after grabbing the user's Authentication Bearer token header (remember, websockets are like HTTP, so they have headers and cookies too! Additionally, if authentication fails, instead of sending `websocket.accept`, send `websocket.close`). Use the `get_user` [method's code](https://github.com/SimpleJWT/django-rest-framework-simplejwt/blob/master/rest_framework_simplejwt/authentication.py#L121) method and other stuff from SimpleJWT in the `authentication.py` file to get the **user's pk** (I don't automatically set the Experimentation feature in SimpleJWT settings. I just took its code for websocket sake. I'm looking into implementing websockets for cookiecutter-django since the upgraded to 3.0 and SimpleJWT as I'm commited to making this public without publishing code and... legal stuff). Then, access the cache and look for that `ws_checker_(USER PK)` cache key. If it's not found, then send `websocket.close`; otherwise, invalidate the cache as to not waste memory and send `websocket.accept`. Let's roll.

Now that you're connected, you will need to use asyncio to receive messages from the opposite user. I've created an asyncio loop done with `run_forever` that checks for specific cache keys to know if the opposite user sent a message (remember, this is for private chats but can be made for group chats as well. Let your imagination grow. Not too hard naming cache keys wink wink). When sending messages with `websocket.text`, you want to attach a custom header that says the chat id. The next part is difficult as it opens a future theme: async database calling which means more threads. 

If I recall from the Django dev group on Google, the creator of psycopg family will be creating an async safe or thread safe psycopg3 soon! In the meantime, we have to use Django channel's `database_sync_to_async` method (they use asgiref which comes packaged with Django 3.0) to do the following when verifying the chat id is correct (i.e. whether or not the user belongs in this private chat) and saving messages. Unfortunately, when writing this, Celery 5.0 hasn't come out yet, so calling celery tasks asynchronously won't be possible, so we have to use the aforementioned method. 

Anyways, I first want to insert the text into the database and then send the text to the other user via caches so that that user's `run_forever` event loop was activated since that user would be connected via websocket to the server. I have a model with user 1 and user 2 as FKs for each chat, so I created an async function that will first get the instance from the chat id header to make sure the user is actually in that chat THEN insert the text to the database in a separate model (since I only have 1-1 messaging, I just have a BooleanField attribute to represent User 1 and 2). Make sure you do `await` when calling that function. Once that's done, insert into the cache a certain cache key that _you need to make up_ (I had other needs, so can't share what I did). That aforementioned forever event loop is looking for cache key prefixes (not entire cache key names. Prefixes is key here!). There is a little bit more magic going on such as counting the number of messages within that application and yada yada to help you organize these chat messages. That's for you to work on though.

Oh, I forgot: the event loop function has a parameter `send`. It's the exact same "send" as the `async def websocket_application` send. When you first create your loop, pass your send instance to that loop. Thus, when your loop catches an incoming message via the cache, you can use `send` to actually send the message. For the initial sender, you simply send back "Success" or status 200 afterwards.

That's it! Good luck coming up with cache key names. I apologize for 1. no code and 2. somewhat confusing sentences. I wanted to share my entire journey learning this without getting sued, that's why there are so many links and side notes. Again, the main reason I wanted to share this was because 1. I never learned Django channels and thought Django 3.0 was good enough, 2. my implementation would not have changed whatsoever if I had used Django channels since I was using one websocket per user for multiple chats, 3. I just like learning, and 4. AWS is stupid expensive so I could only limit myself to one connection per user. Have fun learning too!

If you need multi chat, when I said I had a MessageThread model with two FKs, what you can do instead, if using PostgreSQL, is to use JSONField with user's ids. Then, when it comes to knowing who sent what in the Message model, replace BooleanField with FK. It costs more data wise, but not that much.

Additionally, I use Daphne instead of uvicorn since I believe only Daphne does ping-interval checks by itself, [according to @andrewgodwin](https://github.com/django/daphne/issues/168#issuecomment-365397557) (note: if uvicorn does this, please let me know!), and the server will `send("websocket.disconnect")` if the user truly disconnected. Make sure your client does automatic pongs when the server pings the client! When I developed my client's iOS chat, I used Starscream which also automatically does ping pongs since these ping intervals are set to very short amount of time (e.g. 10-20 seconds). Make sure your mobile libraries are doing that!

### Important Edit

~~For those looking into how to do this, I have successfully done it for a private necessity. Unfortunately, I'm bound from sharing the code but the idea can still be spread. Inspired by wanting a cached JWT authentication, the current user needs to first go to a view to to get a "identification_tag" which is saved in your cache (like redis). Make sure you cryptographically sign this. Next, your user needs to connect to the websocket (on web, HTTP303 redirect the user; on mobile, get the id and save it. Then connect using a websocket library like starscream for iOS).~~

~~On websocket connection, use the identification to correctly connect the user to a chat. That chat should have a path that only works with the assigned cryptographic identifications for the two users. You check via the cache in the on connection scope.~~

~~Confusing? I know, but I legally can't say too much. Good luck!~~

## Note

Unfortunately, Django 3.0 doesn't support database_sync_to_async like Django Channels, so the experiment must stop on my part.

However, if you look at the code, it could be of assistance to you. Instead of chats being the MessageThread id, you can make a huge number in the form of characters (with Django IP throttling) that represents the MessageThread rather than autoincrement.

Although the view blocks a user on desktop from infiltrating a chat, someone with basic JS knowledge can understand the autoincrementing schema and access a chat via the websocket itself.

To view message history, you can use a different method: in utils.py of the native directory, there is a method of grabbing the session ID (from django source code and django extensions) and finding out who the user is. In that case, you can basically have another endpoint (like an API endpoint) that you POST request the session ID along with it. 

---

The purpose of this setup is to test a one-to-one messaging system.

We will only use Django 3.0 ~~instead of~~ Django Channels as an experiment.
- Changed (forgot to change after writing rest of README): We will be doing both Django Channels and Django 3.0 to see performance.

This is also my first time with async code, so point out some good practices in the issues section in GitHub.

### Setup and Run

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

### How does Django 3.0 work in our context?

Since I've never used async Python for Django and Channels, I'll try my best not to screw up:

Basically, I've set this up so that you load the HTML for a chat synchronously. Using vanilla JS, I've added some scripts that run with the WebSocket. That WebSocket connects with the Django server's ASGI side (which you can find in the project(either native or dependency)/websocket.py).

To plainly sum it up, serve the HTML synchronously. Asynchronously serve your messages with the JS that you loaded with the HTML.

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
    - This means we'd have to add JWT authentication...
    
### Misc Notes / Credits

Note 1: Websocket implementation with native Django 3.0: https://dev.to/jaydenwindle/adding-websockets-to-your-django-app-with-no-extra-dependencies-2f6h
    - IMPORTANT: Andrew's note: Uvicorn is not supposed to run all WSGI and ASGI. Instead, you should run it on gunicorn mixed with uvicorn,
    which can be detailed here: https://www.uvicorn.org under the section Running with Gunicorn
    - So in deployment, use ASGI to deploy since we've setup a route for HTTP and WS.

Note 2: When using uvicorn, it isn't going to work like runserver does. When you edit some code, you must stop the uvicorn worker (ctrl + break like Django's) and start it up again.

Note 3: Debugging messages are shown in your terminal/cmd.

Note 4: If I've said anything wrong here (most likely since I'm also just learning with y'all!), please let me know in a GitHub issue and ping me. Good luck learning!

Note 5: Getting the user from the WebSocket came from Django channel's source code: https://github.com/django/channels/blob/master/channels/auth.py
    - Within a WS scope is the user's session ID
    - When implementing this for mobile, your header needs to include a JWT token.

### FAQ

Where did my staticfiles go?

Since you're using a different server, you have to append them yourself during development: https://stackoverflow.com/a/12801140

I've already added them to the global urls.py in both `native` and `dependency`.

### License

LICENSE is under BSD-3-Clause, Andrew Chen Wang

Please add attributions if you use a MOST of this code; this is just to prevent some medium article from taking credit. For commercial, it MAY not be necessary to add attributions, but you **must** add this license. Thank you!
