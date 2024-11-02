from django.urls import path

from . import views


urlpatterns = [
    path('fanbanter/<int:post_id>/', views.fanbanter, name='fanbanter'),
    # path('fanbanter_post_detail/<int:post_id>/', views.fanbanter_post_detail, name='fanbanter_post_detail'),

    
    path('toggle_fanbanter_like/<int:post_id>/', views.toggle_fanbanter_like, name='toggle_fanbanter_like'),
    path('toggle_fanbanter_like/comment/<int:comment_id>/', views.toggle_fanbanter_like, name='toggle_fanbanter_like_comment'),
    path('toggle_fanbanter_like/comment/<int:child_comment_id>/', views.toggle_fanbanter_like, name='toggle_fanbanter_like_child_comment'),
    
    path('fanbanter_comment/<int:post_id>/', views.fanbanter_comment, name='fanbanter_comment'),
    path('delete_fanbanter_comment/<int:comment_id>/', views.delete_fanbanter_comment, name='delete_fanbanter_comment'),
]