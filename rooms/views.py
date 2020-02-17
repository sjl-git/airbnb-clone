from django.http import Http404
from django.db.models import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, View, UpdateView, FormView
from django_countries import countries
from django.core.paginator import Paginator
from . import models, forms
from users import mixins


class HomeView(ListView):
    model = models.Room
    paginate_by = 12
    ordering = "price"
    paginate_orphans = 5
    context_object_name = "rooms"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class RoomDetailView(DetailView):
    model = models.Room


class SearchView(View):
    def get(self, request):
        country = request.GET.get("country")
        if country:
            form = forms.SearchForm(request.GET)
            if form.is_valid():
                city = form.cleaned_data.get("city")
                country = form.cleaned_data.get("country")
                room_type = form.cleaned_data.get("room_type")
                price = form.cleaned_data.get("price")
                guests = form.cleaned_data.get("guests")
                bedrooms = form.cleaned_data.get("bedrooms")
                beds = form.cleaned_data.get("beds")
                baths = form.cleaned_data.get("baths")
                instant_book = form.cleaned_data.get("instant_book")
                superhost = form.cleaned_data.get("superhost")
                amenities = form.cleaned_data.get("amenities")
                facilities = form.cleaned_data.get("facilities")

                filter_args = {}

                if city != "Anywhere":
                    filter_args["city__startswith"] = city

                filter_args["country"] = country

                if room_type is not None:
                    filter_args["room_type"] = room_type

                if price is not None:
                    filter_args["price__lte"] = price

                if guests is not None:
                    filter_args["guests__gte"] = guests

                if bedrooms is not None:
                    filter_args["bedrooms__gte"] = bedrooms

                if beds is not None:
                    filter_args["beds__gte"] = beds

                if baths is not None:
                    filter_args["baths__gte"] = baths

                if instant_book is True:
                    filter_args["instant_book"] = True

                if superhost is True:
                    filter_args["host__superhost"] = True

                for amenity in amenities:
                    filter_args["amenities"] = amenity

                for facility in facilities:
                    filter_args["facilities"] = facility

                qs = models.Room.objects.filter(**filter_args).order_by("-created")
                paginator = Paginator(qs, 10, orphans=5)
                page = request.GET.get("page", 1)
                rooms = paginator.get_page(page)
                return render(
                    request, "rooms/search.html", {"form": form, "rooms": rooms}
                )
        else:
            form = forms.SearchForm()
        return render(request, "rooms/search.html", {"form": form})


class EditRoomView(mixins.LoggedInOnlyView, UpdateView):
    model = models.Room
    fields = (
        "name",
        "description",
        "country",
        "city",
        "price",
        "address",
        "guests",
        "beds",
        "bedrooms",
        "baths",
        "check_in",
        "check_out",
        "instant_book",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
    )
    template_name = "rooms/edit_room.html"

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if self.request.user.pk != room.host.pk:
            raise Http404()
        return room


class RoomPhotosView(mixins.LoggedInOnlyView, DetailView):
    model = models.Room
    template_name = "rooms/room_photos.html"

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if self.request.user.pk != room.host.pk:
            raise Http404()
        return room


@login_required
def delete_photo(request, room_pk, photo_pk):
    user = request.user
    try:
        room = models.Room.objects.get(pk=room_pk)
        if room.host != user:
            pass
        else:
            models.Photo.objects.filter(pk=photo_pk).delete()
            return redirect(reverse("rooms:photos", kwargs={"pk": room_pk}))
    except models.Room.ObjectDoesNotExist:
        return redirect(reverse("core:home"))


class EditPhotoView(mixins.LoginRequiredMixin, UpdateView):
    model = models.Photo
    template_name = "rooms/edit_photo.html"
    fields = ("caption",)
    pk_url_kwarg = "photo_pk"

    def get_success_url(self):
        room_pk = self.kwargs.get("room_pk")
        return reverse("rooms:photos", kwargs={"pk": room_pk})


class AddPhotoView(mixins.LoggedInOnlyView, FormView):
    model = models.Photo
    template_name = "rooms/photo_create.html"

    form_class = forms.CreatePhotoForm

    def form_valid(self, form):
        pk = self.kwargs.get("pk")
        form.save(pk)
        return redirect(reverse("rooms:photos", kwargs={"pk": pk}))


class UploadRoomView(mixins.LoggedInOnlyView, FormView):
    model = models.Room
    template_name = "rooms/room_create.html"
    form_class = forms.CreateRoomForm

    def form_valid(self, form):
        room = form.save()
        room.host = self.request.user
        room.save()
        form.save_m2m()
        return redirect(reverse("rooms:detail", kwargs={"pk": room.pk}))
