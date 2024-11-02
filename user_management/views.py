from django.shortcuts import render, redirect, get_object_or_404

from django.core.validators import validate_email





from django.contrib.auth import authenticate, login as authlogin, logout as authlogout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.core.files.storage import default_storage

import os
import random
import os
from PIL import Image, ImageFile
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile


from django.contrib.auth import update_session_auth_hash

from .utils import send_email




from .models import UserProfile, Post, Comment, Like
from competition_management.models import Player, Team

# Create your views here.




def loginform(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return JsonResponse({'success': False, 'error': 'Username and password are required'})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            authlogin(request, user)
            # Determine the appropriate redirect URL
            # try:
            #     Player.objects.get(name=user)
            #     redirect_url = reverse('player', kwargs={'player_name': user.username})
            # except Player.DoesNotExist:
            #     UserProfile.objects.get_or_create(user=user)  # Example of handling user profiles
            #     redirect_url = reverse('userprofile', kwargs={'username': user.username})
            # return JsonResponse({'success': True, 'redirect': True, 'redirect_url': redirect_url})
            return JsonResponse({'success': True, 'redirect': True, 'redirect_url': reverse('home')})
            
        else:
            return JsonResponse({'success': False, 'error': 'Invalid username or password'})

    return render(request, 'loginform.html')



def forget_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        users = User.objects.filter(email=email)
        if users.exists():
            if users.count() == 1:
                user = users.first()
                reset_code = ''.join(random.choices('0123456789', k=6))
                request.session['reset_code'] = reset_code
                request.session['reset_email'] = email
                
                send_email(
                    'Password Reset Code',
                    f'Your password reset code is: {reset_code}',
                    email
                )
                
                return JsonResponse({'success': True, 'redirect': True, 'redirect_url': '/loginform/forget_password/verify_code/'})
            else:
                return JsonResponse({'success': False, 'error': 'Multiple users found with this email address.'})
        else:
            return JsonResponse({'success': False, 'error': 'Email does not exist.'})

    return render(request, 'forget_password.html')


def verify_code(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        reset_code = request.session.get('reset_code')
        if code == reset_code:
            return JsonResponse({'success': True, 'message': 'Code verified successfully, proceed to change password.', 'redirect': True, 'redirect_url': '/loginform/change_password/'})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid code, enter correct code!'})

    return render(request, 'verify_code.html')


def resend_code(request):
    reset_email = request.session.get('reset_email')

    if reset_email:
        # Generate a new 6-digit reset code
        reset_code = ''.join(random.choices('0123456789', k=6))
        
        # Store the new reset code in the session
        request.session['reset_code'] = reset_code
        
        # Resend the reset code via email
        send_email(
            'Password Reset Code',
            f'Your password reset code is: {reset_code}',
            reset_email
        )
        return redirect('/loginform/forget_password/verify_code/')
        # return JsonResponse({'success': True, 'message': 'Code sent successfully, check your email', 'redirect': True, 'redirect_url': '/loginform/forget_password/verify_code/'})
    else:
        return JsonResponse({'success': False, 'error': 'Session expired or invalid. Please start the password reset process again.', 'redirect': True, 'redirect_url': '/loginform/forget_password/'})



def change_password(request):
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 == password2:
            email = request.session.get('reset_email')
            user = User.objects.get(email=email)
            user.set_password(password1)
            user.save()
            # It's a good practice to update the session hash after changing the password
            update_session_auth_hash(request, user)
            # Clear session data
            del request.session['reset_code']
            del request.session['reset_email']

            # messages.success(request, 'Password successfully changed.')
            return JsonResponse({'success': True, 'redirect': True, 'redirect_url': '/loginform/'})
            # return redirect('loginform')  # Redirect to login page
        else:
            # messages.error(request, 'Passwords do not match.')
            return JsonResponse({'success': False, 'error': 'Passwords do not match.', })
    return render(request, 'change_password.html')




def registrationform(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        date_of_birth = request.POST.get('date_of_birth')  # New field
        bio = request.POST.get('bio')  # New field
        
        # Initial checks for field presence
        if not all([email, username, first_name, last_name, password1, password2, date_of_birth]):  # Check dob
            return JsonResponse({'success': False, 'error': 'All fields are required'})

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'success': False, 'error': 'Invalid email format'})
        
        # Check if passwords match
        if password1 != password2:
            return JsonResponse({'success': False, 'error': 'Passwords do not match'})
        
        # Check password length
        if len(password1) < 6:
            return JsonResponse({'success': False, 'error': 'Password must be at least 6 characters long'})
        
        # Check if username and email are unique
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'Username already exists'})
        elif User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'Email already in use'})
        
        # Create User with first name and last name
        user = User.objects.create_user(username=username, email=email, password=password1,
                                        first_name=first_name, last_name=last_name)
        
        # Optionally create a UserProfile instance
        UserProfile.objects.create(user=user, date_of_birth=date_of_birth, bio=bio)

        
        # Authenticate user
        user = authenticate(request, username=username, password=password1)
        
        if user is not None:
            authlogin(request, user)
            try:
                player = Player.objects.get(name=user)  # Assuming `name` is the username field
                redirect_url = reverse('player', kwargs={'player_name': user.username})

            except Player.DoesNotExist:
                userprofile = UserProfile.objects.get(user=user)
                redirect_url = reverse('userprofile', kwargs={'username': user.username})
                
            return JsonResponse({
                'success': True,
                'redirect': True,
                'redirect_url': redirect_url
            })
        
        else:
            return JsonResponse({'success': False, 'error': 'Invalid username or password'})

    return render(request, 'loginform.html')


