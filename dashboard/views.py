from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from home.models import DareExchange
from django.contrib.auth.models import User
from django.db.models import Count, Case, When, IntegerField

@login_required
def dashboard(request):
    user = request.user
    
    # Get all dares for the current user
    user_dares = DareExchange.objects.filter(user=user)
    
    # Calculate statistics
    total_dares = user_dares.count()
    
    # Since your model doesn't have a status field, we'll use deadline to determine completion
    # You might want to add a status field or completion field later
    current_date = timezone.now().date()
    
    # For now, let's assume dares past deadline without images are incomplete
    # and dares with images are completed (you can modify this logic)
    completed_dares = user_dares.filter(dare_image__isnull=False).count()
    pending_dares = total_dares - completed_dares
    
    # Get recent dares (last 5)
    recent_dares = user_dares.order_by('-id')[:5]
    
    # Calculate leaderboard rank (based on number of completed dares)
    # Get all users with their completed dare counts
    
    user_rankings = User.objects.annotate(
        completed_count=Count(
            Case(
                When(dareexchange__dare_image__isnull=False, then=0),
                output_field=IntegerField()
            )
        )
    ).order_by('-completed_count', 'id')
    
    # Find current user's rank
    leaderboard_rank = 1
    for index, ranked_user in enumerate(user_rankings, 1):
        if ranked_user.id == user.id:
            leaderboard_rank = index
            break
    
    # Get user's basic info (assuming you have these fields in User model or related profile)
    # If you don't have phone_number in User model, you'll need to get it from DareExchange
    user_phone = None
    if user_dares.exists():
        user_phone = user_dares.first().phone_number
    
    context = {
        'student': {
            'first_name': user.first_name or user.username,
            'phone_number': user_phone or 'Not provided'
        },
        'total_dares': total_dares,
        'completed_dares': completed_dares,
        'pending_dares': pending_dares,
        'leaderboard_rank': leaderboard_rank,
        'recent_dares': recent_dares,
    }
    
    return render(request, 'dashboard/index.html', context)