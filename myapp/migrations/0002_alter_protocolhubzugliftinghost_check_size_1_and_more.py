# Generated by Django 4.2.1 on 2024-08-08 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='check_size_1',
            field=models.TextField(null=True, verbose_name='1. Horizontaler Abstand der Anschlussbohrungen* / Horizontal distance of connecting holes*'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='check_size_10',
            field=models.TextField(null=True, verbose_name='10. Durchmesser der beiden Aufnahmebohrungen der Klinke / Diameter of both holes for the Catch lever'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='check_size_2',
            field=models.TextField(null=True, verbose_name='2. Vertikaler Abstand der Anschlussbohrungen / Vertical distance of connecting holes*'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='check_size_3',
            field=models.TextField(null=True, verbose_name='3. Durchmesser 1.Anschlussbohrung / Diameter of 1st connecting hole'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='check_size_4',
            field=models.TextField(null=True, verbose_name='4. Durchmesser 2. Anschlussbohrung / Diameter of 2nd connecting hole'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='check_size_4a',
            field=models.TextField(null=True, verbose_name='4a. Abstand zwischen Gehäuseseiten* / Distance between the frame sides *'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='check_size_5',
            field=models.TextField(null=True, verbose_name='5. Horizontaler Abstand zu Lochkreismitte für Lageranbau* / Horizontal distance to centre of drum bearing*'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='check_size_6',
            field=models.TextField(null=True, verbose_name='6. Vertikaler Abstand zu Lochkreismitte für Lageranbau* / Vertical distance to centre of drum bearing*'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='check_size_7',
            field=models.TextField(null=True, verbose_name='7. Durchmesser der Lagerbohrung* / Diameter of the holes for the bearings*'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='check_size_8',
            field=models.TextField(null=True, verbose_name='8. Abstand zwischen Trommelachse und Bohrung für Klinke / Distance between centre of drum shaft and hole for catch lever'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='check_size_9',
            field=models.TextField(null=True, verbose_name='9. Abstand zwischen Trommelachse und Bohrung für Klinke / Distance between centre of drum shaft and hole for catch lever'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='company',
            field=models.TextField(null=True, verbose_name='Firma / Company'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='date',
            field=models.CharField(help_text='Format: dd.mm.yyyy', max_length=10, null=True, verbose_name='Datum / Date'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='device',
            field=models.TextField(null=True, verbose_name='Geräte-Nr. / Device No.'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='drawing',
            field=models.TextField(null=True, verbose_name='Zeichnung-Nr / Drawing No.'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='hoist',
            field=models.TextField(null=True, verbose_name='Hubzug-Nr. / Hoist No.'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='inspector',
            field=models.CharField(max_length=20, null=True, verbose_name='Prüfer / Inspector'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='order',
            field=models.TextField(null=True, verbose_name='Auftragsnr. / Order No.'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='order_sag',
            field=models.TextField(null=True, verbose_name='Auftragsnr.-SAG / Order No.-SAG'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='position_tolerance_11',
            field=models.TextField(null=True, verbose_name='11. Rechtwinkligkeit Trommellagerachse zu beiden Flächen der Seitenscheiben Pos. 1+2 / Right angle drum axle to both sides of the hoist frame Pos. 1 and Pos. 2'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='quantity',
            field=models.TextField(null=True, verbose_name='Stückzahl / Quantity'),
        ),
        migrations.AlterField(
            model_name='protocolhubzugliftinghost',
            name='rev',
            field=models.TextField(null=True, verbose_name='Rev'),
        ),
    ]
