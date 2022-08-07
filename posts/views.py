from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Group, Follow, Post
COUNTER_POST = 10
User = get_user_model()


def paginator_dec(queryset, request):
    paginator = Paginator(queryset, COUNTER_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_number': page_number,
        'page_obj': page_obj,
    }


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    context = {
        'title': 'Последние обновления на сайте',
    }
    context.update(paginator_dec(post_list, request))
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {
        'group': group,
    }
    context.update(paginator_dec(post_list, request))
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    template = 'posts/profile.html'
    post_list = author.posts.all()
    following = author.following.filter(user__username=request.user).count()
    context = {
        'author': author,
        'post_list': post_list,
        'following': following,
    }
    context.update(paginator_dec(post_list, request))
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    posts_count = author.posts.all().count()
    form = CommentForm(
        request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'author': author,
        'posts_count': posts_count,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=request.user)
        return render(request, template, {'form': form})
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    context = {'is_edit': True}
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id)
    context.update({'form': form, 'post': post})
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    post_list = Post.objects.filter(
        author__following__user=request.user)
    context = {
        'title': 'Посты авторов, на которых вы подписаны'
    }
    context.update(paginator_dec(post_list, request))
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    if username != request.user.username:
        author = get_object_or_404(User, username=username)
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    ).delete()
    return redirect('posts:profile', username=username)
