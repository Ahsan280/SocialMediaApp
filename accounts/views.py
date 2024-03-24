from django.db.models import Q, Subquery, Count
from django.db.models import Exists, OuterRef
from django.shortcuts import render, redirect
from .models import Account, UserFollower, UserFollowing, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.decorators import login_required
from posts.models import Post, Like
# Create your views here.

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        email = request.POST.get('email')
        username=email.split('@')[0]
        if Account.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'accounts/register.html')
        
        if password!=confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
        
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user = Account.objects.create_user(username=username,
                                           email=email,
                                           first_name=first_name,
                                           last_name=last_name,
                                           password=password)
        user.save()
        # User Activation
        current_site=get_current_site(request)
        mail_subject="Please activate your account"
        message=render_to_string('accounts/account_verification_email.html',{
            'user':user,
            'domain':current_site,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':default_token_generator.make_token(user)
        })
        to_email=email
        send_email=EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()
        messages.success(request, "Verification Email sent successfully")
        return redirect("register")
    else:
        return render(request, 'accounts/register.html')
    
def activate(request, uidb64, token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active=True
        user.save()
        userprofile=UserProfile.objects.create(user=user)
        userprofile.save()
        messages.success(request, 'Your account has been activated')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
    
def login(request):
    if request.method == 'POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        user=auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid Credentials")

    return render(request, 'accounts/login.html')
@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')

@login_required(login_url='login')
def index(request):
    following=UserFollowing.objects.filter(follower=request.user)
    followers=UserFollower.objects.filter(following=request.user)
    following_list=[]
    following_list_ids=[]
    user_followers=[]
    for f in following:
        following_list.append(f.following)
        user_followers.append(f.follower)
        following_list_ids.append(f.following.id)
    for f in followers:
        user_followers.append(f.follower)

    if len(following_list)<=0:
        people_you_may_know =Account.objects.exclude(id=request.user.id).order_by('date_joined')[:10]

    else:
        peoples=UserFollowing.objects.filter(follower__in=following_list)
        people_you_may_know=[]
        for people in peoples:
            if not (people.following in following_list):
                people_you_may_know.append(people.following)
        for follower in followers:
            if follower.follower not in following_list:
                people_you_may_know.append(follower.follower)
        if not people_you_may_know:
            people_you_may_know = Account.objects.exclude(id__in=following_list_ids).exclude(id=request.user.id).order_by('date_joined')[:10]
        for follower in followers:
            if follower.follower not in following_list:
                people_you_may_know.append(follower.follower)
    user_profiles=UserProfile.objects.filter(user__in=people_you_may_know)

    posts=Post.objects.filter(Q(user__in=following_list)|Q(user__in=user_followers) | Q(user=request.user)).order_by('-created_at')
    if not posts.exists():
        posts_likes=Post.objects.annotate(likes_count=Count('like'))
        posts_with_likes_excluded = posts_likes.exclude(likes_count=0)
        posts=posts_with_likes_excluded.order_by("-likes_count")


    posts=posts.annotate(liked=Exists(Like.objects.filter(post=OuterRef('pk'), liked_by=request.user)))

    # Subquery to fetch profile picture for the user associated with each post
    profile_picture_subquery = UserProfile.objects.filter(user=OuterRef('user')).values('profile_picture')
    # Annotate each post with the profile picture of the associated user
    posts = posts.annotate(profile_picture=Subquery(profile_picture_subquery[:1]))

    likes=Like.objects.filter(post__in=posts)
    # myposts=Post.objects.filter(user=request.user)
    context={'posts':posts,
             'following_list':following_list,
             'followers':followers,
             'user_profiles':user_profiles,
             'people_you_may_know':people_you_may_know,
             'likes':likes}
    return render(request, 'accounts/index.html', context)

@login_required(login_url='login')
def user_details(request, pk):
    is_following=False
    current_user=Account.objects.get(pk=pk)
    following=UserFollowing.objects.filter(follower=current_user)
    followers=UserFollower.objects.filter(following=current_user)
    user_profile=UserProfile.objects.get(user=current_user)
    for follower in followers:
        if request.user==follower.follower:
            is_following=True
    posts=Post.objects.filter(user=current_user)
    logged_in_user = request.user==current_user
    context={'current_user':current_user,
             'posts':posts,
             'logged_in_user':logged_in_user,
             'following':following,
             'followers':followers,
             'is_following':is_following,
             'user_profile':user_profile}
    return render(request, 'accounts/user_details.html', context)