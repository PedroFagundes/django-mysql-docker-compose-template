from rest_framework.serializers import ModelSerializer

from .models import Lead


class LeadSerializer(ModelSerializer):
    class Meta:
        model = Lead
        fields = ['email', 'last_interaction']
