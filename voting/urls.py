from django.urls import path
from . import views
from .views import existing_elections

urlpatterns=[
    path("home/", views.home,name="home"),
    path("About/", views.About, name="About"),
    path("login/", views.user_login_view, name="login"),
    path("elections/", views.elections, name="elections"),
    path("viewcandidates/", views.viewcandidates, name="viewcandidates"), 
    path("profile/", views.profile, name="profile"),
    path("logout/", views.logout, name="logout"),
    
    path('', views.election_list, name='election_list'),
    path('<int:election_id>/candidates/', views.view_candidates, name='view_candidates'),
    path('<int:election_id>/vote/', views.vote, name='vote'),
    path('<int:election_id>/results/', views.results, name='results'),


    path("admin-section/", views.adminsection,name="adminsection"),
    path('manage_elections/', views.manage_elections, name='manage_elections'),
    path('api/departments/', views.get_departments, name='get_departments'),
    path('api/candidates/', views.get_candidates, name='get_candidates'),
    path('existing-elections/', existing_elections, name='existing_elections'),
    path('create-title/', views.create_title, name='create_title'),

]
