from django.urls import path

from api.views import CreateUser, LoginUser, ManageUser, ManageFriendship, PendingFriendRequests, AllFriends, \
    Suggestions

urlpatterns = [
    path('create_user/', CreateUser.as_view()),
    path('login_user/', LoginUser.as_view()),
    path('user/<int:user_id>', ManageUser.as_view()),
    path('add/<int:sender_id>/<int:receiver_id>', ManageFriendship.as_view()),
    path('friend_requests/<int:receiver_id>', PendingFriendRequests.as_view()),
    path('friends/<int:user_id>', AllFriends.as_view()),
    path('suggestions/<int:user_id>', Suggestions.as_view()),
]
