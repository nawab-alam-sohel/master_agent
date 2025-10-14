from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.agents_table_view, name='home'),
    path('agents/', views.agents_table_view, name='agents_page'),

    # Blog URLs
    path('blog/', views.blog_list, name='blog_list'),
  re_path(r'^blog/category/(?P<slug>[-\w\u0980-\u09FF]+)/$', views.blog_list, name='category_posts'),
    path('blog/post/<slug:slug>/', views.post_detail, name='post_detail'),

    # Static pages
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
    path('privacy-policy/', views.privacy_policy_page, name='privacy_policy'),
    path('terms-and-conditions/', views.terms_page, name='terms'),
]
