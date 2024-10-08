# Generated by Django 4.2.1 on 2024-08-18 11:33

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='AllProtocols',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('baustelle', models.CharField(max_length=30)),
                ('fahrzeug', models.CharField(max_length=30)),
                ('teil', models.CharField(max_length=30)),
                ('protokolType', models.CharField(max_length=30)),
                ('path', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Baustelle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('baustelle', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Elektrik',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('baustelle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.baustelle')),
            ],
        ),
        migrations.CreateModel(
            name='Fahrzeug',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fahrzeug', models.CharField(max_length=30)),
                ('baustelle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.baustelle')),
            ],
        ),
        migrations.CreateModel(
            name='Hubzug',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('baustelle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.baustelle')),
                ('fahrzeug', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.fahrzeug')),
            ],
        ),
        migrations.CreateModel(
            name='Mechanik',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('baustelle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.baustelle')),
                ('fahrzeug', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.fahrzeug')),
            ],
        ),
        migrations.CreateModel(
            name='newBaustelle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('baustelleName', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='ProtocolHubzugLiftingHost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isSaved', models.BooleanField(default=False)),
                ('isExported', models.BooleanField(default=False)),
                ('drawing', models.TextField(blank=True, null=True, verbose_name='Zeichnung-Nr / Drawing No.')),
                ('rev', models.TextField(blank=True, null=True, verbose_name='Rev')),
                ('order', models.TextField(blank=True, null=True, verbose_name='Auftragsnr. / Order No.')),
                ('order_sag', models.TextField(blank=True, null=True, verbose_name='Auftragsnr.-SAG / Order No.-SAG')),
                ('device', models.TextField(blank=True, null=True, verbose_name='Geräte-Nr. / Device No.')),
                ('hoist', models.TextField(blank=True, null=True, verbose_name='Hubzug-Nr. / Hoist No.')),
                ('company', models.TextField(blank=True, null=True, verbose_name='Firma / Company')),
                ('quantity', models.TextField(blank=True, null=True, verbose_name='Stückzahl / Quantity')),
                ('check_size_1', models.TextField(blank=True, null=True, verbose_name='1. Horizontaler Abstand der Anschlussbohrungen* / Horizontal distance of connecting holes*')),
                ('check_size_2', models.TextField(blank=True, null=True, verbose_name='2. Vertikaler Abstand der Anschlussbohrungen / Vertical distance of connecting holes*')),
                ('check_size_3', models.TextField(blank=True, null=True, verbose_name='3. Durchmesser 1.Anschlussbohrung / Diameter of 1st connecting hole')),
                ('check_size_4', models.TextField(blank=True, null=True, verbose_name='4. Durchmesser 2. Anschlussbohrung / Diameter of 2nd connecting hole')),
                ('check_size_4a', models.TextField(blank=True, null=True, verbose_name='4a. Abstand zwischen Gehäuseseiten* / Distance between the frame sides *')),
                ('check_size_5', models.TextField(blank=True, null=True, verbose_name='5. Horizontaler Abstand zu Lochkreismitte für Lageranbau* / Horizontal distance to centre of drum bearing*')),
                ('check_size_6', models.TextField(blank=True, null=True, verbose_name='6. Vertikaler Abstand zu Lochkreismitte für Lageranbau* / Vertical distance to centre of drum bearing*')),
                ('check_size_7', models.TextField(blank=True, null=True, verbose_name='7. Durchmesser der Lagerbohrung* / Diameter of the holes for the bearings*')),
                ('check_size_8', models.TextField(blank=True, null=True, verbose_name='8. Abstand zwischen Trommelachse und Bohrung für Klinke / Distance between centre of drum shaft and hole for catch lever')),
                ('check_size_9', models.TextField(blank=True, null=True, verbose_name='9. Abstand zwischen Trommelachse und Bohrung für Klinke / Distance between centre of drum shaft and hole for catch lever')),
                ('check_size_10', models.TextField(blank=True, null=True, verbose_name='10. Durchmesser der beiden Aufnahmebohrungen der Klinke / Diameter of both holes for the Catch lever')),
                ('position_tolerance_11', models.TextField(blank=True, null=True, verbose_name='11. Rechtwinkligkeit Trommellagerachse zu beiden Flächen der Seitenscheiben Pos. 1+2 / Right angle drum axle to both sides of the hoist frame Pos. 1 and Pos. 2')),
                ('miscellaneous', models.TextField(blank=True, null=True, verbose_name='Sonstiges / Miscellaneous')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='Bemerkungen / Remarks')),
                ('measure', models.TextField(blank=True, null=True, verbose_name='Messgerät / Measure tools')),
                ('date', models.CharField(blank=True, help_text='Format: dd.mm.yyyy', max_length=10, null=True, verbose_name='Datum / Date')),
                ('inspector', models.CharField(blank=True, max_length=20, null=True, verbose_name='Prüfer / Inspector')),
                ('department', models.TextField(blank=True, null=True, verbose_name='Abteilung / Department')),
                ('last_changer', models.CharField(blank=True, max_length=100, null=True, verbose_name='Last modified by')),
                ('baustelle', models.CharField(blank=True, max_length=100, null=True, verbose_name='Baustelle')),
            ],
        ),
        migrations.CreateModel(
            name='TestProtokol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(blank=True, max_length=30, null=True)),
                ('size', models.CharField(blank=True, max_length=30, null=True)),
                ('lastChanger', models.CharField(blank=True, max_length=30, null=True)),
                ('massnahme', models.JSONField(blank=True, null=True)),
                ('hubzug', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.hubzug')),
            ],
        ),
        migrations.CreateModel(
            name='ProtokolMechanik',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(blank=True, max_length=30, null=True)),
                ('size', models.CharField(blank=True, max_length=30, null=True)),
                ('lastChanger', models.CharField(blank=True, max_length=30, null=True)),
                ('mechanik', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.mechanik')),
            ],
        ),
        migrations.CreateModel(
            name='ProtokolElektrik',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(blank=True, max_length=30, null=True)),
                ('size', models.CharField(blank=True, max_length=30, null=True)),
                ('lastChanger', models.CharField(blank=True, max_length=30, null=True)),
                ('elektrikInside', models.JSONField(blank=True, null=True)),
                ('elektrik', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.elektrik')),
            ],
        ),
        migrations.CreateModel(
            name='Protokol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(blank=True, max_length=30, null=True)),
                ('size', models.CharField(blank=True, max_length=30, null=True)),
                ('lastChanger', models.CharField(blank=True, max_length=30, null=True)),
                ('hubzug', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.hubzug')),
            ],
        ),
        migrations.CreateModel(
            name='newHubzug',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protocol1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.protocolhubzugliftinghost')),
            ],
        ),
        migrations.CreateModel(
            name='newFahrzeug',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fahrzeugName', models.CharField(max_length=30)),
                ('isVisible', models.BooleanField(default=False)),
                ('baustelle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.newbaustelle')),
                ('hubzug', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.newhubzug')),
            ],
        ),
        migrations.AddField(
            model_name='elektrik',
            name='fahrzeug',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.fahrzeug'),
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('age', models.IntegerField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
