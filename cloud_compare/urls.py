"""cloud-compare URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from pricing import view_main

urlpatterns = [
    url(r'^pricing/', include('pricing.urls')),
    url(r'^about/$', view_main.about, name='about'),
    url(r'^admin/', admin.site.urls),
    url(r'^$', view_main.main, name='main')
]

handler400 = view_main.error400
handler403 = view_main.error403
handler404 = view_main.error404
handler500 = view_main.error500
