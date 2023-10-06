import logging
from django.conf import settings
from drf_yasg import openapi
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from contracts.models import Contract
from Crypto.Hash import SHA256
from web3 import Web3
from django.shortcuts import render
from .models import Verifier, VerifiedTicket

logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method='POST',
    request_body=openapi.Schema(
        'request_body',
        type=openapi.TYPE_OBJECT,
        properties={
            'user_wallet': openapi.Schema('user_wallet', type=openapi.TYPE_STRING),
            'T2': openapi.Schema('T2', type=openapi.TYPE_STRING),
            'nft_id': openapi.Schema('nft_id', type=openapi.TYPE_STRING),
            'verifier_id': openapi.Schema('verifier_id', type=openapi.TYPE_INTEGER),
            'contract_id': openapi.Schema('contract_id', type=openapi.TYPE_INTEGER)
        }
    ),
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'balance': openapi.Schema('balance', type=openapi.TYPE_INTEGER),
                'is_valid': openapi.Schema('is_valid', type=openapi.TYPE_BOOLEAN),
                'contract_address': openapi.Schema('contract_address', type=openapi.TYPE_STRING),
                'nft_id': openapi.Schema('nft_id', type=openapi.TYPE_INTEGER),
                'user_wallet': openapi.Schema('user_wallet', type=openapi.TYPE_STRING),
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([HasAPIKey])
def balance_validate_check(request):
    """
    Token balance (by on-chain) and Validation check
    ---
    """
    # check all the required parameters are in request.data
    required_params = ['user_wallet', 'T2', 'nft_id', 'contract_id', 'verifier_id']
    for param in required_params:
        if param not in request.data:
            return Response({'message': 'required parameter missing'}, status=status.HTTP_400_BAD_REQUEST)
    contract = Contract.objects.filter(pk=request.data['contract_id']).first()
    if contract is None:
        return Response({'message': 'contract not found'}, status=status.HTTP_400_BAD_REQUEST)
    contract_address = contract.contract_address
    verifier = Verifier.objects.filter(pk=request.data['verifier_id']).first()
    if verifier is None:
        return Response({'message': 'verifier not found'}, status=status.HTTP_400_BAD_REQUEST)
    # check the verifier is legitimate or not
    if verifier.contract.contract_address != contract_address:
        return Response({'message': 'invalid verifier id'}, status=status.HTTP_400_BAD_REQUEST)
    # check the verifier is active or not
    if not verifier.active:
        return Response({'message': 'verifier is not active'}, status=status.HTTP_400_BAD_REQUEST)
    user_wallet = request.data['user_wallet']
    verifier_code = verifier.verifier_code
    secret_shared_token = settings.SECRET_SHARED_TOKEN
    data_to_sign = str(request.data['nft_id']) + str(request.data['verifier_id']) + \
                   contract_address.lower() + user_wallet.lower() + secret_shared_token + verifier_code
    hash_obj = SHA256.new(data=data_to_sign.encode())
    calculated_t2 = hash_obj.hexdigest()
    logging.info("data_to_sign: {}".format(data_to_sign))
    logging.info("calculated_t2: {}".format(calculated_t2))
    if calculated_t2 != request.data['T2']:
        return Response({'message': 'invalid T2'}, status=status.HTTP_400_BAD_REQUEST)

    # check the ticket is already verified or not, by matching verifier_id, user_wallet, nft_id
    verified_ticket = VerifiedTicket.objects.filter(verifier=verifier,
                                                    user_wallet=user_wallet,
                                                    nft_id=request.data['nft_id']).first()
    if verified_ticket is not None:
        return Response({'message': 'already verified',
                         'redeemed_date': verified_ticket.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                         'nft_id': verified_ticket.nft_id,
                         'contract_address': verified_ticket.contract_address,
                         'user_wallet': verified_ticket.user_wallet,
                         'redeemed_balance': verified_ticket.amount,
                         }, status=status.HTTP_400_BAD_REQUEST)

    # check the balance of the ticket(token) from on-chain
    # todo : here

    return Response({'message': 'success'}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='POST',
    request_body=openapi.Schema(
        'request_body',
        type=openapi.TYPE_OBJECT,
        properties={
            'user_wallet': openapi.Schema('user_wallet', type=openapi.TYPE_STRING),
            'T2': openapi.Schema('T2', type=openapi.TYPE_STRING),
            'contract_address': openapi.Schema('contract_address', type=openapi.TYPE_STRING),
            'nft_id': openapi.Schema('nft_id', type=openapi.TYPE_INTEGER),
        }
    ),
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'balance': openapi.Schema('balance', type=openapi.TYPE_INTEGER),
                'validity': openapi.Schema('validity', type=openapi.TYPE_BOOLEAN),
                'message': openapi.Schema('message', type=openapi.TYPE_STRING),
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([HasAPIKey])
def redeem_ticket(request):
    """
    Redeem Ticket
    ---
    """
    logger.info("redeem_ticket: request.data: %s" % request.data)
    return Response({'message': 'success'}, status=status.HTTP_200_OK)
