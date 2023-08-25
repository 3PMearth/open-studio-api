import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_api_key.permissions import HasAPIKey
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserSerializer
from .models import User

logger = logging.getLogger(__name__)
logger.setLevel('INFO')

@swagger_auto_schema(
    method='GET',
    responses={
        200: openapi.Response(
            description='Successful response',
            schema=UserSerializer
        ),
        404: openapi.Response(
            description='User not found',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='not found user'
                    )
                }
            )
        )
    }
)
@api_view(['GET'])
@permission_classes([HasAPIKey])
def user_detail_view(request, wallet_address):
    """
    User Detail View search by wallet address
    ---
    wallet_address: wallet address of the user(start from 0x)
    """
    logger.info("user_detail_view: wallet_address: %s" % wallet_address)
    try:
        user = User.objects.get(wallet_address=wallet_address)
    except User.DoesNotExist:
        return Response({'message': 'not found user'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user)
    return Response(serializer.data)

@swagger_auto_schema(
    method='POST',
    request_body=UserSerializer,
    responses={201: UserSerializer,
               400: "Bad Request"}
)
@api_view(['POST'])
@permission_classes([HasAPIKey])
def user_create_view(request):
    """
    User Create
    ---
    """
    logger.info("user_create_view: request.data: %s" % request.data)
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'successfully created user',
                         'user': serializer.data}, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='PATCH',
    request_body=UserSerializer,
    responses={201: UserSerializer,
               400: "Bad Request"}
)
@api_view(['PATCH', 'GET'])
@permission_classes([HasAPIKey])
def user_modify_view(request, user_id):
    """
    User Modification and Get user detail
    ---
    """
    user = User.objects.filter(id=user_id).first()
    if user is None:
        return Response({'message': 'not found user'}, status=status.HTTP_404_NOT_FOUND)
    else:
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'successfully modified user',
                                 'user': serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    responses={201: UserSerializer,
               400: "Bad Request"}
)
@api_view(['GET'])
@permission_classes([HasAPIKey])
def user_detail_view_by_slug(request, user_slug):
    """tb_tokens_assets
    Get user detail by user slug
    ---
    """
    user = User.objects.filter(slug=user_slug).first()
    if user is None:
        return Response({'message': 'not found user'}, status=status.HTTP_404_NOT_FOUND)
    else:
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

