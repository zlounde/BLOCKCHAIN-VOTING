from django.urls import path  # ✅ Ensure correct import
from . import views  # ✅ Ensure correct import of views

# ✅ Ensure `urlpatterns` is properly defined
urlpatterns = [
    path("home/", views.home, name="home"),
    path("about/", views.about, name="About"),  # Fixed inconsistent name
    path("login/", views.user_login_view, name="login"),
    path("logout/", views.user_logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    
    path("", views.election_list, name="election_list"),
    path("elections/", views.elections, name="elections"),
    
    # Manage Elections
    path("manage-election/<int:title_id>/", views.view_candidates, name="manage_election"),
    path("election/<int:election_id>/", views.view_candidates, name="view_candidates"),
    path("election/<int:election_id>/vote/", views.vote, name="vote"),
    path("election/<int:election_id>/results/", views.results, name="results"),

    # Admin Section
    path("admin-section/", views.admin_section, name="admin_section"),
    path("add-candidate/<int:election_id>/", views.add_or_edit_candidate, name="add_candidate"),
    path("edit-candidate/<int:candidate_id>/", views.add_or_edit_candidate, name="edit_candidate"),
    path("delete-candidate/<int:candidate_id>/", views.delete_candidate, name="delete_candidate"),

    # Election Titles
    path("existing-elections/", views.existing_elections, name="existing_elections"),
    path("create-title/", views.create_title, name="create_title"),
    path("delete-election/<int:election_id>/", views.delete_election, name="delete_election"),
    path("election-detail/<int:election_id>/", views.election_detail, name="election_detail"),

    # Timer Page
    path("timer/", views.timer_page, name="timer_page"),
]
