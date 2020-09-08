from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from nest_box_helper.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm, SheetForm, UpdateSheetForm, AddParkForm, AddBoxForm, AddAttemptForm
from django.http import HttpResponse, HttpResponseRedirect
from nest_box_helper.models import Sheet, Account, Park, Box, Attempt, UserParks
from django.db import connection
from operator import attrgetter
import datetime



def delete_user_park(request, park_id):
    user_park = UserParks.objects.get(id=park_id)
    user_park.delete()
    return redirect('dashboard')


def delete_box(request, park_id, box_id):
    box = Box.objects.get(id=box_id)
    box.delete()
    return HttpResponseRedirect(reverse('park_summary', args=[park_id]))


def delete_attempt(request, park_id, box_id, attempt_id):
    attempt = Attempt.objects.get(id=attempt_id)
    attempt.delete()
    return HttpResponseRedirect(reverse('attempt_summary', args=[park_id, box_id]))


def delete_sheet(request, park_id, box_id, attempt_id, slug):
    sheet = get_object_or_404(Sheet, slug=slug)
    sheet.delete()
    return HttpResponseRedirect(reverse('attempt_detail', args=[park_id, box_id, attempt_id]))


def detail_sheet_view(request, park_id, box_id, attempt_id, slug):
    context = {}
    sheet =  get_object_or_404(Sheet, slug=slug)
    attempt_obj_query = Attempt.objects.get(id=sheet.attempt_number_id)
    box_obj_query = attempt_obj_query.box_number_id
    park_name = Box.objects.get(id=box_obj_query)

    context= {
        'sheet': sheet,
        'attempt_query': attempt_obj_query,
        'park_id': park_id,
        'box_id': box_id,
        'attempt_id': attempt_id,
        'park_query': park_name,
        }
    return render(request, 'nest_box_helper/detail_sheet.html', context)


def create_sheet_form_view(request, park_id, box_id, attempt_id):
    context = {}
    current_date = datetime.datetime.now().strftime("%m/%d/%Y")
    user = request.user
    if user.is_authenticated:
        if request.POST:
            form = SheetForm(request.POST or None)

            current_date = datetime.datetime.now().strftime("%m/%d/%Y")

            if form.is_valid():
                obj = form.save(commit=False)
                monitor_name = Account.objects.filter(email=user.email).first()
                obj.monitor_name = monitor_name
                obj.park_id = park_id
                obj.box_id = box_id
                obj.attempt_number_id = attempt_id

                current_date = datetime.datetime.now().strftime("%m/%d/%Y")

                obj.save()

                attempt_number = form.cleaned_data.get('attempt_number')
                monitor_name=form.cleaned_data.get('monitor_name')
                date = form.cleaned_data.get('date')
                species = form.cleaned_data.get('species')
                nest_status = form.cleaned_data.get('nest_status')
                eggs=form.cleaned_data.get('eggs')
                live_young=form.cleaned_data.get('live_young')
                dead_young=form.cleaned_data.get('dead_young')
                adult_activity=form.cleaned_data.get('adult_activity')
                young_status=form.cleaned_data.get('young_status')
                management_activity=form.cleaned_data.get('management_activity')
                cowbird_evidence=form.cleaned_data.get('cowbird_evidence')
                comments=form.cleaned_data.get('comments')

                form=SheetForm()
                return HttpResponseRedirect(reverse('attempt_detail', args=[park_id, box_id, attempt_id]))
            else:
                current_date = datetime.datetime.now().strftime("%m/%d/%Y")
                context= {
                    'sheet_form': form,
                    'current_date': current_date,
                    }

        else:
            current_date = datetime.datetime.now().strftime("%m/%d/%Y")
            form = SheetForm()
            context= {
                'sheet_form': form,
                'park_id': park_id,
                'box_id': box_id,
                'attempt_id': attempt_id,
                'current_date': current_date,
                }
        return render(request, 'nest_box_helper/create_sheet.html', context)
    else:
        return redirect('authenticate')


