"""
AMC MCP Server - Main server implementation
"""
import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import uuid

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    EmbeddedResource
)
from pydantic import BaseModel, Field


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    format: str  # "Standard", "IMAX", "3D", "Dolby"
    price: float

class Seat(BaseModel):
    seat_number: str
    row: str
    column: int
    is_available: bool
    price_tier: str  # "Standard", "Premium", "Recliner"

class Booking(BaseModel):
    booking_id: str
    showtime_id: str
    seats: List[str]
    user_id: str
    status: str  # "pending", "confirmed", "cancelled"
    total_price: float
    created_at: str

class Payment(BaseModel):
    payment_id: str
    booking_id: str
    amount: float
    payment_method: str
    status: str  # "pending", "success", "failed"
    receipt_url: Optional[str] = None


class AMCMCPServer:
    """AMC MCP Server implementation"""
    
    def __init__(self):
        self.server = Server("amc-mcp")
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.bookings: Dict[str, Booking] = {}
        self.payments: Dict[str, Payment] = {}
        self._load_mock_data()
        self._setup_handlers()
    
    def _load_mock_data(self):
        """Load mock data from JSON files"""
        try:
            with open(self.data_dir / "movies.json", "r") as f:
                self.movies = {m["movie_id"]: Movie(**m) for m in json.load(f)}
            
            with open(self.data_dir / "theaters.json", "r") as f:
                self.theaters = {t["theater_id"]: Theater(**t) for t in json.load(f)}
            
            with open(self.data_dir / "showtimes.json", "r") as f:
                self.showtimes = {s["showtime_id"]: Showtime(**s) for s in json.load(f)}
            
            with open(self.data_dir / "seats.json", "r") as f:
                self.seats_data = json.load(f)
                
        except Exception as e:
            logger.error(f"Error loading mock data: {e}")
            self.movies = {}
            self.theaters = {}
            self.showtimes = {}
            self.seats_data = {}
    
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="get_now_showing",
                        description="Returns a list of movies currently showing in a given city or ZIP code",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "location": {"type": "string", "description": "City, state or ZIP code"}
                            },
                            "required": ["location"]
                        }
                    ),
                    Tool(
                        name="get_recommendations",
                        description="Suggests movies based on mood, genre, or time preferences",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "genre": {"type": "string", "description": "Movie genre (optional)"},
                                "mood": {"type": "string", "description": "Mood description (optional)"},
                                "time_preference": {"type": "string", "description": "Time of day preference (optional)"}
                            }
                        }
                    ),
                    Tool(
                        name="get_showtimes",
                        description="Fetches available showtimes for a specific movie and location",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "movie_id": {"type": "string", "description": "Movie ID"},
                                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                                "location": {"type": "string", "description": "City, state or ZIP code"}
                            },
                            "required": ["movie_id", "date", "location"]
                        }
                    ),
                    Tool(
                        name="get_seat_map",
                        description="Displays available and reserved seats for a specific showtime",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "showtime_id": {"type": "string", "description": "Showtime ID"}
                            },
                            "required": ["showtime_id"]
                        }
                    ),
                    Tool(
                        name="book_seats",
                        description="Reserves selected seats for the user",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "showtime_id": {"type": "string", "description": "Showtime ID"},
                                "seats": {"type": "array", "items": {"type": "string"}, "description": "List of seat numbers (e.g., ['A5', 'A6'])"},
                                "user_id": {"type": "string", "description": "User identifier"}
                            },
                            "required": ["showtime_id", "seats", "user_id"]
                        }
                    ),
                    Tool(
                        name="process_payment",
                        description="Handles simulated payment transaction",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "booking_id": {"type": "string", "description": "Booking ID"},
                                "payment_method": {"type": "string", "description": "Payment method (card, cash, etc.)"},
                                "amount": {"type": "number", "description": "Payment amount"}
                            },
                            "required": ["booking_id", "payment_method", "amount"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(request: CallToolRequest) -> CallToolResult:
            """Handle tool calls"""
            try:
                if request.name == "get_now_showing":
                    return await self._get_now_showing(request.arguments)
                elif request.name == "get_recommendations":
                    return await self._get_recommendations(request.arguments)
                elif request.name == "get_showtimes":
                    return await self._get_showtimes(request.arguments)
                elif request.name == "get_seat_map":
                    return await self._get_seat_map(request.arguments)
                elif request.name == "book_seats":
                    return await self._book_seats(request.arguments)
                elif request.name == "process_payment":
                    return await self._process_payment(request.arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {request.name}")]
                    )
            except Exception as e:
                logger.error(f"Error calling tool {request.name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )
    
    async def _get_now_showing(self, args: Dict[str, Any]) -> CallToolResult:
        """Get movies currently showing in a location"""
        location = args.get("location", "")
        
        # Filter movies by location (simplified - match any theater in the area)
        showing_movies = []
        for movie in self.movies.values():
            # Simple mock logic - show all movies for any location
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
            "movies": showing_movies[:10]  # Limit to 10 movies
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    
    async def _get_recommendations(self, args: Dict[str, Any]) -> CallToolResult:
        """Get movie recommendations based on preferences"""
        genre = args.get("genre", "").lower()
        mood = args.get("mood", "").lower()
        
        recommendations = []
        for movie in self.movies.values():
            # Simple matching logic
            if genre and genre in movie.genre.lower():
                recommendations.append({
                    "movie_id": movie.movie_id,
                    "title": movie.title,
                    "genre": movie.genre,
                    "description": movie.description,
                    "rating": movie.rating
                })
            elif mood and (mood in movie.description.lower() or mood in movie.genre.lower()):
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
                for movie in list(self.movies.values())[:5]
            ]
        
        result = {
            "criteria": {"genre": genre, "mood": mood},
            "recommendations": recommendations[:5]
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    
    async def _get_showtimes(self, args: Dict[str, Any]) -> CallToolResult:
        """Get showtimes for a movie on a specific date and location"""
        movie_id = args.get("movie_id")
        date = args.get("date")
        location = args.get("location")
        
        if not movie_id or movie_id not in self.movies:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"error": "Invalid movie ID"}))]
            )
        
        movie = self.movies[movie_id]
        showtimes = []
        
        for showtime in self.showtimes.values():
            if showtime.movie_id == movie_id and showtime.date == date:
                theater = self.theaters.get(showtime.theater_id)
                if theater:
                    showtimes.append({
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
            "showtimes": showtimes
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    
    async def _get_seat_map(self, args: Dict[str, Any]) -> CallToolResult:
        """Get seat map for a showtime"""
        showtime_id = args.get("showtime_id")
        
        if not showtime_id or showtime_id not in self.showtimes:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"error": "Invalid showtime ID"}))]
            )
        
        # Get seats for this showtime (mock data)
        seats = self.seats_data.get(showtime_id, [])
        seat_map = []
        
        for seat_data in seats:
            # Check if seat is already booked
            is_booked = any(
                seat_data["seat_number"] in booking.seats and booking.status == "confirmed"
                for booking in self.bookings.values()
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
        
        showtime = self.showtimes[showtime_id]
        theater = self.theaters.get(showtime.theater_id)
        movie = self.movies.get(showtime.movie_id)
        
        result = {
            "showtime_id": showtime_id,
            "movie": movie.title if movie else "Unknown",
            "theater": theater.name if theater else "Unknown Theater",
            "date": showtime.date,
            "time": showtime.time,
            "seat_map": seat_map
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    
    async def _book_seats(self, args: Dict[str, Any]) -> CallToolResult:
        """Book seats for a showtime"""
        showtime_id = args.get("showtime_id")
        seats = args.get("seats", [])
        user_id = args.get("user_id")
        
        if not showtime_id or showtime_id not in self.showtimes:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"error": "Invalid showtime ID"}))]
            )
        
        if not seats or not user_id:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"error": "Seats and user_id are required"}))]
            )
        
        # Check seat availability
        unavailable_seats = []
        total_price = 0.0
        
        showtime_seats = self.seats_data.get(showtime_id, [])
        seat_lookup = {s["seat_number"]: s for s in showtime_seats}
        
        for seat_num in seats:
            # Check if seat exists
            if seat_num not in seat_lookup:
                unavailable_seats.append(f"{seat_num} (doesn't exist)")
                continue
            
            # Check if already booked
            is_booked = any(
                seat_num in booking.seats and booking.status == "confirmed"
                for booking in self.bookings.values()
                if booking.showtime_id == showtime_id
            )
            
            if is_booked:
                unavailable_seats.append(f"{seat_num} (already booked)")
            else:
                seat_price = seat_lookup[seat_num].get("price", 15.00)
                total_price += seat_price
        
        if unavailable_seats:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"error": f"Unavailable seats: {', '.join(unavailable_seats)}"}))]
            )
        
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
        
        self.bookings[booking_id] = booking
        
        showtime = self.showtimes[showtime_id]
        theater = self.theaters.get(showtime.theater_id)
        movie = self.movies.get(showtime.movie_id)
        
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
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    
    async def _process_payment(self, args: Dict[str, Any]) -> CallToolResult:
        """Process payment for a booking"""
        booking_id = args.get("booking_id")
        payment_method = args.get("payment_method")
        amount = args.get("amount")
        
        if not booking_id or booking_id not in self.bookings:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"error": "Invalid booking ID"}))]
            )
        
        booking = self.bookings[booking_id]
        
        if booking.status != "pending":
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"error": f"Booking status is {booking.status}, expected pending"}))]
            )
        
        if abs(amount - booking.total_price) > 0.01:  # Allow for small rounding differences
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"error": f"Amount mismatch. Expected ${booking.total_price:.2f}, got ${amount:.2f}"}))]
            )
        
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
        
        self.payments[payment_id] = payment
        
        # Update booking status
        booking.status = "confirmed"
        
        showtime = self.showtimes[booking.showtime_id]
        theater = self.theaters.get(showtime.theater_id)
        movie = self.movies.get(showtime.movie_id)
        
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
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Main entry point"""
    server = AMCMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()