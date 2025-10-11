from rest_framework import generics, status
from user_auth_app.models import UserProfile
from .serializers import UserProfileSerializer, RegistrationSerializer
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token 
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken


class UserProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data = request.data)

        data = {}
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user = user)
            data = {
                'token': token.key,
                'fullname': user.username,
                'email': user.email
            }
        else:
            data = serializer.errors
        
        return Response(data)
    

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data = request.data)

        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user = saved_account)
            data = {
                'token': token.key,
                'username': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.id,
            }
        else:
            data = serializer.errors
        
        return Response(data)
    
class EmailCheckView(APIView):
    # permission_classes = [IsAuthenticated]  # ✅ only logged-in users

    def get(self, request):
        user = request.user

        if user.is_anonymous:
            return Response({"detail": "User not authenticated."},
                            status=status.HTTP_401_UNAUTHORIZED)

        data = {
            "id": user.id,
            "name": user.get_full_name() or user.username,
            "email": user.email
        }
        return Response(data, status=status.HTTP_200_OK)