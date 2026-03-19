from django.shortcuts import redirect, render, HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from .helper.modelsHelper import *
from django.shortcuts import render, get_object_or_404
from .models import Protokol
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.staticfiles import finders
from siemens import settings
from django.db.models import Q
from django.views.decorators.http import require_POST


import os
import io
import json
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.views.decorators.http import require_http_methods
from datetime import datetime


from .forms import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import copy

GLOBAL_DIR = "/home/mammadli98/Documents/huseynSiemens/Protokols/"

def update_baustellen(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id)
        baustellen_ids = request.POST.getlist('baustellen')
        baustellen = newBaustelle.objects.filter(id__in=baustellen_ids)
        user.baustellen.set(baustellen)
        protokollen_list = request.POST.getlist('protokolle')

        if "h" in protokollen_list:
            user.hubzug = True
        else:
            user.hubzug = False
        
        if "m" in protokollen_list:
            user.mechanik = True
        else:
            user.mechanik = False
        
        if "e" in protokollen_list:
            user.elektrik = True
        else:
            user.elektrik = False
        
        user.save()

        return redirect("/adminView/")

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
    
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            request.session['username'] = username
            request.session['id'] = user.id
            if username == 'admin':
                return redirect("adminView/")
            elif user.pruefer == True:
                return redirect("prueferView/")
            return redirect("userView/")
        else:
            messages.info(request, "invalid credentials")
            return redirect("/")
    else:
        return render(request, "userViews/loginView.html")

def logout(request):
    auth.logout(request)
    return redirect("/")

def sollWertView(request):
    username = request.session.get('username', '')
    fahrzeug_id = request.GET.get('fahrzeugId', None)

    protocols = newFahrzeug.objects.all()
    filter_form = ProtocolFilterForm(request.GET or None)
    newPermanentProtocol = PermanentProtocol.objects.all()
    # Apply filters based on form input
    if filter_form.is_valid():
        baustelle = filter_form.cleaned_data.get('baustelle')
        fahrzeug = filter_form.cleaned_data.get('fahrzeug')
        protocol_name = filter_form.cleaned_data.get('protocol_name')
        status = filter_form.cleaned_data.get('status')
        teil = filter_form.cleaned_data.get('teil')

        if baustelle:
            protocols = protocols.filter(baustelle__baustelleName__icontains=baustelle)
        if fahrzeug:
            protocols = protocols.filter(fahrzeugName__icontains=fahrzeug)
        if protocol_name:
            protocols = protocols.filter(hubzug__protocol1__protocolName__icontains=protocol_name)
        if status:
            if status == 'exported':
                protocols = protocols.filter(hubzug__protocol1__isExported=True)
            elif status == 'closed':
                protocols = protocols.filter(hubzug__protocol1__isClosed=True)
                protocols = protocols.filter(hubzug__protocol1__isExported=False)
            elif status == 'saved':
                protocols = protocols.filter(hubzug__protocol1__isSaved=True)
                protocols = protocols.filter(hubzug__protocol1__isClosed=False)
                protocols = protocols.filter(hubzug__protocol1__isExported=False)
            elif status == 'offen':
                protocols = protocols.filter(hubzug__protocol1__isSaved=False)
            elif status == 'correction':
                protocols = protocols.filter(hubzug__protocol1__isCorrecturNeeded=True)

    context = {
        'username': username,
        'fahrzeug_id': fahrzeug_id,
        'fahrzeugs': protocols,
        'filter_form': filter_form,
        'permanentProtocol' : newPermanentProtocol
    }
    return render(request, 'sollWertView.html', context)

@login_required(login_url="/")
def adminView(request):
    baustellen_list = newBaustelle.objects.all()
    fahrzeugen_list = newFahrzeug.objects.all()  # Initially, no Fahrzeuge displayed
    user_list = CustomUser.objects.all()
    
    if request.method == 'POST':
        if 'baustelleName' in request.POST:
            baustelle_form = NewBaustelleForm(request.POST)
            if baustelle_form.is_valid():
                baustelle_form.save()
        elif 'fahrzeugName' in request.POST:
            fahrzeug_names = newFahrzeug.objects.all().values_list('fahrzeugName', flat=True)
            fahrzeugFrom = int(request.POST.get('fahrzeug_number_from'))
            fahrzeugTo = int(request.POST.get('fahrzeug_number_to'))
            fahrzeugType = request.POST.get('fahrzeug_type')
            fahrzeugName = request.POST.get('fahrzeugName')

            permanentHubzugProtocol1 = ProtocolHubzugLiftingHost()
            permanentHubzugProtocol1.save()
            permanentHubzugProtocol4 = ProtocolLaufHubzug()
            permanentHubzugProtocol4.save()
            newPermanentProtocol = PermanentProtocol.objects.create(
                permanentProtocolName=f"{fahrzeugName}_{fahrzeugFrom:03}_{fahrzeugTo:03} ({fahrzeugType})",
                permanentProtocol1 = permanentHubzugProtocol1,
                permanentProtocol4 = permanentHubzugProtocol4
            )
            newPermanentProtocol.save() 

            if fahrzeugFrom <= fahrzeugTo:
                for fahrzeug in range(int(fahrzeugFrom), int(fahrzeugTo) + 1):
                    fahrzeug_form = NewFahrzeugForm(request.POST)
                    if fahrzeug_form.is_valid():
                        fahrzeugName = request.POST.get('fahrzeugName')
                        if f"{fahrzeugName}_{fahrzeug:03} ({fahrzeugType})" in fahrzeug_names:
                            continue
                        
                        # Create unique protocol instances for this fahrzeug
                        hubzugProtocol1 = ProtocolHubzugLiftingHost()
                        hubzugProtocol1.save()

                        hubzugProtocol2 = ProtocolHubzugLaufSeiltrommel()
                        hubzugProtocol2.save()

                        hubzugProtocol3 = ProtocolHubzugMassSeiltrommel()
                        hubzugProtocol3.save()

                        hubzugProtocol4 = ProtocolLaufHubzug()
                        hubzugProtocol4.save()

                        hubzugProtocol5 = ProtocolEndkontrolle()
                        hubzugProtocol5.save()

                        # Create hubzug and associate unique protocols
                        hubzug = newHubzug()
                        hubzug.protocol1 = hubzugProtocol1
                        hubzug.protocol2 = hubzugProtocol2
                        hubzug.protocol3 = hubzugProtocol3
                        hubzug.protocol4 = hubzugProtocol4
                        hubzug.protocol5 = hubzugProtocol5
                        hubzug.save()

                        # Save fahrzeug with hubzug association
                        fahrzeug_form = fahrzeug_form.save(commit=False)
                        fahrzeug_form.hubzug = hubzug 
                        fahrzeug_form.fahrzeugName = f"{fahrzeug_form.fahrzeugName}_{fahrzeug:03} ({fahrzeugType})"
                        fahrzeug_form.save()

                        # Add only the unique protocol to the current PermanentProtocol
                        newPermanentProtocol.protocol1.add(hubzugProtocol1)
                        newPermanentProtocol.protocol4.add(hubzugProtocol4)
            newPermanentProtocol.save()
        elif 'username' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            adresse = request.POST.get('adresse')
            pruefer = request.POST.get('pruefer')
            baustellen_ids = request.POST.getlist('baustellen')
            # Create the user
            new_user = CustomUser(username=username)
            new_user.set_password(password)
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.email = email
            new_user.address = adresse
            new_user.pruefer = pruefer
            new_user.save()
            for baustelle_id in baustellen_ids:
                baustelle = newBaustelle.objects.get(id=baustelle_id)
                new_user.baustellen.add(baustelle)
            new_user.save()
                
        return redirect('/adminView/')
    else:
        baustelle_form = NewBaustelleForm()
        fahrzeug_form = NewFahrzeugForm()

    context = {
        'baustellen_list': baustellen_list,
        'fahrzeug_list': fahrzeugen_list,
        'user_list': user_list,
        'baustelle_form': baustelle_form,
        'fahrzeug_form': fahrzeug_form
    }
    
    #permanent_protocol_a = PermanentProtocol.objects.get(permanentProtocolName="C_001_003 (H)")
    #print(permanent_protocol_a.id)

    return render(request, "adminView.html", context)

@login_required(login_url="/")
def userView(request):
    modal_show = False  # Flag to control modal display
    if request.method == 'POST':
        userPasswordForm = PasswordChangeForm(request.user, request.POST)
        if userPasswordForm.is_valid():
            user = userPasswordForm.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/')  # Adjust the redirect as needed
        else:
            modal_show = True  # Set the flag to keep the modal open
    else:
        userPasswordForm = PasswordChangeForm(request.user)

    username = request.session.get('username', '')
    id = request.session.get('id', '')
    baustelle = CustomUser.objects.get(id=id).baustellen.all()
    user = get_object_or_404(CustomUser, id=id)

    context = {
        'user':user,
        'username': username,
        'baustellen_list': baustelle,
        'fahrzeug_list': newFahrzeug.objects.all(),
        'userPassword_form': userPasswordForm,
        'modal_show': modal_show  # Pass this flag to the template
    }
    return render(request, "userView.html", context)
    
@login_required(login_url="/")
def prueferView(request):
    username = request.session.get('username', '')
    fahrzeug_id = request.GET.get('fahrzeugId', None)

    user_id = request.session.get('id', '')
    user = CustomUser.objects.get(id=user_id)
    user_baustellen = user.baustellen.all()

    # Filter newFahrzeug objects where baustelle is in user's baustellen
    protocols = newFahrzeug.objects.filter(baustelle__in=user_baustellen)
    filter_form = ProtocolFilterForm(request.GET or None)
    # Apply filters based on form input
    if filter_form.is_valid():
        baustelle = filter_form.cleaned_data.get('baustelle')
        fahrzeug = filter_form.cleaned_data.get('fahrzeug')
        protocol_name = filter_form.cleaned_data.get('protocol_name')
        status = filter_form.cleaned_data.get('status')
        teil = filter_form.cleaned_data.get('teil')

        if baustelle:
            protocols = protocols.filter(baustelle__baustelleName__icontains=baustelle)
        if fahrzeug:
            protocols = protocols.filter(fahrzeugName__icontains=fahrzeug)
        if protocol_name:
            protocols = protocols.filter(hubzug__protocol1__protocolName__icontains=protocol_name)
        if status:
            if status == 'exported':
                protocols = protocols.filter(hubzug__protocol1__isExported=True)
            elif status == 'closed':
                protocols = protocols.filter(hubzug__protocol1__isClosed=True)
                protocols = protocols.filter(hubzug__protocol1__isExported=False)
            elif status == 'saved':
                protocols = protocols.filter(hubzug__protocol1__isSaved=True)
                protocols = protocols.filter(hubzug__protocol1__isClosed=False)
                protocols = protocols.filter(hubzug__protocol1__isExported=False)
            elif status == 'offen':
                protocols = protocols.filter(hubzug__protocol1__isSaved=False)
            elif status == 'correction':
                protocols = protocols.filter(hubzug__protocol1__isCorrecturNeeded=True)

    context = {
        'username': username,
        'fahrzeug_id': fahrzeug_id,
        'fahrzeugs': protocols,
        'filter_form': filter_form
    }
    return render(request, 'prueferView.html', context)

@csrf_exempt
def update_fahrzeug_visibility(request, fahrzeug_id):
    if request.method == 'POST':
        try:
            fahrzeug = newFahrzeug.objects.get(id=fahrzeug_id)
            data = json.loads(request.body)
            fahrzeug.isVisible = data['isVisible']
            fahrzeug.save()
            return JsonResponse({'status': 'success'})
        except newFahrzeug.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Fahrzeug not found'})
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'})

@csrf_exempt
def reset(request, fahrzeug_id, protokol):
    if request.method == 'POST':
        try:
            fahrzeug = newFahrzeug.objects.get(id=fahrzeug_id)
            #data = json.loads(request.body)
            return JsonResponse({'status': 'success'})
        except newFahrzeug.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Fahrzeug not found'})
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'})

