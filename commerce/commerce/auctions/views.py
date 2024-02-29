from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from pyexpat.errors import messages
from django.contrib import messages
from .forms import CreateListingForm
from .models import User, Listing, Bid, Comment


def index(request):
    current_date = timezone.now().date()
    print(current_date)
    # Filter listings where the date part of end_time is greater than the current date
    active_listingss = Listing.objects.filter(end_time__gt=current_date, is_active=True)

    return render(request, 'auctions/index.html', {'active_listings': active_listingss})


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
            print("Form errors:", form.errors)  # Print form errors for debugging
            return HttpResponseServerError("Form is not valid")  # Return an error response
    else:
        form = CreateListingForm()
    return render(request, 'auctions/create_listing.html', {'form': form})


# @login_required(login_url='login')
def listing_page(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    user = request.user
    watchlisted = user.watchlist.filter(pk=listing_id).exists() if user.is_authenticated else False
    is_seller = user.is_authenticated and user == listing.seller

    # Get all bids for the listing
    bids = listing.bid_set.all()
    print("Listing ID:", listing_id)
    print("Number of Bids:", bids.count())

    # Get the highest bid for the listing
    highest_bid = bids.order_by('-bid_amount').first()
    print(highest_bid)
    is_closed = (listing.end_time < timezone.now()) or not listing.is_active

    winner = None
    is_winner = False
    if is_closed and highest_bid:
        winner = highest_bid.bidder
        listing.winner = winner
        listing.save()
        is_winner = user.is_authenticated and highest_bid.bidder == user
        print(winner)

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
            bid_amount = request.POST.get('bid_amount')
            try:
                bid_amount = float(bid_amount)
                if bid_amount < listing.starting_bid:
                    messages.error(request, 'Bid must be at least as large as the starting bid.')
                elif bid_amount <= listing.current_bid:
                    messages.error(request, 'Bid must be greater than the current highest bid.')
                else:
                    # Create a new Bid object and save it to the database
                    new_bid = Bid.objects.create(listing=listing, bidder=user, bid_amount=bid_amount)
                    new_bid.save()

                    # Update the current bid of the listing
                    listing.current_bid = bid_amount
                    listing.save()
                    messages.success(request, 'Bid placed successfully!')
            except ValueError:
                messages.error(request, 'Invalid bid amount.')
            return redirect('listing_page', listing_id=listing_id)
        elif 'close_auction' in request.POST:
            if 'close_auction' in request.POST:
                # Check if the user is the seller and the auction is still open
                if is_seller and not is_closed:

                    # Close the auction
                    if highest_bid:
                        winner = highest_bid.bidder
                        listing.winner_id = winner
                        listing.save()
                        print(winner)
                        messages.success(request, f'Auction closed. Winner: {winner}')
                    else:
                        messages.info(request, 'Auction closed. No bids were placed.')
                    listing.is_active = False
                    listing.save()

                else:
                    messages.error(request, 'You cannot close the auction at this time.')
                return redirect('listing_page', listing_id=listing_id)
        elif 'post_comment' in request.POST:
            # Handle comment submission
            comment_text = request.POST.get('comment_text')
            if comment_text:
                comment = Comment(listing=listing, commenter=user, comment_text=comment_text)
                comment.save()
                messages.success(request, 'Your comment has been posted successfully!')
                return redirect('listing_page', listing_id=listing_id)
            else:
                messages.error(request, 'Please enter a valid comment!')

    comments = Comment.objects.filter(listing=listing)
    return render(request, 'auctions/listing_page.html', {
        'listing': listing,
        'watchlist': watchlisted,
        'is_winner': is_winner,
        'is_closed': is_closed,
        'winner': winner,
        'comments': comments
    })


# @login_required(login_url='login')
def watchlist(request):
    user = request.user
    watchlist_items = user.watchlist.all()
    return render(request, 'auctions/watchlist.html', {'watchlist_items': watchlist_items})


def categories(request):
    categories = Listing.objects.values_list('category', flat=True).distinct().order_by('category')
    return render(request, 'auctions/categories.html', {'categories': categories})


def category_listings(request, category):
    listings = Listing.objects.filter(category=category, end_time__gt=timezone.now())
    return render(request, 'auctions/category_listing.html', {'listings': listings, 'category': category})
