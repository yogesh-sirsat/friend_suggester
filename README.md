# Steps to run project locally

1. Clone the repository.
2. Run `pip install -r requirements.txt` to install all the dependencies.
3. Run `python manage.py runserver` to start the server.
4. Superuser credentials are `yogesh` and `yogesh`.
5. Then go to `http://127.0.0.1:8000` to view the project is running.

## API endpoints
* `POST` /api/create_user/ - Create a new user
* `POST` /api/login_user/ - Login a user
* `GET` /api/user/{user_id} - Get user details
* `POST` /api/add/{sender_id}/{receiver_id} - Send a friend request/ Accept a friend request
* `GET` /api/friends/{user_id} - Get all friends of a user
* `GET` /api/friend_requests/{user_id} - Get all received friend requests of a user
* `GET` /api/suggestions/{user_id} - Get all suggestions for a user until 2 degrees of friends