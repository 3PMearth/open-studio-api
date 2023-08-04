from rest_framework import status, viewsets
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_api_key.permissions import HasAPIKey
import logging

from .models import Contract
from .serializers import ContractSerializer


# Create your views here.
logger = logging.getLogger(__name__)

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






