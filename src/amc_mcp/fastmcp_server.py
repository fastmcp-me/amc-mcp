"""
AMC MCP Server - FastMCP Implementation
A comprehensive movie booking server using FastMCP
"""
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("amc-mcp")

# Data models
class Movie(BaseModel):
    movie_id: str
    title: str
    rating: str
    duration: int  # minutes
    genre: str
    description: str
    poster_url: str

class Theater(BaseModel):
    theater_id: str
    name: str
    address: str
    city: str
    state: str
    zip_code: str

class Showtime(BaseModel):
    showtime_id: str
    movie_id: str
    theater_id: str
    date: str
    time: str
    format: str
    price: float

class Booking(BaseModel):
    booking_id: str
    showtime_id: str
    seats: List[str]
    user_id: str
    status: str
    total_price: float
    created_at: str

class Payment(BaseModel):
    payment_id: str
    booking_id: str
    amount: float
    payment_method: str
    status: str
    receipt_url: Optional[str] = None

# Global state
movies: Dict[str, Movie] = {}
theaters: Dict[str, Theater] = {}
showtimes: Dict[str, Showtime] = {}
seats_data: Dict[str, List[Dict]] = {}
bookings: Dict[str, Booking] = {}
payments: Dict[str, Payment] = {}

def load_mock_data():
    """Load mock data from JSON files"""
    global movies, theaters, showtimes, seats_data
    
    try:
        # Get the data directory path
        data_dir = Path(__file__).parent.parent.parent / "data"
        logger.info(f"Loading data from: {data_dir}")
        
        with open(data_dir / "movies.json", "r") as f:
            movies_list = json.load(f)
            movies = {m["movie_id"]: Movie(**m) for m in movies_list}
        
        with open(data_dir / "theaters.json", "r") as f:
            theaters_list = json.load(f)
            theaters = {t["theater_id"]: Theater(**t) for t in theaters_list}
        
        with open(data_dir / "showtimes.json", "r") as f:
            showtimes_list = json.load(f)
            showtimes = {s["showtime_id"]: Showtime(**s) for s in showtimes_list}
        
        with open(data_dir / "seats.json", "r") as f:
            seats_data = json.load(f)
        
        logger.info(f"Loaded {len(movies)} movies, {len(theaters)} theaters, {len(showtimes)} showtimes")
    except Exception as e:
        logger.error(f"Error loading mock data: {e}")

# Load data on module import
load_mock_data()


def _get_now_showing(location: str) -> str:
    """
    Returns a list of movies currently showing in a given city or ZIP code.
    
    Args:
        location: City, state or ZIP code (e.g., "Boston, MA")
    
    Returns:
        JSON string with list of movies
    """
    showing_movies = []
    for movie in movies.values():
        movie_data = {
            "movie_id": movie.movie_id,
            "title": movie.title,
            "rating": movie.rating,
            "duration": movie.duration,
            "genre": movie.genre,
            "description": movie.description
        }
        showing_movies.append(movie_data)
    
    result = {
        "location": location,
        "movies": showing_movies[:10]
    }
    
    return json.dumps(result, indent=2)


@mcp.tool()
def get_now_showing(location: str) -> str:
    """
    Returns a list of movies currently showing in a given city or ZIP code.
    
    Args:
        location: City, state or ZIP code (e.g., "Boston, MA")
    
    Returns:
        JSON string with list of movies
    """
    return _get_now_showing(location)


def _get_recommendations(
    genre: Optional[str] = None,
    mood: Optional[str] = None,
    time_preference: Optional[str] = None
) -> str:
    """Get movie recommendations based on preferences"""
    recommendations = []
    
    genre_lower = genre.lower() if genre else ""
    mood_lower = mood.lower() if mood else ""
    
    for movie in movies.values():
        if genre_lower and genre_lower in movie.genre.lower():
            recommendations.append({
                "movie_id": movie.movie_id,
                "title": movie.title,
                "genre": movie.genre,
                "description": movie.description,
                "rating": movie.rating
            })
        elif mood_lower and (mood_lower in movie.description.lower() or mood_lower in movie.genre.lower()):
            recommendations.append({
                "movie_id": movie.movie_id,
                "title": movie.title,
                "genre": movie.genre,
                "description": movie.description,
                "rating": movie.rating
            })
    
    if not recommendations and not genre and not mood:
        # Return top picks if no specific criteria
        recommendations = [
            {
                "movie_id": movie.movie_id,
                "title": movie.title,
                "genre": movie.genre,
                "description": movie.description,
                "rating": movie.rating
            }
            for movie in list(movies.values())[:5]
        ]
    
    result = {
        "criteria": {"genre": genre, "mood": mood, "time_preference": time_preference},
        "recommendations": recommendations[:5]
    }
    
    return json.dumps(result, indent=2)


