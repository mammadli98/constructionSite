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

GLOBAL_DIR = "/home/mammadli98/Documents/huseynSiemens/Protokols/"

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

    
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            request.session['username'] = username
            if username == 'admin':
                return redirect("adminView/")
            return redirect("userView/")
        else:
            messages.info(request, "invalid credentials")
            return redirect("/")
    else: 
        return render(request, "login.html")

@login_required(login_url="/")
def adminView(request):
    baustellen_list = newBaustelle.objects.all()
    fahrzeugen_list = newFahrzeug.objects.all()  # Initially, no Fahrzeuge displayed
    user_list = User.objects.all()
    
    if request.method == 'POST':
        if 'baustelleName' in request.POST:
            baustelle_form = NewBaustelleForm(request.POST)
            if baustelle_form.is_valid():
                baustelle_form.save()
        elif 'fahrzeugName' in request.POST:
            fahrzeug_form = NewFahrzeugForm(request.POST)
            if fahrzeug_form.is_valid():
                hubzug = newHubzug()
                hubzugProtocol = ProtocolHubzugLiftingHost()
                hubzugProtocol.save()
                hubzug.protocol1 = hubzugProtocol
                hubzug.save()
                fahrzeug_form = fahrzeug_form.save(commit=False)
                fahrzeug_form.hubzug = hubzug
                fahrzeug_form.save()
        elif 'username' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            # Create the user
            new_user = User(username=username)
            new_user.set_password(password)
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

    context = {
        'baustellen_list': newBaustelle.objects.all(),
        'fahrzeug_list': newFahrzeug.objects.all(),
        'userPassword_form': userPasswordForm,
        'modal_show': modal_show  # Pass this flag to the template
    }
    return render(request, "userView.html", context)
    
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
    protokol = get_object_or_404(ProtocolHubzugLiftingHost, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    return render(request, 'protocolHubzugLiftingHost.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id})

@require_http_methods(["POST"])
def protocolHubzugLiftingHostUpdate(request, protocol_id):
    protokol = get_object_or_404(ProtocolHubzugLiftingHost, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', '')
    
    protokol.lastChanger = request.session.get('username', '')
    protokol.drawing = request.POST.get('drawing', '')
    protokol.rev = request.POST.get('rev', '')
    protokol.order = request.POST.get('order', '')
    protokol.order_sag = request.POST.get('order_sag', '')
    protokol.device = request.POST.get('device', '')
    protokol.hoist = request.POST.get('hoist', '')
    protokol.company = request.POST.get('company', '')
    protokol.quantity = request.POST.get('quantity', '')
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
    protokol.position_tolerance_11 = request.POST.get('position_tolerance_11', '')
    protokol.miscellaneous = request.POST.get('miscellaneous', '')
    protokol.remark = request.POST.get('remark', '')
    protokol.measure = request.POST.get('measure', '')
    protokol.date = request.POST.get('date', '')
    protokol.inspector = request.POST.get('inspector', '')
    protokol.department = request.POST.get('department', '')
    protokol.baustelle = request.POST.get('baustelle', '')

    protokol.isSaved = True
    protokol.save()
    return render(request, 'protocolHubzugLiftingHost.html', {'protokol': protokol, 'fahrzeug_id': fahrzeug_id})

@require_http_methods(["POST"])
def exportProtokolHubzugLiftingHost(request, protocol_id):
    protokol = get_object_or_404(ProtocolHubzugLiftingHost, pk=protocol_id)
    fahrzeug_id = request.GET.get('fahrzeugId', None)
    fahrzeug = newFahrzeug.objects.get(id=fahrzeug_id)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Finding the absolute path of the css file
    css_path = finders.find('pdf/pdfProtocolHubzugLiftingHost.css')
    css_url = request.build_absolute_uri(settings.STATIC_URL + 'pdf/pdfProtocolHubzugLiftingHost.css')

    html_string = render_to_string('protokol_pdf_template.html', {
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




















"---------------------------------------------------------------------------------"
def protocol_list(request):
    # Retrieve and sort data from the AllProtocols model
    protocols = newFahrzeug.objects.all()

    return render(request, 'protocol_list.html', {'protocols': protocols})



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

    if not baustelle or not fahrzeug:
        return redirect('/baustelle/') 
    
    mechanik = Mechanik.objects.get(baustelle=baustelle, fahrzeug=fahrzeug)
    

    # Fetch Protokolnames linked with Hubzug ID from the database
    protokolnames = ProtokolMechanik.objects.filter(mechanik=mechanik)

    context = {
        'username': username,
        'protokolnames': protokolnames,
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

