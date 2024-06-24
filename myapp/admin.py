from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Movie, MovieGenre, MovieCountry, Director, Filming

admin.site.register(Movie)
admin.site.register(MovieGenre)
admin.site.register(MovieCountry)
admin.site.register(Director)
admin.site.register(Filming)
