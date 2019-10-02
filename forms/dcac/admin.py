from django.contrib import admin

from .models import *

admin.site.register(Student)
admin.site.register(ACGReimbursementForm)
admin.site.register(Organization)
admin.site.register(AcademicYear)
admin.site.register(OrganizationAdministrator)
admin.site.register(ACGReimbursementFormItemEntry)
admin.site.register(AdminUser)
admin.site.register(ACGReimbursementFormReceiptEntry)

admin.site.site_header = "DCAC Reimbursement"
admin.site.site_title = "DCAC Reimbursement"
admin.site.index_title = "Backend Administration"