def protocolHubzugLiftingHostView(request, protocol_id):
    # Assume `get_protokol` is a function that retrieves the protocol data by ID
    currentUser = request.user
    protokol = get_object_or_404(ProtocolHubzugLiftingHost, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    return render(request, 'protocolHubzugLiftingHost.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id, 'current_user': currentUser})

def protocolHubzugLiftingHostAdminView(request, protocol_id):
    # Assume `get_protokol` is a function that retrieves the protocol data by ID
    currentUser = request.user
    protokol = get_object_or_404(ProtocolHubzugLiftingHost, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    return render(request, 'protocolHubzugLiftingHostAdmin.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id, 'current_user': currentUser})

def protocolHubzugLaufSeiltrommelView(request, protocol_id):
    # Assume `get_protokol` is a function that retrieves the protocol data by ID
    currentUser = request.user
    protokol = get_object_or_404(ProtocolHubzugLaufSeiltrommel, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    return render(request, 'protocolHubzugLaufSeiltrommel.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id, 'current_user': currentUser})

def protocolHubzugMassSeiltrommelView(request, protocol_id):
    # Assume `get_protokol` is a function that retrieves the protocol data by ID
    currentUser = request.user
    protokol = get_object_or_404(ProtocolHubzugMassSeiltrommel, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    return render(request, 'protocolHubzugMassSeiltrommel.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id, 'current_user': currentUser})

def protocolLaufHubzugView(request, protocol_id):
    # Assume `get_protokol` is a function that retrieves the protocol data by ID
    currentUser = request.user
    protokol = get_object_or_404(ProtocolLaufHubzug, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    return render(request, 'protocolLaufHubzug.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id, 'current_user': currentUser})

def protocolEndkontrolleView(request, protocol_id):
    # Assume `get_protokol` is a function that retrieves the protocol data by ID
    currentUser = request.user
    protokol = get_object_or_404(ProtocolEndkontrolle, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    return render(request, 'protocolEndkontrolle.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id, 'current_user': currentUser})

@require_http_methods(["POST"])
def protocolHubzugLiftingHostUpdate(request, protocol_id):
    protokol = get_object_or_404(ProtocolHubzugLiftingHost, pk=protocol_id)
    currentUser = request.user
    fahrzeug_id = request.GET.get('fahrzeugId', '')


    protokol.oknok_1_1 = request.POST.get('oknok_1_1', '')
    protokol.oknok_1_1_remark = request.POST.get('oknok_1_1_remark', '')
    protokol.oknok_1_2 = request.POST.get('oknok_1_2', '')
    protokol.oknok_1_2_remark = request.POST.get('oknok_1_2_remark', '')
    protokol.oknok_1_3 = request.POST.get('oknok_1_3', '')
    protokol.oknok_1_3_remark = request.POST.get('oknok_1_3_remark', '')
    protokol.oknok_1_4 = request.POST.get('oknok_1_4', '')
    protokol.oknok_1_4_remark = request.POST.get('oknok_1_4_remark', '')
    protokol.oknok_1_5 = request.POST.get('oknok_1_5', '')
    protokol.oknok_1_5_remark = request.POST.get('oknok_1_5_remark', '')
    protokol.oknok_1_6 = request.POST.get('oknok_1_6', '')
    protokol.oknok_1_6_remark = request.POST.get('oknok_1_6_remark', '')
    protokol.oknok_1_7 = request.POST.get('oknok_1_7', '')
    protokol.oknok_1_7_remark = request.POST.get('oknok_1_7_remark', '')
    protokol.oknok_1_8 = request.POST.get('oknok_1_8', '')
    protokol.oknok_1_8_remark = request.POST.get('oknok_1_8_remark', '')
    protokol.oknok_1_9 = request.POST.get('oknok_1_9', '')
    protokol.oknok_1_9_remark = request.POST.get('oknok_1_9_remark', '')
    protokol.oknok_1_10 = request.POST.get('oknok_1_10', '')
    protokol.oknok_1_10_remark = request.POST.get('oknok_1_10_remark', '')
    protokol.oknok_1_11 = request.POST.get('oknok_1_11', '')
    protokol.oknok_1_11_remark = request.POST.get('oknok_1_11_remark', '')
    protokol.oknok_1_12 = request.POST.get('oknok_1_12', '')
    protokol.oknok_1_12_remark = request.POST.get('oknok_1_12_remark', '')
    protokol.oknok_1_13 = request.POST.get('oknok_1_13', '')
    protokol.oknok_1_13_remark = request.POST.get('oknok_1_13_remark', '')
    protokol.oknok_1_14 = request.POST.get('oknok_1_14', '')
    protokol.oknok_1_14_remark = request.POST.get('oknok_1_14_remark', '')
    protokol.oknok_1_15 = request.POST.get('oknok_1_15', '')
    protokol.oknok_1_15_remark = request.POST.get('oknok_1_15_remark', '')
    protokol.oknok_1_16 = request.POST.get('oknok_1_16', '')
    protokol.oknok_1_16_remark = request.POST.get('oknok_1_16_remark', '')
    protokol.oknok_1_17 = request.POST.get('oknok_1_17', '')
    protokol.oknok_1_17_remark = request.POST.get('oknok_1_17_remark', '')
    protokol.oknok_1_18 = request.POST.get('oknok_1_18', '')
    protokol.oknok_1_18_remark = request.POST.get('oknok_1_18_remark', '')
    protokol.oknok_1_19 = request.POST.get('oknok_1_19', '')
    protokol.oknok_1_19_remark = request.POST.get('oknok_1_19_remark', '')
    protokol.oknok_1_20 = request.POST.get('oknok_1_20', '')
    protokol.oknok_1_20_remark = request.POST.get('oknok_1_20_remark', '')
    protokol.oknok_1_23 = request.POST.get('oknok_1_23', '')
    protokol.oknok_1_23_remark = request.POST.get('oknok_1_23_remark', '')
    protokol.oknok_1_24 = request.POST.get('oknok_1_24', '')
    protokol.oknok_1_24_remark = request.POST.get('oknok_1_24_remark', '')
    protokol.oknok_1_25 = request.POST.get('oknok_1_25', '')
    protokol.oknok_1_25_remark = request.POST.get('oknok_1_25_remark', '')
    protokol.oknok_1_26 = request.POST.get('oknok_1_26', '')
    protokol.oknok_1_26_remark = request.POST.get('oknok_1_26_remark', '')
    protokol.oknok_1_27 = request.POST.get('oknok_1_27', '')
    protokol.oknok_1_27_remark = request.POST.get('oknok_1_27_remark', '')
    protokol.oknok_1_28 = request.POST.get('oknok_1_28', '')
    protokol.oknok_1_28_remark = request.POST.get('oknok_1_28_remark', '')
    protokol.oknok_1_29 = request.POST.get('oknok_1_29', '')
    protokol.oknok_1_29_remark = request.POST.get('oknok_1_29_remark', '')
    protokol.oknok_1_30 = request.POST.get('oknok_1_30', '')
    protokol.oknok_1_30_remark = request.POST.get('oknok_1_30_remark', '')
    protokol.oknok_1_31 = request.POST.get('oknok_1_31', '')
    protokol.oknok_1_31_remark = request.POST.get('oknok_1_31_remark', '')
    protokol.oknok_1_32 = request.POST.get('oknok_1_32', '')
    protokol.oknok_1_32_remark = request.POST.get('oknok_1_32_remark', '')
    protokol.oknok_1_33 = request.POST.get('oknok_1_33', '')
    protokol.oknok_1_33_remark = request.POST.get('oknok_1_33_remark', '')
    protokol.oknok_1_34 = request.POST.get('oknok_1_34', '')
    protokol.oknok_1_34_remark = request.POST.get('oknok_1_34_remark', '')
    protokol.oknok_1_35 = request.POST.get('oknok_1_35', '')
    protokol.oknok_1_35_remark = request.POST.get('oknok_1_35_remark', '')
    protokol.oknok_1_36 = request.POST.get('oknok_1_36', '')
    protokol.oknok_1_36_remark = request.POST.get('oknok_1_36_remark', '')
    protokol.oknok_2_1 = request.POST.get('oknok_2_1', '')
    protokol.oknok_2_1_remark = request.POST.get('oknok_2_1_remark', '')
    protokol.oknok_2_2 = request.POST.get('oknok_2_2', '')
    protokol.oknok_2_2_remark = request.POST.get('oknok_2_2_remark', '')
    protokol.oknok_2_3 = request.POST.get('oknok_2_3', '')
    protokol.oknok_2_3_remark = request.POST.get('oknok_2_3_remark', '')
    protokol.oknok_2_4 = request.POST.get('oknok_2_4', '')
    protokol.oknok_2_4_remark = request.POST.get('oknok_2_4_remark', '')
    protokol.oknok_2_5 = request.POST.get('oknok_2_5', '')
    protokol.oknok_2_5_remark = request.POST.get('oknok_2_5_remark', '')
    protokol.oknok_2_6 = request.POST.get('oknok_2_6', '')
    protokol.oknok_2_6_remark = request.POST.get('oknok_2_6_remark', '')
    protokol.oknok_2_7 = request.POST.get('oknok_2_7', '')
    protokol.oknok_2_7_remark = request.POST.get('oknok_2_7_remark', '')
    protokol.oknok_2_8 = request.POST.get('oknok_2_8', '')
    protokol.oknok_2_8_remark = request.POST.get('oknok_2_8_remark', '')
    protokol.oknok_2_9 = request.POST.get('oknok_2_9', '')
    protokol.oknok_2_9_remark = request.POST.get('oknok_2_9_remark', '')
    protokol.oknok_2_10 = request.POST.get('oknok_2_10', '')
    protokol.oknok_2_10_remark = request.POST.get('oknok_2_10_remark', '')
    protokol.oknok_2_11 = request.POST.get('oknok_2_11', '')
    protokol.oknok_2_11_remark = request.POST.get('oknok_2_11_remark', '')
    protokol.oknok_2_12 = request.POST.get('oknok_2_12', '')
    protokol.oknok_2_12_remark = request.POST.get('oknok_2_12_remark', '')
    protokol.oknok_2_13 = request.POST.get('oknok_2_13', '')
    protokol.oknok_2_13_remark = request.POST.get('oknok_2_13_remark', '')
    protokol.oknok_2_14 = request.POST.get('oknok_2_14', '')
    protokol.oknok_2_14_remark = request.POST.get('oknok_2_14_remark', '')
    protokol.oknok_3_1 = request.POST.get('oknok_3_1', '')
    protokol.oknok_3_1_remark = request.POST.get('oknok_3_1_remark', '')
    protokol.oknok_3_2 = request.POST.get('oknok_3_2', '')
    protokol.oknok_3_2_remark = request.POST.get('oknok_3_2_remark', '')
    protokol.oknok_3_3 = request.POST.get('oknok_3_3', '')
    protokol.oknok_3_3_remark = request.POST.get('oknok_3_3_remark', '')
    protokol.oknok_3_4 = request.POST.get('oknok_3_4', '')
    protokol.oknok_3_4_remark = request.POST.get('oknok_3_4_remark', '')
    protokol.oknok_3_5 = request.POST.get('oknok_3_5', '')
    protokol.oknok_3_5_remark = request.POST.get('oknok_3_5_remark', '')
    protokol.oknok_3_6 = request.POST.get('oknok_3_6', '')
    protokol.oknok_3_6_remark = request.POST.get('oknok_3_6_remark', '')
    protokol.oknok_3_8 = request.POST.get('oknok_3_8', '')
    protokol.oknok_3_8_remark = request.POST.get('oknok_3_8_remark', '')
    protokol.oknok_3_10 = request.POST.get('oknok_3_10', '')
    protokol.oknok_3_10_remark = request.POST.get('oknok_3_10_remark', '')
    protokol.oknok_3_11 = request.POST.get('oknok_3_11', '')
    protokol.oknok_3_11_remark = request.POST.get('oknok_3_11_remark', '')
    protokol.oknok_3_12 = request.POST.get('oknok_3_12', '')
    protokol.oknok_3_12_remark = request.POST.get('oknok_3_12_remark', '')
    protokol.oknok_3_13 = request.POST.get('oknok_3_13', '')
    protokol.oknok_3_13_remark = request.POST.get('oknok_3_13_remark', '')
    protokol.oknok_3_14 = request.POST.get('oknok_3_14', '')
    protokol.oknok_3_14_remark = request.POST.get('oknok_3_14_remark', '')
    protokol.oknok_3_15 = request.POST.get('oknok_3_15', '')
    protokol.oknok_3_15_remark = request.POST.get('oknok_3_15_remark', '')
    protokol.oknok_3_16 = request.POST.get('oknok_3_16', '')
    protokol.oknok_3_16_remark = request.POST.get('oknok_3_16_remark', '')
    protokol.oknok_3_17 = request.POST.get('oknok_3_17', '')
    protokol.oknok_3_17_remark = request.POST.get('oknok_3_17_remark', '')
    protokol.oknok_3_18 = request.POST.get('oknok_3_18', '')
    protokol.oknok_3_18_remark = request.POST.get('oknok_3_18_remark', '')
    protokol.oknok_3_19 = request.POST.get('oknok_3_19', '')
    protokol.oknok_3_19_remark = request.POST.get('oknok_3_19_remark', '')
    protokol.oknok_3_20 = request.POST.get('oknok_3_20', '')
    protokol.oknok_3_20_remark = request.POST.get('oknok_3_20_remark', '')
    protokol.oknok_3_21 = request.POST.get('oknok_3_21', '')
    protokol.oknok_3_21_remark = request.POST.get('oknok_3_21_remark', '')
    protokol.oknok_3_22 = request.POST.get('oknok_3_22', '')
    protokol.oknok_3_22_remark = request.POST.get('oknok_3_22_remark', '')
    protokol.oknok_3_23 = request.POST.get('oknok_3_23', '')
    protokol.oknok_3_23_remark = request.POST.get('oknok_3_23_remark', '')
    protokol.oknok_3_24 = request.POST.get('oknok_3_24', '')
    protokol.oknok_3_24_remark = request.POST.get('oknok_3_24_remark', '')
    protokol.oknok_3_25 = request.POST.get('oknok_3_25', '')
    protokol.oknok_3_25_remark = request.POST.get('oknok_3_25_remark', '')
    protokol.oknok_3_26 = request.POST.get('oknok_3_26', '')
    protokol.oknok_3_26_remark = request.POST.get('oknok_3_26_remark', '')
    protokol.oknok_3_27 = request.POST.get('oknok_3_27', '')
    protokol.oknok_3_27_remark = request.POST.get('oknok_3_27_remark', '')
    protokol.oknok_3_28 = request.POST.get('oknok_3_28', '')
    protokol.oknok_3_28_remark = request.POST.get('oknok_3_28_remark', '')
    protokol.oknok_3_29 = request.POST.get('oknok_3_29', '')
    protokol.oknok_3_29_remark = request.POST.get('oknok_3_29_remark', '')
    protokol.oknok_3_30 = request.POST.get('oknok_3_30', '')
    protokol.oknok_3_30_remark = request.POST.get('oknok_3_30_remark', '')
    protokol.oknok_3_31 = request.POST.get('oknok_3_31', '')
    protokol.oknok_3_31_remark = request.POST.get('oknok_3_31_remark', '')
    protokol.oknok_3_32 = request.POST.get('oknok_3_32', '')
    protokol.oknok_3_32_remark = request.POST.get('oknok_3_32_remark', '')
    protokol.oknok_4_1 = request.POST.get('oknok_4_1', '')
    protokol.oknok_4_1_remark = request.POST.get('oknok_4_1_remark', '')
    protokol.oknok_4_2 = request.POST.get('oknok_4_2', '')
    protokol.oknok_4_2_remark = request.POST.get('oknok_4_2_remark', '')
    protokol.oknok_4_3 = request.POST.get('oknok_4_3', '')
    protokol.oknok_4_3_remark = request.POST.get('oknok_4_3_remark', '')
    protokol.oknok_4_4 = request.POST.get('oknok_4_4', '')
    protokol.oknok_4_4_remark = request.POST.get('oknok_4_4_remark', '')

    protokol.text_4_5 = request.POST.get('text_4_5', '')
    protokol.text_4_5_remark = request.POST.get('text_4_5_remark', '')
    protokol.text_7_5 = request.POST.get('text_7_5', '')
    protokol.text_7_5_remark = request.POST.get('text_7_5_remark', '')
    protokol.text_7_6 = request.POST.get('text_7_6', '')
    protokol.text_7_6_remark = request.POST.get('text_7_6_remark', '')
    protokol.text_9_1=request.POST.get('text_9_1','')
    protokol.text_9_1_remark=request.POST.get('text_9_1_remark','')
    protokol.text_9_2=request.POST.get('text_9_2','')
    protokol.text_9_2_remark=request.POST.get('text_9_2_remark','')
    protokol.text_9_3=request.POST.get('text_9_3','')
    protokol.text_9_3_remark=request.POST.get('text_9_3_remark','')
    protokol.text_9_4=request.POST.get('text_9_4','')
    protokol.text_9_4_remark=request.POST.get('text_9_4_remark','')
    protokol.text_9_5=request.POST.get('text_9_5','')
    protokol.text_9_5_remark=request.POST.get('text_9_5_remark','')
    protokol.text_9_6=request.POST.get('text_9_6','')
    protokol.text_9_6_remark=request.POST.get('text_9_6_remark','')
    protokol.text_9_7=request.POST.get('text_9_7','')
    protokol.text_9_7_remark=request.POST.get('text_9_7_remark','')
    protokol.text_9_7_1=request.POST.get('text_9_7_1','')
    protokol.text_9_7_1_remark=request.POST.get('text_9_7_1_remark','')
    protokol.text_9_7_2=request.POST.get('text_9_7_2','')
    protokol.text_9_7_2_remark=request.POST.get('text_9_7_2_remark','')
    protokol.text_9_7_3=request.POST.get('text_9_7_3','')
    protokol.text_9_7_3_remark=request.POST.get('text_9_7_3_remark','')
    protokol.text_9_7_4=request.POST.get('text_9_7_4','')
    protokol.text_9_7_4_remark=request.POST.get('text_9_7_4_remark','')
    protokol.text_9_7_5=request.POST.get('text_9_7_5','')
    protokol.text_9_7_5_remark=request.POST.get('text_9_7_5_remark','')
    protokol.text_9_7_6=request.POST.get('text_9_7_6','')
    protokol.text_9_7_6_remark=request.POST.get('text_9_7_6_remark','')
    protokol.text_9_7_7=request.POST.get('text_9_7_7','')
    protokol.text_9_7_7_remark=request.POST.get('text_9_7_7_remark','')
    protokol.text_9_7_8=request.POST.get('text_9_7_8','')
    protokol.text_9_7_8_remark=request.POST.get('text_9_7_8_remark','')

    protokol.oknok_4_6 = request.POST.get('oknok_4_6', '')
    protokol.oknok_4_6_remark = request.POST.get('oknok_4_6_remark', '')
    protokol.oknok_4_7 = request.POST.get('oknok_4_7', '')
    protokol.oknok_4_7_remark = request.POST.get('oknok_4_7_remark', '')
    protokol.oknok_4_8 = request.POST.get('oknok_4_8', '')
    protokol.oknok_4_8_remark = request.POST.get('oknok_4_8_remark', '')
    protokol.oknok_4_9 = request.POST.get('oknok_4_9', '')
    protokol.oknok_4_9_remark = request.POST.get('oknok_4_9_remark', '')
    protokol.oknok_4_10 = request.POST.get('oknok_4_10', '')
    protokol.oknok_4_10_remark = request.POST.get('oknok_4_10_remark', '')
    protokol.oknok_4_11 = request.POST.get('oknok_4_11', '')
    protokol.oknok_4_11_remark = request.POST.get('oknok_4_11_remark', '')
    protokol.oknok_4_12 = request.POST.get('oknok_4_12', '')
    protokol.oknok_4_12_remark = request.POST.get('oknok_4_12_remark', '')
    protokol.oknok_4_13 = request.POST.get('oknok_4_13', '')
    protokol.oknok_4_13_remark = request.POST.get('oknok_4_13_remark', '')
    protokol.oknok_4_14 = request.POST.get('oknok_4_14', '')
    protokol.oknok_4_14_remark = request.POST.get('oknok_4_14_remark', '')
    protokol.oknok_5_1 = request.POST.get('oknok_5_1', '')
    protokol.oknok_5_1_remark = request.POST.get('oknok_5_1_remark', '')
    protokol.oknok_5_2 = request.POST.get('oknok_5_2', '')
    protokol.oknok_5_2_remark = request.POST.get('oknok_5_2_remark', '')
    protokol.oknok_5_3 = request.POST.get('oknok_5_3', '')
    protokol.oknok_5_3_remark = request.POST.get('oknok_5_3_remark', '')
    protokol.oknok_5_4 = request.POST.get('oknok_5_4', '')
    protokol.oknok_5_4_remark = request.POST.get('oknok_5_4_remark', '')
    protokol.oknok_5_5 = request.POST.get('oknok_5_5', '')
    protokol.oknok_5_5_remark = request.POST.get('oknok_5_5_remark', '')
    protokol.oknok_5_6 = request.POST.get('oknok_5_6', '')
    protokol.oknok_5_6_remark = request.POST.get('oknok_5_6_remark', '')
    protokol.oknok_5_7 = request.POST.get('oknok_5_7', '')
    protokol.oknok_5_7_remark = request.POST.get('oknok_5_7_remark', '')
    protokol.oknok_5_8 = request.POST.get('oknok_5_8', '')
    protokol.oknok_5_8_remark = request.POST.get('oknok_5_8_remark', '')
    protokol.oknok_5_9 = request.POST.get('oknok_5_9', '')
    protokol.oknok_5_9_remark = request.POST.get('oknok_5_9_remark', '')
    protokol.oknok_5_10 = request.POST.get('oknok_5_10', '')
    protokol.oknok_5_10_remark = request.POST.get('oknok_5_10_remark', '')
    protokol.oknok_5_11 = request.POST.get('oknok_5_11', '')
    protokol.oknok_5_11_remark = request.POST.get('oknok_5_11_remark', '')
    protokol.oknok_5_12 = request.POST.get('oknok_5_12', '')
    protokol.oknok_5_12_remark = request.POST.get('oknok_5_12_remark', '')
    protokol.oknok_5_13 = request.POST.get('oknok_5_13', '')
    protokol.oknok_5_13_remark = request.POST.get('oknok_5_13_remark', '')
    protokol.oknok_5_14 = request.POST.get('oknok_5_14', '')
    protokol.oknok_5_14_remark = request.POST.get('oknok_5_14_remark', '')
    protokol.oknok_5_15 = request.POST.get('oknok_5_15', '')
    protokol.oknok_5_15_remark = request.POST.get('oknok_5_15_remark', '')
    protokol.oknok_5_16 = request.POST.get('oknok_5_16', '')
    protokol.oknok_5_16_remark = request.POST.get('oknok_5_16_remark', '')
    protokol.oknok_5_17 = request.POST.get('oknok_5_17', '')
    protokol.oknok_5_17_remark = request.POST.get('oknok_5_17_remark', '')
    protokol.oknok_5_18 = request.POST.get('oknok_5_18', '')
    protokol.oknok_5_18_remark = request.POST.get('oknok_5_18_remark', '')
    protokol.oknok_5_19 = request.POST.get('oknok_5_19', '')
    protokol.oknok_5_19_remark = request.POST.get('oknok_5_19_remark', '')
    protokol.oknok_5_20 = request.POST.get('oknok_5_20', '')
    protokol.oknok_5_20_remark = request.POST.get('oknok_5_20_remark', '')
    protokol.oknok_5_21 = request.POST.get('oknok_5_21', '')
    protokol.oknok_5_21_remark = request.POST.get('oknok_5_21_remark', '')
    protokol.oknok_5_22 = request.POST.get('oknok_5_22', '')
    protokol.oknok_5_22_remark = request.POST.get('oknok_5_22_remark', '')
    protokol.oknok_5_23 = request.POST.get('oknok_5_23', '')
    protokol.oknok_5_23_remark = request.POST.get('oknok_5_23_remark', '')
    protokol.oknok_5_24 = request.POST.get('oknok_5_24', '')
    protokol.oknok_5_24_remark = request.POST.get('oknok_5_24_remark', '')
    protokol.oknok_5_25 = request.POST.get('oknok_5_25', '')
    protokol.oknok_5_25_remark = request.POST.get('oknok_5_25_remark', '')
    protokol.oknok_5_26 = request.POST.get('oknok_5_26', '')
    protokol.oknok_5_26_remark = request.POST.get('oknok_5_26_remark', '')
    protokol.oknok_5_27 = request.POST.get('oknok_5_27', '')
    protokol.oknok_5_27_remark = request.POST.get('oknok_5_27_remark', '')
    protokol.oknok_5_28 = request.POST.get('oknok_5_28', '')
    protokol.oknok_5_28_remark = request.POST.get('oknok_5_28_remark', '')
    protokol.oknok_5_29 = request.POST.get('oknok_5_29', '')
    protokol.oknok_5_29_remark = request.POST.get('oknok_5_29_remark', '')
    protokol.oknok_5_30 = request.POST.get('oknok_5_30', '')
    protokol.oknok_5_30_remark = request.POST.get('oknok_5_30_remark', '')
    protokol.oknok_5_31 = request.POST.get('oknok_5_31', '')
    protokol.oknok_5_31_remark = request.POST.get('oknok_5_31_remark', '')
    protokol.oknok_5_32 = request.POST.get('oknok_5_32', '')
    protokol.oknok_5_32_remark = request.POST.get('oknok_5_32_remark', '')
    protokol.oknok_5_33 = request.POST.get('oknok_5_33', '')
    protokol.oknok_5_33_remark = request.POST.get('oknok_5_33_remark', '')
    protokol.oknok_5_34 = request.POST.get('oknok_5_34', '')
    protokol.oknok_5_34_remark = request.POST.get('oknok_5_34_remark', '')
    protokol.oknok_5_35 = request.POST.get('oknok_5_35', '')
    protokol.oknok_5_35_remark = request.POST.get('oknok_5_35_remark', '')
    protokol.oknok_5_36 = request.POST.get('oknok_5_36', '')
    protokol.oknok_5_36_remark = request.POST.get('oknok_5_36_remark', '')
    protokol.oknok_5_37 = request.POST.get('oknok_5_37', '')
    protokol.oknok_5_37_remark = request.POST.get('oknok_5_37_remark', '')
    protokol.oknok_5_38 = request.POST.get('oknok_5_38', '')
    protokol.oknok_5_38_remark = request.POST.get('oknok_5_38_remark', '')
    protokol.oknok_5_39 = request.POST.get('oknok_5_39', '')
    protokol.oknok_5_39_remark = request.POST.get('oknok_5_39_remark', '')
    protokol.oknok_5_40 = request.POST.get('oknok_5_40', '')
    protokol.oknok_5_40_remark = request.POST.get('oknok_5_40_remark', '')
    protokol.oknok_5_41 = request.POST.get('oknok_5_41', '')
    protokol.oknok_5_41_remark = request.POST.get('oknok_5_41_remark', '')
    protokol.oknok_5_42 = request.POST.get('oknok_5_42', '')
    protokol.oknok_5_42_remark = request.POST.get('oknok_5_42_remark', '')
    protokol.oknok_5_43 = request.POST.get('oknok_5_43', '')
    protokol.oknok_5_43_remark = request.POST.get('oknok_5_43_remark', '')
    protokol.oknok_5_44 = request.POST.get('oknok_5_44', '')
    protokol.oknok_5_44_remark = request.POST.get('oknok_5_44_remark', '')
    protokol.oknok_5_45 = request.POST.get('oknok_5_45', '')
    protokol.oknok_5_45_remark = request.POST.get('oknok_5_45_remark', '')
    protokol.oknok_5_46 = request.POST.get('oknok_5_46', '')
    protokol.oknok_5_46_remark = request.POST.get('oknok_5_46_remark', '')
    protokol.oknok_5_47 = request.POST.get('oknok_5_47', '')
    protokol.oknok_5_47_remark = request.POST.get('oknok_5_47_remark', '')
    protokol.oknok_5_48 = request.POST.get('oknok_5_48', '')
    protokol.oknok_5_48_remark = request.POST.get('oknok_5_48_remark', '')
    protokol.oknok_5_49 = request.POST.get('oknok_5_49', '')
    protokol.oknok_5_49_remark = request.POST.get('oknok_5_49_remark', '')
    protokol.oknok_5_50 = request.POST.get('oknok_5_50', '')
    protokol.oknok_5_50_remark = request.POST.get('oknok_5_50_remark', '')
    protokol.oknok_5_51 = request.POST.get('oknok_5_51', '')
    protokol.oknok_5_51_remark = request.POST.get('oknok_5_51_remark', '')
    protokol.oknok_6_1 = request.POST.get('oknok_6_1', '')
    protokol.oknok_6_1_remark = request.POST.get('oknok_6_1_remark', '')
    protokol.oknok_6_2 = request.POST.get('oknok_6_2', '')
    protokol.oknok_6_2_remark = request.POST.get('oknok_6_2_remark', '')
    protokol.oknok_6_3 = request.POST.get('oknok_6_3', '')
    protokol.oknok_6_3_remark = request.POST.get('oknok_6_3_remark', '')
    protokol.oknok_6_4 = request.POST.get('oknok_6_4', '')
    protokol.oknok_6_4_remark = request.POST.get('oknok_6_4_remark', '')
    protokol.oknok_6_5 = request.POST.get('oknok_6_5', '')
    protokol.oknok_6_5_remark = request.POST.get('oknok_6_5_remark', '')
    protokol.oknok_6_6 = request.POST.get('oknok_6_6', '')
    protokol.oknok_6_6_remark = request.POST.get('oknok_6_6_remark', '')
    protokol.oknok_6_7 = request.POST.get('oknok_6_7', '')
    protokol.oknok_6_7_remark = request.POST.get('oknok_6_7_remark', '')
    protokol.oknok_6_8 = request.POST.get('oknok_6_8', '')
    protokol.oknok_6_8_remark = request.POST.get('oknok_6_8_remark', '')
    protokol.oknok_6_9 = request.POST.get('oknok_6_9', '')
    protokol.oknok_6_9_remark = request.POST.get('oknok_6_9_remark', '')
    protokol.oknok_6_10 = request.POST.get('oknok_6_10', '')
    protokol.oknok_6_10_remark = request.POST.get('oknok_6_10_remark', '')
    protokol.oknok_6_11 = request.POST.get('oknok_6_11', '')
    protokol.oknok_6_11_remark = request.POST.get('oknok_6_11_remark', '')
    protokol.oknok_6_12 = request.POST.get('oknok_6_12', '')
    protokol.oknok_6_12_remark = request.POST.get('oknok_6_12_remark', '')
    protokol.oknok_6_13 = request.POST.get('oknok_6_13', '')
    protokol.oknok_6_13_remark = request.POST.get('oknok_6_13_remark', '')
    protokol.oknok_7_1 = request.POST.get('oknok_7_1', '')
    protokol.oknok_7_1_remark = request.POST.get('oknok_7_1_remark', '')
    protokol.oknok_7_2 = request.POST.get('oknok_7_2', '')
    protokol.oknok_7_2_remark = request.POST.get('oknok_7_2_remark', '')
    protokol.oknok_7_3 = request.POST.get('oknok_7_3', '')
    protokol.oknok_7_3_remark = request.POST.get('oknok_7_3_remark', '')
    protokol.oknok_7_4 = request.POST.get('oknok_7_4', '')
    protokol.oknok_7_4_remark = request.POST.get('oknok_7_4_remark', '')
    protokol.oknok_8_1 = request.POST.get('oknok_8_1', '')
    protokol.oknok_8_1_remark = request.POST.get('oknok_8_1_remark', '')
    protokol.oknok_8_2 = request.POST.get('oknok_8_2', '')
    protokol.oknok_8_2_remark = request.POST.get('oknok_8_2_remark', '')
    protokol.oknok_8_3 = request.POST.get('oknok_8_3', '')
    protokol.oknok_8_3_remark = request.POST.get('oknok_8_3_remark', '')
    protokol.oknok_8_4 = request.POST.get('oknok_8_4', '')
    protokol.oknok_8_4_remark = request.POST.get('oknok_8_4_remark', '')
    protokol.oknok_8_5 = request.POST.get('oknok_8_5', '')
    protokol.oknok_8_5_remark = request.POST.get('oknok_8_5_remark', '')
    protokol.oknok_10_1 = request.POST.get('oknok_10_1', '')
    protokol.oknok_10_1_remark = request.POST.get('oknok_10_1_remark', '')
    protokol.oknok_10_2 = request.POST.get('oknok_10_2', '')
    protokol.oknok_10_2_remark = request.POST.get('oknok_10_2_remark', '')
    protokol.oknok_10_3 = request.POST.get('oknok_10_3', '')
    protokol.oknok_10_3_remark = request.POST.get('oknok_10_3_remark', '')
    protokol.oknok_10_4 = request.POST.get('oknok_10_4', '')
    protokol.oknok_10_4_remark = request.POST.get('oknok_10_4_remark', '')
    protokol.oknok_10_5 = request.POST.get('oknok_10_5', '')
    protokol.oknok_10_5_remark = request.POST.get('oknok_10_5_remark', '')

    protokol.oknok_1_8_lp = request.POST.get('oknok_1_8_lp', '')
    protokol.oknok_1_29_lp = request.POST.get('oknok_1_29_lp', '')
    protokol.oknok_1_35_lp = request.POST.get('oknok_1_35_lp', '')
    protokol.oknok_1_36_lp = request.POST.get('oknok_1_36_lp', '')
    protokol.oknok_2_13_lp = request.POST.get('oknok_2_13_lp', '')
    protokol.oknok_2_14_lp = request.POST.get('oknok_2_14_lp', '')
    protokol.oknok_3_1_lp = request.POST.get('oknok_3_1_lp', '')
    protokol.oknok_3_31_lp = request.POST.get('oknok_3_31_lp', '')
    protokol.oknok_3_32_lp = request.POST.get('oknok_3_32_lp', '')
    protokol.oknok_4_13_lp = request.POST.get('oknok_4_13_lp', '')
    protokol.oknok_4_14_lp = request.POST.get('oknok_4_14_lp', '')
    protokol.oknok_5_26_lp = request.POST.get('oknok_5_26_lp', '')
    protokol.oknok_5_29_lp = request.POST.get('oknok_5_29_lp', '')
    protokol.oknok_5_30_lp = request.POST.get('oknok_5_30_lp', '')
    protokol.oknok_5_35_lp = request.POST.get('oknok_5_35_lp', '')
    protokol.oknok_5_38_lp = request.POST.get('oknok_5_38_lp', '')
    protokol.oknok_5_46_lp = request.POST.get('oknok_5_46_lp', '')
    protokol.oknok_5_47_lp = request.POST.get('oknok_5_47_lp', '')
    protokol.oknok_5_50_lp = request.POST.get('oknok_5_50_lp', '')
    protokol.oknok_5_51_lp = request.POST.get('oknok_5_51_lp', '')
    protokol.oknok_6_12_lp = request.POST.get('oknok_6_12_lp', '')
    protokol.oknok_6_13_lp = request.POST.get('oknok_6_13_lp', '')
    protokol.oknok_8_1_lp = request.POST.get('oknok_8_1_lp', '')
    protokol.oknok_8_2_lp = request.POST.get('oknok_8_2_lp', '')
    protokol.oknok_8_3_lp = request.POST.get('oknok_8_3_lp', '')
    protokol.oknok_8_4_lp = request.POST.get('oknok_8_4_lp', '')
    protokol.oknok_8_5_lp = request.POST.get('oknok_8_5_lp', '')





    protokol.check_size_1_21 = request.POST.get('check_size_1_21', '')
    protokol.check_size_1_21_remark = request.POST.get('check_size_1_21_remark', '')
    protokol.check_size_1_22 = request.POST.get('check_size_1_22', '')
    protokol.check_size_1_22_remark = request.POST.get('check_size_1_22_remark', '')
    protokol.check_size_3_7 = request.POST.get('check_size_3_7', '')
    protokol.check_size_3_7_remark = request.POST.get('check_size_3_7_remark', '')
    protokol.check_size_3_9 = request.POST.get('check_size_3_9', '')
    protokol.check_size_3_9_remark = request.POST.get('check_size_3_9_remark', '')

    protokol.last_changer = request.user.username
    protokol.drawing = request.POST.get('drawing', '')
    protokol.rev = request.POST.get('rev', '')
    protokol.order = request.POST.get('order', '')
    protokol.order_sag = request.POST.get('order_sag', '')
    protokol.device = request.POST.get('device', '')
    protokol.hoist = request.POST.get('hoist', '')
    protokol.company = request.POST.get('company', '')
    protokol.quantity = request.POST.get('quantity', '')
    protokol.check_size_1 = request.POST.get('check_size_1', '')
    protokol.oknok_size_1 = request.POST.get('oknok_size_1', '')
    protokol.check_size_3 = request.POST.get('check_size_3', '')
    protokol.check_size_4 = request.POST.get('check_size_4', '')
    protokol.check_size_4a = request.POST.get('check_size_4a', '')
    protokol.check_size_5 = request.POST.get('check_size_5', '')
    protokol.check_size_6 = request.POST.get('check_size_6', '')
    protokol.check_size_7 = request.POST.get('check_size_7', '')
    protokol.check_size_8 = request.POST.get('check_size_8', '')
    protokol.check_size_9 = request.POST.get('check_size_9', '')
    protokol.check_size_10 = request.POST.get('check_size_10', '')
    protokol.position_tolerance_11 = request.POST.get('position_tolerance_11', '')
    protokol.miscellaneous = request.POST.get('miscellaneous', '')
    protokol.remark = request.POST.get('remark', '')
    protokol.measure = request.POST.get('measure', '')
    protokol.date = request.POST.get('date', '')
    protokol.inspector = request.POST.get('inspector', '')
    protokol.department = request.POST.get('department', '')
    protokol.baustelle = request.POST.get('baustelle', '')

    for number in protokol.additional_data:
        soll_value = request.POST.get(f'check_size_{number}')
        if soll_value:
            protokol.additional_data[number]["aktuellWert"] = soll_value
        

    if request.POST.get('korrektur', '') == 'True':
        protokol.isCorrecturNeeded = True
    else:
        protokol.isCorrecturNeeded = False

    protokol.isSaved = True
    protokol.save()
    if str(currentUser) == "admin":
        return render(request, 'protocolHubzugLiftingHostAdmin.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id, 'current_user': currentUser})
    return render(request, 'protocolHubzugLiftingHost.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id, 'current_user': currentUser})

@require_http_methods(["POST"])
def protocolHubzugLaufSeiltrommelUpdate(request, protocol_id):
    currentUser = request.user
    protokol = get_object_or_404(ProtocolHubzugLaufSeiltrommel, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    protokol.last_changer = request.user.username
    protokol.drawing = request.POST.get('drawing', '')
    protokol.rev = request.POST.get('rev', '')
    protokol.order = request.POST.get('order', '')
    protokol.order_sag = request.POST.get('order_sag', '')
    protokol.component = request.POST.get('component', '')
    protokol.company = request.POST.get('company', '')
    protokol.quantity = request.POST.get('quantity', '')
    protokol.check_size_1 = request.POST.get('check_size_1', '')
    protokol.check_size_2 = request.POST.get('check_size_2', '')
    protokol.check_size_3 = request.POST.get('check_size_3', '')
    protokol.check_size_4 = request.POST.get('check_size_4', '')
    protokol.check_size_5 = request.POST.get('check_size_5', '')
    protokol.check_size_6 = request.POST.get('check_size_6', '')
    protokol.check_size_7 = request.POST.get('check_size_7', '')
    protokol.check_size_8 = request.POST.get('check_size_8', '')
    protokol.check_size_9 = request.POST.get('check_size_9', '')
    protokol.remark = request.POST.get('remark', '')
    protokol.date = request.POST.get('date', '')
    protokol.inspector = request.POST.get('inspector', '')
    protokol.department = request.POST.get('department', '')
    protokol.baustelle = request.POST.get('baustelle', '')

    if request.POST.get('korrektur', '') == 'True':
        protokol.isCorrecturNeeded = True
    else:
        protokol.isCorrecturNeeded = False

    protokol.isSaved = True
    protokol.save()
    return render(request, 'protocolHubzugLaufSeiltrommel.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id, 'current_user': currentUser})

@require_http_methods(["POST"])
def protocolHubzugMassSeiltrommelUpdate(request, protocol_id):
    currentUser = request.user
    protokol = get_object_or_404(ProtocolHubzugMassSeiltrommel, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    protokol.last_changer = request.user.username
    protokol.drawing = request.POST.get('drawing', '')
    protokol.rev = request.POST.get('rev', '')
    protokol.order = request.POST.get('order', '')
    protokol.order_sag = request.POST.get('order_sag', '')
    protokol.device = request.POST.get('device', '')
    protokol.component = request.POST.get('component', '')
    protokol.company = request.POST.get('company', '')
    protokol.quantity = request.POST.get('quantity', '')
    protokol.check_size_1 = request.POST.get('check_size_1', '')
    protokol.check_size_2 = request.POST.get('check_size_2', '')
    protokol.check_size_3 = request.POST.get('check_size_3', '')
    protokol.check_size_4 = request.POST.get('check_size_4', '')
    protokol.check_size_5 = request.POST.get('check_size_5', '')
    protokol.check_size_6 = request.POST.get('check_size_6', '')
    protokol.check_size_7 = request.POST.get('check_size_7', '')
    protokol.check_size_8 = request.POST.get('check_size_8', '')
    protokol.check_size_9 = request.POST.get('check_size_9', '')
    protokol.check_size_10 = request.POST.get('check_size_10', '')
    protokol.check_size_11 = request.POST.get('check_size_11', '')
    protokol.check_size_12 = request.POST.get('check_size_12', '')
    protokol.check_size_13 = request.POST.get('check_size_13', '')
    protokol.remark = request.POST.get('remark', '')
    protokol.measure = request.POST.get('measure', '')
    protokol.date = request.POST.get('date', '')
    protokol.inspector = request.POST.get('inspector', '')
    protokol.department = request.POST.get('department', '')
    protokol.baustelle = request.POST.get('baustelle', '')

    if request.POST.get('korrektur', '') == 'True':
        protokol.isCorrecturNeeded = True
    else:
        protokol.isCorrecturNeeded = False

    protokol.isSaved = True
    protokol.save()
    return render(request, 'protocolHubzugMassSeiltrommel.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id, 'current_user': currentUser})

@require_http_methods(["POST"])
def protocolLaufHubzugUpdate(request, protocol_id):
    currentUser = request.user
    protokol = get_object_or_404(ProtocolLaufHubzug, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    protokol.last_changer = request.user.username
    protokol.drawing = request.POST.get('drawing', '')
    protokol.rev = request.POST.get('rev', '')
    protokol.order = request.POST.get('order', '')
    protokol.order_sag = request.POST.get('order_sag', '')
    protokol.device = request.POST.get('device', '')
    protokol.component = request.POST.get('component', '')
    protokol.company = request.POST.get('company', '')
    protokol.quantity = request.POST.get('quantity', '')
    protokol.hoist = request.POST.get('hoist', '')
    protokol.loadTp = request.POST.get('loadTp', '')
    protokol.check_size_1 = request.POST.get('check_size_1', '')
    protokol.check_size_2 = request.POST.get('check_size_2', '')
    protokol.check_size_3 = request.POST.get('check_size_3', '')
    protokol.check_size_4 = request.POST.get('check_size_4', '')
    protokol.check_size_4a = request.POST.get('check_size_4a', '')
    protokol.check_size_5 = request.POST.get('check_size_5', '')
    protokol.check_size_6 = request.POST.get('check_size_6', '')
    protokol.check_size_7 = request.POST.get('check_size_7', '')
    protokol.check_size_8 = request.POST.get('check_size_8', '')
    protokol.check_size_9 = request.POST.get('check_size_9', '')
    protokol.check_size_10 = request.POST.get('check_size_10', '')
    protokol.check_size_11 = request.POST.get('check_size_11', '')
    protokol.check_size_12 = request.POST.get('check_size_12', '')
    protokol.check_size_13 = request.POST.get('check_size_13', '')
    protokol.check_size_14 = request.POST.get('check_size_14', '')
    protokol.check_size_15 = request.POST.get('check_size_15', '')
    protokol.check_size_16 = request.POST.get('check_size_16', '')
    protokol.check_size_17 = request.POST.get('check_size_17', '')
    protokol.check_size_18 = request.POST.get('check_size_18', '')
    protokol.check_size_19 = request.POST.get('check_size_19', '')
    protokol.check_size_20 = request.POST.get('check_size_20', '')
    protokol.check_size_21 = request.POST.get('check_size_21', '')
    protokol.check_size_22 = request.POST.get('check_size_22', '')
    protokol.check_size_23 = request.POST.get('check_size_23', '')
    protokol.remark = request.POST.get('remark', '')
    protokol.measure = request.POST.get('measure', '')
    protokol.date = request.POST.get('date', '')
    protokol.inspector = request.POST.get('inspector', '')
    protokol.department = request.POST.get('department', '')
    protokol.baustelle = request.POST.get('baustelle', '')

    if request.POST.get('korrektur', '') == 'True':
        protokol.isCorrecturNeeded = True
    else:
        protokol.isCorrecturNeeded = False

    if request.POST.get('nacharbeit', '') == 'True':
        protokol.isNacharbeiterNeeded = True
    else:
        protokol.isNacharbeiterNeeded = False

    protokol.isSaved = True
    protokol.save()
    return render(request, 'protocolLaufHubzug.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id, 'current_user': currentUser})

@require_http_methods(["POST"])
def protocolEndkontrolleUpdate(request, protocol_id):
    currentUser = request.user
    protokol = get_object_or_404(ProtocolEndkontrolle, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    protokol.last_changer = request.user.username
    protokol.drawing = request.POST.get('drawing', '')
    protokol.rev = request.POST.get('rev', '')
    protokol.order = request.POST.get('order', '')
    protokol.order_sag = request.POST.get('order_sag', '')
    protokol.device = request.POST.get('device', '')
    protokol.component = request.POST.get('component', '')
    protokol.company = request.POST.get('company', '')
    protokol.quantity = request.POST.get('quantity', '')
    protokol.hoist = request.POST.get('hoist', '')
    protokol.loadTp = request.POST.get('loadTp', '')
    protokol.unitNO = request.POST.get('unitNO', '')
    protokol.check_size_1 = request.POST.get('check_size_1', '')
    protokol.check_size_2 = request.POST.get('check_size_2', '')
    protokol.check_size_3 = request.POST.get('check_size_3', '')
    protokol.check_size_4 = request.POST.get('check_size_4', '')
    protokol.check_size_4a = request.POST.get('check_size_4a', '')
    protokol.check_size_5 = request.POST.get('check_size_5', '')
    protokol.check_size_5a = request.POST.get('check_size_5a', '')
    protokol.check_size_6 = request.POST.get('check_size_6', '')
    protokol.check_size_6a = request.POST.get('check_size_6a', '')
    protokol.check_size_7 = request.POST.get('check_size_7', '')
    protokol.check_size_8 = request.POST.get('check_size_8', '')
    protokol.check_size_9 = request.POST.get('check_size_9', '')
    protokol.check_size_10 = request.POST.get('check_size_10', '')
    protokol.check_size_11 = request.POST.get('check_size_11', '')
    protokol.check_size_12 = request.POST.get('check_size_12', '')
    protokol.check_size_13 = request.POST.get('check_size_13', '')
    protokol.check_size_14 = request.POST.get('check_size_14', '')
    protokol.check_size_15 = request.POST.get('check_size_15', '')
    protokol.check_size_16 = request.POST.get('check_size_16', '')
    protokol.check_size_17 = request.POST.get('check_size_17', '')
    protokol.check_size_18 = request.POST.get('check_size_18', '')
    protokol.check_size_19 = request.POST.get('check_size_19', '')
    protokol.check_size_20 = request.POST.get('check_size_20', '')
    protokol.check_size_21 = request.POST.get('check_size_21', '')
    protokol.check_size_22 = request.POST.get('check_size_22', '')
    protokol.check_size_23 = request.POST.get('check_size_23', '')
    protokol.remark = request.POST.get('remark', '')
    protokol.measure = request.POST.get('measure', '')
    protokol.date = request.POST.get('date', '')
    protokol.inspector = request.POST.get('inspector', '')
    protokol.department = request.POST.get('department', '')
    protokol.baustelle = request.POST.get('baustelle', '')

    if request.POST.get('korrektur', '') == 'True':
        protokol.isCorrecturNeeded = True
    else:
        protokol.isCorrecturNeeded = False

    protokol.isSaved = True
    protokol.save()
    return render(request, 'protocolEndkontrolle.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id, 'current_user': currentUser})

@require_http_methods(["POST"])
def protocolHubzugLiftingHostClose(request, protocol_id):


    def get_post_or_zero(key):
        return request.POST.get(key, '').strip() or '0'

    currentUser = request.user
    protokol = get_object_or_404(ProtocolHubzugLiftingHost, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    protokol.isClosed = True

    # Assign POST data to protocol
    protokol.check_size_1 = request.POST.get('check_size_1', '')
    protokol.check_size_2 = request.POST.get('check_size_2', '')
    protokol.check_size_3 = request.POST.get('check_size_3', '')
    protokol.check_size_4 = request.POST.get('check_size_4', '')
    protokol.check_size_4a = request.POST.get('check_size_4a', '')
    protokol.check_size_5 = request.POST.get('check_size_5', '')
    protokol.check_size_6 = request.POST.get('check_size_6', '')
    protokol.check_size_7 = request.POST.get('check_size_7', '')
    protokol.check_size_8 = request.POST.get('check_size_8', '')
    protokol.check_size_9 = request.POST.get('check_size_9', '')
    protokol.check_size_10 = request.POST.get('check_size_10', '')
    protokol.check_size_11 = request.POST.get('check_size_11', '')

    # Check if any are empty
    fields_to_check = [
        protokol.check_size_1, protokol.check_size_2, protokol.check_size_3,
        protokol.check_size_4, protokol.check_size_4a, protokol.check_size_5,
        protokol.check_size_6, protokol.check_size_7, protokol.check_size_8,
        protokol.check_size_9, protokol.check_size_10
    ]

    protokol.isCorrecturNeeded = any(field == '' for field in fields_to_check)

    protokol.check_size_1 = get_post_or_zero('check_size_1')
    protokol.check_size_2 = get_post_or_zero('check_size_2')
    protokol.check_size_3 = get_post_or_zero('check_size_3')
    protokol.check_size_4 = get_post_or_zero('check_size_4')
    protokol.check_size_4a = get_post_or_zero('check_size_4a')
    protokol.check_size_5 = get_post_or_zero('check_size_5')
    protokol.check_size_6 = get_post_or_zero('check_size_6')
    protokol.check_size_7 = get_post_or_zero('check_size_7')
    protokol.check_size_8 = get_post_or_zero('check_size_8')
    protokol.check_size_9 = get_post_or_zero('check_size_9')
    protokol.check_size_10 = get_post_or_zero('check_size_10')
    protokol.check_size_11 = get_post_or_zero('check_size_11')

    protokol.save()

    fahrzeug_id = request.GET.get('fahrzeugId', None)
    fahrzeug = newFahrzeug.objects.get(id=fahrzeug_id)
    context = {
        'username': currentUser.username,
        'fahrzeug_id': fahrzeug_id,
        'hubzug': fahrzeug.hubzug
    }
    return render(request, 'hubzug.html', context)


@require_http_methods(["POST"])
def protocolHubzugLaufSeiltrommelClose(request, protocol_id):
    currentUser = request.user
    protokol = get_object_or_404(ProtocolHubzugLaufSeiltrommel, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    protokol.isClosed = True
    protokol.save()

    fahrzeug_id = request.GET.get('fahrzeugId', None)
    fahrzeug = newFahrzeug.objects.get(id=fahrzeug_id)
    context = {
        'username': currentUser.username,
        'fahrzeug_id': fahrzeug_id,
        'hubzug': fahrzeug.hubzug
    }
    return render(request, 'hubzug.html', context)

@require_http_methods(["POST"])
def protocolHubzugMassSeiltrommelClose(request, protocol_id):
    currentUser = request.user
    protokol = get_object_or_404(ProtocolHubzugMassSeiltrommel, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    protokol.isClosed = True
    protokol.save()

    fahrzeug_id = request.GET.get('fahrzeugId', None)
    fahrzeug = newFahrzeug.objects.get(id=fahrzeug_id)
    context = {
        'username': currentUser.username,
        'fahrzeug_id': fahrzeug_id,
        'hubzug': fahrzeug.hubzug
    }
    return render(request, 'hubzug.html', context)

@require_http_methods(["POST"])
def protocolLaufHubzugClose(request, protocol_id):
    currentUser = request.user
    protokol = get_object_or_404(ProtocolLaufHubzug, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    protokol.isClosed = True
    protokol.save()

    fahrzeug_id = request.GET.get('fahrzeugId', None)
    fahrzeug = newFahrzeug.objects.get(id=fahrzeug_id)
    context = {
        'username': currentUser.username,
        'fahrzeug_id': fahrzeug_id,
        'hubzug': fahrzeug.hubzug
    }
    return render(request, 'hubzug.html', context)

@require_http_methods(["POST"])
def protocolEndkontrolleClose(request, protocol_id):
    currentUser = request.user
    protokol = get_object_or_404(ProtocolEndkontrolle, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    protokol.isClosed = True
    protokol.save()

    fahrzeug_id = request.GET.get('fahrzeugId', None)
    fahrzeug = newFahrzeug.objects.get(id=fahrzeug_id)
    context = {
        'username': currentUser.username,
        'fahrzeug_id': fahrzeug_id,
        'hubzug': fahrzeug.hubzug
    }
    return render(request, 'hubzug.html', context)


@require_http_methods(["POST"])
def exportProtokolHubzugLiftingHost(request, protocol_id):
    protokol = get_object_or_404(ProtocolHubzugLiftingHost, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId')
    fahrzeug = get_object_or_404(newFahrzeug, id=fahrzeug_id)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    css_url = request.build_absolute_uri(settings.STATIC_URL + 'pdf/pdfProtocolHubzugLiftingHost.css')

    html_string = render_to_string('protokol_pdf_template.html', {
        'protokol': protokol,
        'css_url': css_url
    })

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_file = io.BytesIO()
    html.write_pdf(target=pdf_file)

    protokol.isExported = True
    protokol.save()

    pdf_file.seek(0)
    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{protokol.protocolName}_{now}.pdf"'
    return response

    # Return the PDF as a response
    """ pdf_file.seek(0)
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{protokol.protocolName}_{now}.pdf"'
    return response """


    '''
    try:
        protokol = get_object_or_404(ProtocolHubzugLiftingHost, pk=protocol_id)
        fahrzeug_id = request.GET.get('fahrzeugId', None)
        fahrzeug = newFahrzeug.objects.get(id=fahrzeug_id)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        os.makedirs(os.path.dirname(f'{GLOBAL_DIR}{fahrzeug.baustelle.baustelleName}/{fahrzeug.fahrzeugName}/Hubzug/{protokol.protocolName}/'), exist_ok=True)
        html_string = render_to_string('protokol_pdf_template.html', {'protokol': protokol})
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        file_path = f'{GLOBAL_DIR}{fahrzeug.baustelle.baustelleName}/{fahrzeug.fahrzeugName}/Hubzug/{protokol.protocolName}/{now}.pdf'
        html.write_pdf(target=file_path)

        protocol = AllProtocols(
            baustelle=fahrzeug.baustelle.baustelleName,
            fahrzeug=fahrzeug.fahrzeugName,
            teil="Hubzug",
            protokolType=protokol.protocolName,
            path=file_path
        )
        protocol.save()

        protokol.isExported = True
        protokol.save()

        return JsonResponse({'path': file_path})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
        '''

@require_http_methods(["POST"])
def exportProtokolHubzugLaufSeiltrommel(request, protocol_id):
    protokol = get_object_or_404(ProtocolHubzugLaufSeiltrommel, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', None)
    fahrzeug = newFahrzeug.objects.get(id=fahrzeug_id)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Finding the absolute path of the css file
    css_path = finders.find('pdf/pdfProtocolHubzugLiftingHost.css')
    css_url = request.build_absolute_uri(settings.STATIC_URL + 'pdf/pdfProtocolHubzugLiftingHost.css')

    html_string = render_to_string('protokolPDFHubzugLaufSeiltrommel.html', {
        'protokol': protokol,
        'css_url': css_url  # Pass the CSS URL to the template
    })

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_file = io.BytesIO()
    html.write_pdf(target=pdf_file)
    
    # Update the database entries
    protocol = AllProtocols(
        baustelle=fahrzeug.baustelle.baustelleName,
        fahrzeug=fahrzeug.fahrzeugName,
        teil="Hubzug",
        protokolType=protokol.protocolName,
        path=""  # Not saving to path since we are sending directly
    )
    protocol.save()

    protokol.isExported = True
    protokol.save()

    # Return the PDF as a response
    pdf_file.seek(0)
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{protokol.protocolName}_{now}.pdf"'
    return response

@require_http_methods(["POST"])
def exportProtokolHubzugMassSeiltrommel(request, protocol_id):
    protokol = get_object_or_404(ProtocolHubzugMassSeiltrommel, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', None)
    fahrzeug = newFahrzeug.objects.get(id=fahrzeug_id)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Finding the absolute path of the css file
    css_path = finders.find('pdf/pdfProtocolHubzugLiftingHost.css')
    css_url = request.build_absolute_uri(settings.STATIC_URL + 'pdf/pdfProtocolHubzugLiftingHost.css')

    html_string = render_to_string('protokolPDFHubzugMassSeiltrommel.html', {
        'protokol': protokol,
        'css_url': css_url  # Pass the CSS URL to the template
    })

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_file = io.BytesIO()
    html.write_pdf(target=pdf_file)
    
    # Update the database entries
    protocol = AllProtocols(
        baustelle=fahrzeug.baustelle.baustelleName,
        fahrzeug=fahrzeug.fahrzeugName,
        teil="Hubzug",
        protokolType=protokol.protocolName,
        path=""  # Not saving to path since we are sending directly
    )
    protocol.save()

    protokol.isExported = True
    protokol.save()

    # Return the PDF as a response
    pdf_file.seek(0)
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{protokol.protocolName}_{now}.pdf"'
    return response

def protocolHubzugLiftingHostSollWert(request, protocol_id):
    # Assume `get_protokol` is a function that retrieves the protocol data by ID
    currentUser = request.user
    protokol = get_object_or_404(ProtocolHubzugLiftingHost, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    return render(request, 'protocolHubzugLiftingHostSollWert.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id, 'current_user': currentUser})

def protocolLaufHubzugSollWert(request, protocol_id):
    # Assume `get_protokol` is a function that retrieves the protocol data by ID
    currentUser = request.user
    protokol = get_object_or_404(ProtocolLaufHubzug, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    return render(request, 'protocolLaufHubzugSollWert.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id, 'current_user': currentUser})


@require_http_methods(["POST"])
def protocolHubzugLiftingHostSollWertUpdate(request, protocol_id):
    currentUser = request.user
    protokol = get_object_or_404(ProtocolHubzugLiftingHost, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    # Define the base names of your fields correctly according to the ones you provided
    field_bases = [
        ('oknok_1_7_soll','oknok_1_7_soll'),
        ('oknok_1_1_soll','oknok_1_1_soll'),
        ('oknok_1_2_soll','oknok_1_2_soll'),
        ('oknok_1_3_soll','oknok_1_3_soll'),
        ('oknok_1_4_soll','oknok_1_4_soll'),
        ('oknok_1_5_soll','oknok_1_5_soll'),
        ('oknok_1_6_soll','oknok_1_6_soll'),
        ('oknok_1_7_soll','oknok_1_7_soll'),
        ('oknok_1_8_soll','oknok_1_8_soll'),
        ('oknok_1_9_soll','oknok_1_9_soll'),
        ('oknok_1_10_soll','oknok_1_10_soll'),
        ('oknok_1_11_soll','oknok_1_11_soll'),
        ('oknok_1_12_soll','oknok_1_12_soll'),
        ('oknok_1_13_soll','oknok_1_13_soll'),
        ('oknok_1_14_soll','oknok_1_14_soll'),
        ('oknok_1_15_soll','oknok_1_15_soll'),
        ('oknok_1_16_soll','oknok_1_16_soll'),
        ('oknok_1_17_soll','oknok_1_17_soll'),
        ('oknok_1_18_soll','oknok_1_18_soll'),
        ('oknok_1_19_soll','oknok_1_19_soll'),
        ('oknok_1_20_soll','oknok_1_20_soll'),
        ('oknok_1_23_soll','oknok_1_23_soll'),
        ('oknok_1_24_soll','oknok_1_24_soll'),
        ('oknok_1_25_soll','oknok_1_25_soll'),
        ('oknok_1_26_soll','oknok_1_26_soll'),
        ('oknok_1_27_soll','oknok_1_27_soll'),
        ('oknok_1_28_soll','oknok_1_28_soll'),
        ('oknok_1_29_soll','oknok_1_29_soll'),
        ('oknok_1_30_soll','oknok_1_30_soll'),
        ('oknok_1_31_soll','oknok_1_31_soll'),
        ('oknok_1_32_soll','oknok_1_32_soll'),
        ('oknok_1_33_soll','oknok_1_33_soll'),
        ('oknok_1_34_soll','oknok_1_34_soll'),
        ('oknok_1_35_soll','oknok_1_35_soll'),
        ('oknok_1_36_soll','oknok_1_36_soll'),
        ('oknok_2_1_soll','oknok_2_1_soll'),
        ('oknok_2_2_soll','oknok_2_2_soll'),
        ('oknok_2_3_soll','oknok_2_3_soll'),
        ('oknok_2_4_soll','oknok_2_4_soll'),
        ('oknok_2_5_soll','oknok_2_5_soll'),
        ('oknok_2_6_soll','oknok_2_6_soll'),
        ('oknok_2_7_soll','oknok_2_7_soll'),
        ('oknok_2_8_soll','oknok_2_8_soll'),
        ('oknok_2_9_soll','oknok_2_9_soll'),
        ('oknok_2_10_soll','oknok_2_10_soll'),
        ('oknok_2_11_soll','oknok_2_11_soll'),
        ('oknok_2_12_soll','oknok_2_12_soll'),
        ('oknok_2_13_soll','oknok_2_13_soll'),
        ('oknok_2_14_soll','oknok_2_14_soll'),
        ('oknok_3_1_soll','oknok_3_1_soll'),
        ('oknok_3_2_soll','oknok_3_2_soll'),
        ('oknok_3_3_soll','oknok_3_3_soll'),
        ('oknok_3_4_soll','oknok_3_4_soll'),
        ('oknok_3_5_soll','oknok_3_5_soll'),
        ('oknok_3_6_soll','oknok_3_6_soll'),
        ('oknok_3_8_soll','oknok_3_8_soll'),
        ('oknok_3_10_soll','oknok_3_10_soll'),
        ('oknok_3_11_soll','oknok_3_11_soll'),
        ('oknok_3_12_soll','oknok_3_12_soll'),
        ('oknok_3_13_soll','oknok_3_13_soll'),
        ('oknok_3_14_soll','oknok_3_14_soll'),
        ('oknok_3_15_soll','oknok_3_15_soll'),
        ('oknok_3_16_soll','oknok_3_16_soll'),
        ('oknok_3_17_soll','oknok_3_17_soll'),
        ('oknok_3_18_soll','oknok_3_18_soll'),
        ('oknok_3_19_soll','oknok_3_19_soll'),
        ('oknok_3_20_soll','oknok_3_20_soll'),
        ('oknok_3_21_soll','oknok_3_21_soll'),
        ('oknok_3_22_soll','oknok_3_22_soll'),
        ('oknok_3_23_soll','oknok_3_23_soll'),
        ('oknok_3_24_soll','oknok_3_24_soll'),
        ('oknok_3_25_soll','oknok_3_25_soll'),
        ('oknok_3_26_soll','oknok_3_26_soll'),
        ('oknok_3_27_soll','oknok_3_27_soll'),
        ('oknok_3_28_soll','oknok_3_28_soll'),
        ('oknok_3_29_soll','oknok_3_29_soll'),
        ('oknok_3_30_soll','oknok_3_30_soll'),
        ('oknok_3_31_soll','oknok_3_31_soll'),
        ('oknok_3_32_soll','oknok_3_32_soll'),
        ('oknok_4_1_soll','oknok_4_1_soll'),
        ('oknok_4_2_soll','oknok_4_2_soll'),
        ('oknok_4_3_soll','oknok_4_3_soll'),
        ('oknok_4_4_soll','oknok_4_4_soll'),
        ('oknok_4_6_soll','oknok_4_6_soll'),
        ('oknok_4_7_soll','oknok_4_7_soll'),
        ('oknok_4_8_soll','oknok_4_8_soll'),
        ('oknok_4_9_soll','oknok_4_9_soll'),
        ('oknok_4_10_soll','oknok_4_10_soll'),
        ('oknok_4_11_soll','oknok_4_11_soll'),
        ('oknok_4_12_soll','oknok_4_12_soll'),
        ('oknok_4_13_soll','oknok_4_13_soll'),
        ('oknok_4_14_soll','oknok_4_14_soll'),
        ('oknok_5_1_soll','oknok_5_1_soll'),
        ('oknok_5_2_soll','oknok_5_2_soll'),
        ('oknok_5_3_soll','oknok_5_3_soll'),
        ('oknok_5_4_soll','oknok_5_4_soll'),
        ('oknok_5_5_soll','oknok_5_5_soll'),
        ('oknok_5_6_soll','oknok_5_6_soll'),
        ('oknok_5_7_soll','oknok_5_7_soll'),
        ('oknok_5_8_soll','oknok_5_8_soll'),
        ('oknok_5_9_soll','oknok_5_9_soll'),
        ('oknok_5_10_soll','oknok_5_10_soll'),
        ('oknok_5_11_soll','oknok_5_11_soll'),
        ('oknok_5_12_soll','oknok_5_12_soll'),
        ('oknok_5_13_soll','oknok_5_13_soll'),
        ('oknok_5_14_soll','oknok_5_14_soll'),
        ('oknok_5_15_soll','oknok_5_15_soll'),
        ('oknok_5_16_soll','oknok_5_16_soll'),
        ('oknok_5_17_soll','oknok_5_17_soll'),
        ('oknok_5_18_soll','oknok_5_18_soll'),
        ('oknok_5_19_soll','oknok_5_19_soll'),
        ('oknok_5_20_soll','oknok_5_20_soll'),
        ('oknok_5_21_soll','oknok_5_21_soll'),
        ('oknok_5_22_soll','oknok_5_22_soll'),
        ('oknok_5_23_soll','oknok_5_23_soll'),
        ('oknok_5_24_soll','oknok_5_24_soll'),
        ('oknok_5_25_soll','oknok_5_25_soll'),
        ('oknok_5_26_soll','oknok_5_26_soll'),
        ('oknok_5_27_soll','oknok_5_27_soll'),
        ('oknok_5_28_soll','oknok_5_28_soll'),
        ('oknok_5_29_soll','oknok_5_29_soll'),
        ('oknok_5_30_soll','oknok_5_30_soll'),
        ('oknok_5_31_soll','oknok_5_31_soll'),
        ('oknok_5_32_soll','oknok_5_32_soll'),
        ('oknok_5_33_soll','oknok_5_33_soll'),
        ('oknok_5_34_soll','oknok_5_34_soll'),
        ('oknok_5_35_soll','oknok_5_35_soll'),
        ('oknok_5_36_soll','oknok_5_36_soll'),
        ('oknok_5_37_soll','oknok_5_37_soll'),
        ('oknok_5_38_soll','oknok_5_38_soll'),
        ('oknok_5_39_soll','oknok_5_39_soll'),
        ('oknok_5_40_soll','oknok_5_40_soll'),
        ('oknok_5_41_soll','oknok_5_41_soll'),
        ('oknok_5_42_soll','oknok_5_42_soll'),
        ('oknok_5_43_soll','oknok_5_43_soll'),
        ('oknok_5_44_soll','oknok_5_44_soll'),
        ('oknok_5_45_soll','oknok_5_45_soll'),
        ('oknok_5_46_soll','oknok_5_46_soll'),
        ('oknok_5_47_soll','oknok_5_47_soll'),
        ('oknok_5_48_soll','oknok_5_48_soll'),
        ('oknok_5_49_soll','oknok_5_49_soll'),
        ('oknok_5_50_soll','oknok_5_50_soll'),
        ('oknok_5_51_soll','oknok_5_51_soll'),
        ('oknok_6_1_soll','oknok_6_1_soll'),
        ('oknok_6_2_soll','oknok_6_2_soll'),
        ('oknok_6_3_soll','oknok_6_3_soll'),
        ('oknok_6_4_soll','oknok_6_4_soll'),
        ('oknok_6_5_soll','oknok_6_5_soll'),
        ('oknok_6_6_soll','oknok_6_6_soll'),
        ('oknok_6_7_soll','oknok_6_7_soll'),
        ('oknok_6_8_soll','oknok_6_8_soll'),
        ('oknok_6_9_soll','oknok_6_9_soll'),
        ('oknok_6_10_soll','oknok_6_10_soll'),
        ('oknok_6_11_soll','oknok_6_11_soll'),
        ('oknok_6_12_soll','oknok_6_12_soll'),
        ('oknok_6_13_soll','oknok_6_13_soll'),
        ('oknok_7_1_soll','oknok_7_1_soll'),
        ('oknok_7_2_soll','oknok_7_2_soll'),
        ('oknok_7_3_soll','oknok_7_3_soll'),
        ('oknok_7_4_soll','oknok_7_4_soll'),
        ('oknok_8_1_soll','oknok_8_1_soll'),
        ('oknok_8_2_soll','oknok_8_2_soll'),
        ('oknok_8_3_soll','oknok_8_3_soll'),
        ('oknok_8_4_soll','oknok_8_4_soll'),
        ('oknok_8_5_soll','oknok_8_5_soll'),
        ('oknok_10_1_soll','oknok_10_1_soll'),
        ('oknok_10_2_soll','oknok_10_2_soll'),
        ('oknok_10_3_soll','oknok_10_3_soll'),
        ('oknok_10_4_soll','oknok_10_4_soll'),
        ('oknok_10_5_soll','oknok_10_5_soll'),






        
        ('check_size_10_2_soll', 'check_size_10_2_soll_avr'),

        ('check_size_3_soll', 'check_size_3_soll_avr'),
        ('oknok_size_1_soll', 'check_size_4_soll_avr'),
        ('check_size_4a_soll', 'check_size_4a_soll_avr'),
        ('check_size_5_soll', 'check_size_5_soll_avr'),
        ('check_size_6_soll', 'check_size_6_soll_avr'),
        ('check_size_7_soll', 'check_size_7_soll_avr'),
        ('check_size_8_soll', 'check_size_8_soll_avr'),
        ('check_size_9_soll', 'check_size_9_soll_avr'),
        ('check_size_10_soll', 'check_size_10_soll_avr'),
        ('position_tolerance_11_soll', 'position_tolerance_11_soll_avr')
    ]

    # Loop through each pair of field names and update the model if there's a meaningful POST value
    for soll_field, avr_field in field_bases:
        # Update soll value if present
        soll_value = request.POST.get(soll_field)
        if soll_value:
            setattr(protokol, soll_field, soll_value)

        # Update average value if present
        avr_value = request.POST.get(avr_field)
        if avr_value:
            setattr(protokol, avr_field, avr_value)
    
    for number in protokol.additional_data:
        soll_value = request.POST.get(f'check_size_{number}_soll')
        if soll_value:
            protokol.additional_data[number]["wert"] = soll_value
        
        avr_value = request.POST.get(f'check_size_{number}_soll_avr')
        if avr_value:
            protokol.additional_data[number]["avr"] = avr_value

            
    protokol.save()
    return render(request, 'protocolHubzugLiftingHostSollWert.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id, 'current_user': currentUser})

@require_http_methods(["POST"])
def protocolHubzugLiftingHostSollWertClose(request, protocol_id):
    protokol = get_object_or_404(ProtocolHubzugLiftingHost, pk=protocol_id)
    protokol.isPermanentDone = True
    protokol.save()
    return sollWertView(request)

@require_http_methods(["POST"])
def protocolLaufHubzugSollWertClose(request, protocol_id):
    protokol = get_object_or_404(ProtocolLaufHubzug, pk=protocol_id)
    protokol.isPermanentDone = True
    protokol.save()
    return sollWertView(request)

#@require_http_methods(["POST"])
def protocolHubzugLiftingHostSollWertOffentlich(request, protocol_id):
    permanentProtokol = get_object_or_404(PermanentProtocol, pk=protocol_id)
    protokol1 = permanentProtokol.permanentProtocol1
    protokol4 = permanentProtokol.permanentProtocol4
    print(protokol1.isPermanentDone)

    for protocol in permanentProtokol.protocol1.all():
        protokol = get_object_or_404(ProtocolHubzugLiftingHost, pk=protocol.id)
        print(protokol.isPermanentDone)
        protokol.isPermanentDone = protokol1.isPermanentDone

        protokol.oknok_3_6_soll = protokol1.oknok_3_6_soll
        protokol.oknok_1_10_soll = protokol1.oknok_1_10_soll


        protokol.check_size_2_soll_avr = protokol1.check_size_2_soll_avr
        protokol.check_size_3_soll = protokol1.check_size_3_soll
        protokol.check_size_3_soll_avr = protokol1.check_size_3_soll_avr
        protokol.check_size_4_soll = protokol1.check_size_4_soll
        protokol.check_size_4_soll_avr = protokol1.check_size_4_soll_avr
        protokol.check_size_4a_soll = protokol1.check_size_4a_soll
        protokol.check_size_4a_soll_avr = protokol1.check_size_4a_soll_avr
        protokol.check_size_5_soll = protokol1.check_size_5_soll
        protokol.check_size_5_soll_avr = protokol1.check_size_5_soll_avr
        protokol.check_size_6_soll = protokol1.check_size_6_soll
        protokol.check_size_6_soll_avr = protokol1.check_size_6_soll_avr
        protokol.check_size_7_soll = protokol1.check_size_7_soll
        protokol.check_size_7_soll_avr = protokol1.check_size_7_soll_avr
        protokol.check_size_8_soll = protokol1.check_size_8_soll
        protokol.check_size_8_soll_avr = protokol1.check_size_8_soll_avr
        protokol.check_size_9_soll = protokol1.check_size_9_soll
        protokol.check_size_9_soll_avr = protokol1.check_size_9_soll_avr
        protokol.check_size_10_soll = protokol1.check_size_10_soll
        protokol.check_size_10_soll_avr = protokol1.check_size_10_soll_avr
        protokol.position_tolerance_11_soll = protokol1.position_tolerance_11_soll
        protokol.position_tolerance_11_soll_avr = protokol1.position_tolerance_11_soll_avr
        protokol.additional_data = protokol1.additional_data
        protokol.save()
        print(protokol.isPermanentDone)
    
    for protocol in permanentProtokol.protocol4.all():
        protokol = get_object_or_404(ProtocolLaufHubzug, pk=protocol.id)
        protokol.isPermanentDone = protokol4.isPermanentDone
        protokol.save()

    protokol1.delete()
    protokol4.delete()
    permanentProtokol.delete()

    return sollWertView(request)

def protocolHubzugLiftingHostAddNewField(request, protocol_id):
    if request.method == "POST":
        currentUser = request.user
        protokol = get_object_or_404(ProtocolHubzugLiftingHost, pk=protocol_id)

        # Get fahrzeug_id from URL query parameters
        fahrzeug_id = request.GET.get("fahrzeugId", "")

        # Retrieve POST data
        new_number = protokol.count  # Must match name="new_field"
        new_field = request.POST.get("new_field", "")  # Must match name="new_field"
        new_type = request.POST.get("new_type", "")  # Must match name="new_type"

        print("🚀 Received POST request!")
        print(f"New Number: {new_number}")
        print(f"New Field: {new_field}")
        print(f"New Type: {new_type}")
        print(f"Fahrzeug ID: {fahrzeug_id}")
        if new_field:
            protokol.additional_data[new_number] = {"name": new_field, 
                                                    "type": new_type,
                                                    "wert": 0,
                                                    "avr": 0}
            protokol.save()
        print(protokol.additional_data)

        protokol.count+=1
        protokol.save()

        # Return JSON response for debugging
        return render(request, 'protocolHubzugLiftingHostSollWert.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id, 'current_user': currentUser})

    
    return JsonResponse({"error": "Invalid request"}, status=400)

def protocolHubzugLiftingHostAdminAddNewField(request, protocol_id):
    if request.method == "POST":
        currentUser = request.user
        protokol = get_object_or_404(ProtocolHubzugLiftingHost, pk=protocol_id)

        # Get fahrzeug_id from URL query parameters
        fahrzeug_id = request.GET.get("fahrzeugId", "")

        # Retrieve POST data
        new_number = protokol.count  # Must match name="new_field"
        new_field = request.POST.get("new_field", "")  # Must match name="new_field"
        new_type = request.POST.get("new_type", "")  # Must match name="new_type"

        print("🚀 Received POST request!")
        print(f"New Number: {new_number}")
        print(f"New Field: {new_field}")
        print(f"New Type: {new_type}")
        print(f"Fahrzeug ID: {fahrzeug_id}")
        if new_field:
            protokol.additional_data[new_number] = {"name": new_field, 
                                                    "type": new_type,
                                                    "wert": 0,
                                                    "avr": 0}
            protokol.save()
        print(protokol.additional_data)

        protokol.count+=1
        protokol.save()

        # Return JSON response for debugging
        return render(request, 'protocolHubzugLiftingHostAdmin.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id, 'current_user': currentUser})

    
    return JsonResponse({"error": "Invalid request"}, status=400)


@require_POST
def toggle_nacharbeit_status(request, protocol_id):
    protokol = get_object_or_404(ProtocolHubzugLiftingHost, pk=protocol_id)
    protokol.isNacharbeitNeeded = not protokol.isNacharbeitNeeded
    protokol.save()
    currentUser = request.user


    fahrzeug_id = request.GET.get('fahrzeugId', None)
    fahrzeug = newFahrzeug.objects.get(id=fahrzeug_id)
    context = {
        'username': currentUser.username,
        'fahrzeug_id': fahrzeug_id,
        'hubzug': fahrzeug.hubzug
    }
    return redirect("/prueferView/")





"---------------------------------------------------------------------------------"
def protocol_list(request):
    protocols = newFahrzeug.objects.all()
    filter_form = ProtocolFilterForm(request.GET or None)

    # Apply filters based on form input
    if filter_form.is_valid():
        baustelle = filter_form.cleaned_data.get('baustelle')
        fahrzeug = filter_form.cleaned_data.get('fahrzeug')
        protocol_name = filter_form.cleaned_data.get('protocol_name')
        status = filter_form.cleaned_data.get('status')
        teil = filter_form.cleaned_data.get('teil')

        if baustelle:
            protocols = protocols.filter(baustelle__baustelleName__icontains=baustelle)
        if fahrzeug:
            protocols = protocols.filter(fahrzeugName__icontains=fahrzeug)
        if protocol_name:
            protocols = protocols.filter(
                Q(hubzug__protocol1__protocolName__icontains=protocol_name) |
                Q(hubzug__protocol2__protocolName__icontains=protocol_name) |
                Q(hubzug__protocol3__protocolName__icontains=protocol_name)
            )
        if status:
            if status == 'exported':
                protocols = protocols.filter(
                    Q(hubzug__protocol1__isExported=True) |
                    Q(hubzug__protocol2__isExported=True) |
                    Q(hubzug__protocol3__isExported=True)
                )
            elif status == 'closed':
                protocols = protocols.filter(
                    Q(hubzug__protocol1__isClosed=True, hubzug__protocol1__isExported=False) |
                    Q(hubzug__protocol2__isClosed=True, hubzug__protocol2__isExported=False) |
                    Q(hubzug__protocol3__isClosed=True, hubzug__protocol3__isExported=False)
                )
            elif status == 'saved':
                protocols = protocols.filter(
                    Q(hubzug__protocol1__isSaved=True, hubzug__protocol1__isClosed=False, hubzug__protocol1__isExported=False) |
                    Q(hubzug__protocol2__isSaved=True, hubzug__protocol2__isClosed=False, hubzug__protocol2__isExported=False) |
                    Q(hubzug__protocol3__isSaved=True, hubzug__protocol3__isClosed=False, hubzug__protocol3__isExported=False)
                )
            elif status == 'offen':

               

                protocols = protocols.filter(hubzug__protocol3__isSaved=False)

                print("--------------------------------------")

                queryset = newFahrzeug.objects.select_related('newHubzug').all()
                queryset1 = newFahrzeug.objects.all()

                for x in queryset:
                    print(x.protocol1)

            elif status == 'correction':
                protocols = protocols.filter(
                    Q(hubzug__protocol1__isCorrecturNeeded=True) |
                    Q(hubzug__protocol2__isCorrecturNeeded=True) |
                    Q(hubzug__protocol3__isCorrecturNeeded=True)
                )

    return render(request, 'protocol_list.html', {'protocols': protocols, 'filter_form': filter_form})



@login_required(login_url="/")
def welcome_page(request):
    username = request.session.get('username', '') 
    return render(request, 'home.html', {'username': username})

@login_required(login_url="/")
def baustellen(request):
    baustellen_list = Baustelle.objects.all()
    fahrzeugen_list = Fahrzeug.objects.all()
    selected_baustelle_id = request.GET.get('baustelle') 
    selected_fahrzeug_id = request.GET.get('fahrzeug') 

    if not selected_baustelle_id and baustellen_list.exists():
        selected_baustelle_id = baustellen_list.first().id

    if selected_baustelle_id:
        selected_baustelle = Baustelle.objects.get(id=selected_baustelle_id)
        fahrzeug_list = Fahrzeug.objects.filter(baustelle=selected_baustelle)
    else:
        selected_baustelle = None
        fahrzeug_list = Fahrzeug.objects.none()  # Or handle as suitable for your app

    
    context = {
        'baustellen_list': baustellen_list,
        'fahrzeug_list': fahrzeug_list,
        'selected_baustelle_id': selected_baustelle_id,
        'selected_fahrzeug_id': selected_fahrzeug_id   # Pass this to your template
    }
    return render(request, 'baustelle.html', context)

@login_required(login_url="/")
def fahrzeugsnummer(request):
    username = request.session.get('username', '') 
    return render(request, 'fahrzeugsnummer.html', {'username': username})

@login_required(login_url="/")
def menu(request):
    username = request.session.get('username', '')

    baustelle = request.GET.get('baustelle', None)
    fahrzeug = request.GET.get('fahrzeug', None)

    if not baustelle or not fahrzeug:
        return redirect('/baustelle/') 

    context = {
        'username': username,
        'baustelle': Baustelle.objects.get(id=baustelle),
        'fahrzeug': Fahrzeug.objects.get(id=fahrzeug)
    }
    return render(request, 'menu.html', context)


"""
Hubzug side
------------------------------------------------------------------------------------------------
"""
def hubzug_view(request):
    username = request.session.get('username', '')
    fahrzeug_id = request.GET.get('fahrzeugId', None)

    fahrzeug = newFahrzeug.objects.get(id=fahrzeug_id)

    context = {
        'username': username,
        'fahrzeug_id': fahrzeug_id,
        'hubzug': fahrzeug.hubzug
    }
    return render(request, 'hubzug.html', context)

def protokol_detail(request, id):
    # Assume `get_protokol` is a function that retrieves the protocol data by ID
    protokol = get_object_or_404(Protokol, pk=id)
    return render(request, 'protokol_detail.html', {'protokol': protokol})

@require_http_methods(["POST"])
def protokol_update(request, id):
    protokol = get_object_or_404(Protokol, pk=id)
    protokol.lastChanger = request.session.get('username', '')
    protokol.description = request.POST.get('description', '')
    protokol.size = request.POST.get('size', '')
    protokol.save()
    return redirect('protokol_detail', id=id)  # Redirect back to the detail view

@require_http_methods(["POST"])
def protokol_reset(request, id):
    protokol = get_object_or_404(Protokol, pk=id)
    # Resetting the fields you want to clear, e.g., description
    protokol.lastChanger = request.session.get('username', '')
    protokol.description = ""
    protokol.size = ""
    protokol.save()
    return redirect('protokol_detail', id=id)  # Redirect back to the detail view of the protocol

@require_http_methods(["POST"])
def protokol_export_pdf(request, id):
    protokol = get_object_or_404(Protokol, pk=id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(f'{GLOBAL_DIR}{protokol.hubzug.baustelle.baustelle}/{protokol.hubzug.fahrzeug.fahrzeug}/Hubzug/{protokol.name}/'), exist_ok=True)
    html_string = render_to_string('protokol_pdf_template.html', {'protokol': protokol})
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    html.write_pdf(target=f'{GLOBAL_DIR}{protokol.hubzug.baustelle.baustelle}/{protokol.hubzug.fahrzeug.fahrzeug}/Hubzug/{protokol.name}/{now}.pdf')

    protocol = AllProtocols(
            baustelle=protokol.hubzug.baustelle.baustelle,
            fahrzeug=protokol.hubzug.fahrzeug.fahrzeug,
            teil="Hubzug",
            protokolType=protokol.name,
            path=f'{GLOBAL_DIR}{protokol.hubzug.baustelle.baustelle}/{protokol.hubzug.fahrzeug.fahrzeug}/Hubzug/{protokol.name}/{now}.pdf'
        )
    protocol.save()

    return redirect('protokol_detail', id=id)


"""
------------------------------------------------------------------------------------------------
"""

"""
Mechanik side
------------------------------------------------------------------------------------------------
"""
def mechanik_view(request):
    username = request.session.get('username', '')
    baustelle = request.GET.get('baustelle', None)
    fahrzeug = request.GET.get('fahrzeug', None)

    """ if not baustelle or not fahrzeug:
        return redirect('/baustelle/') 
     """
    """ mechanik = Mechanik.objects.get(baustelle=baustelle, fahrzeug=fahrzeug)
    

    # Fetch Protokolnames linked with Hubzug ID from the database
    protokolnames = ProtokolMechanik.objects.filter(mechanik=mechanik)
 """
    context = {
        'username': username,
    }
    return render(request, 'mechanik.html', context)


def protokolMechanik_detail(request, id):
    # Assume `get_protokol` is a function that retrieves the protocol data by ID
    protokol = get_object_or_404(ProtokolMechanik, pk=id)
    return render(request, 'protokolMechanik_detail.html', {'protokol': protokol})

@require_http_methods(["POST"])
def protokolMechanik_update(request, id):
    protokol = get_object_or_404(ProtokolMechanik, pk=id)
    protokol.lastChanger = request.session.get('username', '')
    protokol.description = request.POST.get('description', '')
    protokol.size = request.POST.get('size', '')
    protokol.save()
    return redirect('protokolMechanik_detail', id=id)  # Redirect back to the detail view

@require_http_methods(["POST"])
def protokolMechanik_reset(request, id):
    protokol = get_object_or_404(ProtokolMechanik, pk=id)
    # Resetting the fields you want to clear, e.g., description
    protokol.lastChanger = request.session.get('username', '')
    protokol.description = ""
    protokol.size = ""
    protokol.save()
    return redirect('protokolMechanik_detail', id=id)  # Redirect back to the detail view of the protocol

@require_http_methods(["POST"])
def protokolMechanik_export_pdf(request, id):
    protokol = get_object_or_404(ProtokolMechanik, pk=id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(f'{GLOBAL_DIR}{protokol.mechanik.baustelle.baustelle}/{protokol.mechanik.fahrzeug.fahrzeug}/Mechanik/{protokol.name}/'), exist_ok=True)
    html_string = render_to_string('protokol_pdf_template.html', {'protokol': protokol})
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    html.write_pdf(target=f'{GLOBAL_DIR}{protokol.mechanik.baustelle.baustelle}/{protokol.mechanik.fahrzeug.fahrzeug}/Mechanik/{protokol.name}/{now}.pdf')

    protocol = AllProtocols(
            baustelle=protokol.mechanik.baustelle.baustelle,
            fahrzeug=protokol.mechanik.fahrzeug.fahrzeug,
            teil="Mechanik",
            protokolType=protokol.name,
            path=f'{GLOBAL_DIR}{protokol.mechanik.baustelle.baustelle}/{protokol.mechanik.fahrzeug.fahrzeug}/Hubzug/{protokol.name}/{now}.pdf'
        )
    protocol.save()

    return redirect('protokolMechanik_detail', id=id)

"""
------------------------------------------------------------------------------------------------
"""

"""
Elektrik side
------------------------------------------------------------------------------------------------
"""

def elektrik_view(request):
    username = request.session.get('username', '')
    baustelle = request.GET.get('baustelle', None)
    fahrzeug = request.GET.get('fahrzeug', None)

    if not baustelle or not fahrzeug:
        return redirect('/baustelle/') 
    
    elektrik = Elektrik.objects.get(baustelle=baustelle, fahrzeug=fahrzeug)
    

    # Fetch Protokolnames linked with Hubzug ID from the database
    protokolnames = ProtokolElektrik.objects.filter(elektrik=elektrik)

    context = {
        'username': username,
        'protokolnames': protokolnames,
    }
    return render(request, 'elektrik.html', context)

def protokolElektrik_detail(request, id):
    # Assume `get_protokol` is a function that retrieves the protocol data by ID
    protokol = get_object_or_404(ProtokolElektrik, pk=id)
    return render(request, 'protokolElektrik_detail.html', {'protokol': protokol})

@require_http_methods(["POST"])
def protokolElektrik_update(request, id):
    protokol = get_object_or_404(ProtokolElektrik, pk=id)
    protokol.lastChanger = request.session.get('username', '')
    protokol.description = request.POST.get('description', '')
    protokol.size = request.POST.get('size', '')

    # Update the nested JSON field
    elektrikInside = {}
    for key, value in request.POST.items():
        print(key)
        if key not in ['csrfmiddlewaretoken', 'description', 'size', 'lastChanger']:
            outer_key, inner_key = key.split('_', 1)
            if outer_key not in elektrikInside:
                elektrikInside[outer_key] = {}
            elektrikInside[outer_key][inner_key] = value

    protokol.elektrikInside = elektrikInside
    protokol.save()
    return redirect('protokolElektrik_detail', id=id)  # Redirect back to the detail view

@require_http_methods(["POST"])
def protokolElektrik_reset(request, id):
    protokol = get_object_or_404(ProtokolElektrik, pk=id)
    # Resetting the fields you want to clear, e.g., description
    protokol.lastChanger = request.session.get('username', '')
    protokol.description = ""
    protokol.size = ""
    protokol.save()
    return redirect('protokolElektrik_detail', id=id)  # Redirect back to the detail view of the protocol

@require_http_methods(["POST"])
def protokolElektrik_export_pdf(request, id):
    protokol = get_object_or_404(ProtokolElektrik, pk=id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(f'{GLOBAL_DIR}{protokol.elektrik.baustelle.baustelle}/{protokol.elektrik.fahrzeug.fahrzeug}/Elektrik/{protokol.name}/'), exist_ok=True)
    html_string = render_to_string('protokol_pdf_template.html', {'protokol': protokol})
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    html.write_pdf(target=f'{GLOBAL_DIR}{protokol.elektrik.baustelle.baustelle}/{protokol.elektrik.fahrzeug.fahrzeug}/Elektrik/{protokol.name}/{now}.pdf')
    
    protocol = AllProtocols(
            baustelle=protokol.elektrik.baustelle.baustelle,
            fahrzeug=protokol.elektrik.fahrzeug.fahrzeug,
            teil="Elektrik",
            protokolType=protokol.name,
            path=f'{GLOBAL_DIR}{protokol.elektrik.baustelle.baustelle}/{protokol.elektrik.fahrzeug.fahrzeug}/Hubzug/{protokol.name}/{now}.pdf'
        )
    protocol.save()


    return redirect('protokolElektrik_detail', id=id)
    

"""
------------------------------------------------------------------------------------------------
"""

