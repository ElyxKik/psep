from django.db import models



from django.db import models
from compte.models import AppUser


class Institution(models.Model):
    nom = models.CharField(max_length=256)
    dirigeant = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    photo_dirigeant = models.ImageField(upload_to='photos/', blank=True, null=True)
    created_time = models.DateTimeField(auto_now=True)
    membres_equipe = models.ManyToManyField(AppUser)

    def __str__(self):
        return self.nom
    

class Projet(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    proprietaire = models.ForeignKey(Institution, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nom


class Jalons(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date_echeance = models.DateField()
    est_complet = models.BooleanField(default=False)

    def __str__(self):
        return self.nom
    

class Tache(models.Model):
    jalon = models.ForeignKey(Jalons, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date_echeance = models.DateField()
    est_complet = models.BooleanField(default=False)

    def __str__(self):
        return self.nom
    

class KPI(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    valeur_cible = models.FloatField()
    valeur_actuelle = models.FloatField(default=0.0)
    description = models.TextField(blank=True)
    date_echeance = models.DateField()
    
    def __str__(self):
        return self.nom

    @property
    def progression(self):
        return (self.valeur_actuelle / self.valeur_cible) * 100 if self.valeur_cible else 0.0
    

class HistoriqueKPI(models.Model):
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE)
    valeur = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.kpi.nom} - {self.date}"
    

class Affectation(models.Model):
    agent = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    date = models.DateField(auto_now=True)



class Visite(models.Model):
    ip = models.CharField(max_length=100)
    page = models.CharField(max_length=20)
    date = models.DateTimeField(auto_now=True)

