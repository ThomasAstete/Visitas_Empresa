from django.contrib.auth.models import Group, User
from rest_framework import serializers
from .models import Visita

class VisitaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Visita
        fields = [
            "url",
            "nombre",
            "rut",
            "motivo",
            "hora_entrada",
            "hora_salida"
            ]

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]