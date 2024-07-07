from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProjetSerializer, JalonsSerializer, TacheSerializer

from theapp.models import Institution, Projet,Jalons, Affectation, Tache
from compte.models import AppUser

# Create your views here.

@login_required
def team_home(request):
    institutions = Institution.objects.all()
    nbre_institution = institutions.count
    return render(request, 'team-home.html', {'institutions':institutions,
                                              'nbre_institution':nbre_institution
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
    return render(request, 'institution-detail.html', {'institution':institution,
                                                       'projets':projets,
                                                       'membres':membres})

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
    

# API 

@api_view(['GET'])
def projet_detail(request, id):
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






