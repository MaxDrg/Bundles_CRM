from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from django.shortcuts import render
from django.db.models import Q
from random import randint
from . import models
import datetime
import requests
import hashlib
import urllib
import json
import os

ADMOB_CONNECTIONS = {}

def app_info(request):
    app = ""
    day = False
    search = True
    labels = []
    chart_data = []
    app_installs = ''
    status = ''
    last_update = ''
    app_name = ''
    admob = None
    date_from = datetime.datetime.now() - datetime.timedelta(weeks=1)
    date_to = datetime.datetime.now()
    date_day = datetime.datetime.now()

    if request.method == "POST":
        if request.POST['from'] == 'search':
            app = models.Apps.objects.filter(app_id = request.POST['app_bundle']).values('id')
            if not app:
                search = False
                day = True
                app = ''
            else:
                app = app[0]['id']
        else:
            app = request.POST['app_id']
        if request.POST['from'] == 'date_day':
            day = True
            date_day = datetime.datetime.strptime(request.POST['date_day'],'%Y-%m-%d')
            for hour in range(1, 25):
                history_data = models.History.objects.filter(app_id = app,
                                date_time__date = date_day.date(),
                                date_time__hour = hour)
                install = 0
                for data in history_data: 
                    install += data.installs
                chart_data.append(install)
                if len(str(hour)) == 1:
                    labels.append(f'0{hour}:00')
                else:
                    labels.append(f'{hour}:00')
        elif request.POST['from'] == 'date_from_to':
            date_from = datetime.datetime.strptime(request.POST['date_from'],'%Y-%m-%d')
            date_to = datetime.datetime.strptime(request.POST['date_to'],'%Y-%m-%d')
    elif request.method == "GET" and not request.GET.get('app') == None:
        app = request.GET.get('app')

    if search:
        app_data = models.Apps.objects.filter(id = app).values('app_name', 'installs', 'status', 'last_update', 'admob_id')[0]
        app_installs = app_data['installs']
        status = app_data['status']
        last_update = app_data['last_update']
        app_name =  app_data['app_name']
        admob = app_data['admob_id']

    if not day:
        current_day = date_from
        while current_day.date() <= date_to.date():
            history_data = sorted(models.History.objects.filter(app_id = app,
                                date_time__date = current_day.date()),
                                key=lambda history: history.date_time)
            labels.append(current_day.date())
            install = 0
            for installs in history_data:
                install += installs.installs
            chart_data.append(install)
            current_day += datetime.timedelta(days=1)

    return render(request, "app_info.html", 
    {
        "labels": labels,
        "chart_data": chart_data,
        "current_sidebar": 'apps', 
        "title": 'title',
        "date_from": datetime.datetime.strftime(date_from,'%Y-%m-%d'),
        "date_to": datetime.datetime.strftime(date_to,'%Y-%m-%d'),
        "date_day": datetime.datetime.strftime(date_day,'%Y-%m-%d'),
        "app_id": app,
        "installs": app_installs,
        "status": status,
        "last_update": last_update,
        "app_name": app_name,
        "search": search,
        "admob": admob
    })

def folders(request):
    if request.method == "GET" and not request.GET.get('synch') == None:
        for dev in models.Developers.objects.all():
            dev = {'dev': dev.dev}
            params = urllib.parse.urlencode(dev, quote_via=urllib.parse.quote)
            headers = {"Authorization": f"Bearer {os.environ.get('APPSTORESPY_TOKEN')}"}
            response = requests.get(os.environ.get('APPSTORESPY_URL'), headers=headers, params=params)
            for data in response.json()['data']:
                for app in models.Apps.objects.filter(last_update='Не существует'):
            	    if data['id'] == app.app_id:
                        app_info = models.Apps.objects.get(id=app.id)
                        app_info.app_name = data['name']
                        app_info.last_update = data['updated']
                        app_info.installs = data['installs_exact']
                        app_info.status = data['available']
                        app_info.save()
    return render(request, "folders.html", 
    {
        "current_sidebar": 'apps', 
        "folders": models.Folders.objects.all(),
        "apps": models.Apps.objects.filter(last_update='Не существует')
    })

