from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey
from .serializers import OrderSerializer
from contracts.serializers import TransactionSerializer
from .models import Order
import logging

# Create your views here.
logger = logging.getLogger(__name__)

class OrderListView(APIView):
    """
    order detail view by order id
    """

    permission_classes = [HasAPIKey]
    @swagger_auto_schema(
        responses={status.HTTP_200_OK: OrderSerializer,
                   status.HTTP_404_NOT_FOUND: "if order is not found"}
    )
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'message': 'not found order'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    methods=['GET'],
    responses={status.HTTP_200_OK: TransactionSerializer,
               status.HTTP_404_NOT_FOUND: "if order is not found"}
)
@api_view(['GET'])
@permission_classes([HasAPIKey])
def order_transaction_list(request, order_id):
    """
    order transaction list view by order id
    """
    try:
        transaction = Order.objects.get(id=order_id).transactions.all()
    except Order.DoesNotExist:
        return Response({'message': 'not found order'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TransactionSerializer(transaction, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




