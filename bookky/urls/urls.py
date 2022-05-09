from django.urls import path
from bookky.views import views, userviews, bookviews, socialview, userfunctionviews, communityviews, reviewviews
from rest_framework import permissions

#url(r'^pnsApp/(?P<slug>[-a-zA-Z0-9_]+)$', views.pns_detail),
urlpatterns = [ #POST형식으로 바꿔야함
    path('home',userfunctionviews.getHomeData), #GET
    path('myprofile', userfunctionviews.getMyProfileData), #GET
    path('user/signin', userviews.userSignIn), #POST
    path('user/signup', userviews.userSignUp), #POST
    path('user', userviews.user), #GET, DELETE, PUT
    path('user/email', userviews.checkEmail), #GET
    path('user/check', userviews.checkCode), #POST
    path('user/signout', userviews.signOut),#POST
    path('user/nickname', userviews.nicknameCheck), #GET
    path('user/favoritebook', userfunctionviews.favoriteBook), #POST, DELETE
    path('user/tag',userfunctionviews.updateBoundary), #pPUT
    path('user/social/auth/google', socialview.socialCallbackGoogle),
    path('books/detail/<slug:slug>', bookviews.book), #GET
    path('books/tag/<slug:slug>',bookviews.getBooksByTag),
    path('books/reviews/<int:pk>',reviewviews.bookReviews),
    path('auth/refresh',userviews.refresh_token), #POST,
    path('tags', userfunctionviews.getTags),
    path('books/search', bookviews.bookSearch),
    path('review/<int:pk>',reviewviews.reviews),
    path('review/like/<int:pk>',reviewviews.reviewLike),
    path('test8', userfunctionviews.getMoreTag),
    path('community/postlist/<slug:slug>', communityviews.getCommunityPostList), #GET
    path('community/postdetail/<slug:slug1>/<slug:slug2>', communityviews.getCommunityPostdetail), #GET
    path('community/writepost/<slug:slug>', communityviews.writeCommunityPost), #POST
    path('community/writecomment/<slug:slug>', communityviews.writeCommunityComment), #POST
    path('community/deltepost/<slug:slug>', communityviews.delteCommunityPost), #DELETE
    path('community/deltecomment/<slug:slug>', communityviews.delteCommunityComment), #DELETE
    path('community/modifypost/<slug:slug>', communityviews.modifyCommunityPost), #PUT
]