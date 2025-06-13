import pytest
from datetime import datetime
from hotel.lab1 import services, rooms

def calculate_total(booking, room):
    nights = (booking["check_out"] - booking["check_in"]).days
    room_total = nights * room["price"]
    services_total = sum(services[s] for s in booking["services"])
    return room_total + services_total

#Тести
def test_room_price_calculation():
    check_in = datetime(2025,6,10)
    check_out = datetime(2025,6,13)  
    nights = (check_out - check_in).days
    assert nights == 3
    price = rooms[101]["price"]
    assert price == 50
    assert nights * price == 150

def test_services_total():
    selected_services = ["Басейн", "SPA"]
    total = sum(services[s] for s in selected_services)
    assert total == 10 + 30

def test_booking_total_price_with_services():
    booking = {
        "check_in": datetime(2025,6,1),
        "check_out": datetime(2025,6,4),
        "services": ["Масаж", "Транспорт"]
    }
    room = rooms[201]  
    total = calculate_total(booking, room)
    expected = 3 * 150 + 15 + 40
    assert total == expected

def test_add_service_to_booking():
    booking = {"services": []}
    service_name = "SPA"
    booking["services"].append(service_name)
    assert "SPA" in booking["services"]
    assert len(booking["services"]) == 1

def test_create_booking_structure():
    booking = {
        "name": "Іван",
        "room": 101,
        "check_in": datetime(2025, 6, 1),
        "check_out": datetime(2025, 6, 5),
        "paid": False,
        "services": []
    }
    assert booking["name"] == "Іван"
    assert booking["room"] == 101
    assert not booking["paid"]
    assert isinstance(booking["services"], list)