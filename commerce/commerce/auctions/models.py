from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', related_name='watchlist_users')
    pass


class Listing(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=50, blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_listings')
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,  related_name='won_listings')

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
