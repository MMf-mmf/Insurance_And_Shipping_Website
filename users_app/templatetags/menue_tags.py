from django import template
from pricing_app.models import ShipmentFile

register = template.Library()

@register.simple_tag
def cart_count(request):
    if request.user.is_authenticated:
        cart_count = ShipmentFile.objects.filter(in_cart=True, user_id=request.user.id).count()
    else:
        cart_count = 0
    return cart_count