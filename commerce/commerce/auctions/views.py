from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from pyexpat.errors import messages

from .forms import CreateListingForm
from .models import User, Listing, Bid


def index(request):
    return render(request, "auctions/index.html")


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

def create_listing(request):
    if request.method == 'POST':
        form = CreateListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            return redirect('active_listings')  # Redirect to active listings page
    else:
        form = CreateListingForm()
    return render(request, 'create_listing.html', {'form': form})

def active_listings(request):
    active_listings = Listing.objects.filter(end_time__gt=timezone.now())  # Filter active listings
    return render(request, 'active_listings.html', {'active_listings': active_listings})

@login_required (login_url='login')
def listing_page(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    user = request.user
    watchlisted = user.watchlist.filter(pk=listing_id).exists() if user.is_authenticated else False

    if request.method == 'POST':
        if 'add_watchlist' in request.POST:
            if not watchlisted:
                user.watchlist.add(listing)
                messages.success(request, 'Listing added to watchlist!')
            else:
                messages.error(request, 'Listing already on watchlist!')
            return redirect('listing_page', listing_id=listing_id)
        elif 'remove_watchlist' in request.POST:
            if watchlisted:
                user.watchlist.remove(listing)
                messages.success(request, 'Listing removed from watchlist!')
            else:
                messages.error(request, 'Listing not on watchlist!')
            return redirect('listing_page', listing_id=listing_id)
        elif 'place_bid' in request.POST:
            bid_amount = float(request.POST['bid_amount'])
            if bid_amount >= listing.starting_bid and bid_amount > listing.current_bid:
                bid = Bid(listing=listing, bidder=user, bid_amount=bid_amount)
                bid.save()
                listing.current_bid = bid_amount
                listing.save()
                messages.success(request, 'Bid placed successfully!')
            else:
                messages.error(request, 'Invalid bid!')
            return redirect('listing_page', listing_id=listing_id)
        elif 'close_auction' in request.POST:
            if user == listing.seller:
                winning_bid = listing.bid_set.order_by('-bid_amount').first()
                if winning_bid:
                    messages.success(request, f'Auction closed. Winner: {winning_bid.bidder}')
                else:
                    messages.info(request, 'Auction closed. No bids were placed.')
                listing.delete()
                return redirect('active_listings')

    comments = listing.comment_set.all()
    return render(request, 'listing_page.html', {
        'listing': listing,
        'watchlisted': watchlisted,
        'comments': comments
    })

@login_required (login_url='login')
def watchlist(request):
    user = request.user
    watchlist_items = user.watchlist.all()
    return render(request, 'watchlist.html', {'watchlist_items': watchlist_items})

def categories(request):
    categories = Listing.objects.values_list('category', flat=True).distinct().order_by('category')
    return render(request, 'categories.html', {'categories': categories})

def category_listings(request, category):
    listings = Listing.objects.filter(category=category, end_time__gt=timezone.now())
    return render(request, 'category_listings.html', {'listings': listings, 'category': category})