def devs(request):
    if request.method == "POST":
        if request.POST['from'] == 'form_devs':
            models.Developers(
                dev = request.POST['dev']
            ).save()
        elif request.POST['from'] == 'devs':
            for dev_id in request.POST.getlist('list_dev'):
               models.Developers.objects.filter(id = dev_id).delete()
    return render(request, "devs.html", 
    {
        "current_sidebar": 'devs', 
        "devs": models.Developers.objects.all()
    })

def form_devs(request):
    return render(request, "form_devs.html", 
    {
        "current_sidebar": 'devs'
    })

def apps(request):
    apps = []
    admob_id = None
    current_sidebar = 'apps'
    if request.method == "GET":
        if not request.GET.get('folder') == None:
            apps = models.Apps.objects.filter(
                ~Q(last_update = 'Не существует'),
                folder_id = models.Folders.objects.filter(
                    folder_name = request.GET.get('folder')
                ).values('id')[0]['id']
            )
        elif not request.GET.get('admob_id') == None:
            apps = models.Apps.objects.filter(
                ~Q(last_update = 'Не существует'),
                admob_id = request.GET.get('admob_id')
            )
            admob_id = request.GET.get('admob_id')
            current_sidebar = 'admobs'
    return render(request, "apps.html", 
    {
        "current_sidebar": current_sidebar,
        "apps": apps,
        "admob_id": admob_id
    })

def apps_dashboard(request):
    labels = []
    chart_data_available = []
    chart_data_unavailable = []
    date_from = datetime.datetime.now() - datetime.timedelta(weeks=1)
    date_to = datetime.datetime.now()
    date_day = datetime.datetime.now()
    day = False
    if request.method == "POST":
        if request.POST['from'] == 'date_day':
            day = True
            date_day = datetime.datetime.strptime(request.POST['date_day'],'%Y-%m-%d')
            for hour in range(1, 25):
                data = models.Apps.objects.filter(
                                add_time__date = date_day.date(),
                                add_time__hour = hour,
                                status=True)
                adding = 0
                for add in data: 
                    adding += 1
                chart_data_available.append(adding)
                if len(str(hour)) == 1:
                    labels.append(f'0{hour}:00')
                else:
                    labels.append(f'{hour}:00')
            for hour in range(1, 25):
                data = models.Apps.objects.filter(
                                add_time__date = date_day.date(),
                                add_time__hour = hour,
                                status=False)
                adding = 0
                for add in data: 
                    adding += 1
                chart_data_unavailable.append(adding)
        elif request.POST['from'] == 'date_from_to':
            date_from = datetime.datetime.strptime(request.POST['date_from'],'%Y-%m-%d')
            date_to = datetime.datetime.strptime(request.POST['date_to'],'%Y-%m-%d')
    if not day:
        current_day = date_from
        while current_day.date() <= date_to.date():
            data = sorted(models.Apps.objects.filter(
                            add_time__date = current_day.date(),
                            status=True),
                            key=lambda data: data.add_time)
            labels.append(current_day.date())
            adding = 0
            for add in data:
                adding += 1
            chart_data_available.append(adding)
            data = sorted(models.Apps.objects.filter(
                            add_time__date = current_day.date(),
                            status=False),
                            key=lambda data: data.add_time)
            adding = 0
            for add in data:
                adding += 1
            chart_data_unavailable.append(adding)
            current_day += datetime.timedelta(days=1)
    return render(request, "apps_dashboard.html", 
    {
        "current_sidebar": 'apps_dashboard',
        "date_from": datetime.datetime.strftime(date_from,'%Y-%m-%d'),
        "date_to": datetime.datetime.strftime(date_to,'%Y-%m-%d'),
        "date_day": datetime.datetime.strftime(date_day,'%Y-%m-%d'),
        "labels": labels,
        "chart_data": chart_data_available,
        "chart_data1": chart_data_unavailable
    })

def admobs(request):
    if request.method == "POST":
        if request.POST['from'] == 'form_devs':
            models.Developers(
                dev = request.POST['dev']
            ).save()
        elif request.POST['from'] == 'admobs':
            for admob_id in request.POST.getlist('list_admob'):
                apps = models.Apps.objects.filter(admob_id = admob_id)
                for app in apps:
                    update_app = models.Apps.objects.get(id = app.id)
                    update_app.admob_id = None
                    update_app.save()
                models.Admobs.objects.filter(id = admob_id).delete()
    return render(request, "admobs.html", 
    {
        "current_sidebar": 'admobs',
        "admobs": models.Admobs.objects.all(),
        "message_success": False
    })

