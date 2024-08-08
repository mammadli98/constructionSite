from django.db import models
from django.contrib.auth.models import User
from .helper.modelsHelper import *
    
class newBaustelle(models.Model):
    baustelleName=models.CharField(max_length=30)

    def __str__(self):
        return self.baustelleName

class newHubzug(models.Model):
    protocol1 = models.ForeignKey(ProtocolHubzugLiftingHost, on_delete = models.CASCADE)

class newFahrzeug(models.Model):
    baustelle = models.ForeignKey(newBaustelle, on_delete = models.CASCADE)
    fahrzeugName = models.CharField(max_length=30)
    isVisible = models.BooleanField(default=False)
    hubzug = models.OneToOneField(newHubzug, on_delete=models.CASCADE, null=True, blank=True) 

    def __str__(self):
        return self.fahrzeugName
    













"-------------------------------------------------"

class Baustelle(models.Model):
    baustelle=models.CharField(max_length=30)


    def __str__(self):
        return self.baustelle
    

class Fahrzeug(models.Model):
    baustelle = models.ForeignKey(Baustelle, on_delete = models.CASCADE)
    fahrzeug = models.CharField(max_length=30)

    def __str__(self):
        return self.fahrzeug


class Hubzug(models.Model):
    baustelle = models.ForeignKey(Baustelle, on_delete = models.CASCADE)
    fahrzeug = models.ForeignKey(Fahrzeug, on_delete = models.CASCADE)

    def __str__(self):
        return "Hubzug " + self.baustelle.baustelle + " " + self.fahrzeug.fahrzeug

class Mechanik(models.Model):
    baustelle = models.ForeignKey(Baustelle, on_delete = models.CASCADE)
    fahrzeug = models.ForeignKey(Fahrzeug, on_delete = models.CASCADE)

    def __str__(self):
        return "Mechanik " + self.baustelle.baustelle + " " + self.fahrzeug.fahrzeug

class Elektrik(models.Model):
    baustelle = models.ForeignKey(Baustelle, on_delete = models.CASCADE)
    fahrzeug = models.ForeignKey(Fahrzeug, on_delete = models.CASCADE)

    def __str__(self):
        return "Elektrik " + self.baustelle.baustelle + " " + self.fahrzeug.fahrzeug

class Protokol(models.Model):
    name=models.CharField(max_length=30)
    description=models.CharField(max_length=30, blank=True, null=True)
    size=models.CharField(max_length=30, blank=True, null=True)
    lastChanger=models.CharField(max_length=30, blank=True, null=True)
    hubzug = models.ForeignKey(Hubzug, on_delete = models.CASCADE)

    def __str__(self):
        return "Protokoll "+ self.name + " Hubzug " + self.hubzug.baustelle.baustelle + " " + self.hubzug.fahrzeug.fahrzeug

class ProtokolMechanik(models.Model):
    name=models.CharField(max_length=30)
    description=models.CharField(max_length=30, blank=True, null=True)
    size=models.CharField(max_length=30, blank=True, null=True)
    lastChanger=models.CharField(max_length=30, blank=True, null=True)
    mechanik = models.ForeignKey(Mechanik, on_delete = models.CASCADE)

    def __str__(self):
        return "Protokoll "+ self.name + " Mechanik " + self.mechanik.baustelle.baustelle + " " + self.mechanik.fahrzeug.fahrzeug


class ProtokolElektrik(models.Model):
    name=models.CharField(max_length=30)
    description=models.CharField(max_length=30, blank=True, null=True)
    size=models.CharField(max_length=30, blank=True, null=True)
    lastChanger=models.CharField(max_length=30, blank=True, null=True)
    elektrik = models.ForeignKey(Elektrik, on_delete = models.CASCADE)

    elektrikInside = models.JSONField(blank=True, null=True) 

    def __str__(self):
        return "Protokoll "+ self.name + " Elektrik " + self.elektrik.baustelle.baustelle + " " + self.elektrik.fahrzeug.fahrzeug


class AllProtocols(models.Model):
    baustelle = models.CharField(max_length=30)
    fahrzeug = models.CharField(max_length=30)
    teil = models.CharField(max_length=30)
    protokolType = models.CharField(max_length=30)
    path = models.CharField(max_length=100)

    def __str__(self):
        return self.path


class TestProtokol(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=30, blank=True, null=True)
    size = models.CharField(max_length=30, blank=True, null=True)
    lastChanger = models.CharField(max_length=30, blank=True, null=True)
    hubzug = models.ForeignKey(Hubzug, on_delete=models.CASCADE)
    massnahme = models.JSONField(blank=True, null=True)  # JSONField to store dictionary




