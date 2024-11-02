from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from .models import FanBanterPost, FanBanterLike, FanBanterComment
from user_management.models import UserProfile

@login_required(login_url='loginform')
def fanbanter(request, post_id=None):
    login_user_profile = UserProfile.objects.get(user=request.user)
    
    prefetch_queries = [
        'fanbanter_comments',
        'fanbanter_comments__fanbanter_replies',
        'fanbanter_comments__fanbanter_likes',
        'fanbanter_comments__fanbanter_replies__fanbanter_likes',
        'fanbanter_likes'
    ]

    fanbanter_posts = FanBanterPost.objects.all().prefetch_related(*prefetch_queries).order_by('-created_at')

    if post_id:
        selected_post = get_object_or_404(FanBanterPost.objects.prefetch_related(*prefetch_queries), id=post_id)
        fanbanter_posts = [selected_post]
        
    for post in fanbanter_posts:
        post.num_likes = post.fanbanter_likes.count()
        post.user_has_liked = post.fanbanter_likes.filter(user=request.user.profile).exists()
        post.num_comments = post.fanbanter_comments.filter(parent__isnull=True).count()

        for comment in post.fanbanter_comments.all():
            comment.num_likes = comment.fanbanter_likes.count()
            comment.user_has_liked = comment.fanbanter_likes.filter(user=request.user.profile).exists()

            for reply in comment.fanbanter_replies.all():
                reply.num_likes = reply.fanbanter_likes.count()
                reply.user_has_liked = reply.fanbanter_likes.filter(user=request.user.profile).exists()

    return render(request, 'fanbanter/fan_banter.html', {'fanbanter_posts': fanbanter_posts, 'login_user': login_user_profile})



# @login_required(login_url='loginform')
# def fanbanter_post_detail(request, post_id):
#     fanbanter_post = get_object_or_404(FanBanterPost, id=post_id)
#     comments = fanbanter_post.fanbanter_comments.all()
#     likes = fanbanter_post.fanbanter_likes.all()

#     context = {
#         'fanbanter_post': fanbanter_post,
#         'comments': comments,
#         'likes': likes,
#     }

#     return render(request, 'fanbanter/fan_banter.html', context)



@login_required(login_url='loginform')
def fanbanter_comment(request, post_id):
    post = get_object_or_404(FanBanterPost, id=post_id)

    if request.method == "POST" and request.POST.get('message'):
        comment_text = request.POST.get('message')
        parent_id = request.POST.get('parent_id', None)
        try:
            if parent_id:
                parent_comment = FanBanterComment.objects.get(id=parent_id)
                comment = FanBanterComment.objects.create(
                    post=post,
                    author=request.user.profile,
                    content=comment_text,
                    parent=parent_comment
                )
            else:
                comment = FanBanterComment.objects.create(
                    post=post,
                    author=request.user.profile,
                    content=comment_text
                )
            messages.success(request, "Comment successfully posted.")
        except FanBanterComment.DoesNotExist:
            messages.error(request, 'Parent comment not found.')
        return redirect('fanbanter', post_id=post.id)

    # If it's not a POST request or no message provided, render fanbanter page
    return redirect('fanbanter', post_id=post.id)

    



@login_required(login_url='loginform')
def delete_fanbanter_comment(request, comment_id):
    comment = get_object_or_404(FanBanterComment, id=comment_id)

    if request.user == comment.author.user:
        comment.delete()
        messages.success(request, "Comment successfully deleted.")
        return redirect('fanbanter', post_id=comment.post.id)
    else:
        messages.error(request, "You do not have permission to delete this comment.")
        return redirect('fanbanter', post_id=comment.post.id)




@login_required(login_url='loginform')
def toggle_fanbanter_like(request, post_id=None, comment_id=None):
    user = request.user.profile
    if request.method == 'POST':
        item = None
        model_type = None

        if post_id:
            item = get_object_or_404(FanBanterPost, id=post_id)
            model_type = 'post'
        elif comment_id:
            item = get_object_or_404(FanBanterComment, id=comment_id)
            model_type = 'comment'

        if not item:
            return JsonResponse({'success': False, 'error': 'Invalid like toggle request'}, status=400)

        filter_kwargs = {'user': user}
        filter_kwargs[model_type] = item
        liked = FanBanterLike.objects.filter(**filter_kwargs).exists()

        if liked:
            FanBanterLike.objects.filter(**filter_kwargs).delete()
            liked = False
        else:
            FanBanterLike.objects.create(**filter_kwargs)
            liked = True

        # Count the likes using the correct related_name
        num_likes = item.fanbanter_likes.count()

        return JsonResponse({'success': True, 'liked': liked, 'num_likes': num_likes, 'item_type': model_type, 'item_id': item.id})
    else:
        return JsonResponse({'success': False, 'error': 'This request requires POST method.'}, status=400)
