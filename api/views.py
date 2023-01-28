from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Friendship
from .serializers import UserSerializer


def index(request):
    return render(request, 'index.html')


class CreateUser(APIView):

    @staticmethod
    def post(request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                response = Response(serializer.data, status=status.HTTP_201_CREATED)
                response.set_cookie(key='token', value=token.key, httponly=True)
                response.data['token'] = token.key
                return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUser(APIView):

    @staticmethod
    def post(request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)
            response = Response({'token': token.key}, status=status.HTTP_200_OK)
            response.set_cookie(key='token', value=token.key, httponly=True)
            return response
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class ManageUser(APIView):

    @staticmethod
    def get(request, user_id):
        user = User.objects.filter(pk=user_id).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class ManageFriendship(APIView):
    @staticmethod
    def post(request, sender_id, receiver_id):
        sender = User.objects.filter(pk=sender_id).first()
        receiver = User.objects.filter(pk=receiver_id).first()
        if not sender:
            return Response({'error': 'Friend request from invalid user'}, status=status.HTTP_404_NOT_FOUND)
        if not receiver:
            return Response({'error': 'Friend request to invalid user'}, status=status.HTTP_404_NOT_FOUND)

        if sender == receiver:
            return Response({'error': 'Cannot send friend request to self'}, status=status.HTTP_400_BAD_REQUEST)

        if Friendship.objects.filter(sender=sender, receiver=receiver).exists():
            friendship = Friendship.objects.get(sender=sender, receiver=receiver)
            if friendship.pending:
                return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': 'Sender is already friend with requested user'},
                            status=status.HTTP_400_BAD_REQUEST)

        if Friendship.objects.filter(sender=receiver, receiver=sender).exists():
            friendship = Friendship.objects.get(sender=receiver, receiver=sender)
            if not friendship.pending:
                return Response({'error': 'Sender is already friend with requested user'},
                                status=status.HTTP_400_BAD_REQUEST)
            friendship.pending = False
            friendship.accepted_at = timezone.now()
            friendship.save()
            return Response({'success': 'Friendship created'}, status=status.HTTP_200_OK)

        Friendship.objects.create(sender=sender, receiver=receiver)
        return Response({'success': 'Friendship requested'}, status=status.HTTP_202_ACCEPTED)


class PendingFriendRequests(APIView):
    @staticmethod
    def get(request, receiver_id):
        receiver = User.objects.filter(pk=receiver_id).first()
        if not receiver:
            return Response({'error': 'Invalid user'}, status=status.HTTP_404_NOT_FOUND)
        pending_friendships = User.objects.filter(sent_friendship__receiver=receiver,
                                                  sent_friendship__pending=True)
        if not pending_friendships:
            return Response({'error': 'No pending friend requests'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(pending_friendships, many=True)
        return Response(serializer.data)


class AllFriends(APIView):
    @staticmethod
    def get(request, user_id):
        user = User.objects.filter(pk=user_id).first()
        if not user:
            return Response({'error': 'Invalid user'}, status=status.HTTP_404_NOT_FOUND)
        all_friends = User.objects.filter(
            Q(sent_friendship__receiver=user, sent_friendship__pending=False) | Q(
                received_friendship__sender=user, received_friendship__pending=False)).prefetch_related(
            'received_friendship__sender', 'sent_friendship__receiver').distinct()
        if not all_friends:
            return Response({'error': 'No friends'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(all_friends, many=True)
        return Response(serializer.data)


class Suggestions(APIView):
    """
    List of friend suggestions until 2 degrees of friends
    """

    @staticmethod
    def get(request, user_id):
        user = User.objects.filter(pk=user_id).first()
        if not user:
            return Response({'error': 'Invalid user'}, status=status.HTTP_404_NOT_FOUND)
        friends = User.objects.filter(
            Q(sent_friendship__receiver=user, sent_friendship__pending=False) | Q(
                received_friendship__sender=user, received_friendship__pending=False)).prefetch_related(
            'received_friendship__sender', 'sent_friendship__receiver').distinct()
        if not friends:
            return Response({'error': 'No suggestions'}, status=status.HTTP_404_NOT_FOUND)
        # First degree of friends
        friends_of_friends = User.objects.filter(
            Q(sent_friendship__receiver__in=friends, sent_friendship__pending=False) | Q(
                received_friendship__sender__in=friends, received_friendship__pending=False)).prefetch_related(
            'received_friendship__sender', 'sent_friendship__receiver').distinct().exclude(
            pk__in=friends).exclude(pk=user_id)
        if not friends_of_friends:
            return Response({'error': 'No suggestions'}, status=status.HTTP_404_NOT_FOUND)
        # Second degree of friends
        friends_of_friends_of_friends = User.objects.filter(
            Q(sent_friendship__receiver__in=friends_of_friends, sent_friendship__pending=False) | Q(
                received_friendship__sender__in=friends_of_friends,
                received_friendship__pending=False)).prefetch_related(
            'received_friendship__sender', 'sent_friendship__receiver').distinct().exclude(pk__in=friends).exclude(
            pk=user_id)

        suggestions = (friends_of_friends_of_friends | friends_of_friends)
        if not suggestions:
            return Response({'error': 'No suggestions'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(suggestions, many=True)
        return Response(serializer.data)
