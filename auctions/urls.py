from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("category/<int:category_id>", views.category, name="category"),
    path("auction/<int:auction_id>", views.auction, name="auction"),
    path("newlisting/", views.NewListing, name="newlisting"),
    path("comment/<int:auction_id>", views.NewComment, name="newcomment"),
    path("watchlist/<int:auction_id>", views.WatchList, name="watchlist"),
    path("watchlist/", views.GetWatchList, name="getwatchlist"),
    path("newbid/<int:auction_id>", views.Bidding, name="newbid"),
    path("closeauction/<int:auction_id>", views.CloseAuction, name="closeauction"),
  
]
