import logging
from django.conf import settings
from rest_framework.views import APIView
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
from .serializers import VerifierSerializer

logger = logging.getLogger(__name__)


class VerifierListView(APIView):
    """
    Verifier List
    """
    permission_classes = [HasAPIKey]

    def get(self, request):
        verifiers = Verifier.objects.all()
        serializer = VerifierSerializer(verifiers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = VerifierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.info("verifier_create_view: serializer.errors: %s" % serializer.errors)
        return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)


class VerifierDetailView(APIView):
    """
    Verifier Detail
    """
    permission_classes = [HasAPIKey]

    def get(self, request, verifier_id):
        verifier = Verifier.objects.get(id=verifier_id)
        serializer = VerifierSerializer(verifier)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # update
    def patch(self, request, verifier_id):
        verifier = Verifier.objects.get(id=verifier_id)
        serializer = VerifierSerializer(verifier, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.info("verifier_create_view: serializer.errors: %s" % serializer.errors)
        return Response({'message': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

    # delete
    def delete(self, request, verifier_id):
        verifier = Verifier.objects.get(id=verifier_id)
        verifier.delete()
        return Response({'message': 'deleted'}, status=status.HTTP_200_OK)

def get_contract_and_verifier(contract_id, verifier_id):
    """
    Retrieve a contract and verifier from the database based on their respective IDs.

    :param contract_id: The ID of the contract to retrieve.
    :param verifier_id: The ID of the verifier to retrieve.

    :return: A tuple containing the contract and verifier objects if found, or (None, None) if not found.
    """
    contract = Contract.objects.filter(pk=contract_id).first()
    verifier = Verifier.objects.filter(pk=verifier_id).first()
    return contract, verifier


def check_required_params(request, required_params):
    """
    Check if all the required parameters are present in the request data.

    :param request: The HTTP request object containing the data to be checked.
    :param required_params: A list of parameter names that are required in the request data.

    :return: None if all required parameters are present, or a response with an error message if any are missing.
    """
    missing_params = [param for param in required_params if param not in request.data]
    if missing_params:
        return Response({'message': f'Required parameters missing: {", ".join(missing_params)}'}, status=status.HTTP_400_BAD_REQUEST)
    return None


def validate_ticket(request, operation):
    """
    Validate and process a ticket based on the provided operation.

    :param request: The HTTP request object containing the ticket data to be validated and processed.
    :param operation: A string indicating the ticket operation ('validate' or 'redeem') to be performed.

    :return: Response containing the result of the validation or redemption operation.
    """
    required_params = ['user_wallet', 'T2', 'nft_id', 'contract_id', 'verifier_id']
    error_response = check_required_params(request, required_params)
    if error_response:
        return error_response

    contract_id = request.data['contract_id']
    verifier_id = request.data['verifier_id']

    contract, verifier = get_contract_and_verifier(contract_id, verifier_id)

    if contract is None:
        return Response({'message': 'contract not found'}, status=status.HTTP_400_BAD_REQUEST)

    if verifier is None:
        return Response({'message': 'verifier not found'}, status=status.HTTP_400_BAD_REQUEST)

    contract_address = contract.contract_address

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

    success, token_balance = check_balance_of_token(contract_address, request.data['nft_id'], user_wallet)
    if not success:
        return Response({'message': token_balance}, status=status.HTTP_400_BAD_REQUEST)
    logging.info("token_balance: {}".format(token_balance))

    token = contract.tokens.filter(nft_id=request.data['nft_id']).first()
    if token is None:
        return Response({'message': 'token not found'}, status=status.HTTP_400_BAD_REQUEST)

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

    if operation == 'redeem':
        verified_ticket = VerifiedTicket.objects.create(verifier=verifier,
                                                        user_wallet=user_wallet,
                                                        contract_address=contract_address,
                                                        nft_id=request.data['nft_id'],
                                                        amount=token_balance)
        verified_ticket.save()

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
            'nft_id': openapi.Schema('nft_id', type=openapi.TYPE_INTEGER,
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
    return validate_ticket(request, 'validate')


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
            'nft_id': openapi.Schema('nft_id', type=openapi.TYPE_INTEGER,
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
                                          description="redeemed token balance of the user's wallet address from "
                                                      "on-chain"),
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
def redeem_ticket(request):
    """
    Redeem Ticket
    ---
    """
    return validate_ticket(request, 'redeem')
