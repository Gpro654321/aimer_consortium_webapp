import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from django.db.models import Count, Q


from registration.models import WorkshopPricing, ParticipantRegistration

# ✅ Function to allow only staff/superusers
def admin_required(user):
    return user.is_staff or user.is_superuser

# ✅ Admin Dashboard (Home Page)
# ✅ Admin Dashboard (Home Page)
@login_required(login_url='/admin/login/')  # Explicitly redirect to Django admin login
@user_passes_test(admin_required, login_url='/admin/login/')
def admin_dashboard(request):
    # Fetch all workshops
    #workshops = WorkshopPricing.objects.all().order_by('-is_alive', '-workshop_start_date')

    workshops = WorkshopPricing.objects.annotate(
        participant_count=Count(
            'workshop_name__participantregistration',
            filter=Q(workshop_name__participantregistration__payment_status=True)  # ✅ Filter only successful payments
            )
    ).order_by('-is_alive', '-workshop_start_date')

    
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        workshops = workshops.filter(workshop_name__name__icontains=search_query)


    # Pagination (10 per page)
    paginator = Paginator(workshops, 10)
    page = request.GET.get('page')
    workshops = paginator.get_page(page)

    return render(request, './admin_dashboard.html', {'workshops': workshops, 'search_query': search_query})




# Check if user is an admin
def admin_required(user):
    return user.is_staff or user.is_superuser

# ✅ workshop chart (Home Page)
@login_required(login_url='/admin/login/')  # Explicitly redirect to Django admin login
@user_passes_test(admin_required, login_url='/admin/login/')
def workshop_statewise_chart(request, workshop_id):
    workshop = get_object_or_404(WorkshopPricing, id=workshop_id)

    # Get state-wise participant counts
    statewise_counts = (
        ParticipantRegistration.objects
        .filter(registration_type=workshop.workshop_name,payment_status=True)
        .values('participant__state__name')
        .annotate(count=Count('participant__state'))
    )

    # Convert queryset to JSON-friendly format
    state_data = [
        {"state": item['participant__state__name'], "count": item['count']}
        for item in statewise_counts
    ]

    return JsonResponse({"statewise_counts": state_data})


# ✅ Workshop Dashboard (Detailed View)
@login_required(login_url='/admin/login/')
@user_passes_test(admin_required, login_url='/admin/login/')
def workshop_dashboard(request, workshop_id):
    workshop = get_object_or_404(WorkshopPricing, id=workshop_id)
    
    # Total Participants
    total_participants = ParticipantRegistration.objects.filter(
        registration_type=workshop.workshop_name,
        payment_status=True
        ).count()

    # State-wise Participant Count
    statewise_counts = (
        ParticipantRegistration.objects
        .filter(registration_type=workshop.workshop_name, payment_status=True)
        .values('participant__state__name')
        .annotate(count=Count('participant__state'))
        .order_by('-count')
    )

    # Fetch Participants with Search
    search_query = request.GET.get('search', '')
    participants = ParticipantRegistration.objects.filter(
            registration_type=workshop.workshop_name,
            payment_status=True
            ).select_related('participant')

        

    if search_query:
        participants = participants.filter(
            Q(participant__name__icontains=search_query) |  # ✅ Search by Name
            Q(participant__email__icontains=search_query) |  # ✅ Search by Email
            Q(participant__mobile_number__icontains=search_query) |  # ✅ Search by Mobile Number
            Q(participant__participantregistration__registration_type__name__icontains=search_query)  # ✅ Search by Other Workshops
        )


    # Fetch other workshops for each participant
    participant_other_workshops = {
        reg.participant.id: ", ".join([
            other_reg.registration_type.name for other_reg in 
            ParticipantRegistration.objects.filter(
                participant=reg.participant,
                payment_status=True
            ).exclude(registration_type=workshop.workshop_name)
        ])
        for reg in participants
    }


    # Paginate results (10 per page)
    paginator = Paginator(participants, 10)
    page_number = request.GET.get('page')
    registrations = paginator.get_page(page_number)

    context = {
        'workshop': workshop,
        'total_participants': total_participants,
        'statewise_counts': list(statewise_counts),
        'registrations': registrations,
        'participant_other_workshops': participant_other_workshops
    }

    return render(request, 'workshop_dashboard.html', context)


# ✅ CSV Export Function

@login_required
@user_passes_test(admin_required)
def export_workshop_csv(request, workshop_id):
    """ Export workshop participant details as CSV """
    workshop = get_object_or_404(WorkshopPricing, id=workshop_id)
    
    # Fetch related participant data
    participants = ParticipantRegistration.objects.filter(
        registration_type=workshop.workshop_name,
        payment_status=True
    ).select_related('participant')


    # Prepare list for CSV export
    data = []

    for participant in participants:
        # Fetch other workshops (excluding the current one)
        other_workshops = ParticipantRegistration.objects.filter(
            participant=participant.participant,
            payment_status=True
        ).exclude(registration_type=workshop.workshop_name).values_list('registration_type__name', flat=True)

        data.append({
            'Name': participant.participant.name,
            'Mobile Number': participant.participant.mobile_number,
            'Email': participant.participant.email,
            'Institute': participant.participant.institute,
            'District': participant.participant.district.name if participant.participant.district else '',
            'State': participant.participant.state.name if participant.participant.state else '',
            'Registration Type': participant.registration_type.name,
            'Razorpay Payment ID': participant.razorpay_payment_id,
            'Amount Paid': participant.amount_paid,
            'Payment Status': "Paid" if participant.payment_status else "Not Paid",
            'Registered At': participant.registered_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Other Workshops': ", ".join(other_workshops) if other_workshops else "-"  # Include other workshops
        })

    # Convert list to DataFrame
    df = pd.DataFrame(data)



    # Create HTTP response with CSV content
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{workshop.workshop_name.name}_participants.csv"'

    # Convert DataFrame to CSV and write to response
    df.to_csv(response, index=False)

    return response

