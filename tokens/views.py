from rest_framework import status, viewsets
from django.db.models.signals import post_delete
from django.dispatch import receiver
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import logging
from drf_yasg.utils import swagger_auto_schema
from .models import Token, Asset
from .serializers import TokenSerializer, AssetSerializer
from rest_framework_api_key.permissions import HasAPIKey
from .tasks import mint_token



logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method='POST',
    request_body=TokenSerializer,
    responses={201: TokenSerializer,
               400: "Bad Request"}
)
@api_view(['POST'])
@permission_classes([HasAPIKey])
def token_create_view(request):
    """
    Token Create
    ---
    """
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        # todo : mint token
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    logger.info("token data : %s" % request.data)
    logger.info("token_create_view: serializer.errors: %s" % serializer.errors)
    return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='GET',
    responses={200: TokenSerializer,
               404: "해당하는 데이터가 없을 경우"}
)
@api_view(['GET'])
@permission_classes([HasAPIKey])
def token_list_view_by_user(request, user_id):
    """
    Token List owned by user
    ---
    """
    tokens = Token.objects.filter(user=user_id).all()
    if len(tokens) == 0:
        return Response({'status': 'not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        serializer = TokenSerializer(tokens, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH', 'GET'])
@permission_classes([HasAPIKey])
def token_update_get_view(request, token_id):
    """
    Token Update and Get token detail
    ---
    """
    if request.method == 'PATCH':
        token = Token.objects.filter(id=token_id).first()
        if token is None:
            return Response({'status': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = TokenSerializer(token, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            logger.info("token_update_view: serializer.errors: %s" % serializer.errors)
            return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        token = Token.objects.filter(id=token_id).first()
        if token is None:
            return Response({'status': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = TokenSerializer(token, many=False)
            #run celery task, mint_token on blockchain
            task = mint_token.delay(token.id)
            logger.info("celery task id : %s" % task.id)
            return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='PATCH',
    request_body=AssetSerializer,
    responses={200: AssetSerializer,
               404: "해당하는 데이터가 없을 경우"}
)
@api_view(['PATCH'])
@permission_classes([HasAPIKey])
def asset_update_view(request, asset_id):
    """
    Asset Update (only asset information)
    """
    asset = Asset.objects.filter(id=asset_id).first()
    if asset is None:
        return Response({'status': 'not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        serializer = AssetSerializer(asset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='DELETE',
    responses={204: "deleted",
               404: "해당하는 데이터가 없을 경우"}
)
@api_view(['DELETE'])
@permission_classes([HasAPIKey])
def asset_delete_view(request, asset_id):
    """
    Delete Asset
    """
    asset = Asset.objects.filter(id=asset_id).first()
    if asset is None:
        return Response({'status': 'not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        asset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# for delete S3 files
@receiver(post_delete, sender=Asset)
def submission_delete(sender, instance, **kwargs):
    instance.media.delete(False)

@receiver(post_delete, sender=Token)
def submission_delete(sender, instance, **kwargs):
    instance.token_img.delete(False)
    instance.animation.delete(False)

