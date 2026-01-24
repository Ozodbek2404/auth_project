from django.urls import path
from .views import *

urlpatterns = [
    path('craete/', OrderCreateView.as_view()),
    path('list/', OrderListView.as_view()),
    path('detail/<int:pk>', OrderDetailView.as_view()),
    path('status/<int:pk>', OrderStatusView.as_view()),
    path('cancel/<int:pk>', OrderCancellView.as_view()),
]


