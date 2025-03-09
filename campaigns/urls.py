from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    path('report/<int:campaign_id>/', views.report_phishing, name='report_phishing'),
    path('tutorial/<int:campaign_id>/', views.phishing_tutorial, name='phishing_tutorial'),
    path('dashboard/', views.report_dashboard, name='dashboard'),
    path('send/<int:campaign_id>/', views.send_campaign_emails, name='send_campaign_emails'),
]