@login_required(login_url='loginform')
def logout(request):

    authlogout(request)
    # Redirect to login page or home page after logout
    
    return redirect('home')


@login_required(login_url='loginform')
def userprofile(request, username):
    target_user = get_object_or_404(User, username=username)
    login_user_profile = UserProfile.objects.get(user=target_user)
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            new_username = request.POST.get('username')
            bio = request.POST.get('bio')
            favorite_team_id = request.POST.get('favorite_team')
            
            # Check if the new username is taken by another user
            if new_username != username and User.objects.filter(username=new_username).exists():
                messages.error(request, 'This username is already taken. Please choose another one.')
            else:
                # Proceed with updates if the username is not taken or unchanged
                if new_username:
                    target_user.username = new_username
                    target_user.save()
                if bio is not None:
                    login_user_profile.bio = bio
                if favorite_team_id:
                    favorite_team = Team.objects.get(id=favorite_team_id)
                    login_user_profile.favorite_team = favorite_team
                else:
                    login_user_profile.favorite_team = None

                login_user_profile.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('userprofile', username=new_username)


    is_followed = login_user_profile.is_followed_by(request.user)

    posts = Post.objects.filter(author=login_user_profile) \
                        .prefetch_related('comments__author', 'comments__replies__author', 'comments__replies__likes', 'comments__likes', 'likes') \
                        .order_by('-created_at')

    for post in posts:
        post.num_likes = post.likes.count()
        post.user_has_liked = post.likes.filter(user=request.user).exists()
        post.num_comments = post.comments.filter(parent__isnull=True).count()

        for comment in post.comments.all():
            comment.num_likes = comment.likes.count()
            comment.user_has_liked = comment.likes.filter(user=request.user).exists()

            for reply in comment.replies.all():
                reply.num_likes = reply.likes.count()
                reply.user_has_liked = reply.likes.filter(user=request.user).exists()


    num_followers = login_user_profile.followers.all().count()
    num_following = login_user_profile.following.count()
    num_posts = posts.count()
    

    context = {
        'login_user': login_user_profile,
        'is_followed': is_followed,
        'posts': posts,
        'num_followers': num_followers,
        'num_following': num_following,
        'num_posts': num_posts,
    }
    
    # print(f"Login User Username: {login_user_profile.user.username}")
    return render(request, 'userprofile.html', context)




