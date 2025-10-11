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
            """Allow spaces and strip leading/trailing whitespace."""
            value = value.strip()
            if not value:
                raise serializers.ValidationError("Username cannot be empty.")
            return value

    def validate_email(self, value):
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError('Email already exists')
            return value

    def save(self):
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
    
