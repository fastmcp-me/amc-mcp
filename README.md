# AMC MCP Server 🎬

An Model Context Protocol (MCP) server that provides a comprehensive movie booking experience for AMC Theatres. This server enables conversational AI assistants to help users discover movies, find showtimes, book seats, and process payments through a simple API interface.

## Features ✨

- **Movie Discovery**: Browse currently showing movies and get personalized recommendations
- **Showtime Lookup**: Find available showtimes by location, date, and movie
- **Seat Selection**: View interactive seat maps and check availability
- **Booking Management**: Reserve seats with real-time availability checking
- **Payment Processing**: Handle mock payment transactions with confirmation receipts
- **Multi-location Support**: Search across multiple AMC theater locations

## Quick Start 🚀

### Prerequisites

- Python 3.8+
- Docker (optional, for containerized deployment)

### Installation

#### Option 1: Local Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd amc-mcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package:
```bash
pip install -e .
```

4. Run the server:
```bash
python -m amc_mcp.server
```

#### Option 2: Docker Deployment

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Or build and run manually:
```bash
docker build -t amc-mcp .
docker run -it amc-mcp
```

## MCP Tools Reference 🛠️

### 1. get_now_showing
Returns a list of movies currently showing in a given location.

**Input:**
```json
{
  "location": "Boston, MA"
}
```

**Output:**
```json
{
  "location": "Boston, MA",
  "movies": [
    {
      "movie_id": "mv001",
      "title": "Dune: Part Two",
      "rating": "PG-13",
      "duration": 166,
      "genre": "Sci-Fi/Action",
      "description": "Paul Atreides unites with Chani..."
    }
  ]
}
```

### 2. get_recommendations
Suggests movies based on mood, genre, or preferences.

**Input:**
```json
{
  "genre": "action",
  "mood": "exciting"
}
```

**Output:**
```json
{
  "criteria": {"genre": "action", "mood": "exciting"},
  "recommendations": [...]
}
```

### 3. get_showtimes
Fetches available showtimes for a specific movie and location.

**Input:**
```json
{
  "movie_id": "mv001",
  "date": "2025-10-28",
  "location": "Boston, MA"
}
```

**Output:**
```json
{
  "movie": {"id": "mv001", "title": "Dune: Part Two"},
  "date": "2025-10-28",
  "location": "Boston, MA",
  "showtimes": [
    {
      "showtime_id": "st001",
      "theater_name": "AMC Boston Common 19",
      "theater_address": "175 Tremont Street",
      "time": "14:00",
      "format": "IMAX",
      "price": 18.50
    }
  ]
}
```

### 4. get_seat_map
Displays available and reserved seats for a specific showtime.

**Input:**
```json
{
  "showtime_id": "st001"
}
```

**Output:**
```json
{
  "showtime_id": "st001",
  "movie": "Dune: Part Two",
  "theater": "AMC Boston Common 19",
  "date": "2025-10-28",
  "time": "14:00",
  "seat_map": [
    {
      "seat_number": "A5",
      "row": "A",
      "column": 5,
      "is_available": true,
      "price_tier": "Standard",
      "price": 18.50
    }
  ]
}
```

### 5. book_seats
Reserves selected seats for the user.

**Input:**
```json
{
  "showtime_id": "st001",
  "seats": ["A5", "A6"],
  "user_id": "user123"
}
```

**Output:**
```json
{
  "booking_id": "booking-uuid",
  "status": "pending",
  "movie": "Dune: Part Two",
  "theater": "AMC Boston Common 19",
  "date": "2025-10-28",
  "time": "14:00",
  "seats": ["A5", "A6"],
  "total_price": 37.00
}
```

### 6. process_payment
Handles simulated payment transaction.

**Input:**
```json
{
  "booking_id": "booking-uuid",
  "payment_method": "card",
  "amount": 37.00
}
```

**Output:**
```json
{
  "payment_id": "payment-uuid",
  "payment_status": "success",
  "booking_id": "booking-uuid",
  "receipt_url": "https://amc.com/receipts/payment-uuid",
  "confirmation": {
    "movie": "Dune: Part Two",
    "theater": "AMC Boston Common 19",
    "date": "2025-10-28",
    "time": "14:00",
    "seats": ["A5", "A6"],
    "total_paid": 37.00
  }
}
```

## Example Conversation Flow 💬

Here's how a typical movie booking conversation would work:

1. **User**: "Find an action movie near me tonight."
   - Server calls: `get_now_showing` + `get_recommendations`
   - Returns: List of action movies with showtimes