@login_required(login_url='loginform')
def change_profile_picture(request, username):
    if request.method == 'POST':
        try:
            user_profile = UserProfile.objects.get(user__username=username)
            # If there's an existing picture, delete it before saving the new one
            if user_profile.picture:
                if default_storage.exists(user_profile.picture.name):
                    default_storage.delete(user_profile.picture.name)
            # Replace with new picture from the form
            user_profile.picture = request.FILES['new_picture']
            user_profile.save()
            # Redirect to the profile page or wherever appropriate
            return redirect('userprofile', username=username)
        except UserProfile.DoesNotExist:
            pass  # Handle error or redirect as appropriate
    # If not a POST request or some other condition, redirect or show an error
    return redirect('userprofile', username=username)




ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']
ALLOWED_VIDEO_EXTENSIONS = ['mp4', 'avi', 'mov']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']
ALLOWED_VIDEO_EXTENSIONS = ['mp4', 'avi', 'mov']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

def validate_file(file):
    ext = os.path.splitext(file.name)[1].lower().lstrip('.')

    if ext in ALLOWED_IMAGE_EXTENSIONS:
        file_type = 'image'
        allowed_extensions = ALLOWED_IMAGE_EXTENSIONS
    elif ext in ALLOWED_VIDEO_EXTENSIONS:
        file_type = 'video'
        allowed_extensions = ALLOWED_VIDEO_EXTENSIONS
    else:
        raise ValidationError("Unsupported file type.")

    extension_validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
    try:
        extension_validator(file)
    except ValidationError as e:
        raise ValidationError(f"Invalid file type: {e}")

    if file.size > MAX_FILE_SIZE:
        raise ValidationError(f"File size exceeds the maximum limit of {MAX_FILE_SIZE // (1024 * 1024)} MB.")

    if file_type == 'image':
        try:
            img = Image.open(file)
            img.verify()  # Verifies that it is an actual image
        except Exception as e:
            raise ValidationError(f"Invalid image file: {e}")
    
    # Skip detailed validation for videos since Pillow can't handle it
    if file_type == 'video':
        pass  # Basic checks like extension and size have already been done

    return file_type



@login_required(login_url='loginform')
def create_post(request, username):
    user_profile = get_object_or_404(UserProfile, user__username=username)
    target_user = get_object_or_404(User, username=username)
    login_user_profile = get_object_or_404(UserProfile, user=target_user)
    
    if request.method == 'POST':
        caption = request.POST.get('caption', '').strip()
        file = request.FILES.get('media')

        if caption or file:
            if file:
                try:
                    print('hello')
                    file_type = validate_file(file)
                    print(file_type)
                    post_data = {
                        'author': user_profile,
                        'caption': caption,
                    }
                    if file_type == 'image':
                        post_data['image'] = file
                    elif file_type == 'video':
                        post_data['video'] = file
                    Post.objects.create(**post_data)
                    return redirect('userprofile', username=username)
                except ValidationError as e:
                    messages.error(request, f"File upload failed: {e}")
                    print(e)
                    return redirect('userprofile', username=username)
            else:
                Post.objects.create(
                    author=user_profile,
                    caption=caption,
                )
                return redirect('userprofile', username=username)
        else:
            messages.error(request, 'You must provide either a caption or a media file.')

            return redirect('userprofile', username=username)
        
    context = {
        'username': username,
        'login_user': login_user_profile,
    }

    return render(request, 'userprofile.html', context)



@login_required(login_url='loginform')
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author.user:
        return redirect('error404.html', username=request.user.username)  # Or to some error page

    if request.method == 'POST':
        post.caption = request.POST.get('content')
        post.save()

        return redirect('userprofile', username=request.user.username)  # Or wherever you want to redirect



@login_required(login_url='loginform')
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # Fetch only top-level comments (those without a parent) and prefetch replies
    comments = post.comments.filter(parent__isnull=True).prefetch_related('replies')

    
    likes = post.likes.all()  # Assuming a related_name='likes' on the Like model

    context = {
        'post': post,
        'comments': comments,
        'likes': likes,  # Uncomment if you are fetching likes
    }
    return render(request, 'post_detail.html', context)



