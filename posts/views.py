from django.db.models import Q, Exists, OuterRef
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.models import Account, UserFollowing, UserFollower, UserProfile
from .models import Post, Like, Comment, Notification
# Create your views here.

login_required(login_url='login')
def make_post(request):
    if request.method=='POST':
        following=UserFollower.objects.filter(follower=request.user)
        followers=UserFollowing.objects.filter(following=request.user)

        send_to_users=[]
        for fol in following:
            send_to_users.append(fol.following)
        for fol in followers:
            send_to_users.append(fol.follower)

        caption=request.POST.get('caption')
        myfile=request.FILES.get('myfile')
        post=Post.objects.create(caption=caption,
                                 user=request.user,
                                 mypost=myfile)
        post.save()
        for receiver in send_to_users:
            notification=Notification.objects.create(post=post,
                                                     sender=request.user,
                                                     receiver=receiver
                                                     )
            notification.save()


        return redirect('user_details', pk=request.user.id)

login_required(login_url='login')
def follow(request, pk):
    being_followed=Account.objects.get(id=pk)
    follower=request.user
    user_follower=UserFollower.objects.create(follower=follower, following=being_followed)
    user_follower.save()
    user_following=UserFollowing.objects.create(follower=follower, following=being_followed)
    user_following.save()
    return redirect('user_details', pk=being_followed.id)

login_required(login_url='login')
def unfollow(request, pk):
    being_unfollowed = Account.objects.get(id=pk)
    unfollower = request.user
    user_follower = UserFollower.objects.get(follower=unfollower, following=being_unfollowed)
    user_follower.delete()
    user_following = UserFollowing.objects.get(follower=unfollower, following=being_unfollowed)
    user_following.delete()
    return redirect('user_details', pk=being_unfollowed.id)

login_required(login_url='login')
def edit_profile(request):
    if request.method=='POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        profile_picture=request.FILES.get('profile_picture')

        if last_name=="" and first_name=="" and profile_picture==None:
            return redirect('user_details', pk=request.user.id)
        else:
            user_profile=UserProfile.objects.get(user=request.user)
            if profile_picture is not None:
                user_profile.profile_picture=profile_picture
            if not (first_name==""):
                request.user.first_name=first_name
            if not (last_name==""):
                request.user.last_name=last_name
            request.user.save()
            user_profile.save()

            return redirect('user_details', pk=request.user.id)

def search(request):
    if request.method=="GET":
        search=request.GET.get('search')
        following=UserFollowing.objects.filter(follower=request.user)
        follow_id=[]
        for follow in following:
            follow_id.append(follow.following.id)
        users=Account.objects.filter(Q(username__icontains=search) | Q(first_name__icontains=search)).exclude(id__in=follow_id)
        searched_userprofiles=UserProfile.objects.filter(user__in=users)
        posts=Post.objects.filter(caption__icontains=search)
        posts = posts.annotate(liked=Exists(Like.objects.filter(post=OuterRef('pk'), liked_by=request.user)))

        context={
            'searched_profiles':searched_userprofiles,
            'posts':posts
        }
        return render(request, 'posts/search.html', context)

def thinking(request):
    if request.method=='POST':
        thinking_about=request.POST.get('thinking')
        thought=Post.objects.create(thinking=thinking_about,
                                    user=request.user)
        thought.save()
        return redirect('index')
    else:
        return redirect('index')

def like_post(request, pk):
    post=Post.objects.get(id=pk)
    like=Like.objects.create(post=post,
                             liked_by=request.user)
    notification = Notification.objects.create(like=like,
                                               sender=request.user,
                                               receiver=like.post.user
                                               )
    notification.save()
    return redirect("index")

def unlike_post(request, pk):
    post = Post.objects.get(id=pk)
    unlike = Like.objects.get(post=post,
                               liked_by=request.user)
    unlike.delete()
    return redirect('index')

@login_required(login_url='login')
def comment(request, post_id):
    if request.method=="POST":
        comment=request.POST.get('comment')
        post=Post.objects.get(id=post_id)
        comment=Comment.objects.create(post=post, commentor=request.user, comment=comment)
        comment.save()


        notification=Notification.objects.create(comment=comment,
                                                 sender=request.user,
                                                 receiver=comment.post.user
                                                 )
        notification.save()
        return redirect('index')
    else:
        return redirect('index')

def post_details(request, post_id):
    post=Post.objects.get(id=post_id)
    post.liked = Like.objects.filter(post=post, liked_by=request.user).exists()

    return render(request, 'posts/post_details.html', context={'post':post})

def delete_notification(request, notification_id, post_id):
    notification=Notification.objects.get(id=notification_id)
    notification.delete()
    return redirect('post_details', post_id=post_id)