2. **User**: "Book two seats for Dune: Part Two at 8 PM."
   - Server calls: `get_showtimes` → `get_seat_map` → `book_seats`
   - Returns: Seat selection and booking confirmation

3. **User**: "Pay with my card."
   - Server calls: `process_payment`
   - Returns: Payment confirmation with digital receipt

## Architecture 🏗️

```
amc-mcp/
├── src/
│   └── amc_mcp/
│       ├── __init__.py
│       └── server.py          # Main MCP server implementation
├── data/
│   ├── movies.json           # Movie catalog
│   ├── theaters.json         # Theater locations
│   ├── showtimes.json        # Showtime schedules
│   └── seats.json           # Seat maps by showtime
├── config/
│   └── nginx.conf           # Web server configuration
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Multi-service orchestration
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Package configuration
└── README.md               # This file
```

## Data Models 📊

### Movie
```python
{
  "movie_id": str,
  "title": str,
  "rating": str,         # PG, PG-13, R, etc.
  "duration": int,       # Minutes
  "genre": str,
  "description": str,
  "poster_url": str
}
```

### Theater
```python
{
  "theater_id": str,
  "name": str,
  "address": str,
  "city": str,
  "state": str,
  "zip_code": str
}
```

### Showtime
```python
{
  "showtime_id": str,
  "movie_id": str,
  "theater_id": str,
  "date": str,           # YYYY-MM-DD
  "time": str,           # HH:MM
  "format": str,         # Standard, IMAX, 3D, Dolby
  "price": float
}
```

## Development 👨‍💻

### Adding New Movies
Edit `data/movies.json` to add new movies:

```json
{
  "movie_id": "mv011",
  "title": "New Movie Title",
  "rating": "PG-13",
  "duration": 120,
  "genre": "Action",
  "description": "Description of the movie...",
  "poster_url": "https://example.com/poster.jpg"
}
```

### Adding New Theaters
Edit `data/theaters.json`:

```json
{
  "theater_id": "th011",
  "name": "AMC New Location 15",
  "address": "123 Main Street",
  "city": "New City",
  "state": "NY",
  "zip_code": "12345"
}
```

### Adding Showtimes
Edit `data/showtimes.json` and `data/seats.json` to add new showtimes and corresponding seat maps.

### Testing

#### Manual Testing
You can test individual tools using the MCP inspector or by connecting to any MCP-compatible client.

#### Testing with Claude Desktop
1. Configure Claude Desktop to connect to your MCP server
2. Use natural language to test the booking flow
3. Example: "Find me a sci-fi movie showing tonight in Boston"

## Configuration ⚙️

### Environment Variables

- `PYTHONPATH`: Set to `/app/src` for proper module resolution
- `PYTHONUNBUFFERED`: Set to `1` for real-time logging
- `MCP_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)

### Docker Configuration

The server runs in a lightweight Python 3.11 container with:
- Non-root user for security
- Health checks for monitoring
- Volume mounts for data persistence
- Network isolation

## Security Considerations 🔒

This is a **mock implementation** for demonstration purposes. In production:

1. **Payment Processing**: Integrate with real payment gateways (Stripe, PayPal)
2. **Authentication**: Add user authentication and authorization
3. **Data Validation**: Implement comprehensive input validation
4. **Rate Limiting**: Add API rate limiting
5. **Encryption**: Use HTTPS and encrypt sensitive data
6. **Database**: Replace JSON files with a real database
7. **Logging**: Implement structured logging and monitoring

## Future Enhancements 🔮

- **Real AMC API Integration**: Connect to actual AMC Theatres API
- **User Accounts**: Persistent user profiles and booking history  
- **Group Bookings**: Support for multiple users booking together
- **Loyalty Programs**: AMC Stubs integration
- **Mobile Tickets**: Generate QR codes for mobile entry
- **Seat Recommendations**: AI-powered optimal seat suggestions
- **Price Alerts**: Notify users of discounts and promotions
- **Social Features**: Share movie plans with friends
- **Accessibility**: ADA-compliant seat selection
- **Multi-language**: International language support

## Contributing 🤝

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add new feature'`
5. Push to the branch: `git push origin feature/new-feature`
6. Submit a pull request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Support 💬

For questions, issues, or feature requests:
- Create an issue in the GitHub repository
- Check the documentation for common solutions
- Review the example conversation flows

---

**Happy movie booking! 🍿🎬**