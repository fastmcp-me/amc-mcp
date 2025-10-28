#!/usr/bin/env python3
"""
Test script for AMC MCP Server
Run basic tests to verify server functionality
"""
import asyncio
import json
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from amc_mcp.server import AMCMCPServer


async def test_server():
    """Test basic server functionality"""
    print("🧪 Testing AMC MCP Server...")
    
    server = AMCMCPServer()
    
    # Test 1: Get now showing
    print("\n1. Testing get_now_showing...")
    result = await server._get_now_showing({"location": "Boston, MA"})
    data = json.loads(result.content[0].text)
    print(f"   ✅ Found {len(data['movies'])} movies")
    
    # Test 2: Get recommendations  
    print("\n2. Testing get_recommendations...")
    result = await server._get_recommendations({"genre": "action"})
    data = json.loads(result.content[0].text)
    print(f"   ✅ Found {len(data['recommendations'])} recommendations")
    
    # Test 3: Get showtimes
    print("\n3. Testing get_showtimes...")
    result = await server._get_showtimes({
        "movie_id": "mv001",
        "date": "2025-10-28", 
        "location": "Boston, MA"
    })
    data = json.loads(result.content[0].text)
    if "error" in data:
        print(f"   ❌ Error: {data['error']}")
        return
    print(f"   ✅ Found {len(data['showtimes'])} showtimes")
    
    # Test 4: Get seat map
    print("\n4. Testing get_seat_map...")
    result = await server._get_seat_map({"showtime_id": "st001"})
    data = json.loads(result.content[0].text)
    if "error" in data:
        print(f"   ❌ Error: {data['error']}")
        return
    print(f"   ✅ Found {len(data['seat_map'])} seats")
    
    # Test 5: Book seats
    print("\n5. Testing book_seats...")
    result = await server._book_seats({
        "showtime_id": "st001",
        "seats": ["A5", "A6"],
        "user_id": "test_user"
    })
    data = json.loads(result.content[0].text)
    booking_id = data.get('booking_id')
    print(f"   ✅ Created booking: {booking_id}")
    
    # Test 6: Process payment
    print("\n6. Testing process_payment...")
    result = await server._process_payment({
        "booking_id": booking_id,
        "payment_method": "card",
        "amount": data['total_price']
    })
    payment_data = json.loads(result.content[0].text)
    print(f"   ✅ Payment processed: {payment_data['payment_status']}")
    
    print("\n🎉 All tests passed! Server is working correctly.")


if __name__ == "__main__":
    asyncio.run(test_server())