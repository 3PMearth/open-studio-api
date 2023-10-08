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
from utils.common import check_balance_of_token, validate_t2
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
            'user_wallet': openapi.Schema('user_wallet', type=openapi.TYPE_STRING,
                                          description="wallet address of the user"),
            'T2': openapi.Schema('T2', type=openapi.TYPE_STRING,
                                 description="calculated by the scheme"),
            'nft_id': openapi.Schema('nft_id', type=openapi.TYPE_STRING,
                                     description="NFT ID(ERC1155 token ID)"),
            'verifier_id': openapi.Schema('verifier_id', type=openapi.TYPE_INTEGER,
                                          description="registered verifier id"),
            'contract_id': openapi.Schema('contract_id', type=openapi.TYPE_INTEGER,
                                          description="registered contract id")
        }
    ),
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'balance': openapi.Schema('balance', type=openapi.TYPE_INTEGER,
                                          description="token balance of the user's wallet address from on-chain"),
                'contract_address': openapi.Schema('contract_address', type=openapi.TYPE_STRING,
                                                   description="contract address of the ticket"),
                'nft_id': openapi.Schema('nft_id', type=openapi.TYPE_INTEGER,
                                         description="NFT ID(ERC1155 token ID)"),
                'user_wallet': openapi.Schema('user_wallet', type=openapi.TYPE_STRING,
                                              description="wallet address of the user"),
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
    missing_params = [param for param in required_params if param not in request.data]

    if missing_params:
        return Response({'message': f'Required parameters missing: {", ".join(missing_params)}'},
                        status=status.HTTP_400_BAD_REQUEST)

    contract_id = request.data['contract_id']
    verifier_id = request.data['verifier_id']

    contract = Contract.objects.filter(pk=contract_id).first()
    verifier = Verifier.objects.filter(pk=verifier_id).first()

    contract_address = contract.contract_address

    if contract is None:
        return Response({'message': 'contract not found'}, status=status.HTTP_400_BAD_REQUEST)

    if verifier is None:
        return Response({'message': 'verifier not found'}, status=status.HTTP_400_BAD_REQUEST)

    if verifier.contract.contract_address != contract_address:
        return Response({'message': 'Invalid verifier ID'}, status=status.HTTP_400_BAD_REQUEST)

    if not verifier.active:
        return Response({'message': 'Verifier is not active'}, status=status.HTTP_400_BAD_REQUEST)

    user_wallet = request.data['user_wallet']
    verifier_code = verifier.verifier_code
    (success, message) = validate_t2(request.data['nft_id'], verifier_id, contract_address, user_wallet,
                                     verifier_code, request.data['T2'])
    if not success:
        return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)

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
    success, token_balance = check_balance_of_token(contract_address, request.data['nft_id'], user_wallet)
    if not success:
        return Response({'message': token_balance}, status=status.HTTP_400_BAD_REQUEST)
    logging.info("token_balance: {}".format(token_balance))

    # check the validity of the ticket
    token = contract.tokens.filter(nft_id=request.data['nft_id']).first()

    if token is None:
        return Response({'message': 'token not found'}, status=status.HTTP_400_BAD_REQUEST)
    if token.stock < token_balance:
        return Response({'message': 'invalid token balance'}, status=status.HTTP_400_BAD_REQUEST)

    response_data = {
        'balance': token_balance,
        'contract_address': contract_address,
        'nft_id': request.data['nft_id'],
        'user_wallet': user_wallet,
    }
    return Response(response_data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='POST',
    request_body=openapi.Schema(
        'request_body',
        type=openapi.TYPE_OBJECT,
        properties={
            'user_wallet': openapi.Schema('user_wallet', type=openapi.TYPE_STRING,
                                          description="wallet address of the user"),
            'T2': openapi.Schema('T2', type=openapi.TYPE_STRING,
                                 description="calculated by the scheme"),
            'contract_address': openapi.Schema('contract_address', type=openapi.TYPE_STRING,
                                               description="contract address of the ticket"),
            'nft_id': openapi.Schema('nft_id', type=openapi.TYPE_INTEGER,
                                     description="NFT ID(ERC1155 token ID)"),
        }
    ),
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'balance': openapi.Schema('balance', type=openapi.TYPE_INTEGER,
                                          description="token balance of the user's wallet address from on-chain"),
                'validity': openapi.Schema('validity', type=openapi.TYPE_BOOLEAN,
                                           description="validity of the ticket"),
                'message': openapi.Schema('message', type=openapi.TYPE_STRING,
                                          description="message"),
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
