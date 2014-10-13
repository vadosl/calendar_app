from django.contrib import admin
from .models import Entry

# Register your models here.
### Admin

class EntryAdmin(admin.ModelAdmin):
    #list_display = ["creator", "date", "title", "snippet"]
    #search_fields = ["title", "snippet"]
    #list_filter = ["creator"]
    pass

admin.site.register(Entry, EntryAdmin)