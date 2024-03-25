# Create your views here.
from sqlite3 import IntegrityError

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.contrib import messages

from .forms import UserProfileForm
from .models import User, Question
from .utils import generate_multiplication_question


def index(request):
    return render(request, "index.html")


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            if user.first_login:
                # Set first_login to False
                user.first_login = False
                user.save()
                # Redirect to the edit profile page
                return redirect('edit_profile')
            else:
                # Redirect to the index page
                return redirect('index')
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")

        # Ensure password matches confirmation
        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            return redirect("index")  # Redirect to the index page after successful registration
        except IntegrityError:
            return render(request, "register.html", {
                "message": "An error occurred during registration."
            })
    else:
        return render(request, "register.html")


@login_required
def generate_question(request):
    user = request.user
    if user.level == 'beginner':
        min_value = 1
        max_value = 10
    elif user.level == 'medium':
        min_value = 10
        max_value = 20
    elif user.level == 'pro':
        min_value = 20
        max_value = 30
    question_text, correct_answer = generate_multiplication_question(min_value, max_value)
    question = Question.objects.create(question_text=question_text, correct_answer=correct_answer)
    return JsonResponse({'question_text': question.question_text, 'question_id': question.id})


from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Question

from django.contrib import messages
from django.shortcuts import redirect
from .models import Question


@login_required
def check_answer(request):
    if request.method == 'POST':
        question_id = request.POST.get('question_id')
        user_answer = request.POST.get('user_answer')

        # Check if the user provided an answer
        if user_answer.strip() == "":
            return JsonResponse({'error': 'Please provide an answer.'}, status=400)

        try:
            # Attempt to convert the user's answer to an integer
            user_answer_int = int(user_answer)

            # Answer is a number, proceed with checking
            question = Question.objects.get(pk=question_id)
            correct_answer = question.correct_answer

            if user_answer_int == correct_answer:
                # Correct answer
                user = request.user
                user.score += 1
                user.save()

                # Adjust user's level based on score (if needed)
                # Your level adjustment logic goes here
                if user.score >= 10 and user.level == 'beginner':
                    user.level = 'medium'
                elif user.score >= 20 and user.level == 'medium':
                    user.level = 'pro'
                elif user.score >= 30 and user.level == 'pro':  # Adding the missing logic here
                    user.level = 'pro'
                user.save()


                return JsonResponse({'correct': True, 'message': 'Congratulations! Your answer is correct.'})
            else:
                # Incorrect answer
                return JsonResponse({'correct': False, 'message': f'Incorrect answer. The correct answer is {correct_answer}.'})
        except ValueError:
            # User's answer is not a valid number
            return JsonResponse({'error': 'Please provide a valid number as the answer.'}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def scoreboard(request):
    users = User.objects.all()
    print("HI")
    return render(request, 'scoreboard.html', {'users': users})





@login_required
def profile(request):
    # Get the current authenticated user
    user = request.user

    # Create a context dictionary with the user's score
    context = {
        'user': user,
        'score': user.score,  # Assuming the user model has a score attribute
        #'level': user.level
    }

    # Check if the request is AJAX and return a JSON response if true
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'score': user.score,'level': user.level})

    # Render the profile.html template if it's a regular HTTP request
    return render(request, 'profile.html', context)

def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
    return render(request, 'edit_profile.html', {'form': form})
