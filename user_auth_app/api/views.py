from rest_framework import generics, status
from user_auth_app.models import UserProfile
from .serializers import UserProfileSerializer, RegistrationSerializer, EmailAuthTokenSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token 
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User

class UserProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for profiles of specific users.

    Returns the user data of specific primary key.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class CustomLoginView(ObtainAuthToken):
    """
    API endpoint for obtaining authentication tokens for users.

    Inherits from DRF's `ObtainAuthToken` and can be customized to add
    additional logic if needed (e.g., returning user details alongside the token).
    """
    permission_classes = [AllowAny]
    serializer_class = EmailAuthTokenSerializer

    def post(self, request):
        """function for POST request using a token for authentication when loggin in

        Args:
            request (_type_): 

        Returns:
            Response: includes the token, fullname, email and user_id
        """        
        serializer = self.serializer_class(data = request.data)

        data = {}
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user = user)
            data = {
                'token': token.key,
                'fullname': user.username,
                'email': user.email,
                'user_id': user.id,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:   
            data = serializer.errors
            return Response({'detail':data}, status=status.HTTP_400_BAD_REQUEST)


class RegistrationView(APIView):
    """
    API endpoint for registering new users.

    Handles creation of user accounts, including username validation. Returns the created user data.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """function for POST request using a token for authentication when registering as a user

        Args:
            request (_type_): 

        Returns:
            Response: includes the token, fullname, email and user_id
        """
        serializer = RegistrationSerializer(data = request.data)
        if User.objects.filter(username=request.data.get('fullname')).exists():
            return Response(
                {"detail": "Username already exists."},
                status=status.HTTP_400_BAD_REQUEST
    )

        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user = saved_account)
            data = {
                'token': token.key,
                'fullname': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.id,
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = serializer.errors        
            return Response({'detail': data}, status=status.HTTP_400_BAD_REQUEST) 
    
    
class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        """checks if a given email is already registered for a user

        Args:
            request (_type_):   

        Returns:
            response: Contains id, email and fullname of user
        """        
        email = request.query_params.get('email')
        user = User.objects.get(email=email)

        if not email:
            return Response({"detail": "Email query parameter is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            data = {
                "id": user.id,
                "email": user.email,
                "fullname": user.username,
            }        
        except User.DoesNotExist:
            return Response({"detail": "User not found."},
                            status=status.HTTP_404_NOT_FOUND) 
        
        return Response(data)