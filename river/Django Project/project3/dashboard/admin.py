from django.contrib import admin
from .models import SummaryDashboard,IndividualDashboard, ShoppingComparison, AncillariesComparison,Benchmark

# Register your models here.
admin.site.register(SummaryDashboard)
admin.site.register(IndividualDashboard)
admin.site.register(ShoppingComparison)
admin.site.register(AncillariesComparison)
admin.site.register(Benchmark)
