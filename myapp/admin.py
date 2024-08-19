from django.contrib import admin
from .models import *
from .helper.modelsHelper import *

admin.site.register(Baustelle)
admin.site.register(Fahrzeug)
admin.site.register(Hubzug)
admin.site.register(Protokol)
admin.site.register(Mechanik)
admin.site.register(Elektrik)
admin.site.register(ProtokolMechanik)
admin.site.register(ProtokolElektrik)
admin.site.register(AllProtocols)
admin.site.register(TestProtokol)

admin.site.register(newBaustelle)
admin.site.register(newFahrzeug)
admin.site.register(newHubzug)
admin.site.register(ProtocolHubzugLiftingHost)
admin.site.register(CustomUser)
