from django.conf.urls import url
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from .views import FileView


urlpatterns = [
    url(r'^$', views.index),
    path('', views.index, name='index'),  # Register the index view
    path('success/', views.success, name='success'),  # Success route

    url(r'^add_citizen', views.addCitizen),
    url(r'^save_citizen', views.saveCitizen),
    url(r'^view_citizens', views.viewCitizens),

    path('wanted_citizen/<int:citizen_id>/',views.wantedCitizen,name='wanted_citizen'),
    path('free_citizen/<int:citizen_id>/',views.freeCitizen,name='free_citizen'),
    path('recommendations/', views.recommend_crime_avoidance, name='recommend_crime_avoidance'),


    url(r'^login$', views.login),
    url(r'^logout', views.logOut),
    url(r'^detectImage', views.detectImage),
    url(r'^detectWithWebcam', views.detectWithWebcam),
    url(r'^upload', FileView.as_view(), name='file-upload'),

    url(r'^spotted_criminals', views.spottedCriminals),
    path('found_thief/<int:thief_id>/', views.foundThief, name='found_thief'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
