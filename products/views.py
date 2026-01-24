from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import ProductSerializer
from .models import Product
from rest_framework import permissions

class ProdactViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

