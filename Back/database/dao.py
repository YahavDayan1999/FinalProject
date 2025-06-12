from bson import ObjectId
import random
import datetime
from database.database import db_client
from utils.password_encoder import PasswordEncoder
from data.show_data import *
from utils.jwt_handler import JWTHandler
from utils.bson_utils import convert_objectid


# Purchase DAO
class PurchaseDAO:
    def __init__(self, db):
        self.purchases = db["purchases"]
    
    def get_purchases(self, user_id: str):
        return list(self.purchases.find({"user": ObjectId(user_id)}))

    def get_show_purchases(self, show_id: str):
        return list(self.purchases.find({"concert": ObjectId(show_id)}))

    def get_venue_purchases(self, venue_id: str):
        return list(self.purchases.find({"venue": ObjectId(venue_id)}))


# DAO Classes
class UserDAO:
    def __init__(self, db):
        self.users = db["users"]
        self.purchases = db["purchases"]

    def register(self, user_data: UserCreate):
        user = {
            "name": user_data.name,
            "email": user_data.email,
            "password": PasswordEncoder.hash_password(user_data.password),
            "passport_id": user_data.passport_id,
            "admin": False,
            "purchases": [],
        }
        return self.users.insert_one(user).inserted_id

    def get_user_by_email(self, email: str):
        user = self.users.find_one({"email": email})
        return user

    def get_user_by_id(self, uid: str):
        user = self.users.find_one({"_id": ObjectId(uid)})
        return convert_objectid(user)

    def get_user_by_email_or_passport_id(self, email: str, passport_id: str):
        user = self.users.find_one(
            {"$or": [{"email": email}, {"passport_id": passport_id}]}
        )
        return user

    def login(self, login_data: LoginRequest):
        user = self.users.find_one(
            {
                "passport_id": login_data.passport_id,
                "password": PasswordEncoder.hash_password(login_data.password),
            }
        )
        if not user:
            raise ValueError("Incorrect credentials")
        token = JWTHandler.encode(
            {
                "passport_id": login_data.passport_id,
                "_id": str(user["_id"]),
                "is_admin": user.get("is_admin", False),
            }
        )
        return {"token": token}

    def list_users(self):
        users = list(self.users.find())
        for u in users:
            u["purchases"] = list(
                self.purchases.find({"_id": {"$in": u.get("purchases", [])}})
            )
        return users

    def add_purchase(self, purchase_data: ClientPurchase, user:any):
        user = self.users.find_one({"_id": ObjectId(user["_id"])})
        if not user:
            raise Exception("User not found")
        purchase_data = purchase_data.model_dump()
        show = shows_dao.get_by_id(str(purchase_data["concert_id"]))
        price = show["base_price"]
        purchase = {
            "user": user["_id"],
            "seats": purchase_data["seats"],
            "concert": ObjectId(purchase_data["concert_id"]),
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "card_number": purchase_data["card_number"],
            "expiry_date": purchase_data["expiry_date"],
            "cvv": purchase_data["cvv"],
        }
        purchase_id = self.purchases.insert_one(purchase).inserted_id
        total_sold = purchase_dao.get_show_purchases(str(purchase_data["concert_id"]))
        total_sold = sum(len(purchase["seats"]) for purchase in total_sold)
        venue = venues_dao.get_by_id(str(show["venue"]))
        cap = venue["seats"] * venue["rows"]
        demand = (total_sold / cap) * 100 if cap else 0
        if demand >= 90:
            price *= 1.4
        elif demand >= 75:
            price *= 1.2
        elif demand >= 50:
            price *= 1.1
        shows_dao.update_v2(str(purchase_data["concert_id"]), {"price": price})
        self.users.update_one(
            {"_id": user["_id"]}, {"$push": {"purchases": purchase_id}}
        )
        purchase["_id"] = str(purchase_id)
        return  {
            "purchase": convert_objectid(purchase),
            "price": price
        }
    
    def get_purchases(self, user_id: str):
        purchases = list(self.purchases.find({"user": ObjectId(user_id)}))
        return convert_objectid(purchases)

    def get_all_purchases(self):
        purchases = list(self.purchases.find())
        # Get all users once and create a lookup dictionary
        users = {str(user["_id"]): user for user in self.users.find()}
        
        # Add customer info to each purchase using the lookup dictionary
        for purchase in purchases:
            user_id = str(purchase["user"])
            if user_id in users:
                purchase["customer"] = {
                    "name": users[user_id]["name"],
                    "email": users[user_id]["email"],
                    "passport_id": users[user_id]["passport_id"]
                }
        return convert_objectid(purchases)

