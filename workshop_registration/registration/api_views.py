# registration/api_views.py

from django.http import JsonResponse
from .location_models import District, State  # Import your models


from .models import WorkshopPricing

def get_districts(request):
    """Returns a JSON response with all districts"""
    districts = list(District.objects.values_list("name", flat=True))
    return JsonResponse(districts, safe=False)

def get_relevant_districts(request):
    """Returns a JSON response with districts for the selected state"""
    state_id = request.GET.get("state_id")
    
    if not state_id:
        return JsonResponse({"error": "State ID is required"}, status=400)

    try:
        districts = District.objects.filter(state_id=state_id).values("id", "name")
        return JsonResponse({"districts": list(districts)})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_states(request):
    """Returns a JSON response with all states"""
    states = list(State.objects.values_list("name", flat=True))
    return JsonResponse(states, safe=False)

# api_views.py




def get_workshop_details(request):
    """Fetches the workshop details (start date, end date, fee) for a selected registration type."""
    registration_type_id = request.GET.get('registration_type_id')

    if not registration_type_id:
        return JsonResponse({'error': 'Registration type ID is required'}, status=400)

    try:
        # Fetch the workshop pricing for the given registration type
        workshop_pricing = WorkshopPricing.objects.get(workshop_name_id=registration_type_id, is_alive=True)

        # Create the response data structure
        workshop_details = {
            'start_date': workshop_pricing.workshop_start_date,
            'end_date': workshop_pricing.workshop_end_date,
            'early_bird_price': workshop_pricing.early_bird_price,
            'regular_price': workshop_pricing.regular_price,
            'aimer_member_price': workshop_pricing.aimer_member_price,
            'cut_off_date': workshop_pricing.cut_off_date,
            'is_open_for_all': workshop_pricing.is_open_for_all,
            'brochure_link': workshop_pricing.brochure_link,
        }

        return JsonResponse(workshop_details)

    except WorkshopPricing.DoesNotExist:
        return JsonResponse({'error': 'Workshop pricing not found for the selected registration type'}, 
                            status=404)


