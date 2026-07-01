from django.shortcuts import render, redirect
from .models import DareExchange
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import google.generativeai as genai
from django.conf import settings
import traceback

# Configure Gemini AI
genai.configure(api_key=settings.GEMINI_API_KEY)

def analyze_dare_with_gemini(dare_text):
    """Analyze dare using Gemini AI for content moderation and enhancement"""
    model = genai.GenerativeModel('models/gemini-2.0-flash')

    prompt = f"""
    Analyze this dare: "{dare_text}"
    1. Is it abusive, illegal, or extremely hard? (Reply 'Yes' or 'No')
    2. If 'No', rewrite it to make it more creative and exciting.
    """

    response = model.generate_content(prompt)
    print("Full Gemini Response:", response)
    reply = response.candidates[0].content.parts[0].text.strip()
    return reply

# Create your views here.
def home(request):
    return render(request, "home/home.html")

#==========DARES=============================================
@login_required
def dares(request):
    dares = DareExchange.objects.filter(user=request.user)
    # dares = DareExchange.objects.all().order_by("id")

    parameters = {
        "dares": dares
    }
    return render(request, "home/dares.html", parameters)

#=======================dARE KO AI SE ANALYSIS ========================
@login_required
def create_dare(request):
    if request.method == "POST":
        user_name = request.POST.get("name")
        user_email = request.POST.get("email")
        user_phone_number = request.POST.get("phone_number")
        user_deadline = request.POST.get("deadline")
        user_dare = request.POST.get("dare")

        # DARE EMPTY TO NHI HAI
        if not user_dare or not user_dare.strip():
            parameters = {
                'error': 'Dare cannot be empty!'
            }
            return render(request, "home/create_dare.html", parameters)

        # DARE KO GEMINI SE ANALYSIS
        try:
            ai_reply = analyze_dare_with_gemini(user_dare)
            print("AI Reply:", ai_reply)

            # REJECTED DARE CHECKING
            is_rejected = "Yes" in ai_reply.split('\n')[0]
            if is_rejected:
                parameters = {
                    'error': 'This dare is not allowed! It may be abusive, illegal, or extremely difficult.',
                    'name': user_name,
                    'email': user_email,
                    'phone_number': user_phone_number,
                    'deadline': user_deadline,
                    'dare': user_dare
                }
                return render(request, "home/create_dare.html", parameters)

            # ENHANCED DARE FROM AI
            enhanced_dare = user_dare  
            ai_lines = ai_reply.split('\n')
            if len(ai_lines) > 1:
                enhanced_dare = ai_lines[1].strip()
                # NUMBER HTADENA
                if enhanced_dare.startswith('2.'):
                    enhanced_dare = enhanced_dare[2:].strip()

            # Create new dare with enhanced content
            new_dare = DareExchange(
                name=user_name,
                email=user_email,
                phone_number=user_phone_number,
                deadline=user_deadline,
                dare=enhanced_dare, 
                user=request.user
            )

            new_dare.save()
            print("New dare added successfully with AI enhancement!")

            return redirect("dares")

        except Exception as e:
            print("Gemini API Error:", e)
            traceback.print_exc()
            parameters = {
                'error': 'Something went wrong with AI analysis. Please try again.',
                'name': user_name,
                'email': user_email,
                'phone_number': user_phone_number,
                'deadline': user_deadline,
                'dare': user_dare
            }
            return render(request, "home/create_dare.html", parameters)

    return render(request, "home/create_dare.html")

#==========DELETE A DARE=====================================
@login_required
def delete_dare(request, id):
    try:
        dare = DareExchange.objects.get(id=id, user=request.user)
        dare.delete()
        print("Dare deleted successfully!")
    except DareExchange.DoesNotExist:
        print("Dare not found or permission denied")
    
    return redirect("dares")

#==========Edit Dare with AI Analysis=========================================
@login_required
def edit_dare(request, id):
    try:
        dare = DareExchange.objects.get(id=id, user=request.user) 
    except DareExchange.DoesNotExist:
        return redirect("dares")

    if request.method == "POST":
        user_dare = request.POST.get("dare")
        
    #===DARE EMPTY TO NHI======
        if not user_dare or not user_dare.strip():
            parameters = {
                "dare": dare,
                'error': 'Dare cannot be empty!'
            }
            return render(request, "home/edit_dare.html", parameters)

        # Analyze edited dare with Gemini AI
        try:
            ai_reply = analyze_dare_with_gemini(user_dare)
            print("AI Reply for edit:", ai_reply)

            # Check if dare is rejected
            is_rejected = "Yes" in ai_reply.split('\n')[0]
            if is_rejected:
                parameters = {
                    "dare": dare,
                    'error': 'This dare is not allowed! It may be abusive, illegal, or extremely difficult.'
                }
                return render(request, "home/edit_dare.html", parameters)

            # Get the enhanced dare from AI
            enhanced_dare = user_dare 
            ai_lines = ai_reply.split('\n')
            if len(ai_lines) > 1:
                enhanced_dare = ai_lines[1].strip()
                # NUMBER HTADO
                if enhanced_dare.startswith('2.'):
                    enhanced_dare = enhanced_dare[2:].strip()

            # Update dare with AI-
            dare.name = request.POST.get("name")
            dare.email = request.POST.get("email")
            dare.phone_number = request.POST.get("phone_number")
            dare.deadline = request.POST.get("deadline")
            dare.dare = enhanced_dare  
            
            dare.is_edited = True
            dare.save()

            print("Dare updated successfully with AI enhancement!")
            return redirect("dares")

        except Exception as e:
            print("Gemini API Error during edit:", e)
            traceback.print_exc()
            parameters = {
                "dare": dare,
                'error': 'Something went wrong with AI analysis. Please try again.'
            }
            return render(request, "home/edit_dare.html", parameters)

    parameters = {
        "dare": dare
    }
    return render(request, "home/edit_dare.html", parameters)