@mcp.tool()
def get_recommendations(
    genre: Optional[str] = None,
    mood: Optional[str] = None,
    time_preference: Optional[str] = None
) -> str:
    """
    Suggests movies based on mood, genre, or time preferences.
    
    Args:
        genre: Movie genre (optional, e.g., "action", "comedy")
        mood: Mood description (optional, e.g., "exciting", "romantic")
        time_preference: Time of day preference (optional, e.g., "evening")
    
    Returns:
        JSON string with movie recommendations
    """
    return _get_recommendations(genre, mood, time_preference)



def _get_showtimes(movie_id: str, date: str, location: str) -> str:
    """Internal implementation of get_showtimes"""
    if not movie_id or movie_id not in movies:
        return json.dumps({"error": "Invalid movie ID"})
    
    movie = movies[movie_id]
    showtime_list = []
    
    for showtime in showtimes.values():
        if showtime.movie_id == movie_id and showtime.date == date:
            theater = theaters.get(showtime.theater_id)
            if theater:
                showtime_list.append({
                    "showtime_id": showtime.showtime_id,
                    "theater_name": theater.name,
                    "theater_address": theater.address,
                    "time": showtime.time,
                    "format": showtime.format,
                    "price": showtime.price
                })
    
    result = {
        "movie": {"id": movie.movie_id, "title": movie.title},
        "date": date,
        "location": location,
        "showtimes": showtime_list
    }
    
    return json.dumps(result, indent=2)


@mcp.tool()
def get_showtimes(movie_id: str, date: str, location: str) -> str:
    """
    Fetches available showtimes for a specific movie and location.
    
    Args:
        movie_id: Movie ID (e.g., "mv001")
        date: Date in YYYY-MM-DD format (e.g., "2025-10-28")
        location: City, state or ZIP code
    
    Returns:
        JSON string with available showtimes
    """
    return _get_showtimes(movie_id, date, location)




def _get_seat_map(showtime_id: str) -> str:
    """Internal implementation of get_seat_map"""
    if not showtime_id or showtime_id not in showtimes:
        return json.dumps({"error": "Invalid showtime ID"})
    
    # Get seats for this showtime
    seats = seats_data.get(showtime_id, [])
    seat_map = []
    
    for seat_data in seats:
        # Check if seat is already booked
        is_booked = any(
            seat_data["seat_number"] in booking.seats and booking.status == "confirmed"
            for booking in bookings.values()
            if booking.showtime_id == showtime_id
        )
        
        seat_map.append({
            "seat_number": seat_data["seat_number"],
            "row": seat_data["row"],
            "column": seat_data["column"],
            "is_available": not is_booked,
            "price_tier": seat_data["price_tier"],
            "price": seat_data.get("price", 15.00)
        })
    
    showtime = showtimes[showtime_id]
    theater = theaters.get(showtime.theater_id)
    movie = movies.get(showtime.movie_id)
    
    result = {
        "showtime_id": showtime_id,
        "movie": movie.title if movie else "Unknown",
        "theater": theater.name if theater else "Unknown Theater",
        "date": showtime.date,
        "time": showtime.time,
        "seat_map": seat_map
    }
    
    return json.dumps(result, indent=2)


@mcp.tool()
def get_seat_map(showtime_id: str) -> str:
    """
    Displays available and reserved seats for a specific showtime.
    
    Args:
        showtime_id: Showtime ID (e.g., "st001")
    
    Returns:
        JSON string with seat availability map
    """
    return _get_seat_map(showtime_id)




