from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProjetSerializer, JalonsSerializer, TacheSerializer
import plotly.graph_objs as go
from plotly.offline import plot
import pandas as pd

from theapp.models import Institution, Projet,Jalons, Affectation, Tache, Visite
from compte.models import AppUser
from theapp.utils import get_client_ip

# Create your views here.


@login_required
def team_home(request):
    institutions = Institution.objects.all()
    projets = Projet.objects.all()
    nombre_projet = projets.count
    membres = AppUser.objects.exclude(is_superuser=True).count
    nbre_institution = institutions.count
    total_projets = projets.count()
    projets_termines = 0

    for projet in projets:
        jalons = Jalons.objects.filter(projet=projet)
        total_jalons = jalons.count()
        jalons_complets = jalons.filter(est_complet=True).count()

        if total_jalons > 0 and total_jalons == jalons_complets:
            projets_termines += 1

    if total_projets > 0:
        pourcentage_complets = (projets_termines / total_projets) * 100
    else:
        pourcentage_complets = 0

    ip = get_client_ip(request)
    visite = Visite.objects.create(ip=ip, page="Team_Home")
    visite.save()
    
    return render(request, 'team-home.html', {'institutions':institutions,
                                              'nbre_institution':nbre_institution,
                                              'nombre_projet':nombre_projet,
                                              'pourcentage_complets':pourcentage_complets,
                                              'membres':membres
                                              })

@login_required
def institutions(request):
    institutions = Institution.objects.all()
    return render(request, 'institutions.html', {'institutions':institutions})


@login_required
def institution_detail(request, id):
    institution = Institution.objects.get(id=id)
    projets = Projet.objects.filter(proprietaire=institution)
    membres = Affectation.objects.filter(institution=institution)
    count_membres = membres.count()
    return render(request, 'institution-detail.html', {'institution':institution,
                                                       'projets':projets,
                                                       'membres':membres,
                                                       'count_membres': count_membres})

@login_required
def membres(request):
    membres = AppUser.objects.exclude(is_superuser=True)
    return render(request, 'membres.html', {'membres': membres})


