from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from .models import *
from .forms import *

from django.shortcuts import render, redirect
from .models import User
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import School, Department

User = get_user_model()

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        reg_number = request.POST.get('reg_number')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        school_id = request.POST.get('school')
        department_id = request.POST.get('department')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        if User.objects.filter(reg_number=reg_number).exists():
            messages.error(request, "Registration number already exists.")
            return redirect('register')

        school = School.objects.get(id=school_id)
        department = Department.objects.get(id=department_id)

        user = User.objects.create_user(
            reg_number=reg_number,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            school=school,
            department=department
        )

        login(request, user)
        messages.success(request, "Registration Successful!")
        return redirect('home')

    schools = School.objects.all()
    departments = Department.objects.all()
    return render(request, 'voting/student/register.html', {'schools': schools, 'departments': departments})





from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

User = get_user_model()

def user_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)  # Correct usage of login()
            messages.success(request, "Login Successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid Email or Password")
            return redirect('login')

    return render(request, 'voting/student/login.html')


# Home Page
def home(request):
    return render(request, "voting/student/home.html")

# About Page
def about(request):
    return render(request, "voting/student/About.html")


# Logout View
def user_logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')  # Redirect to Login Page

# Profile Page
@login_required
def profile(request):
    user = request.user
    return render(request, "voting/student/profile.html", {'user': user})


# Elections Page
def elections(request):
    # return render(request, "voting/student/elections.html")
     # Fetch all created election titles with a timer set
    election_titles = ElectionTitle.objects.filter(start_time__isnull=False, end_time__isnull=False)
    
    # Filter elections based on their status
    upcoming_elections = [election for election in election_titles if election.status == 'Upcoming']
    ongoing_elections = [election for election in election_titles if election.status == 'Ongoing']
    completed_elections = [election for election in election_titles if election.status == 'Completed']

    return render(request, "voting/student/elections.html", {
        "election_titles": ElectionTitle.objects.filter(start_time__isnull=True),  # Only show titles without a timer
        "upcoming_elections": upcoming_elections,
        "ongoing_elections": ongoing_elections,
        "completed_elections": completed_elections,
    })

# vote page
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ElectionTitle, Candidate, Vote


def vote(request, title_id):
    title = get_object_or_404(ElectionTitle, id=title_id)
    candidates = Candidate.objects.filter(election_title=title)
    return render(request, 'voting/student/vote.html', {'title': title, 'candidates': candidates})

@login_required
def vote(request, election_id):
    election = get_object_or_404(ElectionTitle, id=election_id)
    candidates = Candidate.objects.filter(election_title=election)
    vote_instance = Vote.objects.filter(user=request.user, election=election).first()
    has_voted = vote_instance is not None

    if request.method == 'POST' and not has_voted:
        candidate_id = request.POST.get('selected_candidate')
        candidate = get_object_or_404(Candidate, id=candidate_id, election_title=election)
        
        # Create the vote
        Vote.objects.create(user=request.user, election=election, candidate=candidate)
        messages.success(request, "Vote cast successfully!")
        return redirect('home')

    total_votes = Vote.objects.filter(election=election).count()
    
    # Attach vote count to each candidate
    for candidate in candidates:
        candidate.vote_count = Vote.objects.filter(candidate=candidate).count()

    voted_candidate_id = vote_instance.candidate.id if has_voted else None

    return render(request, 'voting/student/vote.html', {
        'title': election,
        'candidates': candidates,
        'has_voted': has_voted,
        'voted_candidate_id': voted_candidate_id,
        'total_votes': total_votes,
    })

# view results
from django.utils import timezone


@login_required
def view_results(request, election_id):
    election = get_object_or_404(ElectionTitle, id=election_id)
    candidates = Candidate.objects.filter(election_title=election)
    total_votes = Vote.objects.filter(election=election).count()

    # Check if the election is Completed based on the time
    if election.end_time and election.end_time < timezone.now():
        # Calculate vote count for each candidate
        for candidate in candidates:
            candidate.vote_count = Vote.objects.filter(candidate=candidate).count()

        # Sort candidates by vote count (Descending Order)
        candidates = sorted(candidates, key=lambda x: x.vote_count, reverse=True)

        # Pass the highest vote count to the template
        highest_votes = candidates[0].vote_count if candidates else 0

        return render(request, 'voting/student/results.html', {
            'title': election,
            'candidates': candidates,
            'total_votes': total_votes,
            'highest_votes': highest_votes
        })
    else:
        messages.error(request, "Results are not available. The election is still ongoing or upcoming.")
        return redirect('home')





# View Candidates Page
def view_candidates(request, title_id):
    title = get_object_or_404(ElectionTitle, id=title_id)
    candidates = Candidate.objects.filter(election_title=title)
    return render(request, 'voting/admin/view_candidates.html', {'title': title, 'candidates': candidates})

# User Profile Page
def profile(request):
    return render(request, "voting/student/profile.html")

# Display Upcoming & Ongoing Elections
# def election_list(request):
#     upcoming_elections = Election.objects.filter(status="Upcoming").order_by("start_time")
#     ongoing_elections = Election.objects.filter(status="Ongoing").order_by("start_time")
#     return render(request, "voting/student/elections.html", {
#         "upcoming_elections": upcoming_elections,
#         "ongoing_elections": ongoing_elections,
#     }) 

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import ElectionTitle
from datetime import datetime

