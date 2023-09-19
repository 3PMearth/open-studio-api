import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_api_key.permissions import HasAPIKey
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from .serializers import UserSerializer
from orders.serializers import OrderSerializer, OrderTokenSerializer
from orders.models import OrderToken, Order
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


class UserModifyView(APIView):
    """
    User Modification and Get user detail
    ---
    """

    @staticmethod
    def get_user(user_id):
        return User.objects.filter(id=user_id).first()

    permission_classes = [HasAPIKey]

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: UserSerializer,
                   status.HTTP_404_NOT_FOUND: "if user is not found"}
    )
    def get(self, request, user_id):
        user = self.get_user(user_id)
        if user is None:
            return Response({'message': 'not found user'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={status.HTTP_200_OK: UserSerializer,
                   status.HTTP_404_NOT_FOUND: "if user is not found"}
    )
    def patch(self, request, user_id):
        user = self.get_user(user_id)
        if user is None:
            return Response({'message': 'not found user'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'successfully modified user',
                             'user': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='GET',
    responses={201: UserSerializer,
               400: "Bad Request"}
)
@api_view(['GET'])
@permission_classes([HasAPIKey])
def user_detail_view_by_slug(request, user_slug):
    """
    Get user detail by user slug
    ---
    """
    user = User.objects.filter(slug=user_slug).first()
    if user is None:
        return Response({'message': 'not found user'}, status=status.HTTP_404_NOT_FOUND)
    else:
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    responses={201: OrderSerializer,
               400: "Bad Request"}
)
@api_view(['GET'])
@permission_classes([HasAPIKey])
def user_purchase_list(request, user_id):
    """
    User purchase all order list
    ---
    """
    user = User.objects.filter(id=user_id).first()
    if user is None:
        return Response({'message': 'not found user'}, status=status.HTTP_404_NOT_FOUND)
    else:
        orders = user.orders.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    responses={201: OrderSerializer,
               400: "Bad Request"}
)
@api_view(['GET'])
@permission_classes([HasAPIKey])
def user_sale_list(request, user_id):
    """
    User sale all token list
    """
    user = User.objects.filter(id=user_id).first()
    if user is None:
        return Response({'message': 'not found user'}, status=status.HTTP_404_NOT_FOUND)
    else:
        # todo : check request user is the owner of tokens, preventing other user to see other user's sale list
        orders = Order.objects.filter(order_tokens__token__user=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
