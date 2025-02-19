from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

@staff_member_required  # ✅ Ensures only staff users can access
def admin_dashboard(request):
    """Render the custom admin dashboard for staff users."""
    return render(request, "admin_dashboard.html")
