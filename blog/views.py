from django.shortcuts import render
from .models import Post, Tag, Comment
from django.http import Http404, HttpResponseRedirect
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from .forms import AdminForm, CreateForm, TagForm, SearchForm, CommentForm
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
PAGINATION_NUM = 6


def create_url(base_url, attrs=None):
    if attrs is not None:
        k = 0
        attr_str = '?'
        for key, value in zip(attrs, attrs.values()):
            if k != 0:
                attr_str += f'&{key}={value}'
            else:
                attr_str += f'{key}={value}'
            k += 1
        return base_url + attr_str

    return base_url


def add_attrs_to_url(base_url, attrs):
    if '?' not in base_url:
        base_url += '?'

    for key, value in zip(attrs, attrs.values()):
        if base_url[len(base_url)-1] == '?':
            base_url += f'{key}={value}'
        else:
            base_url += f'&{key}={value}'

    return base_url


def admin_required(func):
    def inner_func(*args, **kwargs):
        if not args[0].user.is_authenticated:
            raise PermissionDenied
        return func(*args, **kwargs)
    return inner_func


def is_user_login(request):
    if request.user.is_authenticated:
        return request.user
    else:
        return None


def get_page_obj(request, posts_num, post_list, attrs=None):
    paginator = Paginator(post_list, posts_num)
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1
    page_number = int(page_number)
    page_obj = paginator.get_page(page_number)
    button_list = [i for i in range(1, page_obj.paginator.num_pages+1)]
    length = len(button_list)
    start = page_number - 3
    if start < 0:
        start = 0

    end = page_number + 2
    if end > len(button_list):
        end = len(button_list)

    button_list = button_list[start:end]

    if abs(0 - page_number) >= 5:
        button_list = [1, '...'] + button_list
    elif abs(0 - page_number) == 4:
        button_list = [1] + button_list

    if abs(length - page_number) >= 4:
        button_list = button_list + ['...', length]
    elif abs(length - page_number) == 3:
        button_list = button_list + [length]

    pagination_links = {}
    if page_obj.has_previous():
        pagination_links['previous'] = add_attrs_to_url(
            create_url('', attrs), {'page': page_obj.previous_page_number()}
        )
    else:
        pagination_links['previous'] = add_attrs_to_url(
            create_url('', attrs), {'page': page_obj.number}
        )

    if page_obj.has_next():
        pagination_links['next'] = add_attrs_to_url(
            create_url('', attrs), {'page': page_obj.next_page_number()}
        )
    else:
        pagination_links['next'] = add_attrs_to_url(
            create_url('', attrs), {'page': page_obj.number}
        )

    for num, button in enumerate(button_list):
        button_list[num] = [
            button,
            add_attrs_to_url(create_url('', attrs), {'page': button})
        ]

    return page_obj, button_list, pagination_links


def get_posts(request, template, posts=Post.objects.all().order_by('-date'),
              extra_context={}, attrs=None):
    pagination_data = get_page_obj(request, PAGINATION_NUM, posts, attrs)
    user = is_user_login(request)
    context = {
        'posts': posts,
        'page_obj': pagination_data[0],
        'button_list': pagination_data[1],
        'pagination_links': pagination_data[2],
        'user': user,
    }
    context.update(extra_context)
    return render(request, template, context)


def home(request):
    return get_posts(request, 'blog/home_template.html')


def blog(request):
    return get_posts(request, 'blog/blog_template.html')


def post(request, post_id):
    try:
        p = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise Http404("Post does't exist")

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = Comment(
                author=form.cleaned_data['author'],
                email=form.cleaned_data['email'],
                comment_text=form.cleaned_data['comment_text'],
                post=p,
            )
            new_comment.save()

    form = CommentForm()
    return render(request, 'blog/post_template.html', context={
        'post': p,
        'comments': p.comment_set.all(),
        'form': form,
    })