def attempt_detail_view(request, park_id, box_id, attempt_id):
    user = request.user
    attempt_obj = Attempt.objects.get(id=attempt_id)
    box_obj = Box.objects.get(id=box_id)
    sheet_list = Sheet.objects.filter(attempt_number_id=attempt_id)
    sorted_sheet_list = sorted(sheet_list, key=attrgetter('date'))
    park_obj = UserParks.objects.get(monitor_name_id=user.id, park_name_id=park_id)
    context = {
        'box_id': box_id,
        'park_id': park_id,
        'box_obj': box_obj,
        'attempt_id': attempt_id,
        'attempt_obj': attempt_obj,
        'park_obj': park_obj,
        'sorted_sheet_list': sorted_sheet_list,
        }
    return render(request, 'nest_box_helper/attempt_detail.html', context)


def add_attempt_form_view(request, park_id, box_id):
    context = {}
    user = request.user
    if user.is_authenticated:
        if request.POST:
            form = AddAttemptForm(request.POST or None)
            if form.is_valid():
                obj = form.save(commit=False)
                monitor = Account.objects.get(email=user.email)
                box_obj = Box.objects.get(id=box_id)
                obj.box_number = box_obj
                obj.monitor_name_id = monitor.id
                obj.save()
                return HttpResponseRedirect(reverse('attempt_summary', args=[park_id, box_id]))
            else:
                context = {
                    'add_attempt_form': form,
                    'park_id': park_id,
                    'box_id': box_id,
                }
        else:
            form = AddAttemptForm()
            context = {
                'add_attempt_form': form,
                'park_id': park_id,
                'box_id': box_id,
                }
        return render(request, 'nest_box_helper/add_attempt_form.html', context)
    else:
        return redirect('authenticate')


def attempt_summary_view(request, park_id, box_id):
    box_obj = Box.objects.get(id=box_id)
    park_obj = Park.objects.get(id=park_id)
    attempt_list_by_timestamp = Attempt.objects.filter(box_number_id=box_id).order_by('-timestamp')
    current_year = int(datetime.datetime.now().strftime("%Y"))

    context = {
        'box_id': box_id,
        'park_id': park_id,
        'park_obj': park_obj,
        'box_obj': box_obj,
        'attempt_list_by_timestamp': attempt_list_by_timestamp,
        'current_year': current_year,
        }
    return render(request, 'nest_box_helper/attempt_summary.html', context)


def add_box_form_view(request, park_id):
    context = {}
    user = request.user
    if user.is_authenticated:
        if request.POST:
            form = AddBoxForm(request.POST or None)
            if form.is_valid():
                obj = form.save(commit=False)

                list_of_user_park_boxes = Box.objects.filter(monitor_name_id=user.id, park_name_id=park_id)
                for box in list_of_user_park_boxes:
                    if box.box_number == obj.box_number:
                        messages.error(request, "* This box number already exists for this park! Please select a different box:")
                        return HttpResponseRedirect(reverse('add_box', args=[park_id]))


                monitor = Account.objects.get(email=user.email)
                obj.monitor_name_id = monitor.id
                obj.park_name_id = park_id
                obj.save()
                return HttpResponseRedirect(reverse('park_summary', args=[park_id]))


            else:
                context = {
                'add_box_form' : form,
                'park_id' : park_id,
                }
        else:
            form = AddBoxForm()
            context = {
            'add_box_form' : form,
            'park_id' : park_id,
            }
        return render(request, 'nest_box_helper/add_box.html', context)
    else:
        return redirect('authenticate')


def park_summary_view(request, park_id):

    context = {}
    user = request.user
    park = get_object_or_404(UserParks, monitor_name_id=user.id, park_name_id=park_id)
    box_list = Box.objects.filter(monitor_name_id=user.id, park_name_id=park_id).order_by('box_number')
    context = {
        'park': park,
        'box_list': box_list,
        }
    return render(request, 'nest_box_helper/park_summary.html', context)


