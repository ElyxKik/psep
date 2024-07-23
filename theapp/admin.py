from django.contrib import admin

from theapp.models import Institution, Projet, Affectation, Jalons, Visite


class OrganistationAdmin(admin.ModelAdmin):
    list_display = ('nom', 'dirigeant', 'photo_dirigeant', 'description')


class ProjetAdmin(admin.ModelAdmin):
    list_display = ('nom',)


class JalonAdmin(admin.ModelAdmin):
    list_display = ('nom',)


class AffectationAdmin(admin.ModelAdmin):
    list_display=('agent', 'institution', 'active')


class VisiteAdmin(admin.ModelAdmin):
    list_display = ('ip', 'page', 'date')



admin.site.register(Institution, OrganistationAdmin)
admin.site.register(Projet, ProjetAdmin)
admin.site.register(Affectation, AffectationAdmin)
admin.site.register(Jalons, JalonAdmin)
admin.site.register(Visite, VisiteAdmin)
