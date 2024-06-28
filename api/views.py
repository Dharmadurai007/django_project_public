from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Account, Destination
from .serializers import AccountSerializer, DestinationSerializer
import requests

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.destinations.all().delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

@api_view(['POST'])
def incoming_data(request):
    token = request.headers.get('CL-X-TOKEN')
    if not token:
        return Response({"error": "Un Authenticate"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        account = Account.objects.get(app_secret_token=token)
    except Account.DoesNotExist:
        return Response({"error": "Un Authenticate"}, status=status.HTTP_401_UNAUTHORIZED)

    if not request.data:
        return Response({"error": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)

    for destination in account.destinations.all():
        headers = destination.headers
        url = destination.url
        method = destination.http_method.lower()
        
        if method == 'get':
            response = requests.get(url, headers=headers, params=request.data)
        elif method in ['post', 'put']:
            response = requests.request(method, url, headers=headers, json=request.data)
        
        if response.status_code >= 400:
            return Response({"error": f"Failed to send data to {url}"}, status=response.status_code)

    return Response({"success": "Data sent to all destinations"}, status=status.HTTP_200_OK)