@login_required
def new_organisation(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        dirigeant = request.POST.get('dirigeant')
        photo_dirigeant = request.FILES.get('photo')
        description = request.POST.get('description')
        institution = Institution.objects.create(nom=nom,
                                                 dirigeant=dirigeant,
                                                 photo_dirigeant=photo_dirigeant,
                                                 description=description
                                                  )
        institution.save()
        return redirect('institutions')
    
@login_required
def new_projet(request, id):
    institution = Institution.objects.get(id=id)
    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description')
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        projet = Projet.objects.create(nom=nom,
                                       description=description,
                                       date_debut=date_debut,
                                       date_fin=date_fin,
                                       proprietaire=institution)
        projet.save()
        return redirect(institution_detail, id) 


def new_jalon(request, id):
    projet = Projet.objects.get(id=id)
    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description')
        date_echeance = request.POST.get('date')
        jalon =  Jalons.objects.create(projet=projet, nom=nom, description=description, date_echeance=date_echeance)
        jalon.save()
        return redirect('projet_detail', id)


@login_required
def search(request):
    query = request.GET.get('query')

    if query:
        projets = Projet.objects.filter(nom__icontains=query)

    return render(request, 'search.html', {'projets':projets})


@login_required
def projets_list(request):
    projets = Projet.objects.all()
    projets_data = []

    for projet in projets:
        jalons = Jalons.objects.filter(projet=projet)
        total_jalons = jalons.count()
        jalons_complets = jalons.filter(est_complet=True).count()

        if total_jalons > 0:
            pourcentage_complets = int((jalons_complets / total_jalons) * 100)
        else:
            pourcentage_complets = 0

        projets_data.append({
            'projet': projet,
            'pourcentage_complets': pourcentage_complets,
        })

    return render(request, 'projets.html', {
        'projets_data': projets_data
    })



@login_required
def projet_detail(request, id):
    projet = Projet.objects.get(id=id)
    jalons = Jalons.objects.filter(projet=projet)
    taches = Tache.objects.filter(jalon__in=jalons)
    total_jalons = jalons.count()
    jalons_complets = jalons.filter(est_complet=True).count()
    
    if total_jalons > 0:
        pourcentage_complets = int((jalons_complets / total_jalons) * 100)
    else:
        pourcentage_complets = 0

    return render(request, 'projet-detail.html', {
        'projet': projet,
        'jalons': jalons,
        'taches': taches,
        'pourcentage_complets': pourcentage_complets
    })


@login_required
def profil(request, id):
    membre = AppUser.objects.get(id=id)
    institutions = Institution.objects.all()
    is_affected = Affectation.objects.filter(agent=membre, active=True).exists
    return render(request, 'profil.html', {'membre':membre, 'institutions':institutions, 'is_affected':is_affected})

@login_required
def affectation(request, id):
    agent = AppUser.objects.get(id=id)
    if request.method == 'POST':
        institution_id = request.POST.get('id')
        institution = Institution.objects.get(id=institution_id)
        affectation = Affectation.objects.create(agent=agent, institution=institution, active=True)
        affectation.save()
        return redirect(institution_detail, institution_id)
    

@login_required
def jalon_fini(request, id):
    jalon = Jalons.objects.get(id=id)
    jalon.est_complet = True
    jalon.save()  # Assurez-vous de sauvegarder les changements
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    

def progression_institutions(request):
    institutions = Institution.objects.all()
    institution_data = []

    # Obtenir le trimestre à partir des paramètres de la requête
    trimestre = request.GET.get('trimestre', 'all')
    year = request.GET.get('year', None)

    noms_institutions = []
    total_projets_list = []
    pourcentage_termines_list = []

    for institution in institutions:
        projets = Projet.objects.filter(proprietaire=institution)
        
        if year:
            projets = projets.filter(date_debut__year=year)

        projets_termines = 0

        for projet in projets:
            if trimestre != 'all':
                debut_trimestre, fin_trimestre = get_trimestre_dates(int(trimestre), int(year))
                jalons = Jalons.objects.filter(projet=projet, date_echeance__range=(debut_trimestre, fin_trimestre))
            else:
                jalons = Jalons.objects.filter(projet=projet)

            total_jalons = jalons.count()
            jalons_complets = jalons.filter(est_complet=True).count()

            if total_jalons > 0 and total_jalons == jalons_complets:
                projets_termines += 1

        total_projets = projets.count()
        pourcentage_termines = (projets_termines / total_projets) * 100 if total_projets > 0 else 0

        noms_institutions.append(institution.nom)
        total_projets_list.append(total_projets)
        pourcentage_termines_list.append(pourcentage_termines)

        institution_data.append({
            'institution': institution,
            'total_projets': total_projets,
            'pourcentage_termines': pourcentage_termines
        })

    # Graphique en barres
    bar_fig = go.Figure([go.Bar(x=noms_institutions, y=total_projets_list)])
    bar_div = plot(bar_fig, output_type='div')

    # Graphique en donut
    donut_fig = go.Figure(data=[go.Pie(labels=noms_institutions, values=pourcentage_termines_list, hole=.3)])
    donut_div = plot(donut_fig, output_type='div')

    # Graphique en lignes (progression des projets terminés)
    line_fig = go.Figure(data=go.Scatter(x=noms_institutions, y=pourcentage_termines_list, mode='lines+markers'))
    line_div = plot(line_fig, output_type='div')

    return render(request, 'progressions.html', {
        'institution_data': institution_data,
        'bar_div': bar_div,
        'donut_div': donut_div,
        'line_div': line_div,
        'selected_trimestre': trimestre,
        'selected_year': year
    })

def get_trimestre_dates(trimestre, year):
    if trimestre == 1:
        return pd.Timestamp(year, 1, 1), pd.Timestamp(year, 3, 31)
    elif trimestre == 2:
        return pd.Timestamp(year, 4, 1), pd.Timestamp(year, 6, 30)
    elif trimestre == 3:
        return pd.Timestamp(year, 7, 1), pd.Timestamp(year, 9, 30)
    elif trimestre == 4:
        return pd.Timestamp(year, 10, 1), pd.Timestamp(year, 12, 31)


# API VIEW

@api_view(['GET'])
def api_projet_detail(request, id):
    try:
        projet = Projet.objects.get(id=id)
    except Projet.DoesNotExist:
        return Response(status=404, data={'message': 'Projet not found'})
    
    jalons = Jalons.objects.filter(projet=projet)
    taches = Tache.objects.filter(jalon__in=jalons)
    
    projet_serializer = ProjetSerializer(projet)
    jalons_serializer = JalonsSerializer(jalons, many=True)
    taches_serializer = TacheSerializer(taches, many=True)
    
    return Response({
        'projet': projet_serializer.data,
        'jalons': jalons_serializer.data,
        'taches': taches_serializer.data,
    })

class ProjetListCreate(generics.ListCreateAPIView):
    queryset = Projet.objects.all()
    serializer_class = ProjetSerializer

class JalonsListCreate(generics.ListCreateAPIView):
    queryset = Jalons.objects.all()
    serializer_class = JalonsSerializer

class TacheListCreate(generics.ListCreateAPIView):
    queryset = Tache.objects.all()
    serializer_class = TacheSerializer


class JalonsDetail(generics.RetrieveAPIView):
    queryset = Jalons.objects.all()
    serializer_class = JalonsSerializer

class TacheDetail(generics.RetrieveAPIView):
    queryset = Tache.objects.all()
    serializer_class = TacheSerializer






