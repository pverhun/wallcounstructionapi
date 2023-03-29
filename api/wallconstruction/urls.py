from django.urls import path

from . import views

urlpatterns = [
    path('profiles/days/<int:day>', views.daily),
    path('profiles/<int:wall_profile>/days/<int:day>', views.daily),

    path('profiles/overview/', views.overview),
    path('profiles/overview/<int:day>', views.overview),
    path('profiles/<int:wall_profile>/overview/<int:day>', views.overview),
]
