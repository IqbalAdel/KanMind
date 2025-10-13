from rest_framework import serializers
from user_auth_app.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user']

class EmailAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """validates check-email request for a given email

        Raises:
            serializers.ValidationError: checks if user with given mail exists
            serializers.ValidationError: checks if user with username and password exist 
            serializers.ValidationError: checks if both email and password were given

        Returns:
            attrs: dictionary 
        """        

        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError('Invalid email or password.')

            user = authenticate(username=user.username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

        attrs['user'] = user
        return attrs

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only = True)
    fullname = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id','fullname','email','password', 'repeated_password']
        extra_kwargs = {
            'password' : {
                'write_only': True
            },
        }
    
    def validate_username(self, value):
        """validates username

        Args:
            value (string): username

        Raises:
            serializers.ValidationError: if string is empty, raise

        Returns:
            value (string): valid username
        """            
       
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Username cannot be empty.")
        return value

    def validate_email(self, value):
        """validates email, checks if user with email exists

        Args:
            value (string): email

        Raises:
            serializers.ValidationError: raise error, if email has already been used

        Returns:
            value (string): email
        """            
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def save(self):
        """saves user account on registration

        Raises:
            serializers.ValidationError: password and repeated password don't match

        Returns:
            account: object with account information of user
        """        
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        fullname = self.validated_data['fullname']

        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'passwords dont match'})
        
        username = self.validated_data.get('username') or fullname
        account = User(email = self.validated_data['email'], username=username)
        
        account.set_password(pw)
        account.save()
        profile = UserProfile.objects.create(user=account)
        return account
    