def form_admob(request):
    if request.method == "GET" and not request.GET.get('admob_id') == None:
        admob = models.Admobs.objects.filter(id = request.GET.get('admob_id'))[0]
        auth_url = ''
        if not "flow_id" in request.session:
            auth_url = create_flow(request, admob)
        else:
            auth_url = update_flow(request, admob)
        return render(request, "check_admob.html", 
        {
            "current_sidebar": 'admobs',
            "google_url": auth_url,
            "admob_id": admob.id,
            "from": 'admob_form'
        })
    return render(request, "form_admob.html", 
    {
        "exist_error": False,
        "current_sidebar": 'admobs'
    })

def check_admob(request):
    admob = ''
    from_value = ''
    if request.method == "POST" and not request.POST['admob_file'] == None:
        if request.POST['from'] == 'form_admob':
            from_value = 'admob_form'
            if models.Admobs.objects.filter(admob_name = request.POST['admob_name']).exists() or \
                models.Admobs.objects.filter(admob_secret_file = request.POST['admob_file']).exists():
                return render(request, "form_admob.html", 
                {
                    "exist_error": True,
                    "current_sidebar": 'admobs',
                })
            else:
                models.Admobs(
                    admob_name = request.POST['admob_name'],
                    admob_secret_file = request.POST['admob_file'],
                    publisher_id = request.POST['admob_pub_id']
                ).save()
                admob = models.Admobs.objects.filter(admob_name = request.POST['admob_name'])[0]
        else:
            from_value = 'admob_info'
            admob = models.Admobs.objects.filter(id = request.POST['admob_id'])[0]

    auth_url = create_flow(request, admob)
    return render(request, "check_admob.html", 
    {
        "current_sidebar": 'admobs',
        "google_url": auth_url,
        "admob_id": admob.id,
        "from": from_value
    })

def admob_info(request):
    data = ''
    admob = ''
    chart_data = []
    labels = []
    start_time = datetime.datetime.now() - datetime.timedelta(days=15)
    end_time = datetime.datetime.now()
    if request.method == "POST":
        admob = models.Admobs.objects.filter(id = request.POST['admob_id'])[0]
        if request.POST['from'] == 'admob_form':
            admob_apps = get_admobs_apps(request, admob.publisher_id)
            for ad_app in admob_apps:
                for app in models.Apps.objects.filter(~Q(app_name = 'Не существует'), admob_id = None):
                    try:
                        if app.app_name == ad_app['row']['dimensionValues']['APP']['displayLabel']:
                            update_app = models.Apps.objects.get(
                                id = app.id
                            )
                            update_app.admob_id = admob
                            update_app.save()
                    except:
                        pass
            return render(request, "admobs.html", 
            {
                "current_sidebar": 'admobs',
                "admobs": models.Admobs.objects.all(),
                "message_success": True
            })
        elif request.POST['from'] == 'app_info' or request.POST['from'] == 'date_start_end':
            if request.POST['from'] == 'date_start_end':
                start_time = datetime.datetime.strptime(request.POST['start_time'],'%Y-%m-%d')
                end_time = datetime.datetime.strptime(request.POST['end_time'],'%Y-%m-%d')
            current_app = models.Apps.objects.filter(id = request.POST['app_id'])[0]
            if "flow_id" in request.session:
                make_check = False
                try:
                    data = get_admobs_apps(request, admob.publisher_id,
                                            start_year = start_time.year,
                                            start_month = start_time.month,
                                            start_day = start_time.day,
                                            end_year = end_time.year,
                                            end_month = end_time.month,
                                            end_day = end_time.day)
                except:
                    make_check = True
                if not make_check:
                    summ = 0
                    current_revenue = 0
                    current_day = ''
                    for app in data:
                        try:
                            if app['row']['dimensionValues']['APP']['displayLabel'] == current_app.app_name:
                                revenue = round(int(app['row']['metricValues']['ESTIMATED_EARNINGS']['microsValue']) * 10 ** -6, 2)
                                time = datetime.datetime.strptime(app['row']['dimensionValues']['DATE']['value'], "%Y%m%d")
                                if time == current_day:
                                    current_revenue += revenue
                                else:
                                    chart_data.append(current_revenue)
                                    current_day = time
                                    current_revenue = revenue
                                    labels.append(time.date())
                                summ += int(app['row']['metricValues']['ESTIMATED_EARNINGS']['microsValue'])
                        except:
                            pass
                    return render(request, "admob_info.html", 
                    {
                        "current_sidebar": 'apps',
                        'chart_data': list(reversed(chart_data)),
                        'labels': list(reversed(labels)),
                        'summ': round(summ * 10 ** -6, 2),
                        'app_name': current_app.app_name,
                        'app_id': current_app.id,
                        'admob_id': admob.id,
                        "start_time": datetime.datetime.strftime(start_time,'%Y-%m-%d'),
                        "end_time": datetime.datetime.strftime(end_time,'%Y-%m-%d'),
                    })
            auth_url = create_flow(request, admob)
            return render(request, "check_admob.html", 
            {
                "current_sidebar": 'apps',
                "google_url": auth_url,
                "admob_id": admob.id,
                "app_id": current_app.id,
                "from": 'app_info'
            })

