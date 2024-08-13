from django.db import models

class ProtocolHubzugLiftingHost(models.Model):
    isSaved = models.BooleanField(default=False)
    isExported = models.BooleanField(default=False)

    protocolName  = "Maßkontolle Rahmen"
    drawing = models.TextField(verbose_name="Zeichnung-Nr / Drawing No.", null=True, blank=True)
    rev = models.TextField(verbose_name="Rev", null=True, blank=True)
    order = models.TextField(verbose_name="Auftragsnr. / Order No.", null=True, blank=True)
    order_sag = models.TextField(verbose_name="Auftragsnr.-SAG / Order No.-SAG", null=True, blank=True)
    device = models.TextField(verbose_name="Geräte-Nr. / Device No.", null=True, blank=True)
    hoist = models.TextField(verbose_name="Hubzug-Nr. / Hoist No.", null=True, blank=True)
    company = models.TextField(verbose_name="Firma / Company", null=True, blank=True)
    quantity = models.TextField(verbose_name="Stückzahl / Quantity", null=True, blank=True)
    check_size_1 = models.TextField(verbose_name="1. Horizontaler Abstand der Anschlussbohrungen* / Horizontal distance of connecting holes*", null=True, blank=True)
    check_size_2 = models.TextField(verbose_name="2. Vertikaler Abstand der Anschlussbohrungen / Vertical distance of connecting holes*", null=True, blank=True)
    check_size_3 = models.TextField(verbose_name="3. Durchmesser 1.Anschlussbohrung / Diameter of 1st connecting hole", null=True, blank=True)
    check_size_4 = models.TextField(verbose_name="4. Durchmesser 2. Anschlussbohrung / Diameter of 2nd connecting hole", null=True, blank=True)
    check_size_4a = models.TextField(verbose_name="4a. Abstand zwischen Gehäuseseiten* / Distance between the frame sides *", null=True, blank=True)
    check_size_5 = models.TextField(verbose_name="5. Horizontaler Abstand zu Lochkreismitte für Lageranbau* / Horizontal distance to centre of drum bearing*", null=True, blank=True)
    check_size_6 = models.TextField(verbose_name="6. Vertikaler Abstand zu Lochkreismitte für Lageranbau* / Vertical distance to centre of drum bearing*", null=True, blank=True)
    check_size_7 = models.TextField(verbose_name="7. Durchmesser der Lagerbohrung* / Diameter of the holes for the bearings*", null=True, blank=True)
    check_size_8 = models.TextField(verbose_name="8. Abstand zwischen Trommelachse und Bohrung für Klinke / Distance between centre of drum shaft and hole for catch lever", null=True, blank=True)
    check_size_9 = models.TextField(verbose_name="9. Abstand zwischen Trommelachse und Bohrung für Klinke / Distance between centre of drum shaft and hole for catch lever", null=True, blank=True)
    check_size_10 = models.TextField(verbose_name="10. Durchmesser der beiden Aufnahmebohrungen der Klinke / Diameter of both holes for the Catch lever", null=True, blank=True)
    position_tolerance_11 = models.TextField(verbose_name="11. Rechtwinkligkeit Trommellagerachse zu beiden Flächen der Seitenscheiben Pos. 1+2 / Right angle drum axle to both sides of the hoist frame Pos. 1 and Pos. 2", null=True, blank=True)
    miscellaneous = models.TextField(verbose_name="Sonstiges / Miscellaneous", blank=True, null=True)
    remark = models.TextField(verbose_name="Bemerkungen / Remarks", blank=True, null=True)
    measure = models.TextField(verbose_name="Messgerät / Measure tools", blank=True, null=True)
    date = models.CharField(verbose_name="Datum / Date", max_length=10, help_text="Format: dd.mm.yyyy", null=True, blank=True)
    inspector = models.CharField(verbose_name="Prüfer / Inspector", max_length=20, null=True, blank=True)
    department = models.TextField(verbose_name="Abteilung / Department", blank=True, null=True)
    last_changer = models.CharField(verbose_name="Last modified by", max_length=100, blank=True, null=True)
    baustelle = models.CharField(verbose_name="Baustelle", max_length=100, blank=True, null=True)
    