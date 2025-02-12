from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from .models import *
from .forms import *

# Home Page
def home(request):
    return render(request, "voting/student/home.html")

# About Page
def about(request):
    return render(request, "voting/student/about.html")

# User Login View
def user_login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'voting/student/login.html', {'form': form})

# User Logout View
def user_logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

# Elections Page
def elections(request):
    return render(request, "voting/student/elections.html")

# View Candidates Page
def view_candidates(request, title_id):
    title = get_object_or_404(ElectionTitle, id=title_id)
    candidates = Candidate.objects.filter(election_title=title)
    return render(request, 'voting/admin/view_candidates.html', {'title': title, 'candidates': candidates})

# User Profile Page
def profile(request):
    return render(request, "voting/student/profile.html")

# Display Upcoming & Ongoing Elections
def election_list(request):
    upcoming_elections = Election.objects.filter(status="Upcoming").order_by("start_time")
    ongoing_elections = Election.objects.filter(status="Ongoing").order_by("start_time")
    return render(request, "voting/student/elections.html", {
        "upcoming_elections": upcoming_elections,
        "ongoing_elections": ongoing_elections,
    })

# Set Election Timer
def timer_page(request):
    if request.method == "POST":
        title_id = request.POST.get("title")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        election = get_object_or_404(ElectionTitle, id=title_id)
        election.start_time = start_time
        election.end_time = end_time

        # Automatically update the election status
        election.status = "Upcoming" if election.start_time and election.end_time else "Draft"
        election.save()

        messages.success(request, "Election timer set successfully!")
        return redirect("timer_page")

    # Fetch all created election titles
    election_titles = ElectionTitle.objects.all()
    return render(request, "voting/admin/timer.html", {"election_titles": election_titles})

# Vote for a Candidate
@login_required
def vote(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    candidates = election.candidates.all()

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate')
        candidate = get_object_or_404(Candidate, id=candidate_id, election=election)

        if Vote.objects.filter(user=request.user, election=election).exists():
            messages.error(request, "You have already voted in this election.")
            return redirect('election_list')

        Vote.objects.create(user=request.user, election=election, candidate=candidate)
        messages.success(request, "Vote cast successfully!")
        return redirect('results', election_id=election.id)

    return render(request, 'voting/vote.html', {'election': election, 'candidates': candidates})

# View Election Results
def results(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    candidates = election.candidates.all()
    votes = {candidate.name: Vote.objects.filter(candidate=candidate).count() for candidate in candidates}
    return render(request, 'voting/results.html', {'election': election, 'votes': votes})

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
            form.save()
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
