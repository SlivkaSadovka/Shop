# myshop/shopapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.http import JsonResponse
from .models import Product, Category, Review, Cart, CartItem
from django.db.models import Q, Avg


# Главная страница
def index(request):
    context = {
        'popular_categories': Category.objects.all()[:8],
        'hit_products': Product.objects.filter(is_hit=True)[:8],
        'new_products': Product.objects.filter(is_new=True)[:8],
        'latest_reviews': Review.objects.all()[:6],
        'categories': Category.objects.all(),
    }
    return render(request, 'shopapp/index.html', context)


# Информационные страницы
class AboutView(TemplateView):
    template_name = 'shopapp/about.html'


class DeliveryView(TemplateView):
    template_name = 'shopapp/delivery.html'


class ContactsView(TemplateView):
    template_name = 'shopapp/contacts.html'


class HowToOrderView(TemplateView):
    template_name = 'shopapp/how_to_order.html'


class ReturnsView(TemplateView):
    template_name = 'shopapp/returns.html'


class FAQView(TemplateView):
    template_name = 'shopapp/faq.html'


# Временная заглушка для LoginView (потом замените на свою)
class LoginView(TemplateView):
    template_name = 'shopapp/login.html'


class RegisterView(TemplateView):
    template_name = 'shopapp/register.html'


class ProfileView(TemplateView):
    template_name = 'shopapp/profile.html'


class OrdersView(TemplateView):
    template_name = 'shopapp/orders.html'


# Каталог
class CatalogView(ListView):
    model = Product
    template_name = 'shopapp/catalog.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.all()

        # Фильтрация по цене
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)

        # Фильтрация по категориям
        category_ids = self.request.GET.getlist('categories')
        if category_ids:
            queryset = queryset.filter(category_id__in=category_ids)

        # Сортировка
        sort = self.request.GET.get('sort', 'popular')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'new':
            queryset = queryset.order_by('-created_at')
        elif sort == 'rating':
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class CategoryView(ListView):
    model = Product
    template_name = 'shopapp/category.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Product.objects.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_category'] = self.category
        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'shopapp/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'


# Поиск
class SearchView(ListView):
    model = Product
    template_name = 'shopapp/search_results.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )
        return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


# Акции, хиты, новинки
class SalesView(ListView):
    model = Product
    template_name = 'shopapp/sales.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(discount__gt=0)


class HitsView(ListView):
    model = Product
    template_name = 'shopapp/hits.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(is_hit=True)


class NewsView(ListView):
    model = Product
    template_name = 'shopapp/news.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(is_new=True)


# Избранное
class FavoritesView(TemplateView):
    template_name = 'shopapp/favorites.html'


# Корзина
class CartView(TemplateView):
    template_name = 'shopapp/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            context['cart_items'] = cart.cartitem_set.all()
            context['cart_total'] = sum(
                item.product.price * item.quantity
                for item in context['cart_items']
            )
        else:
            # Для неавторизованных пользователей - корзина в сессии
            cart = self.request.session.get('cart', {})
            context['cart_items'] = []
            context['cart_total'] = 0
        return context


def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': 1}
            )
            if not created:
                cart_item.quantity += 1
                cart_item.save()
        else:
            # Сохраняем в сессии
            cart = request.session.get('cart', {})
            cart[str(product_id)] = cart.get(str(product_id), 0) + 1
            request.session['cart'] = cart

        cart_count = sum(
            item.quantity for item in cart.cartitem_set.all()
        ) if request.user.is_authenticated else sum(cart.values())

        return JsonResponse({
            'success': True,
            'cart_count': cart_count,
        })
    return JsonResponse({'success': False})


# Подписка
class SubscribeView(View):
    def post(self, request):
        email = request.POST.get('email')
        if email:
            # Здесь логика сохранения email
            messages.success(request, 'Вы успешно подписались на рассылку!')
        return redirect('home')