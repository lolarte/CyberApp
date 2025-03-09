from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Campaign, PhishingTestLog
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.models import CustomUser


@login_required
def report_phishing(request, campaign_id):
    # Record that the user reported the phishing email
    campaign = get_object_or_404(Campaign, id=campaign_id)
    PhishingTestLog.objects.create(user=request.user, campaign=campaign, action='reported')
    return render(request, 'campaigns/report_success.html', {'campaign': campaign})

@login_required
def phishing_tutorial(request, campaign_id):
    # Record that the user clicked on the phishing link
    campaign = get_object_or_404(Campaign, id=campaign_id)
    PhishingTestLog.objects.create(user=request.user, campaign=campaign, action='clicked')
    # Render a simple tutorial page explaining the phishing risks
    return render(request, 'campaigns/tutorial.html', {'campaign': campaign})

@staff_member_required
def report_dashboard(request):
    # Aggregate logs per campaign and per action type
    campaign_stats = PhishingTestLog.objects.values('campaign__title', 'action').annotate(count=Count('id'))
    return render(request, 'campaigns/dashboard.html', {'campaign_stats': campaign_stats})

@staff_member_required
def send_campaign_emails(request, campaign_id):
    """
    Sends emails for a campaign.
    Filters recipients by the campaign's specified groups and uses a randomly selected email template.
    """
    campaign = get_object_or_404(Campaign, id=campaign_id)
    
    # Get recipients: select users whose built-in groups intersect with the campaign's groups.
    # Note: CustomUser (derived from AbstractUser) already has a ManyToMany field 'groups'.
    recipients = list(
        CustomUser.objects.filter(groups__in=campaign.groups.all()).distinct()
            .values_list('email', flat=True)
    )
    
    if not recipients:
        messages.error(request, "No users found in the specified groups for this campaign.")
        return redirect('campaigns:dashboard')
    
    # Get campaign templates
    campaign_templates = list(campaign.templates.all())
    if not campaign_templates:
        messages.error(request, "No email templates are associated with this campaign.")
        return redirect('campaigns:dashboard')
    
    num_sent = 0
    for user_email in recipients:
        template = random.choice(campaign_templates)
        subject = template.subject  # From the chosen email template
        message = template.body     # Email body from the template
        from_email = 'no-reply@cyberapp.com'
        try:
            send_mail(subject, message, from_email, [user_email], fail_silently=False)
            num_sent += 1
        except Exception as e:
            messages.error(request, f"Error sending email to {user_email}: {str(e)}")
    
    messages.success(request, f"Successfully sent emails to {num_sent} recipients for campaign '{campaign.title}'.")
    return redirect('campaigns:dashboard')