class VenueDAO:
    def __init__(self, db):
        self.venues = db["venues"]

    def create(self, venue_data: VenueCreate):
        # Check if a venue with the same name already exists (case-insensitive)
        existing_venue = self.venues.find_one(
            {"name": {"$regex": f"^{venue_data['name']}$", "$options": "i"}}
        )
        if existing_venue:
            raise ValueError(
                f"A venue with the name '{venue_data['name']}' already exists."
            )

        # Insert the new venue if no duplicate is found
        return self.venues.insert_one(
            {
                "name": venue_data["name"],
                "rows": venue_data["rows"],
                "seats": venue_data["seats"],
            }
        ).inserted_id

    def list_all(self):
        return list(self.venues.find())

    def get_by_id(self, venue_id):
        return self.venues.find_one({"_id": ObjectId(venue_id)})

    def update(self, venue_id, venue_data: VenueUpdate):
        return self.venues.update_one(
            {"_id": ObjectId(venue_id)}, 
            {"$set": {
                "name": venue_data.name,
                "capacity": venue_data.capacity,
                "rows": venue_data.rows,
                "seats": venue_data.seats
            }}
        )

    def delete(self, venue_id):
        # Check if there are concerts associated with this venue
        associated_concerts = shows_dao.shows.find_one({"venue": ObjectId(venue_id)})
        if associated_concerts:
            raise ValueError(
                f"Cannot delete venue with ID '{venue_id}' because it is associated with one or more concerts."
            )

        # Proceed to delete the venue if no associated concerts are found
        return self.venues.delete_one({"_id": ObjectId(venue_id)})


class ArtistDAO:
    def __init__(self, db):
        self.artists = db["artists"]

    def create(self, artist_data: ArtistCreate):
        # Check if an artist with the same name already exists (case-insensitive)
        existing_artist = self.artists.find_one(
            {"name": {"$regex": f"^{artist_data['name']}$", "$options": "i"}}
        )
        if existing_artist:
            raise ValueError(
                f"An artist with the name '{artist_data['name']}' already exists."
            )

        # Insert the new artist if no duplicate is found
        return self.artists.insert_one(
            {"name": artist_data["name"], "genre": artist_data["genre"]}
        ).inserted_id

    def list_all(self):
        return list(self.artists.find())

    def get_by_id(self, artist_id):
        return self.artists.find_one({"_id": ObjectId(artist_id)})

    def update(self, artist_id, artist_data: ArtistUpdate):
        return self.artists.update_one(
            {"_id": ObjectId(artist_id)},
            {"$set": {
                "name": artist_data["name"],
                "genre": artist_data["genre"]
            }},
        )

    def delete(self, artist_id):
        # Check if there are shows associated with this artist
        associated_shows = shows_dao.shows.find_one({"artist": ObjectId(artist_id)})
        if associated_shows:
            raise ValueError(
                f"Cannot delete artist with ID '{artist_id}' because they are associated with one or more shows."
            )

        # Proceed to delete the artist if no associated shows are found
        return self.artists.delete_one({"_id": ObjectId(artist_id)})


class ShowDAO:
    def __init__(self, db):
        self.shows = db["shows"]
        self.purchases = db["purchases"]

    def create(self, show_data: ShowCreate):
        show = {
            "artist": ObjectId(show_data["artist_id"]),
            "venue": ObjectId(show_data["venue_id"]),
            "price": show_data["price"],
            "base_price": show_data["price"],
            "date": show_data["date"],
        }
        return self.shows.insert_one(show).inserted_id

    def get_unavailable_seats(self, show_id: str):
         purchases = list(self.purchases.find({"concert": ObjectId(show_id)}))
         all_seats = []
         for purchase in purchases:
            all_seats.extend(list(map(lambda p : p["number"], purchase["seats"])))
         return all_seats

    def list_all(self):
        return list(self.shows.find())


    def get_by_id(self, show_id):
        return self.shows.find_one({"_id": ObjectId(show_id)})

    def update_v2(self, show_id, update_data: dict):
        return self.shows.update_one({"_id": ObjectId(show_id)}, {
            "$set": update_data
        })
    
    def update(self, show_id, show_data: ShowUpdate):
        update_data = {
            "artist": ObjectId(show_data["artist_id"]),
            "venue": ObjectId(show_data["venue_id"]),
            "price": show_data["price"],
            "date": show_data["date"],
        }
        return self.shows.update_one({"_id": ObjectId(show_id)}, {"$set": update_data})

    def delete(self, show_id):
        return self.shows.delete_one({"_id": ObjectId(show_id)})

purchase_dao = PurchaseDAO(db_client)
user_dao = UserDAO(db_client)
venues_dao = VenueDAO(db_client)
shows_dao = ShowDAO(db_client)
artists_dao = ArtistDAO(db_client)
