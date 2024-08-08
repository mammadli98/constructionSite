"""
URL configuration for siemens project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from xml.etree.ElementInclude import include
from django.contrib import admin
from django.urls import path, include
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login),
    path('adminView/', views.adminView, name='admin_view'),
    path('userView/', views.userView, name='user_view'),
    path('update_fahrzeug_visibility/<int:fahrzeug_id>/', views.update_fahrzeug_visibility, name='update_fahrzeug_visibility'),
    path('reset/<int:fahrzeug_id>/<str:protokol>', views.reset, name='reset'),

    path('protocolHubzugLiftingHost/<int:protocol_id>/', views.protocolHubzugLiftingHostView, name='protocolHubzugLiftingHost'),
    path('protocolHubzugLiftingHost/update/<int:protocol_id>/', views.protocolHubzugLiftingHostUpdate, name='protocolHubzugLiftingHostUpdate'),
    path('exportProtokolHubzugLiftingHost/<int:protocol_id>/export_pdf/', views.exportProtokolHubzugLiftingHost, name='exportProtokolHubzugLiftingHost'),






    path('home/', views.welcome_page),
    path('baustelle/', views.baustellen),
    path('fahrzeugsnummer/', views.fahrzeugsnummer),
    path('menu/', views.menu),

    path('hubzug/', views.hubzug_view),
    path('protokol/<int:id>/', views.protokol_detail, name='protokol_detail'),
    path('protokol/update/<int:id>/', views.protokol_update, name='protokol_update'),
    path('protokol/reset/<int:id>/', views.protokol_reset, name='protokol_reset'),
    path('protokol/<int:id>/export_pdf/', views.protokol_export_pdf, name='protokol_export_pdf'),

    path('mechanik/', views.mechanik_view),
    path('protokolMechanik/<int:id>/', views.protokolMechanik_detail, name='protokolMechanik_detail'),
    path('protokolMechanik/update/<int:id>/', views.protokolMechanik_update, name='protokolMechanik_update'),
    path('protokolMechanik/reset/<int:id>/', views.protokolMechanik_reset, name='protokolMechanik_reset'),
    path('protokolMechanik/<int:id>/export_pdf/', views.protokolMechanik_export_pdf, name='protokolMechanik_export_pdf'),

    path('elektrik/', views.elektrik_view),
    path('protokolElektrik/<int:id>/', views.protokolElektrik_detail, name='protokolElektrik_detail'),
    path('protokolElektrik/update/<int:id>/', views.protokolElektrik_update, name='protokolElektrik_update'),
    path('protokolElektrik/reset/<int:id>/', views.protokolElektrik_reset, name='protokolElektrik_reset'),
    path('protokolElektrik/<int:id>/export_pdf/', views.protokolElektrik_export_pdf, name='protokolElektrik_export_pdf'),

    path('protocol_list/', views.protocol_list, name='protocol_list'),
]
