from rest_framework import serializers
from .models import User
import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    """
    User Serializer for User model
    """
    class Meta:
        model = User
        fields = '__all__'