def clear_admob_connections():
    for key in list(ADMOB_CONNECTIONS):
        if ADMOB_CONNECTIONS[key]['delete_time'] <= datetime.datetime.now():
            ADMOB_CONNECTIONS.pop(key)

def create_flow(request, admob):
    path = f'json/buffer{randint(10000, 99999)}.json'
    with open(path, "w") as file:
        json.dump(json.loads(admob.admob_secret_file), file)
    flow = Flow.from_client_secrets_file(
        path,
        scopes=['https://www.googleapis.com/auth/admob.readonly'],
        redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    auth_url, _ = flow.authorization_url()
    os.remove(path)
    id = hashlib.sha224(str(randint(1000000000, 9999999999)).encode('utf-8')).hexdigest()
    request.session["flow_id"] = id
    ADMOB_CONNECTIONS.update(
        { 
            id: { 
            'flow': flow,
            "delete_time": datetime.datetime.now() + datetime.timedelta(days=1)
            }
        }
    )
    return auth_url

def update_flow(request, admob):
    path = f'json/buffer{randint(10000, 99999)}.json'
    with open(path, "w") as file:
        json.dump(json.loads(admob.admob_secret_file), file)
    flow = Flow.from_client_secrets_file(
        path,
        scopes=['https://www.googleapis.com/auth/admob.readonly'],
        redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    auth_url, _ = flow.authorization_url()
    os.remove(path)
    ADMOB_CONNECTIONS.update(
        { 
            request.session["flow_id"]: { 
            'flow': flow,
            "delete_time": datetime.datetime.now() + datetime.timedelta(days=1)
            }
        }
    )
    return auth_url

def get_admobs_apps(request, publisher_id, 
                    start_year = (datetime.datetime.now() - datetime.timedelta(days=10)).year,
                    start_month = datetime.datetime.now().month,
                    start_day = datetime.datetime.now().day,
                    end_year = datetime.datetime.now().year,
                    end_month = datetime.datetime.now().month,
                    end_day = datetime.datetime.now().day):
    
    service = 0
    
    try:
        service = build('admob', 'v1', 
        credentials=ADMOB_CONNECTIONS[request.session["flow_id"]]['flow'].credentials)
    except:
        flow = ADMOB_CONNECTIONS[request.session["flow_id"]]['flow']
        flow.fetch_token(code=request.POST['token'])
        credentials = flow.credentials
        service = build('admob', 'v1', credentials=credentials)
        ADMOB_CONNECTIONS[request.session["flow_id"]]['flow'] = flow
    
    date_range = {
    'start_date': {
        'year': start_year, 
        'month': start_month, 
        'day': start_day},
    'end_date': {
        'year': end_year, 
        'month': end_month, 
        'day': end_day }
    }

    dimensions = ['DATE', 'APP', 'PLATFORM', 'COUNTRY']

    metrics = ['ESTIMATED_EARNINGS', 'AD_REQUESTS', 'MATCHED_REQUESTS']

    sort_conditions = {'dimension': 'DATE', 'order': 'DESCENDING'}

    report_spec = {
        'date_range': date_range,
        'dimensions': dimensions,
        'metrics': metrics,
        'sort_conditions': [sort_conditions],
    }

    # Create network report request.
    request = {'report_spec': report_spec}

    # Execute network report request.
    response = service.accounts().networkReport().generate(
        parent='accounts/{}'.format(publisher_id), body=request).execute()

    return response