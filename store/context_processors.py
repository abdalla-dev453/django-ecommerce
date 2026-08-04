from .cart import Cart

# To show the cart in the context of every template, we can create a context processor that adds the cart to the context. This way, we can access the cart in any template without having to pass it explicitly from each view.
def cart(request):
    """Context processor to add the cart to the context"""
    return {'cart': Cart(request)}