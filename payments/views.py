import logging
import time
from django.http import HttpResponseRedirect
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from tokens.models import Token

logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method='POST',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'tokens': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT, description='Token ID and Amount',
                    properties={
                        'token_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Token ID'),
                        'amount': openapi.Schema(type=openapi.TYPE_INTEGER, description='Amount to checkout'),
                    },
                ),
            ),
            'user_address': openapi.Schema(type=openapi.TYPE_STRING, description='Buyer User Wallet Address'),
            'return_url': openapi.Schema(type=openapi.TYPE_STRING, description='redirect URL when payment is done'),
            'country_code': openapi.Schema(type=openapi.TYPE_STRING, description='Country Code(e.g., +82)'),
            'sso_type': openapi.Schema(type=openapi.TYPE_STRING, description='SSO Type'),
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone Number(without 0)(e.g., '
                                                                                 '1012345678)'),
            'outofstock_url': openapi.Schema(type=openapi.TYPE_STRING, description='redirect URL when out of stock'),
            'sum_amount': openapi.Schema(type=openapi.TYPE_INTEGER, description='sum of amount'),
            'sum_price': openapi.Schema(type=openapi.FORMAT_FLOAT, description='sum of price'),
            'currency': openapi.Schema(type=openapi.TYPE_STRING, description='Currency(krw, usd)'),
        },
        required=['tokens', 'user_address', 'return_url', 'country_code', 'sso_type', 'phone_number', 'outofstock_url', 'sum_amount', 'sum_price', 'currency'],
    ),
    responses={200: "OK",
                400: "Bad Request"}
)
@api_view(['POST'])
@permission_classes([HasAPIKey])
def request_payment(request):
    """
    Request Payment (depends on which PG you choose
    ---
    PG is not implemented yet. It depends on the client's choice of PG
    """
    # all required fields are in request.data
    required_fields = ['tokens', 'user_address', 'return_url', 'country_code', 'sso_type', 'phone_number', 'outofstock_url', 'sum_amount', 'sum_price', 'currency']
    for field in required_fields:
        if field not in request.data:
            logger.info("field %s is not in request.data" % field)
            return Response({'status': 'invalid request'}, status=status.HTTP_400_BAD_REQUEST)

    # check sum_amount is equal to sum of amount
    sum_amount = int(request.data['sum_amount'])
    sum_price = float(request.data['sum_price'])
    # check sum_amount and sum_price
    if sum_amount <= 0 or sum_price <= 0:
        return Response({'status': 'invalid sum_amount/sum_price'}, status=status.HTTP_400_BAD_REQUEST)
    currency = request.data['currency']
    # check currency is valid
    if currency != 'krw' and currency != 'usd':
        return Response({'status': 'invalid currency'}, status=status.HTTP_400_BAD_REQUEST)
    cal_sum_price = 0
    cal_amount = 0
    for token_item in request.data['tokens']:
        token_id = token_item['token_id']
        token = Token.objects.get(pk=token_id)
        cal_amount += int(token_item['amount'])
        if currency == 'krw':
            cal_sum_price += float(token.price_krw) * int(token_item['amount'])
        elif currency == 'usd':
            cal_sum_price += float(token.price_usd) * int(token_item['amount'])
    logger.info("sum_amount: %d, cal_amount: %d" % (sum_amount, cal_amount))
    logger.info("sum_price: %d, cal_sum_price: %d" % (sum_price, cal_sum_price))
    if sum_amount != cal_amount:
        return Response({'status': 'invalid sum_amount'}, status=status.HTTP_400_BAD_REQUEST)
    if sum_price != float(cal_sum_price):
        return Response({'status': 'invalid sum_price'}, status=status.HTTP_400_BAD_REQUEST)

    # check user_address is valid
    user_address = request.data['user_address']
    if len(user_address) != 42:
        return Response({'status': 'invalid user_address'}, status=status.HTTP_400_BAD_REQUEST)

    # check country_code is valid
    country_code = request.data['country_code']
    if len(country_code) != 3:
        return Response({'status': 'invalid country_code'}, status=status.HTTP_400_BAD_REQUEST)

    # check stocks
    for token_item in request.data['tokens']:
        token_id = token_item['token_id']
        token = Token.objects.get(pk=token_id)
        if token.stock < int(token_item['amount']):
            return Response({'status': 'out of stock'}, status=status.HTTP_400_BAD_REQUEST)

    # sleep 2 seconds for testing
    time.sleep(2)

    #--------------------------------------
    # PG is not implemented yet
    #--------------------------------------
    # request payment to PG here

    # if payment is done, update stocks and redirect to return_url
    payment_status = True
    if payment_status:
        return HttpResponseRedirect('%s' % request.data['return_url'])
    else:
        return HttpResponseRedirect('%s' % request.data['outofstock_url'])


@api_view(['POST'])
def payment_webhook(request):
    """
    Payment Webhook (PG webhook)
    ---
    webhook for payment result, transferring NFTs and updating stocks
    """
    # 1. check integrity of request here
    # 2. transfer NFTs (async)
    # 3. update stocks
    # 4. update payment status
    return Response({'status': 'ok'}, status=status.HTTP_200_OK)
