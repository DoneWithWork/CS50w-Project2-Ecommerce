from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Auction, Bid, Comment
from django.contrib.auth.decorators import login_required

def index(request):
    auctions = Auction.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        "auctions": auctions
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html",{
        "categories": categories
    })

# get all auctions in a category
def category(request, category_id):
    auctions = Auction.objects.filter(category=category_id,is_active=True)
    # Create a list to hold auctions with their highest bids
    auctions_with_bids = []

    for auction in auctions:
        highest_bid = auction.get_highest_bid()
        auctions_with_bids.append({
            'auction': auction,
            'highest_bid': highest_bid
        })

    return render(request, "auctions/category.html", {
        "auctions_with_bids": auctions_with_bids
    })


@login_required(login_url='/login')
def NewListing(request):
    form = NewListingForm()
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            image = form.cleaned_data["image"]
            category = form.cleaned_data["category"]
            creator = request.user
            new_auction = Auction(title=title, description=description, starting_bid=starting_bid, image=image, category=category, creator=creator)
            new_auction.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/newlisting.html", {
            "form": form
        })


@login_required(login_url='/login')
def auction(request, auction_id):
    commentForm = NewCommentForm()
    auction = Auction.objects.get(id=auction_id)
    highest_bid = auction.get_highest_bid()
    comments = Comment.objects.filter(auction=auction)
    num_bids = auction.get_number_of_bids()

    # watchlist
    user = User.objects.get(id=request.user.id)
    bidForm = BidForm()
    watched = user.watchlist.filter(id=auction_id).exists()
    is_winner = auction.winner == user
    is_creator = (user == auction.creator)
    print(user)
    print(auction.creator)
    print(is_creator)
    return render(request, "auctions/auction.html", {
            "auction": auction,
            "highest_bid": highest_bid,
            "comments": comments,
            "commentForm": commentForm,
            "watched": watched,
            "bidForm": bidForm,
            "num_bids": num_bids,
            "creator": is_creator,
            "is_winner": is_winner
        })
    
@login_required(login_url='/login')
def CloseAuction(request, auction_id):
    auction = Auction.objects.get(id=auction_id)
    highestBidder = auction.get_highest_bid_object().user
    auction.winner = highestBidder
    auction.is_active = False
    auction.save()
    return HttpResponseRedirect(reverse("index"))

@login_required(login_url='/login')
def Bidding(request, auction_id):
    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.cleaned_data["bid"]
            user = User.objects.get(id=request.user.id)
            auction = Auction.objects.get(id=auction_id)
            highest_bid = auction.get_highest_bid()
            is_creator = (user == auction.creator)
            if bid <= highest_bid:
                commentForm = NewCommentForm()
                comments = Comment.objects.filter(auction=auction)
                watched = user.watchlist.filter(id=auction_id).exists()
                return render(request, "auctions/auction.html", {
                    "auction": auction,
                    "highest_bid": highest_bid,
                    "comments": comments,
                    "commentForm": commentForm,
                    "watched": watched,
                    "bidForm": form,
                    "is_creator": is_creator,
                    "error": "Bid must be higher than the current highest bid"
                })
            else:
                new_bid = Bid(user=user, bid_amount=bid, auction=auction)
                new_bid.save()
                return HttpResponseRedirect(reverse("auction", args=(auction_id,)))

@login_required(login_url='/login')
def NewComment(request, auction_id):
    form = NewCommentForm()
    if request.method == "POST":
        form = NewCommentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            user = request.user
            auction = Auction.objects.get(id=auction_id)
            new_comment = Comment(content=content, user=user, auction=auction)
            new_comment.save()
            return HttpResponseRedirect(reverse("auction", args=(auction_id,)))
    else:
        print("GET request rejected" )


def WatchList(request,auction_id):
    user = User.objects.get(id=request.user.id)
    if request.method == "POST":
       

        watched = user.watchlist.filter(id=auction_id).exists()
        if watched:
            user.watchlist.remove(auction_id)
        else:
            user.watchlist.add(auction_id)
        return HttpResponseRedirect(reverse("auction", args=(auction_id,)))
   
    
def GetWatchList(request):  
    user = User.objects.get(id=request.user.id)
    watchlist = user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })
# forms
class NewListingForm(forms.Form):
    title = forms.CharField(label="Title")
    description = forms.CharField(label="Description")
    starting_bid = forms.DecimalField(label="Starting Bid")
    image = forms.URLField(label="Image URL")
    category = forms.ModelChoiceField(queryset=Category.objects.all())

class NewCommentForm(forms.Form):
    content = forms.CharField(label="Comment",min_length=1, max_length=500)

class BidForm(forms.Form):
    bid = forms.DecimalField(label="Bid",min_value=0.01)