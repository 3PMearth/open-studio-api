import logging
from .models import Verifier
from rest_framework import serializers

logger = logging.getLogger(__name__)

class VerifierSerializer(serializers.ModelSerializer):
    """
    Verifier Serializer
    """
    class Meta:
        model = Verifier
        fields = '__all__'