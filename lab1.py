import sys
from datetime import datetime

guests = []
rooms = {
    101: {"type": "Стандарт", "available": True, "price": 50},
    102: {"type": "Стандарт", "available": True, "price": 50},
    103: {"type": "Стандарт", "available": True, "price": 50},
    104: {"type": "Стандарт", "available": True, "price": 50},
    105: {"type": "Стандарт", "available": True, "price": 50},
    201: {"type": "Люкс", "available": True, "price": 150},
    202: {"type": "Люкс", "available": True, "price": 150},
    203: {"type": "Люкс", "available": True, "price": 150},
    301: {"type": "Апартаменти", "available": True, "price": 300},
    302: {"type": "Апартаменти", "available": True, "price": 300}
}
staff = [
    {"name": "Катерина", "position": "Покоївка"},
    {"name": "Творислава", "position": "Покоївка"},
    {"name": "Єлизавета", "position": "Старша покоївка"},
    {"name": "Йосип", "position": "Охоронець"},
    {"name": "Фрол", "position": "Охоронець"},
    {"name": "Яромисл", "position": "Старший охоронець"},
    {"name": "Шаміль", "position": "Ліфтер"},
    {"name": "Земислав", "position": "Швейцар"},
    {"name": "Найден", "position": "Швейцар"},
    {"name": "Найда", "position": "Портьє"},
    {"name": "Льоля", "position": "Портьє"},
    {"name": "Антон", "position": "Хол-менеджер"},
    {"name": "Естер", "position": "Адміністратор"},
    {"name": "Остромов", "position": "Директор"},
    {"name": "Марія", "position": "Масажист"}

]
services = {
    "Басейн": 10,
    "Масаж": 15,
    "SPA": 30,
    "Транспорт": 40
}
bookings = []

def show_main_menu():
    print("\n--- Головне меню ---")
    print("1. Перегляд гостей")
    print("2. Перегляд номерів")
    print("3. Бронювання номера")
    print("4. Сервіси готелю")
    print("5. Меню оплати")
    print("6. Персонал і посади")
    print("0. Вихід")

def view_guests():
    print("\n--- Список гостей ---")
    if guests:
        for guest in guests:
            print(f"- {guest}")
    else:
        print("Гостей поки немає.")

def view_rooms():
    print("\n--- Список номерів ---")
    for room, info in rooms.items():
        status = "Доступний" if info["available"] else "Зайнятий"
        print(f"Номер {room} ({info['type']} - {info['price']}$/ніч): {status}")

def make_booking():
    print("\n--- Бронювання ---")
    name = input("Введіть ім'я гостя: ").strip()
    view_rooms()
    try:
        room = int(input("Оберіть номер для бронювання: "))
        if room in rooms and rooms[room]["available"]:
            check_in = input("Введіть дату заїзду (рррр-мм-дд): ")
            check_out = input("Введіть дату виїзду (рррр-мм-дд): ")
            date_in = datetime.strptime(check_in, "%Y-%m-%d")
            date_out = datetime.strptime(check_out, "%Y-%m-%d")

            if date_out <= date_in:
                print("Дата виїзду повинна бути пізніше дати заїзду.")
                return

            guests.append(name)
            bookings.append({
                "name": name,
                "room": room,
                "check_in": date_in,
                "check_out": date_out,
                "paid": False,
                "services": []
            })
            rooms[room]["available"] = False
            print(f"Номер {room} заброньовано для {name}.")
        else:
            print("Номер недоступний або не існує.")
    except ValueError:
        print("Некоректне введення дати або номера.")

def payment_menu():
    print("\n--- Оплата ---")
    name = input("Ім'я гостя: ").strip()
    guest_bookings = [b for b in bookings if b["name"] == name and not b["paid"]]

    if not guest_bookings:
        print("Активне бронювання не знайдено або вже оплачено.")
        return

    for i, b in enumerate(guest_bookings):
        room_info = rooms[b["room"]]
        nights = (b["check_out"] - b["check_in"]).days
        room_total = nights * room_info["price"]
        services_total = sum(services[s] for s in b["services"])
        total = room_total + services_total

        print(f"\nБронювання {i+1}: Номер {b['room']} ({room_info['type']})")
        print(f"  {nights} ночей x {room_info['price']}$ = {room_total}$")
        print(f"  Сервіси: {', '.join(b['services']) if b['services'] else 'Немає'} = {services_total}$")
        print(f"  До сплати: {total}$")

    try:
        choice = int(input("Оберіть бронювання для оплати: ")) - 1
        if 0 <= choice < len(guest_bookings):
            b = guest_bookings[choice]
            b["paid"] = True
            print("Оплату прийнято. Дякуємо!")
        else:
            print("Невірний вибір.")
    except ValueError:
        print("Некоректне введення.")

def show_services():
    print("\n--- Послуги ---")
    for i, (name, price) in enumerate(services.items(), 1):
        print(f"{i}. {name} — {price}$")
    
    guest_name = input("Ім'я гостя: ").strip()
    guest_booking = next((b for b in bookings if b["name"] == guest_name and not b["paid"]), None)

    if not guest_booking:
        print("Активне бронювання не знайдено.")
        return

    try:
        choice = int(input("Оберіть послугу за номером: ")) - 1
        service_list = list(services.keys())

        if 0 <= choice < len(service_list):
            selected_service = service_list[choice]
            guest_booking["services"].append(selected_service)
            print(f"Послуга '{selected_service}' додана для {guest_name}.")
        else:
            print("Невірний вибір.")
    except ValueError:
        print("Некоректне введення.")

def show_staff():
    print("\n--- Персонал ---")
    for member in staff:
        print(f"{member['name']} - {member['position']}")

def main():
    while True:
        show_main_menu()
        choice = input("Оберіть пункт меню: ")
        if choice == "1":
            view_guests()
        elif choice == "2":
            view_rooms()
        elif choice == "3":
            make_booking()
        elif choice == "4":
            show_services()
        elif choice == "5":
            payment_menu()
        elif choice == "6":
            show_staff()
        elif choice == "0":
            print("До зустрічі!")
            sys.exit()
        else:
            print("Невідомий вибір, спробуйте ще раз.")

if __name__ == "__main__":
    main()
