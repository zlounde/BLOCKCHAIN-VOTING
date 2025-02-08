from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from datetime import date
from django.http import JsonResponse
from .forms import *
from .models import Candidate 



def home(request):
    return render(request,"voting/student/home.html")

def About(request):
    return render(request,"voting/student/About.html")




@login_required
# Login View
def user_login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)  # This now refers to Django's built-in function
            # Redirect to the 'next' page or to the homepage
            next_page = request.GET.get('next', 'home')  # Default to home if 'next' is not provided
            return redirect(next_page)
    else:
        form = AuthenticationForm()

    return render(request, 'voting/student/login.html', {'form': form})



@login_required
def elections(request):
    return render(request,"voting/student/elections.html")

def viewcandidates(request):
    return render(request,"voting/student/viewcandidates.html")

def profile(request):
    return render(request,"voting/student/profile.html")

def logout(request):
    return render(request,"voting/student/logout.html")



def election_list(request):
    upcoming_elections = Election.objects.filter(status="Upcoming").order_by("date")
    ongoing_elections = Election.objects.filter(status="Ongoing").order_by("date")

    return render(request, "voting/student/elections.html", {
        "upcoming_elections": upcoming_elections,
        "ongoing_elections": ongoing_elections,
    })


# View candidates for an election
def view_candidates(request, election_id):
    election = get_object_or_404(election, id=election_id)
    candidates = election.candidates.all()
    return render(request, 'voting/view_candidates.html', {'election': election, 'candidates': candidates})

# Voting page
def vote(request, election_id):
    election = get_object_or_404(election, id=election_id)
    candidates = election.candidates.all()

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate')
        candidate = get_object_or_404(Candidate, id=candidate_id, election=election)
        Vote.objects.create(user=request.user, election=election, candidate=candidate)
        return redirect('results', election_id=election.id)

    return render(request, 'voting/vote.html', {'election': election, 'candidates': candidates})

# View results
def results(request, election_id):
    election = get_object_or_404(election, id=election_id)
    candidates = election.candidates.all()
    votes = {candidate.name: Vote.objects.filter(candidate=candidate).count() for candidate in candidates}
    return render(request, 'voting/results.html', {'election': election, 'votes': votes})


# ====================================================================================================================

def adminsection(request):
    return render (request,'voting/admin/admin.html')


def manage_elections(request):
    if request.method == "POST":
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_elections')  # Refresh the page after submission
    else:
        form = CandidateForm()

    return render(request, 'voting/admin/manage_elections.html', {'form': form})

def get_departments(request):
    departments = Department.objects.all()
    departments_list = [{'id': dept.id, 'name': dept.name} for dept in departments]
    return JsonResponse(departments_list, safe=False)

def get_candidates(request):
    candidates = Candidate.objects.all()
    candidates_list = [{
        'election_title': candidate.election_title.title,
        'name': candidate.name,
        'candidate_department': candidate.candidate_department.name if candidate.candidate_department else 'N/A',
        'agenda': candidate.agenda,
        'department': candidate.department.name if candidate.department else 'All (University-wide)',
        'id': candidate.id
    } for candidate in candidates]
    return JsonResponse(candidates_list, safe=False)

def existing_elections(request):
    candidates = Candidate.objects.all()
    existing_elections = ElectionTitle.objects.all()
    return render(request, 'voting/admin/existing_elections.html', 
                  {'candidates': candidates,'existing_elections':existing_elections,})




from django.shortcuts import render, redirect
from .models import ElectionTitle, School, Department
from .forms import ElectionTitleForm

def create_title(request):
    if request.method == "POST":
        form = ElectionTitleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('existing_elections')
    else:
        form = ElectionTitleForm()

    schools = School.objects.all()
    departments = Department.objects.all()    
    return render(request, 'voting/admin/create_title.html', {
        'form': form,
        'schools': schools,
        'departments': departments,    
    })


