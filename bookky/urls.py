from django.urls import path
from bookky import views, userviews, bookviews, socialview
from rest_framework import permissions

#url(r'^pnsApp/(?P<slug>[-a-zA-Z0-9_]+)$', views.pns_detail),
urlpatterns = [ #POST형식으로 바꿔야함
    path('user/signin', userviews.userSignIn), #POST
    path('user/signup', userviews.userSignUp), #POST
    path('user', userviews.user), #GET, DELETE, PUT
    path('user/email', userviews.checkEmail), #GET
    path('user/check', userviews.checkCode), #POST
    path('auth/refresh',userviews.refresh_token), #POST
    path('user/signout', userviews.signOut),#POST
    path('user/nickname', userviews.nicknameCheck), #GET
    path('test5', views.read_insert),
    path('test2/<slug:slug>', bookviews.book),
    path('test6', views.testAuthorization),
    path('test8', bookviews.bookUpdate),
    path('user/social/auth/google', socialview.socialCallbackGoogle)
]