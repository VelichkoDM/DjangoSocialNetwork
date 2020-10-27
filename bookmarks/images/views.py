from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Image
from actions.utils import create_action


@login_required
def image_create(request):
    if request.method == 'POST':
        # Форма отправлена.
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # Данные формы валидны.
            cd = form.cleaned_data

            new_item = form.save(commit=False)
            # Добавляем пользователя к созданному объекту.
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'bookmarked image', new_item)
            messages.success(request, 'Image added successfully')
            # Перенаправляем пользователя на страницу сохраненного изображения.
            return redirect(new_item.get_absolute_url())
        else:
            # Заполняем форму данными из GET-запроса.
            form = ImageCreateForm(data=request.GET)
    else:
        form = ImageCreateForm()
    return render(request,
                  'images/image/create.html',
                  {'section': 'images', 'form': form})


@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'ok'})
