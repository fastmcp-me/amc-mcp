#!/usr/bin/env python3
"""
Test script for AMC MCP Server (FastMCP version)
Run basic tests to verify server functionality
"""
import json
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the module 
import amc_mcp.fastmcp_server as server_module


def test_server():
    """Test basic server functionality"""
    print("🧪 Testing AMC MCP Server (FastMCP)...")
    
    # Test 1: Get now showing
    print("\n1. Testing get_now_showing...")
    result = server_module._get_now_showing("Boston, MA")
    data = json.loads(result)
    print(f"   ✅ Found {len(data['movies'])} movies")
    
    # Test 2: Get recommendations  
    print("\n2. Testing get_recommendations...")
    result = server_module._get_recommendations(genre="action")
    data = json.loads(result)
    print(f"   ✅ Found {len(data['recommendations'])} recommendations")
    
    # Test 3: Get showtimes
    print("\n3. Testing get_showtimes...")
    result = server_module._get_showtimes(
        movie_id="mv001",
        date="2025-10-28", 
        location="Boston, MA"
    )
    data = json.loads(result)
    if "error" in data:
        print(f"   ❌ Error: {data['error']}")
        return
    print(f"   ✅ Found {len(data['showtimes'])} showtimes")
    
    # Test 4: Get seat map
    print("\n4. Testing get_seat_map...")
    result = server_module._get_seat_map(showtime_id="st001")
    data = json.loads(result)
    if "error" in data:
        print(f"   ❌ Error: {data['error']}")
        return
    print(f"   ✅ Found {len(data['seat_map'])} seats")
    
    # Test 5: Book seats
    print("\n5. Testing book_seats...")
    result = server_module._book_seats(
        showtime_id="st001",
        seats=["A5", "A6"],
        user_id="test_user"
    )
    data = json.loads(result)
    if "error" in data:
        print(f"   ❌ Error: {data['error']}")
        return
    booking_id = data.get('booking_id')
    print(f"   ✅ Created booking: {booking_id}")
    
    # Test 6: Process payment
    print("\n6. Testing process_payment...")
    result = server_module._process_payment(
        booking_id=booking_id,
        payment_method="card",
        amount=data['total_price']
    )
    payment_data = json.loads(result)
    if "error" in payment_data:
        print(f"   ❌ Error: {payment_data['error']}")
        return
    print(f"   ✅ Payment processed: {payment_data['payment_status']}")
    
    print("\n🎉 All tests passed! Server is working correctly.")


if __name__ == "__main__":
    test_server()