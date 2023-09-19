from rest_framework import status, viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_api_key.permissions import HasAPIKey
import logging

from .models import Contract
from tokens.models import Token
from tokens.serializers import TokenSerializer
from .serializers import ContractSerializer

# Create your views here.
logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method='GET',
    responses={status.HTTP_200_OK: ContractSerializer,
               status.HTTP_404_NOT_FOUND: "if contract is not found"}
)
@api_view(['GET'])
@permission_classes([HasAPIKey])
def contract_list_view(request):
    """
    Contract List
    """
    contracts = Contract.objects.filter(active=True).all()
    if len(contracts) == 0:
        return Response({'status': 'not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        serializer = ContractSerializer(contracts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'description': openapi.Schema('description in English', type=openapi.TYPE_STRING),
                'image': openapi.Schema('cover image url', type=openapi.TYPE_STRING),
                'name': openapi.Schema('contract name', type=openapi.TYPE_STRING),
                'seller_fee_basis_points': openapi.Schema('seller fee basis points', type=openapi.TYPE_INTEGER),
            }
        ),
        status.HTTP_404_NOT_FOUND: "if contract is not found"}
)
@api_view(['GET'])
def contract_metadata_view(request, contract_id):
    """
    Contract Metadata for Opensea
    """
    try:
        contract = Contract.objects.filter(active=True).get(pk=contract_id)
    except Contract.DoesNotExist:
        logger.info("contract_metadata_view: contract does not exist")
        return Response({'status': 'not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ContractSerializer(contract)
    # change the response format to match the opensea metadata format
    response = {
        "description": serializer.data['description_en'],
        "image": serializer.data['cover_img'],
        "name": serializer.data['name'],
        "seller_fee_basis_points": 1000,
    }
    return Response(response, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'description': openapi.Schema('description in English', type=openapi.TYPE_STRING),
                'image': openapi.Schema('token image url', type=openapi.TYPE_STRING),
                'name': openapi.Schema('token name', type=openapi.TYPE_STRING),
                'animation_url': openapi.Schema('animation url', type=openapi.TYPE_STRING),
            }
        ),
        status.HTTP_404_NOT_FOUND: "if token is not found"}
)
@api_view(['GET'])
def token_metadata_view(request, contract_id, nft_id):
    """
    Token Metadata for Opensea
    """
    try:
        token = Token.objects.filter(contract__id=contract_id).get(nft_id=nft_id)
    except Token.DoesNotExist:
        logger.info("token_metadata_view: token does not exist")
        return Response({'status': 'not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TokenSerializer(token)
    # change the response format to match the opensea metadata format
    response = {
        "description": serializer.data['description_en'],
        "image": serializer.data['token_img'],
        "name": serializer.data['name'],
        "animation_url": serializer.data['animation'] or "",
    }
    return Response(response, status=status.HTTP_200_OK)
