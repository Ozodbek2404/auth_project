
from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', SignUpView.as_view()),
    path('code-verify/', VerifyCode.as_view()),
    path('new-code-verify/', NewVerifyCode.as_view()),
    path('user-change-info/', UserChangeView.as_view()),
    path('upload-photo/', UserPhotoUploadView.as_view())
]