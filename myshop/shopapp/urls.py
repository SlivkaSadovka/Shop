# myshop/shopapp/urls.py
from django.urls import path
from . import views
from .views import (
    AboutView, DeliveryView, ContactsView, HowToOrderView,
    ReturnsView, FAQView, SearchView, CategoryView,
    ProductDetailView, SalesView, HitsView, NewsView,
    ProfileView, OrdersView, FavoritesView, CartView,
    SubscribeView, CatalogView
)

urlpatterns = [
    # Главная
    path('', views.index, name='home'),

    # Информационные страницы
    path('about/', AboutView.as_view(), name='about'),
    path('delivery/', DeliveryView.as_view(), name='delivery'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('how-to-order/', HowToOrderView.as_view(), name='how-to-order'),
    path('returns/', ReturnsView.as_view(), name='returns'),
    path('faq/', FAQView.as_view(), name='faq'),

    # Каталог
    path('catalog/', CatalogView.as_view(), name='catalog'),
    path('category/<slug:slug>/', CategoryView.as_view(), name='category'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),

    # Поиск
    path('search/', SearchView.as_view(), name='search'),

    # Акции и хиты
    path('sales/', SalesView.as_view(), name='sales'),
    path('hits/', HitsView.as_view(), name='hits'),
    path('news/', NewsView.as_view(), name='news'),

    # Пользователь
    path('profile/', ProfileView.as_view(), name='profile'),
    path('orders/', OrdersView.as_view(), name='orders'),

    # Избранное
    path('favorites/', FavoritesView.as_view(), name='favorites'),

    # Корзина
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    # Подписка
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
]