def _book_seats(showtime_id: str, seats: List[str], user_id: str) -> str:
    """Internal implementation of book_seats"""
    if not showtime_id or showtime_id not in showtimes:
        return json.dumps({"error": "Invalid showtime ID"})
    
    if not seats or not user_id:
        return json.dumps({"error": "Seats and user_id are required"})
    
    # Check seat availability
    unavailable_seats = []
    total_price = 0.0
    
    showtime_seats = seats_data.get(showtime_id, [])
    seat_lookup = {s["seat_number"]: s for s in showtime_seats}
    
    for seat_num in seats:
        # Check if seat exists
        if seat_num not in seat_lookup:
            unavailable_seats.append(f"{seat_num} (doesn't exist)")
            continue
        
        # Check if already booked
        is_booked = any(
            seat_num in booking.seats and booking.status == "confirmed"
            for booking in bookings.values()
            if booking.showtime_id == showtime_id
        )
        
        if is_booked:
            unavailable_seats.append(f"{seat_num} (already booked)")
        else:
            seat_price = seat_lookup[seat_num].get("price", 15.00)
            total_price += seat_price
    
    if unavailable_seats:
        return json.dumps({"error": f"Unavailable seats: {', '.join(unavailable_seats)}"})
    
    # Create booking
    booking_id = str(uuid.uuid4())
    booking = Booking(
        booking_id=booking_id,
        showtime_id=showtime_id,
        seats=seats,
        user_id=user_id,
        status="pending",
        total_price=total_price,
        created_at=datetime.now().isoformat()
    )
    
    bookings[booking_id] = booking
    
    showtime = showtimes[showtime_id]
    theater = theaters.get(showtime.theater_id)
    movie = movies.get(showtime.movie_id)
    
    result = {
        "booking_id": booking_id,
        "status": "pending",
        "movie": movie.title if movie else "Unknown",
        "theater": theater.name if theater else "Unknown Theater",
        "date": showtime.date,
        "time": showtime.time,
        "seats": seats,
        "total_price": total_price
    }
    
    return json.dumps(result, indent=2)


@mcp.tool()
def book_seats(showtime_id: str, seats: List[str], user_id: str) -> str:
    """
    Reserves selected seats for the user.
    
    Args:
        showtime_id: Showtime ID (e.g., "st001")
        seats: List of seat numbers (e.g., ["A5", "A6"])
        user_id: User identifier
    
    Returns:
        JSON string with booking confirmation
    """
    return _book_seats(showtime_id, seats, user_id)


def _process_payment(booking_id: str, payment_method: str, amount: float) -> str:
    """Internal implementation of process_payment"""
    if not booking_id or booking_id not in bookings:
        return json.dumps({"error": "Invalid booking ID"})
    
    booking = bookings[booking_id]
    
    if booking.status != "pending":
        return json.dumps({"error": f"Booking status is {booking.status}, expected pending"})
    
    if abs(amount - booking.total_price) > 0.01:
        return json.dumps({"error": f"Amount mismatch. Expected ${booking.total_price:.2f}, got ${amount:.2f}"})
    
    # Simulate payment processing (always succeeds in mock)
    payment_id = str(uuid.uuid4())
    receipt_url = f"https://amc.com/receipts/{payment_id}"
    
    payment = Payment(
        payment_id=payment_id,
        booking_id=booking_id,
        amount=amount,
        payment_method=payment_method,
        status="success",
        receipt_url=receipt_url
    )
    
    payments[payment_id] = payment
    
    # Update booking status
    booking.status = "confirmed"
    
    showtime = showtimes[booking.showtime_id]
    theater = theaters.get(showtime.theater_id)
    movie = movies.get(showtime.movie_id)
    
    result = {
        "payment_id": payment_id,
        "payment_status": "success",
        "booking_id": booking_id,
        "receipt_url": receipt_url,
        "confirmation": {
            "movie": movie.title if movie else "Unknown",
            "theater": theater.name if theater else "Unknown Theater",
            "date": showtime.date,
            "time": showtime.time,
            "seats": booking.seats,
            "total_paid": amount
        }
    }
    
    return json.dumps(result, indent=2)


@mcp.tool()
def process_payment(booking_id: str, payment_method: str, amount: float) -> str:
    """
    Handles simulated payment transaction.
    
    Args:
        booking_id: Booking ID from book_seats
        payment_method: Payment method (e.g., "card", "cash")
        amount: Payment amount in USD
    
    Returns:
        JSON string with payment confirmation and receipt
    """
    return _process_payment(booking_id, payment_method, amount)


def main():
    """Run the MCP server"""
    logger.info("Starting AMC MCP Server with FastMCP...")
    mcp.run()


if __name__ == "__main__":
    main()
