from django.contrib import admin
from .models import *

# Register other models
admin.site.register(User)
admin.site.register(Candidate)
admin.site.register(School)
admin.site.register(Department) 
admin.site.register(Vote) 

from django.contrib import admin
from .models import ElectionTitle

class ElectionTitleAdmin(admin.ModelAdmin):
    list_display = ('title', 'school', 'department', 'start_time', 'end_time', 'get_status')

    def get_status(self, obj):
        """
        Custom method to display the status in the admin interface.
        """
        return obj.status

    get_status.short_description = 'Status'  # Column header in the admin list view
    get_status.admin_order_field = 'start_time'  # Allow sorting by start_time

admin.site.register(ElectionTitle, ElectionTitleAdmin)