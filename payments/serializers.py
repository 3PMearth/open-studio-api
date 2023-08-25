from rest_framework import serializers
import logging

logger = logging.getLogger(__name__)

class PGDataTokensSerializer(serializers.Serializer):
    token_id = serializers.IntegerField()
    amount = serializers.IntegerField()

class PGDataSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    success_url = serializers.CharField(max_length=256)
    country_code = serializers.CharField(max_length=3)
    phone_number = serializers.CharField(max_length=64)
    error_url = serializers.CharField(max_length=256)
    sum_amount = serializers.IntegerField()
    sum_price = serializers.FloatField()
    currency = serializers.ChoiceField(choices=['krw', 'usd'])
    tokens = PGDataTokensSerializer(many=True)