def timer_page(request):
    if request.method == "POST":
        title_id = request.POST.get("title")
        start_time_str = request.POST.get("start_time")
        end_time_str = request.POST.get("end_time")

        # Convert the strings to datetime objects
        start_time_naive = datetime.fromisoformat(start_time_str)
        end_time_naive = datetime.fromisoformat(end_time_str)

        # Make the datetimes timezone-aware
        start_time = timezone.make_aware(start_time_naive)
        end_time = timezone.make_aware(end_time_naive)

        # Get the election and update its start_time and end_time
        election = ElectionTitle.objects.get(id=title_id)
        election.start_time = start_time
        election.end_time = end_time
        election.save()  # The status will be updated dynamically

        messages.success(request, "Election timer set successfully!")
        return redirect("timer_page")

    # Fetch all created election titles with a timer set
    election_titles = ElectionTitle.objects.filter(start_time__isnull=False, end_time__isnull=False)
    
    # Filter elections based on their status
    upcoming_elections = [election for election in election_titles if election.status == 'Upcoming']
    ongoing_elections = [election for election in election_titles if election.status == 'Ongoing']
    completed_elections = [election for election in election_titles if election.status == 'Completed']

    return render(request, "voting/admin/timer.html", {
        "election_titles": ElectionTitle.objects.filter(start_time__isnull=True),  # Only show titles without a timer
        "upcoming_elections": upcoming_elections,
        "ongoing_elections": ongoing_elections,
        "completed_elections": completed_elections,
    })

def election_detail(request, election_id):
    election = get_object_or_404(ElectionTitle, id=election_id)
    return render(request, 'voting/admin/election_detail.html', {'election': election})

# Vote for a Candidate
# @login_required
# def vote(request, election_id):
#     election = get_object_or_404(Election, id=election_id)
#     candidates = election.candidates.all()

#     if request.method == 'POST':
#         candidate_id = request.POST.get('candidate')
#         candidate = get_object_or_404(Candidate, id=candidate_id, election=election)

#         if Vote.objects.filter(user=request.user, election=election).exists():
#             messages.error(request, "You have already voted in this election.")
#             return redirect('election_list')

#         Vote.objects.create(user=request.user, election=election, candidate=candidate)
#         messages.success(request, "Vote cast successfully!")
#         return redirect('results', election_id=election.id)

#     return render(request, 'voting/vote.html', {'election': election, 'candidates': candidates})

# View Election Results
# def results(request, election_id):
#     election = get_object_or_404(Election, id=election_id)
#     candidates = election.candidates.all()
#     votes = {candidate.name: Vote.objects.filter(candidate=candidate).count() for candidate in candidates}
#     return render(request, 'voting/results.html', {'election': election, 'votes': votes})

# Admin Section
def admin_section(request):
    return render(request, 'voting/admin/admin.html')

# Add or Edit a Candidate to an Election Title
def add_or_edit_candidate(request, election_id=None, candidate_id=None):
    election = get_object_or_404(ElectionTitle, id=election_id) if election_id else None
    candidate = get_object_or_404(Candidate, id=candidate_id) if candidate_id else None

    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            candidate = form.save(commit=False)
            if election:
                candidate.election_title = election
            candidate.save()
            messages.success(request, "Candidate saved successfully!")
            return redirect('election_detail', election_id=candidate.election_title.id)

    else:
        form = CandidateForm(instance=candidate)

    return render(request, 'voting/admin/add_candidate.html', {'form': form, 'election': election})

# Delete Candidate
def delete_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    election_id = candidate.election_title.id

    if request.method == 'POST':
        candidate.delete()
        messages.success(request, 'Candidate deleted successfully!')
    
    return redirect('election_detail', election_id=election_id)

# Get Departments Data (API)
def get_departments(request):
    departments = Department.objects.all()
    data = [{'id': dept.id, 'name': dept.name} for dept in departments]
    return JsonResponse(data, safe=False)

# Get Candidates Data (API)
def get_candidates(request):
    candidates = Candidate.objects.select_related('election_title', 'candidate_department', 'department').all()
    data = [
        {
            'election_title': candidate.election_title.name,
            'name': candidate.name,
            'candidate_department': candidate.candidate_department.name if candidate.candidate_department else 'N/A',
            'agenda': candidate.agenda,
            'department': candidate.department.name if candidate.department else 'All (University-wide)',
            'id': candidate.id
        } for candidate in candidates
    ]
    return JsonResponse(data, safe=False)

# List Existing Elections
def existing_elections(request):
    elections = ElectionTitle.objects.all()
    return render(request, 'voting/admin/existing_elections.html', {'existing_elections': elections})

# Create Election Title
def create_title(request):
    if request.method == "POST":
        form = ElectionTitleForm(request.POST)
        if form.is_valid():
            form.save()  # Save the election title without start_time and end_time
            messages.success(request, "Election title created successfully!")
            return redirect('existing_elections')
    else:
        form = ElectionTitleForm()

    return render(request, 'voting/admin/create_title.html', {
        'form': form,
        'schools': School.objects.all(),
        'departments': Department.objects.all(),
    })  

# Delete an Election Title
def delete_election(request, election_id):
    election = get_object_or_404(ElectionTitle, id=election_id)

    if request.method == 'POST':
        election.delete()
        messages.success(request, 'Election deleted successfully!')
    
    return redirect('existing_elections')

# Election Details Page
def election_detail(request, election_id):
    election = get_object_or_404(ElectionTitle, id=election_id)
    candidates = Candidate.objects.filter(election_title=election)
    return render(request, 'voting/admin/election_detail.html', {'election': election, 'candidates': candidates})
