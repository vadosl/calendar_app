from django.conf.urls import patterns, include, url
from cal import views

urlpatterns = patterns('dbe.cal.views',
    #url(r"^month/(\d+)/(\d+)/(prev|next)/$", "month"),
    #url(r"^month/(\d+)/(\d+)/$", "month"),
    #url(r"^month$", "month"),
    #url(r"^day/(\d+)/(\d+)/(\d+)/$", "day"),
    #url(r"^settings/$", "settings"),
    url(r"^(\d+)/$", views.main, name="main"),
    url(r"^$", views.main, name="main"),
    url(r"^month/(\d+)/(\d+)/(prev|next)/$", views.month, name="month"),
    url(r"^month/(\d+)/(\d+)/$", views.month, name="month"),
    url(r"^month$", views.month, name="month"),
    url(r"^day/(\d+)/(\d+)/(\d+)/$", views.day, name="day"),
    url(r"^settings/$", views.settings, name="settings"),
)