@login_required(login_url='loginform')
def delete_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        # Ensure the user requesting the deletion is the author or has permission
        if request.user == post.author.user:
            post.delete()
            # Assuming 'userprofile' is the view that shows the logged-in user's profile
            return redirect('userprofile', username=request.user.username)  # Just redirect to the profile page without a post_id
        else:
            # Redirect back to the user profile or an error page as needed
            return redirect('userprofile', username=request.user.username)  # or an appropriate error page
    return redirect('userprofile', username=request.user.username)  # Redirecting back if the request method is not POST



@login_required(login_url='loginform')
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_owner_username = post.author.user.username

    if request.method == "POST":
        comment_text = request.POST.get('comment_text')
        redirect_to = request.POST.get('redirect_to', '/')  # Default to home if not specified
        parent_id = request.POST.get('parent_id', None)

        if comment_text:
            try:
                if parent_id:
                    parent_comment = Comment.objects.get(pk=parent_id)
                    comment = Comment(post=post, author=request.user.profile, content=comment_text, parent=parent_comment)
                else:
                    comment = Comment(post=post, author=request.user.profile, content=comment_text)
                comment.save()
                # messages.success(request, 'Your comment has been added.')
            except Comment.DoesNotExist:
                messages.error(request, 'Parent comment not found.')
        else:
            messages.error(request, 'Comment cannot be empty.')

        return HttpResponseRedirect(redirect_to)  # Redirect to the originating page

    # Default to redirecting to userprofile if something goes wrong
    return redirect('userprofile', username=post_owner_username)


@login_required(login_url='loginform')
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_owner_username = request.GET.get('post_owner_username')  # Get the post owner's username from the query parameter

    # Ensure the action is authorized
    if request.user == comment.author.user or request.user == comment.post.author.user or request.user.is_superuser:
        comment.delete()
        messages.success(request, "Comment successfully deleted.")
        # Redirect to the post owner's profile page
        return redirect('userprofile', username=post_owner_username)
    else:
        messages.error(request, "You do not have permission to delete this comment.")
        # Redirect to the fallback or error page; adjust as necessary
        
        return redirect('userprofile', username=post_owner_username)  # Fallback redirect


@login_required(login_url='loginform')
def toggle_like(request, post_id=None, comment_id=None):
    user = request.user
    if request.method == 'POST':
        item = None
        model_type = None

        if post_id:
            item = get_object_or_404(Post, id=post_id)
            model_type = 'post'
        elif comment_id:
            item = get_object_or_404(Comment, id=comment_id)
            model_type = 'comment'

        if not item:
            return JsonResponse({'success': False, 'error': 'Invalid like toggle request'}, status=400)

        # Constructing the correct query based on type
        filter_kwargs = {'user': user}
        filter_kwargs[model_type] = item
        liked = Like.objects.filter(**filter_kwargs).exists()

        if liked:
            Like.objects.filter(**filter_kwargs).delete()
            liked = False
        else:
            Like.objects.create(**filter_kwargs)
            liked = True

        # Count the likes using the correct related_name
        if model_type == 'post':
            num_likes = item.likes.count()
        elif model_type == 'comment':
            num_likes = item.likes.count()

        return JsonResponse({'success': True, 'liked': liked, 'num_likes': num_likes})

    else:
        return JsonResponse({'success': False, 'error': 'This request requires POST method.'}, status=400)



@login_required(login_url='loginform')
def follow_unfollow_user(request, target_username):
    # The user to be followed
    target_user = get_object_or_404(User, username=target_username)
    target_user_profile = UserProfile.objects.get(user=target_user)

    # The current logged-in user's profile
    user_profile = UserProfile.objects.get(user=request.user)

    # Check if already following, then unfollow; else, follow
    if user_profile.following.filter(id=target_user_profile.id).exists():
        user_profile.following.remove(target_user_profile)
    else:
        user_profile.following.add(target_user_profile)

    # Redirect back to the same page
    return redirect(request.META.get('HTTP_REFERER', '/'))



