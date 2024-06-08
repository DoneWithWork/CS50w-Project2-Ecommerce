from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Max  # Import Max

class User(AbstractUser):
    watchlist = models.ManyToManyField('Auction', related_name='watched_auctions', blank=True)
    def __str__(self) -> str:
        return f"{self.username}"

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50,unique=True)
    description = models.CharField(max_length=500)
    def __str__(self) -> str:
        return f"{self.name} | {self.description}"

class Auction(models.Model):
    id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auctions')
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='auctions', blank=True, null=True)
    image = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='won_auction', blank=True, null=True)
    def __str__(self) -> str:
        return f"{self.title} | {self.description} | {self.starting_bid} | {self.category} | {self.image} | {self.is_active}"
    def get_highest_bid(self):
        highest_bid = self.bids.aggregate(Max('bid_amount'))['bid_amount__max']
        return highest_bid if highest_bid is not None else self.starting_bid

    def get_number_of_bids(self):
        return self.bids.count()
    def get_highest_bid_object(self):
        # Retrieve the Bid object with the highest bid_amount for this auction
        highest_bid = self.bids.order_by('-bid_amount').first()
        if highest_bid:
            return highest_bid
        else:
            return None
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
 

    def __str__(self) -> str:
        return f"{self.user} | {self.bid_amount} | {self.auction}"

class Comment(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='comments') 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=500)

    def __str__(self) -> str:
        return f"{self.auction} | {self.user} | {self.content}"