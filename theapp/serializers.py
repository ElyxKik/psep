from rest_framework import serializers
from .models import Projet, Jalons, Tache

class ProjetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projet
        fields = '__all__'

class JalonsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jalons
        fields = '__all__'

class TacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tache
        fields = '__all__'
