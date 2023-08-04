from rest_framework import serializers
from .models import Token, Asset
from users.models import User
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class AssetSerializer(serializers.ModelSerializer):
    """
    Asset Serializer
    """
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        return instance

    class Meta:
        model = Asset
        fields = ['id', 'name', 'type', 'media', 'download']


class TokenSerializer(serializers.ModelSerializer):
    """
    Token Serializer
    """
    assets = AssetSerializer(many=True, required=False, partial=True)

    def create(self, validated_data):
        has_assets = False
        if 'assets' in validated_data:
            assets_data = validated_data.pop('assets')
            has_assets = True
        else:
            logger.info("assets is not included in validated_data")

        user = validated_data.pop('user')
        # check the user is existed in user database
        user_f = User.objects.get(id=user.id)
        if user_f is None:
            logger.warning("user is not existed : {}".format(user.id))
            raise serializers.ValidationError("user is not existed")

        # get the last nft_id in the same contract
        last_nft_id = Token.objects.filter(contract=validated_data['contract']).order_by('-nft_id').first()
        logger.info("last_nft_id : {}".format(last_nft_id))
        if last_nft_id is None:
            logger.info("last_nft_id is None")
            validated_data['nft_id'] = 1
        else:
            if last_nft_id.nft_id is None:
                logger.info("last_nft_id.nft_id is None")
                validated_data['nft_id'] = 1
            else:
                validated_data['nft_id'] = last_nft_id.nft_id + 1

        token = Token.objects.create(**validated_data, user=user)

        if has_assets:
            for asset_data in assets_data:
                Asset.objects.create(token=token, **asset_data)
        return token

    def update(self, instance, validated_data):
        has_assets = False
        if 'assets' in validated_data:
            assets_data = validated_data.pop('assets')
            has_assets = True
        else:
            logger.info("assets is not included in validated_data")

        instance = super().update(instance, validated_data)

        return instance

    class Meta:
        model = Token
        fields = [field.name for field in Token._meta.fields]
        fields.append('assets')

