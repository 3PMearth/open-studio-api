import logging
import time
from django.http import HttpResponseRedirect
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from tokens.models import Token
from users.models import User
from .serializers import PGDataSerializer
from nested_multipart_parser import NestedParser
from rest_framework.parsers import MultiPartParser

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
            error_redirect_url = "{}?error_message=\'sum_amount/sum_price is mismatched\'".format(validate_data['error_url'], "invalid_data")
            return HttpResponseRedirect(error_redirect_url)

        #  check the user is existed
        user_id = validate_data['user_id']
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logger.info("user does not exist, user_id : {}".format(user_id))
            error_redirect_url = "{}?error_message=\'user does not exist\'".format(validate_data['error_url'], "invalid_data")
            return HttpResponseRedirect(error_redirect_url)
        # update country_code, phone_number
        user.country_code = validate_data['country_code']
        user.phone_number = validate_data['phone_number']
        user.save()


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
