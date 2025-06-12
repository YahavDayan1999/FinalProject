from pydantic import BaseModel
from typing import Dict, List

shows = []
clients: Dict[str, dict] = {}
purchases: Dict[str, dict] = {}
generated_ids = set()

class Client(BaseModel):
    name: str
    email: str
    password: str
    passport_id: str
    is_admin: bool = False

class LoginRequest(BaseModel):
    passport_id: str
    password: str


class Seat(BaseModel):
    row: int
    number: int

class ClientPurchase(BaseModel):
    seats: List[Seat]
    concert_id: str
    card_number: str
    expiry_date: str
    cvv: str

class Venue(BaseModel):
    name: str
    capacity: int

class Artist(BaseModel):
    name: str
    genre: str

class Show(BaseModel):
    artist_id: str
    venue_id: str
    price: float
    date: str


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    passport_id: str


class VenueCreate(BaseModel):
    name: str
    rows: int
    seats: int

class VenueUpdate(BaseModel):
    name: str
    capacity: int
    rows: int
    seats: int

class ArtistCreate(BaseModel):
    name: str
    genre: str

class ArtistUpdate(BaseModel):
    name: str
    genre: str

class ShowCreate(BaseModel):
    artist_id: str
    venue_id: str
    price: float
    date: str

class ShowUpdate(BaseModel):
    artist_id: str
    venue_id: str
    price: float
    date: str