def add_park_form_view(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        if request.POST:
            form = AddParkForm(request.POST or None)
            if form.is_valid():
                obj = form.save(commit=False)
                list_of_user_parks = UserParks.objects.filter(monitor_name_id=user.id)
                for park in list_of_user_parks:
                    if park.park_name == obj.park_name:
                        messages.error(request, "* This park already exists on your account! Please select a different park:")
                        return redirect('add_park')
                monitor_name = Account.objects.filter(email=user.email).first()
                obj.monitor_name = monitor_name
                obj.save()

                return redirect('dashboard')
            else:
                context['park_form'] = form
        else:
            form = AddParkForm()
            context['park_form'] = form
        return render(request, 'nest_box_helper/add_park.html', context)
    else:
        return redirect('authenticate')


def update_sheet_form_view(request, park_id, box_id, attempt_id, slug):
    context = {}

    user=request.user
    if not user.is_authenticated:
        return redirect("authenticate")

    sheet = get_object_or_404(Sheet, slug=slug)
    if request.POST:
        form = UpdateSheetForm(request.POST or None, instance=sheet)
        if form.is_valid():
            obj=form.save(commit=False)
            obj.park_id = park_id
            obj.box_id = box_id
            obj.attempt_id = attempt_id
            obj.save()
            context['success_message'] = "Sheet Updated"
            sheet = obj
            return HttpResponseRedirect(reverse('attempt_detail', args=[park_id, box_id, attempt_id]))

    form = UpdateSheetForm(
        initial = {
            "attempt_number": sheet.attempt_number,
            "date": sheet.date,
            "species": sheet.species,
            "eggs": sheet.eggs,
            "nest_status": sheet.nest_status,
            "live_young": sheet.live_young,
            "dead_young": sheet.dead_young,
            "adult_activity": sheet.adult_activity,
            "young_status": sheet.young_status,
            "management_activity": sheet.management_activity,
            "cowbird_evidence": sheet.cowbird_evidence,
            "comments": sheet.comments,
        }
    )
    context= {
        'form' : form,
        'park_id': park_id,
        'box_id': box_id,
        'attempt_id': attempt_id,
        }
    return render(request, 'nest_box_helper/update_sheet.html', context)


def dashboard_view(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        user_park_list = UserParks.objects.filter(monitor_name=request.user)
        context={
            'user_park_list':user_park_list,
            }
        return render(request, 'nest_box_helper/dashboard.html', context)
    else:
        return redirect('authenticate')


def authentication_view(request):
    return render(request, 'nest_box_helper/authenticate.html', {})


def registration_view(request):
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            return redirect('home')
        else:
            context['registration_form'] = form
    else:
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'nest_box_helper/register.html', context)


def logout_view(request):
    logout(request)
    return redirect('home')


def login_view(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        return redirect("dashboard")

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                return redirect("dashboard")

    else:
        form = AccountAuthenticationForm()

    context['login_form'] = form
    return render(request, 'nest_box_helper/login.html', context)


def account_update_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    context = {}

    if request.POST:
        form = AccountUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.initial = {
            "email": request.POST['email'],
            "username": request.POST['username'],
            }
            form.save()
            context['success_message'] = "Account Updated!"
    else:
        form = AccountUpdateForm(
            initial = {
                "email": request.user.email,
                "username": request.user.username,
            }
        )
    context['account_form'] = form
    return render(request, 'nest_box_helper/account_update.html', context)


def home_screen_view(request):
    return render(request, 'nest_box_helper/home.html')


def account_view(request):
    return render(request, 'nest_box_helper/dashboard.html')


def summarize_attempt(request, attempt_id):
    context = {}
    table_sheets = Sheet.objects.filter(attempt_number_id=attempt_id)
    attempt = Attempt.objects.get(id=attempt_id)
    box = Box.objects.get(id=attempt.box_number_id)
    park = Park.objects.get(id=box.park_name_id)
    num_sheets = len(table_sheets)
    context = {
        'table_sheets' : table_sheets,
        'num_sheets': num_sheets,
        'attempt_id': attempt_id,
        'attempt': attempt,
        'box': box,
        'park': park,
    }
    return render(request, 'nest_box_helper/summarize_attempt.html', context)
