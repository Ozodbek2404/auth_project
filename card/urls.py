from django.urls import path
from .views import *

urlpatterns = [
    path('cart/', CartView.as_view()),
    path('add/', CartAddView.as_view()),
    path('delete/', CartRemoveView.as_view()),
    path('update/', CartUpdateView.as_view()),
    path('clear/', CartClearView.as_view()),
]