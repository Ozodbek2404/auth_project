from django.db import models

from django.conf import settings
from products.models import Product

User = settings.AUTH_USER_MODEL
from shared.models import BaseModel


class Cart(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")


    def __str__(self):
        return f"{self.user} cart"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product.title} ({self.quantity})"
