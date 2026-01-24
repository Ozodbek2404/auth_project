from .views import ProdactViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'products', ProdactViewSet, basename='product')
urlpattern = router.urls