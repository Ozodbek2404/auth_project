from django.db import transaction
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from card.models import Cart
from order.models import Order, OrderItem
from order.serializers import OrderItemSerializer, OrderSerializer


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = Cart.objects.get(user=request.user)

        if not cart.items.exists():
            return Response({"error": "Savat bo`sh"}, status=400)

        order = Order.objects.create(user=request.user)
        total = 0

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.products,
                price=item.product.price,
                quantity=item.quantity
            )
            total += item.product.price * item.quantity

        order.total_price = total
        order.save()

        cart.items.all().delete()

        return Response({"detail": "Buyurtma yaratildi", "order_id": order.id})


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        order = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        order = Order.objects.get(id=id, users=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class OrderStatusView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, id):
        status_value = request.data.get("status")
        order = Order.objects.get(id=id)
        order.status = status_value
        order.save()
        return Response({"detail": "Status yangilandi"})


class OrderCancelView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request, id):
        order = get_object_or_404(Order, id=id, user=request.user)

        if order.status not in ["new", "pending"]:
            return Response(
                {"error": "Bu buyurtmani bekor qilib bo‘lmaydi"},
                status=status.HTTP_400_BAD_REQUEST
            )

        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()

        order.status = "cancelled"
        order.save()

        return Response({"detail": "Buyurtma bekor qilindi"})