def admin(request):
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['login_field']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                if request.GET.get('next') is not None:
                    redirect_url = request.GET.get('next')
                else:
                    redirect_url = reverse('home')
                return HttpResponseRedirect(redirect_url)
            else:
                messages.add_message(request, messages.INFO, '''Wrong login or
                                    password''')

    form = AdminForm()

    return render(request, 'blog/admin_form.html', context={
        'form': form,
    })


def logout_view(request):
    logout(request)
    return render(request, 'blog/logout_template.html')


@admin_required
def delete_post(request, post_id):
    post = Post.objects.get(id=post_id)
    post.delete()
    return HttpResponseRedirect(reverse('home'))


@admin_required
def create_post(request):
    tags = Tag.objects.all()
    if request.method == 'POST':
        form = CreateForm(request.POST)
        if form.is_valid():
            new_post = Post(
                title=form.cleaned_data['title'],
                post_text=form.cleaned_data['post_text']
            )
            new_post.save()
            for tag in tags:
                if tag.title in request.POST:
                    new_post.tag.add(tag)
            return HttpResponseRedirect(reverse('home'))
    form = CreateForm()
    return render(request, 'blog/create_post.html', context={
        'form': form,
        'tags': tags,
    })


@admin_required
def edit_post(request, post_id):
    tags = Tag.objects.all()
    if request.method == 'POST':
        form = CreateForm(request.POST)
        if form.is_valid():
            updating_post = Post.objects.filter(id=post_id).update(
                title=form.cleaned_data['title'],
                post_text=form.cleaned_data['post_text']
            )
            updating_post = Post.objects.get(id=post_id)
            updating_post.tag.clear()
            for tag in tags:
                if tag.title in request.POST:
                    updating_post.tag.add(tag)
        #    updating_post.tag.set(form.cleaned_data['tags'])
            return HttpResponseRedirect(reverse('home'))
        else:
            messages.add_message(request, messages.INFO, '''Form error''')

    post = Post.objects.get(id=post_id)
    post_tags = post.tag.all()
    form = CreateForm(initial={'title': post.title,
                               'post_text': post.post_text})
    return render(request, 'blog/create_post.html', context={
        'form': form,
        'edit': True,
        'tags': tags,
        'post_tags': post_tags,
    })


def show_tag(request, url):
    template = 'blog/tag_template.html'
    posts = Post.objects.filter(tag__url=url)
    tag = Tag.objects.get(url=url)
    extra_context = {
        'tag_title': tag.title,
    }
    return get_posts(request, template, posts, extra_context)


def show_all_tags(request):
    tags = Tag.objects.all()
    return render(request, 'blog/all_tags_template.html', context={
        'tags': tags,
    })


@admin_required
def create_tag(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            new_tag = Tag(
                title=form.cleaned_data['title'],
                url=form.cleaned_data['url'],
            )
            new_tag.save()
            return HttpResponseRedirect(reverse('show_all_tags'))

    form = TagForm()
    return render(request, 'blog/generic_form.html', context={
        'form': form,
    })


@admin_required
def edit_tag(request, url):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            updating_tag = Tag.objects.filter(url=url).update(
                title=form.cleaned_data['title'],
                url=form.cleaned_data['url'],
            )
            return HttpResponseRedirect(reverse('show_all_tags'))

    tag = Tag.objects.get(url=url)
    form = TagForm(initial={
        'title': tag.title,
        'url': tag.url,
    })
    return render(request, 'blog/generic_form.html', context={
        'form': form,
    })


@admin_required
def delete_tag(request, url):
    tag = Tag.objects.get(url=url)
    tag.delete()
    return HttpResponseRedirect(reverse('show_all_tags'))


def search(request):
    search_pattern = request.GET.get('search')
    posts = Post.objects.filter(title__icontains=search_pattern)
    posts = posts.order_by('-date')
    template = 'blog/blog_template.html'
    return get_posts(request, template, posts, attrs={
        'search': search_pattern,
    })


@admin_required
def delete_comment(request, comment_id, post_id):
    comment = Comment.objects.get(id=comment_id)
    comment.delete()
    return HttpResponseRedirect(reverse(
        'post',
        kwargs={
            'post_id': post_id,
        }
    ))
