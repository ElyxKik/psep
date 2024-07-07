from django.contrib import admin

from compte.models import AppUser



class AppUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')



admin.site.register(AppUser, AppUserAdmin)
