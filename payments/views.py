import logging
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from tokens.models import Token
from datetime import datetime
from users.models import User
from orders.models import Order, OrderToken
from .serializers import PGDataSerializer
from nested_multipart_parser import NestedParser
from uuid import uuid4

logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method='POST',
    request_body=PGDataSerializer,
)
@api_view(['POST'])
@permission_classes([HasAPIKey])
def request_payment(request):
    """
    Request Payment (depends on which PG you choose), use form-data
    ---
    PG is not implemented yet. It depends on the client's choice of PG
    """
    # all required fields are in request.data
    parser = NestedParser(data=request.data)
    if not parser.is_valid():
        logger.info("error : {}".format(parser.errors))
        #redirect to error page
        error_redirect_url = "{}?error_message=\'{}\'".format(request.data.get('error_url'), "invalid_data")
        return HttpResponseRedirect(error_redirect_url)
    else:
        validate_data = parser.validate_data
        payment_serializer = PGDataSerializer(data=validate_data)
        if not payment_serializer.is_valid():
            logger.info("error : {}".format(payment_serializer.errors))
            # redirect to error page
            error_redirect_url = "{}?error_message=\'{}\'".format(validate_data['error_url'], "invalid_data")
            return HttpResponseRedirect(error_redirect_url)

        sum_amount = int(validate_data['sum_amount'])
        sum_price = float(validate_data['sum_price'])
        # sum of all the tokens' amount and price
        cal_sum_amount = 0
        cal_sum_price = 0
        currency = validate_data['currency']
        for token in validate_data['tokens']:
            cal_sum_amount += int(token['amount'])
            if currency == 'krw':
                cal_sum_price += float(Token.objects.get(pk=token['token_id']).price_krw) * int(token['amount'])
            else:
                cal_sum_price += float(Token.objects.get(pk=token['token_id']).price) * int(token['amount'])

        if sum_amount != cal_sum_amount or sum_price != cal_sum_price:
            logger.info("sum_amount is not equal to sum of amount")
            logger.info("sum_amount: {}, sum_price: {}".format(sum_amount, sum_price))
            logger.info("cal_sum_amount: {}, cal_sum_price: {}".format(cal_sum_amount, cal_sum_price))
            error_redirect_url = "{}?error_message=\'sum_amount/sum_price is mismatched\'".format(validate_data['error_url'])
            return HttpResponseRedirect(error_redirect_url)

        #  check the user is existed
        user_id = validate_data['user_id']
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logger.info("user does not exist, user_id : {}".format(user_id))
            error_redirect_url = "{}?error_message=\'user does not exist\'".format(validate_data['error_url'])
            return HttpResponseRedirect(error_redirect_url)

        country_code = validate_data['country_code']
        phone_number = validate_data['phone_number']

        # check stock of tokens
        for token in validate_data['tokens']:
            token_id = token['token_id']
            amount = int(token['amount'])
            try:
                token = Token.objects.get(pk=token_id)
            except Token.DoesNotExist:
                logger.info("token does not exist, token_id : {}".format(token_id))
                error_redirect_url = "{}?error_message=\'token does not exist\'".format(validate_data['error_url'])
                return HttpResponseRedirect(error_redirect_url)

            if token.stock < amount:
                logger.info("token stock is not enough, token_id : {}".format(token_id))
                error_redirect_url = "{}?error_message=\'token stock is not enough\'".format(validate_data['error_url'])
                return HttpResponseRedirect(error_redirect_url)

        # create new order
        order_number = datetime.now().strftime('%Y%m%d%H%M') + str(uuid4())[:5]
        new_order = Order(
            buyer=user,
            order_number=order_number,
            country_code=country_code,
            phone_number=phone_number,
            currency=currency,
            sum_amount=sum_amount,
            sum_price=sum_price,
            order_status='created',
        )
        new_order.save()

        for token in validate_data['tokens']:
            token_id = token['token_id']
            amount = token['amount']
            token = Token.objects.get(pk=token_id)
            if currency == 'krw':
                price = float(token.price_krw)
            else:
                price = float(token.price_usd)
            new_order_token = OrderToken(
                    order=new_order,
                    token=token,
                    amount=amount,
                    price=price,
                    currency=currency
            )
            new_order_token.save()


        # todo :  Call PG API here ### not implemented yet
        ##########################################

        # if success, redirect to success_url
        success_redirect_url = "{}?success_message=\'{}\'".format(request.data.get('success_url'), "success")
        return HttpResponseRedirect(success_redirect_url)



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
