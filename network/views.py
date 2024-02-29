from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


from .models import User, Post


def index(request):
    # Obtener todos los posts ordenados por fecha de creación
    all_posts = Post.objects.all().order_by('-created_at')

    # Utilizar la función auxiliar para obtener la página actual
    paginated_posts = paginate_posts(request, all_posts)

    return render(request, "network/index.html", {"posts": paginated_posts})



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def new_post(request):
    if request.method == "POST":
        content = request.POST.get("content")

        if content:
            user = request.user
            post = Post(content=content, user=user)
            post.save()

    return redirect("index")


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    # Verificar si el usuario actual sigue al usuario del perfil
    is_following = request.user in profile_user.followers.all()

    # Obtener todas las publicaciones del perfil en orden cronológico inverso
    posts = Post.objects.filter(user=profile_user).order_by('-created_at')

    context = {
        'profile_user': profile_user,
        'is_following': is_following,
    }

    paginated_posts = paginate_posts(request, posts)

    return render(request, "network/profile.html", {"posts": paginated_posts, **context})


@login_required
def follow(request, username):
    if request.method == "POST":
        profile_user = get_object_or_404(User, username=username)
        request.user.following.add(profile_user)
        # Es lo mismo que:
        # profile_user.followers.add(request.user)

    return redirect("profile", username=username)


@login_required
def unfollow(request, username):
    if request.method == "POST":
        profile_user = get_object_or_404(User, username=username)
        request.user.following.remove(profile_user)

    return redirect("profile", username=username)


@login_required
def following(request):
    following_users = request.user.following.all()

    # Obtener todos los posts de los usuarios seguidos
    # __in indica que estamos buscando posts cuyo usuario esta en una lista específica
    following_posts = Post.objects.filter(
        user__in=following_users).order_by('-created_at')

    paginated_posts = paginate_posts(request, following_posts)

    return render(request, "network/following.html", {"posts": paginated_posts})


def paginate_posts(request, posts, num_posts=3):
    # Paginar los posts por página
    paginator = Paginator(posts, num_posts)

    # Obtener el número de página de la consulta GET
    page_number = request.GET.get('page')

    # Obtener la página actual
    paginated_posts = paginator.get_page(page_number)

    return paginated_posts


@login_required
def edit_post(request, post_id):
    # Obtener el post a editar
    post = get_object_or_404(Post, id=post_id)

    # Verificar que el usuario actual sea el autor del post
    if request.user != post.user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # Verificar si la solicitud es GET (para obtener el contenido actual del post)
    if request.method == 'GET':
        return JsonResponse({'content': post.content})

    # Si la solicitud es POST, actualizar el contenido del post
    elif request.method == 'POST':
        new_content = request.POST.get('new_content')

        # Validar que el nuevo contenido no esté vacío
        if not new_content:
            return JsonResponse({'error': 'Content cannot be empty'}, status=400)

        # Actualizar el contenido del post
        post.content = new_content
        post.save()

        return JsonResponse({'success': 'Post updated successfully'})


@login_required
def toggle_like(request, post_id):
    if request.method == "POST":
        # Obtener la publicación
        post = get_object_or_404(Post, id=post_id)

        # Obtener el usuario actual
        user = request.user

        # Verificar si el usuario ya ha dado like a la publicación
        if user in post.likes.all():
            # El usuario ya ha dado like, por lo tanto, lo eliminamos
            post.likes.remove(user)
            liked = False
        else:
            # El usuario no ha dado like, por lo tanto, lo agregamos
            post.likes.add(user)
            liked = True

        # Obtener el conteo actual de likes
        like_count = post.likes.count()

        # Devolver una respuesta JSON con la información actualizada
        return JsonResponse({'liked': liked, 'like_count': like_count})
    else:
        # Si la solicitud no es de tipo POST, devolver un error
        return JsonResponse({'error': 'Invalid request method'})
