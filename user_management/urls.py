from django.urls import path

from . import views


urlpatterns = [

    path('loginform/', views.loginform, name='loginform'),
    
    path('loginform/forget_password/', views.forget_password, name='forget_password'),
    path('loginform/forget_password/resend_code/', views.resend_code, name='resend_code'),
    path('loginform/forget_password/verify_code/', views.verify_code, name='verify_code'),
    path('loginform/change_password/', views.change_password, name='change_password'),




    path('registrationform/', views.registrationform, name='registrationform'),
    path('logout/', views.logout, name='logout'),
    path('userprofile/<str:username>/', views.userprofile, name='userprofile'),
    path('user/<str:username>/change_picture/', views.change_profile_picture, name='change_profile_picture'),




    path('post/create/<str:username>/', views.create_post, name='create_post'),
    path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('post_detail/<int:post_id>/', views.post_detail, name='post_detail'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),

    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),

    path('toggle_like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    path('toggle_like/comment/<int:comment_id>/', views.toggle_like, name='toggle_like_comment'),
    path('toggle_like/comment/<int:child_comment_id>/', views.toggle_like, name='toggle_like_child_comment'),

    # path('user/<int:target_user_id>/follow_unfollow', views.follow_unfollow_user, name='follow_unfollow_user'),

    path('follow_unfollow_user/<str:target_username>/', views.follow_unfollow_user, name='follow_unfollow_user'),

]