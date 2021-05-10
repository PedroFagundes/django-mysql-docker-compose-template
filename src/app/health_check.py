from django.http.response import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@swagger_auto_schema(method='get', operation_description="Service health check endpoint")
@api_view(['GET'])
@permission_classes((AllowAny,))
def health_check(request):
    return HttpResponse("I'm feeling healthy :)")
