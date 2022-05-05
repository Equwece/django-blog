from django.urls import path
from . import views


urlpatterns = [
    path('home/', views.home, name='home'),
    path('', views.blog, name='blog'),
    path('<int:post_id>/', views.post, name='post'),
    path('admin/', views.admin, name='admin'),
    path('logout/', views.logout_view, name='logout'),
    path('<int:post_id>/delete/', views.delete_post, name='delete'),
    path('create/', views.create_post, name='create'),
    path('<int:post_id>/edit/', views.edit_post, name='edit'),
    path('tag/<str:url>/', views.show_tag, name='show_tag'),
    path('tag/', views.show_all_tags, name='show_all_tags'),
    path('create/tag/', views.create_tag, name='create_tag'),
    path('tag/<str:url>/edit/', views.edit_tag, name='edit_tag'),
    path('tag/<str:url>/delete/', views.delete_tag, name='delete_tag'),
    path('search/', views.search, name='search'),
    path(
        '<int:post_id>/<int:comment_id>/delete',
        views.delete_comment,
        name='delete_comment',
    ),

]

