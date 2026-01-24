from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from card.models import Cart, CartItem
from card.serializers import CartSerializer
from products.models import Product


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Mahsulot topilmadi"},
                status=404
            )

        if product.stock < quantity:
            return Response(
                {"error": "Mahsulot yetarli emas"},
                status=409
            )

        cart, _ = Cart.objects.get_or_create(user=request.user)
        product = Product.objects.get(id=product_id)

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product
        )

        if not created:
            item.quantity += quantity
        item.save()

        return Response({"detail": "Mahsulot savatga qo`shildi"})


class CartRemoveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("produst_id")
        cart = Cart.objects.get(user=request.user)
        deleted, _ = CartItem.objects.filter(
            cart=cart,
            product_id=product_id
        ).delete()

        if deleted == 0:
            return Response(
                {"error": "Mahsulot savatda topilmadi"},
                status=404
            )
        return Response({"detail": "Mahsulot savatdan o`chirildi"})


class CartUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 0))

        if quantity <= 0:
            return Response(
                {"error": "Quantity 1 dan katta bo‘lishi kerak"},
                status=400
            )

        cart = Cart.objects.get(user=request.user)

        try:
            item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Mahsulot savatda topilmadi"},
                status=404
            )

        if quantity > item.product.stock:
            return Response(
                {"error": "Mahsulot stocki yetarli emas"},
                status=409
            )

        item.quantity = quantity
        item.save()

        return Response({"detail": "Savat yangilandi"})


class CartClearView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = Cart.objects.get(user=request.user)
        cart.items.all().delete()
        return Response({"detail": "Savat tozalandi"})