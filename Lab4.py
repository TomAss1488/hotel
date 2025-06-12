from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, Float, Enum, exists
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
import datetime

Base = declarative_base()

# ENUMs
class RoomStatus(enum.Enum):
    Вільний = "Вільний"
    Зайнятий = "Зайнятий"
    На_ремонті = "На_ремонті"

class BookingStatus(enum.Enum):
    Активно = "Активно"
    Скасовано = "Скасовано"
    Завершено = "Завершено"

class PaymentMethod(enum.Enum):
    Готівка = "Готівка"
    Карта = "Карта"

# Таблиці
class Hotel(Base):
    __tablename__ = 'hotel'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    city = Column(String)
    address = Column(String)

class Guest(Base):
    __tablename__ = 'guest'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    phone = Column(String)
    email = Column(String)
    passport = Column(String)

class RoomType(Base):
    __tablename__ = 'room_type'
    id = Column(Integer, primary_key=True)
    type = Column(String)
    price = Column(Float)
    max_guests = Column(Integer)

class Room(Base):
    __tablename__ = 'room'
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('room_type.id'))
    status = Column(Enum(RoomStatus))
    price_per_night = Column(Float)
    type = relationship("RoomType")

class Service(Base):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)

class GuestService(Base):
    __tablename__ = 'guest_service'
    id = Column(Integer, primary_key=True)
    guest_id = Column(Integer, ForeignKey('guest.id'))
    service_id = Column(Integer, ForeignKey('service.id'))

class Position(Base):
    __tablename__ = 'position'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    level = Column(String)
    department = Column(String)

class Staff(Base):
    __tablename__ = 'staff'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    position_id = Column(Integer, ForeignKey('position.id'))
    phone = Column(String)
    salary = Column(Float)
    hotel_id = Column(Integer, ForeignKey('hotel.id'))
    position = relationship("Position")
    hotel = relationship("Hotel")

class Booking(Base):
    __tablename__ = 'booking'
    id = Column(Integer, primary_key=True)
    guest_id = Column(Integer, ForeignKey('guest.id'))
    room_id = Column(Integer, ForeignKey('room.id'))
    check_in = Column(Date)
    check_out = Column(Date)
    status = Column(Enum(BookingStatus))
    price_per_night = Column(Float)

class Payment(Base):
    __tablename__ = 'payment'
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('booking.id'))
    amount = Column(Float)
    date = Column(Date)
    method = Column(Enum(PaymentMethod))

# Підключення до SQLite
def main():
    # Підключення до бази
    engine = create_engine('sqlite:///hotel_management.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Створення таблиць, якщо ще не створені
    Base.metadata.create_all(engine)

    print("--- Система управління готелем ---")
    
    while True:
        print("\n=== Головне меню ===")
        print("1. Ініціалізувати готель")
        print("2. Меню гостей")
        print("3. Меню типів кімнат")
        print("4. Меню кімнат")
        print("5. Меню посад")
        print("6. Меню персоналу")
        print("7. Меню послуг")
        print("8. Меню бронювань")
        print("9. Меню послуг гостей")
        print("10. Меню оплат")
        print("0. Вихід")
        choice = input("Виберіть опцію: ")
        if choice == "1":
            init_hotel(session)
        elif choice == "2":
            guest_menu(session)
        elif choice == "3":
            room_type_menu(session)
        elif choice == "4":
            room_menu(session)
        elif choice == "5":
            position_menu(session)
        elif choice == "6":
            staff_menu(session)
        elif choice == "7":
            service_menu(session)
        elif choice == "8":
            booking_menu(session)
        elif choice == "9":
            guest_service_menu(session)
        elif choice == "10":
            payment_menu(session)
        elif choice == "0":
            print("Вихід з програми.")
            break
        else:
            print("Невірний вибір.\n")
    
    session.close()

# Функція ініціалізації готелю 
def init_hotel(session):
    exists_hotel = session.query(Hotel).first()
    if not exists_hotel:
        name = input("Введіть назву готелю: ")
        city = input("Місто: ")
        address = input("Адреса: ")
        hotel = Hotel(name=name, city=city, address=address)
        session.add(hotel)
        session.commit()
        print("Готель успішно додано!\n")
    else:
        print("Готель вже існує у базі даних.\n")

#Меню Guest

def add_guest(session):
    name = input("ПІБ гостя: ")
    age = int(input("Вік: "))
    phone = input("Телефон: ")
    email = input("Email: ")
    passport = input("Номер паспорта: ")

    guest = Guest(name=name, age=age, phone=phone, email=email, passport=passport)
    session.add(guest)
    session.commit()
    print("Гість доданий успішно.\n")

def view_all_guests(session):
    guests = session.query(Guest).all()
    if not guests:
        print("Гості не знайдені.\n")
    for g in guests:
        print(f"ID: {g.id} | ПІБ: {g.name} | Вік: {g.age} | Телефон: {g.phone} | Email: {g.email} | Паспорт: {g.passport}")
    print()

def find_guest(session):
    keyword = input("Введіть ПІБ або номер телефону для пошуку: ")
    results = session.query(Guest).filter(
        (Guest.name.contains(keyword)) | (Guest.phone.contains(keyword))
    ).all()
    if results:
        for g in results:
            print(f"ID: {g.id} | ПІБ: {g.name} | Вік: {g.age} | Телефон: {g.phone} | Email: {g.email} | Паспорт: {g.passport}")
    else:
        print("Гості не знайдені.\n")
    print()

def edit_guest(session):
    view_all_guests(session)
    guest_id = int(input("Введіть ID гостя для редагування: "))
    guest = session.query(Guest).get(guest_id)
    if not guest:
        print("Гість не знайдений.\n")
        return

    guest.name = input(f"ПІБ [{guest.name}]: ") or guest.name
    guest.age = int(input(f"Вік [{guest.age}]: ") or guest.age)
    guest.phone = input(f"Телефон [{guest.phone}]: ") or guest.phone
    guest.email = input(f"Email [{guest.email}]: ") or guest.email
    guest.passport = input(f"Паспорт [{guest.passport}]: ") or guest.passport

    session.commit()
    print("Інформацію оновлено.\n")

def delete_guest(session):
    guest_id = int(input("Введіть ID гостя для видалення: "))
    guest = session.query(Guest).get(guest_id)
    if guest:
        session.delete(guest)
        session.commit()
        print("Гість видалений.\n")
    else:
        print("Гість не знайдений.\n")

def sort_guests_by_age(session):
    guests = session.query(Guest).order_by(Guest.age).all()
    for g in guests:
        print(f"ID: {g.id} | ПІБ: {g.name} | Вік: {g.age} | Телефон: {g.phone} | Email: {g.email} | Паспорт: {g.passport}")
    print()

def guest_menu(session):
    while True:
        print("\n=== Меню гостей ===")
        print("1. Додати гостя")
        print("2. Переглянути всіх гостей")
        print("3. Пошук гостя")
        print("4. Редагувати гостя")
        print("5. Видалити гостя")
        print("6. Сортувати гостей за віком")
        print("0. Назад")

        choice = input("Виберіть опцію: ")
        if choice == "1":
            add_guest(session)
        elif choice == "2":
            view_all_guests(session)
        elif choice == "3":
            find_guest(session)
        elif choice == "4":
            edit_guest(session)
        elif choice == "5":
            delete_guest(session)
        elif choice == "6":
            sort_guests_by_age(session)
        elif choice == "0":
            break
        else:
            print("Невірний вибір.\n")

#Меню Room_Type

def add_room_type(session):
    room_type = input("Тип кімнати (Стандарт / Люкс / Апартаменти): ")
    
    if room_type.lower() == "стандарт":
        price = 50
        max_guests = 2
    elif room_type.lower() == "люкс":
        price = 150
        max_guests = 4
    elif room_type.lower() == "апартаменти":
        price = 300
        max_guests = 6
    else:
        print("Невірний тип кімнати.\n")
        return

    rt = RoomType(type=room_type, price=price, max_guests=max_guests)
    session.add(rt)
    session.commit()
    print("Тип кімнати додано.\n")

def view_all_room_types(session):
    types = session.query(RoomType).all()
    if not types:
        print("Немає типів кімнат.\n")
    for t in types:
        print(f"ID: {t.id} | Тип: {t.type} | Ціна за ніч: {t.price} | Макс. гостей: {t.max_guests}")
    print()

def search_room_type(session):
    keyword = input("Введіть тип для пошуку: ").lower()
    results = session.query(RoomType).filter(RoomType.type.ilike(f"%{keyword}%")).all()
    if results:
        for t in results:
            print(f"ID: {t.id} | Тип: {t.type} | Ціна: {t.price} | Макс. гостей: {t.max_guests}")
    else:
        print("Нічого не знайдено.\n")

def edit_room_type(session):
    view_all_room_types(session)
    type_id = int(input("Введіть ID типу кімнати для редагування: "))
    rt = session.query(RoomType).get(type_id)
    if not rt:
        print("Тип кімнати не знайдено.\n")
        return

    rt.type = input(f"Тип [{rt.type}]: ") or rt.type
    rt.price = float(input(f"Ціна [{rt.price}]: ") or rt.price)
    rt.max_guests = int(input(f"Макс. гостей [{rt.max_guests}]: ") or rt.max_guests)

    session.commit()
    print("Дані оновлено.\n")

def delete_room_type(session):
    view_all_room_types(session)
    type_id = int(input("Введіть ID типу кімнати для видалення: "))
    rt = session.query(RoomType).get(type_id)
    if rt:
        session.delete(rt)
        session.commit()
        print("Тип кімнати видалено.\n")
    else:
        print("Тип не знайдено.\n")

def sort_room_types(session):
    print("1. Сортувати за ціною")
    print("2. Сортувати за макс. кількістю гостей")
    option = input("Вибір: ")
    if option == "1":
        results = session.query(RoomType).order_by(RoomType.price).all()
    elif option == "2":
        results = session.query(RoomType).order_by(RoomType.max_guests).all()
    else:
        print("Невірний вибір.")
        return

    for t in results:
        print(f"ID: {t.id} | Тип: {t.type} | Ціна: {t.price} | Макс. гостей: {t.max_guests}")
    print()

def room_type_menu(session):
    while True:
        print("\n=== Меню типів кімнат ===")
        print("1. Додати тип кімнати")
        print("2. Переглянути всі типи")
        print("3. Пошук типу")
        print("4. Редагувати тип")
        print("5. Видалити тип")
        print("6. Сортувати")
        print("0. Назад")

        choice = input("Ваш вибір: ")
        if choice == "1":
            add_room_type(session)
        elif choice == "2":
            view_all_room_types(session)
        elif choice == "3":
            search_room_type(session)
        elif choice == "4":
            edit_room_type(session)
        elif choice == "5":
            delete_room_type(session)
        elif choice == "6":
            sort_room_types(session)
        elif choice == "0":
            break
        else:
            print("Невірний вибір.\n")

#Меню для кімнат
def add_room(session):
    while True:
        try:
            view_all_room_types(session)
            type_id = int(input("ID типу кімнати (0 для виходу): "))
            if type_id == 0:
                return

            room_type = session.query(RoomType).get(type_id)
            if not room_type:
                print("Тип кімнати не знайдено. Спробуйте ще раз.\n")
                continue

            status = input("Статус (Вільний/Зайнятий/На_ремонті): ")
            if status not in RoomStatus.__members__:
                print("Невірний статус. Спробуйте ще раз.\n")
                continue

            price_per_night = room_type.price

            room = Room(type_id=type_id, status=RoomStatus[status], price_per_night=price_per_night)
            session.add(room)
            session.commit()
            print("Кімната додана.\n")
            break
        
        except ValueError:
            print("Помилка введення. Введіть числове значення ID.\n")

def view_all_room_types(session):
    types = session.query(RoomType).all()
    for t in types:
        print(f"ID: {t.id} | Тип: {t.type} | Ціна: {t.price} | Макс. гостей: {t.max_guests}")
    print()

def view_all_rooms(session):
    rooms = session.query(Room).all()
    for r in rooms:
        print(f"ID: {r.id} | Тип: {r.type.type} | Статус: {r.status.value} | Ціна: {r.price_per_night}")
    print()

def edit_room(session):
    room_id = int(input("ID кімнати для редагування: "))
    room = session.query(Room).get(room_id)
    if not room:
        print("Кімната не знайдена.\n")
        return

    view_all_room_types(session)
    room.type_id = int(input(f"ID типу кімнати [{room.type_id}]: ") or room.type_id)
    status = input(f"Статус (Вільний/Зайнятий/На_ремонті) [{room.status.value}]: ") or room.status.value
    room.status = RoomStatus[status]
    room.price_per_night = float(input(f"Ціна за ніч [{room.price_per_night}]: ") or room.price_per_night)

    session.commit()
    print("Кімната оновлена.\n")

def delete_room(session):
    room_id = int(input("ID кімнати для видалення: "))
    room = session.query(Room).get(room_id)
    if room:
        session.delete(room)
        session.commit()
        print("Кімната видалена.\n")
    else:
        print("Кімната не знайдена.\n")

def room_menu(session):
    while True:
        print("\n=== Меню кімнат ===")
        print("1. Додати кімнату")
        print("2. Переглянути всі кімнати")
        print("3. Редагувати кімнату")
        print("4. Видалити кімнату")
        print("0. Назад")

        choice = input("Виберіть опцію: ")
        if choice == "1":
            add_room(session)
        elif choice == "2":
            view_all_rooms(session)
        elif choice == "3":
            edit_room(session)
        elif choice == "4":
            delete_room(session)
        elif choice == "0":
            break
        else:
            print("Невірний вибір.\n")

#Меню для Посади

def add_position(session):
    title = input("Назва посади: ")
    level = input("Рівень: ")
    department = input("Відділ: ")
    pos = Position(title=title, level=level, department=department)
    session.add(pos)
    session.commit()
    print("Посаду додано.\n")

def view_positions(session):
    positions = session.query(Position).all()
    if not positions:
        print("Посади не знайдені.\n")
        return
    for p in positions:
        print(f"ID: {p.id} | Назва: {p.title} | Рівень: {p.level} | Відділ: {p.department}")
    print()

def find_position(session):
    keyword = input("Введіть назву або відділ для пошуку: ")
    positions = session.query(Position).filter(
        (Position.title.contains(keyword)) | (Position.department.contains(keyword))
    ).all()
    if not positions:
        print("Посади не знайдені.\n")
        return
    for p in positions:
        print(f"ID: {p.id} | Назва: {p.title} | Рівень: {p.level} | Відділ: {p.department}")
    print()

def edit_position(session):
    try:
        pos_id = int(input("Введіть ID посади для редагування: "))
    except ValueError:
        print("Невірний формат ID.")
        return
    pos = session.query(Position).get(pos_id)
    if not pos:
        print("Посада не знайдена.\n")
        return
    pos.title = input(f"Назва [{pos.title}]: ") or pos.title
    pos.level = input(f"Рівень [{pos.level}]: ") or pos.level
    pos.department = input(f"Відділ [{pos.department}]: ") or pos.department
    session.commit()
    print("Дані посади оновлено.\n")

def delete_position(session):
    try:
        pos_id = int(input("Введіть ID посади для видалення: "))
    except ValueError:
        print("Невірний формат ID.")
        return
    pos = session.query(Position).get(pos_id)
    if not pos:
        print("Посада не знайдена.\n")
        return
    session.delete(pos)
    session.commit()
    print("Посаду видалено.\n")

def position_menu(session):
    while True:
        print("\n--- Меню посад ---")
        print("1. Додати посаду")
        print("2. Переглянути всі посади")
        print("3. Пошук посади")
        print("4. Редагувати посаду")
        print("5. Видалити посаду")
        print("0. Назад")
        choice = input("Виберіть опцію: ")
        if choice == "1":
            add_position(session)
        elif choice == "2":
            view_positions(session)
        elif choice == "3":
            find_position(session)
        elif choice == "4":
            edit_position(session)
        elif choice == "5":
            delete_position(session)
        elif choice == "0":
            break
        else:
            print("Невірний вибір.\n")

#Меню для Персоналу

def add_staff(session):
    name = input("Ім'я працівника: ")
    
    # Вибір посади
    positions = session.query(Position).all()
    if not positions:
        print("Спочатку додайте посади.\n")
        return
    print("Доступні посади:")
    for pos in positions:
        print(f"{pos.id}. {pos.title}")
    try:
        position_id = int(input("Введіть ID посади: "))
        if not session.query(Position).filter_by(id=position_id).first():
            print("Посада не знайдена.")
            return
    except ValueError:
        print("Невірний формат ID.")
        return
    
    phone = input("Телефон: ")
    try:
        salary = float(input("Зарплата: "))
    except ValueError:
        print("Зарплата має бути числом.")
        return
    
    # Готель 
    hotel = session.query(Hotel).first()
    if not hotel:
        print("Спочатку ініціалізуйте готель.")
        return
    
    staff = Staff(name=name, position_id=position_id, phone=phone, salary=salary, hotel_id=hotel.id)
    session.add(staff)
    session.commit()
    print("Працівника додано.\n")

def view_staff(session):
    staff_list = session.query(Staff).all()
    if not staff_list:
        print("Персонал не знайдений.\n")
        return
    for s in staff_list:
        print(f"ID: {s.id} | Ім'я: {s.name} | Посада: {s.position.title if s.position else 'Не вказана'} | Телефон: {s.phone} | Зарплата: {s.salary}")
    print()

def find_staff(session):
    keyword = input("Введіть ім'я або телефон для пошуку: ")
    staff_list = session.query(Staff).filter(
        (Staff.name.contains(keyword)) | (Staff.phone.contains(keyword))
    ).all()
    if not staff_list:
        print("Персонал не знайдений.\n")
        return
    for s in staff_list:
        print(f"ID: {s.id} | Ім'я: {s.name} | Посада: {s.position.title if s.position else 'Не вказана'} | Телефон: {s.phone} | Зарплата: {s.salary}")
    print()

def edit_staff(session):
    try:
        staff_id = int(input("Введіть ID працівника для редагування: "))
    except ValueError:
        print("Невірний формат ID.")
        return
    staff = session.query(Staff).get(staff_id)
    if not staff:
        print("Працівника не знайдено.\n")
        return
    staff.name = input(f"Ім'я [{staff.name}]: ") or staff.name
    
    # Посада
    positions = session.query(Position).all()
    if positions:
        print("Доступні посади:")
        for pos in positions:
            print(f"{pos.id}. {pos.title}")
        pos_input = input(f"ID посади [{staff.position_id}]: ")
        if pos_input:
            try:
                pos_id = int(pos_input)
                if session.query(Position).filter_by(id=pos_id).first():
                    staff.position_id = pos_id
                else:
                    print("Невірний ID посади, посаду не змінено.")
            except ValueError:
                print("Невірний формат ID посади, посаду не змінено.")
    
    staff.phone = input(f"Телефон [{staff.phone}]: ") or staff.phone
    salary_input = input(f"Зарплата [{staff.salary}]: ")
    if salary_input:
        try:
            staff.salary = float(salary_input)
        except ValueError:
            print("Зарплата має бути числом. Зміни не збережено.")
            return
    
    session.commit()
    print("Дані працівника оновлено.\n")

def delete_staff(session):
    try:
        staff_id = int(input("Введіть ID працівника для видалення: "))
    except ValueError:
        print("Невірний формат ID.")
        return
    staff = session.query(Staff).get(staff_id)
    if not staff:
        print("Працівника не знайдено.\n")
        return
    session.delete(staff)
    session.commit()
    print("Працівника видалено.\n")

def staff_menu(session):
    while True:
        print("\n--- Меню персоналу ---")
        print("1. Додати працівника")
        print("2. Переглянути всіх працівників")
        print("3. Пошук працівника")
        print("4. Редагувати працівника")
        print("5. Видалити працівника")
        print("0. Назад")
        choice = input("Виберіть опцію: ")
        if choice == "1":
            add_staff(session)
        elif choice == "2":
            view_staff(session)
        elif choice == "3":
            find_staff(session)
        elif choice == "4":
            edit_staff(session)
        elif choice == "5":
            delete_staff(session)
        elif choice == "0":
            break
        else:
            print("Невірний вибір.\n")

#Меню для Сервісу

def add_service(session):
    name = input("Назва послуги: ")
    try:
        price = float(input("Ціна послуги: "))
    except ValueError:
        print("Ціна має бути числом.")
        return
    service = Service(name=name, price=price)
    session.add(service)
    session.commit()
    print("Послуга додана успішно.\n")

def view_services(session):
    services = session.query(Service).all()
    if not services:
        print("Послуги не знайдені.\n")
        return
    for s in services:
        print(f"ID: {s.id} | Назва: {s.name} | Ціна: {s.price}")
    print()

def find_service(session):
    keyword = input("Введіть назву послуги для пошуку: ")
    services = session.query(Service).filter(Service.name.contains(keyword)).all()
    if not services:
        print("Послуги не знайдені.\n")
        return
    for s in services:
        print(f"ID: {s.id} | Назва: {s.name} | Ціна: {s.price}")
    print()

def edit_service(session):
    service_id = int(input("Введіть ID послуги для редагування: "))
    service = session.query(Service).get(service_id)
    if not service:
        print("Послуга не знайдена.\n")
        return
    service.name = input(f"Назва [{service.name}]: ") or service.name
    price_input = input(f"Ціна [{service.price}]: ")
    if price_input:
        try:
            service.price = float(price_input)
        except ValueError:
            print("Ціна має бути числом. Зміни не збережено.")
            return
    session.commit()
    print("Послугу оновлено.\n")

def delete_service(session):
    service_id = int(input("Введіть ID послуги для видалення: "))
    service = session.query(Service).get(service_id)
    if not service:
        print("Послуга не знайдена.\n")
        return
    session.delete(service)
    session.commit()
    print("Послугу видалено.\n")

def sort_services_by_price(session):
    services = session.query(Service).order_by(Service.price).all()
    if not services:
        print("Послуги не знайдені.\n")
        return
    for s in services:
        print(f"ID: {s.id} | Назва: {s.name} | Ціна: {s.price}")
    print()

def service_menu(session):
    while True:
        print("\n--- Меню послуг ---")
        print("1. Додати послугу")
        print("2. Переглянути всі послуги")
        print("3. Пошук послуги")
        print("4. Редагувати послугу")
        print("5. Видалити послугу")
        print("6. Сортувати послуги за ціною")
        print("0. Назад")
        choice = input("Виберіть опцію: ")
        if choice == "1":
            add_service(session)
        elif choice == "2":
            view_services(session)
        elif choice == "3":
            find_service(session)
        elif choice == "4":
            edit_service(session)
        elif choice == "5":
            delete_service(session)
        elif choice == "6":
            sort_services_by_price(session)
        elif choice == "0":
            break
        else:
            print("Невірний вибір.\n")

#Меню для Бронбвання

def add_booking(session):
    # Перегляд гостей
    print("Гості:")
    guests = session.query(Guest).all()
    for g in guests:
        print(f"ID: {g.id} | ПІБ: {g.name}")
    guest_id = int(input("Введіть ID гостя: "))
    guest = session.query(Guest).get(guest_id)
    if not guest:
        print("Гість не знайдений.")
        return

    # Фільтруємо тільки ті кімнати, які не є Зайняті або На ремонті
    rooms = session.query(Room).filter(Room.status == RoomStatus.Вільний).all()

    if not rooms:
        print("Немає доступних кімнат.")
        return

    print("Доступні кімнати:")
    for r in rooms:
        print(f"ID: {r.id} | Тип: {r.type.type} | Ціна: {r.price_per_night} | Макс. гостей: {r.type.max_guests}")
    room_id = int(input("Введіть ID кімнати: "))
    room = session.query(Room).get(room_id)
    if not room or room.status != RoomStatus.Вільний:
        print("Недоступна кімната.")
        return

    check_in_str = input("Дата заїзду (рррр-мм-дд): ")
    check_out_str = input("Дата виїзду (рррр-мм-дд): ")
    try:
        check_in = datetime.datetime.strptime(check_in_str, "%Y-%m-%d").date()
        check_out = datetime.datetime.strptime(check_out_str, "%Y-%m-%d").date()
        if check_out <= check_in:
            print("Дата виїзду повинна бути пізніше дати заїзду.")
            return
    except ValueError:
        print("Невірний формат дати.")
        return

    # Перевірка на кількість активних бронювань у той самий період
    overlapping_bookings = session.query(Booking).filter(
        Booking.room_id == room_id,
        Booking.status == BookingStatus.Активно,
        Booking.check_out > check_in,
        Booking.check_in < check_out
    ).count()

    max_guests = room.type.max_guests
    if overlapping_bookings >= max_guests:
        print(f"Кімната вже зайнята на цей період. Максимальна кількість гостей: {max_guests}")
        return

    booking = Booking(
        guest_id=guest_id,
        room_id=room_id,
        check_in=check_in,
        check_out=check_out,
        status=BookingStatus.Активно,
        price_per_night=room.price_per_night
    )
    session.add(booking)

    # Позначити як зайняту, якщо вже буде заповнена
    if overlapping_bookings + 1 >= max_guests:
        room.status = RoomStatus.Зайнятий

    session.commit()
    print("Бронювання успішно створено.\n")

def view_bookings(session):
    bookings = session.query(Booking).all()
    if not bookings:
        print("Бронювання не знайдено.\n")
        return
    for b in bookings:
        guest = session.query(Guest).get(b.guest_id)
        room = session.query(Room).get(b.room_id)
        print(f"ID: {b.id} | Гість: {guest.name if guest else 'Видалено'} | "
              f"Кімната: {room.type.type if room else 'Видалено'} | "
              f"Заїзд: {b.check_in} | Виїзд: {b.check_out} | Статус: {b.status.value} | Ціна за ніч: {b.price_per_night}")
    print()

def find_booking_by_guest(session):
    keyword = input("Введіть ім'я гостя для пошуку бронювань: ")
    guests = session.query(Guest).filter(Guest.name.contains(keyword)).all()
    if not guests:
        print("Гості не знайдені.\n")
        return
    guest_ids = [g.id for g in guests]
    bookings = session.query(Booking).filter(Booking.guest_id.in_(guest_ids)).all()
    if not bookings:
        print("Бронювання для цього гостя не знайдено.\n")
        return
    for b in bookings:
        room = session.query(Room).get(b.room_id)
        print(f"ID: {b.id} | Гість: {keyword} | Кімната: {room.type.type if room else 'Видалено'} | "
              f"Заїзд: {b.check_in} | Виїзд: {b.check_out} | Статус: {b.status.value}")
    print()

def edit_booking(session):
    view_bookings(session)
    booking_id = int(input("Введіть ID бронювання для редагування: "))
    booking = session.query(Booking).get(booking_id)
    if not booking:
        print("Бронювання не знайдено.\n")
        return

    print(f"Поточний статус: {booking.status.value}")
    print("Статуси:")
    for s in BookingStatus:
        print(f"- {s.name}")
    status_str = input("Введіть новий статус (залиште порожнім для збереження): ")
    if status_str:
        if status_str in BookingStatus.__members__:
            booking.status = BookingStatus[status_str]
        else:
            print("Невірний статус.")
            return

    check_in_str = input(f"Дата заїзду [{booking.check_in}]: ")
    check_out_str = input(f"Дата виїзду [{booking.check_out}]: ")
    try:
        if check_in_str:
            check_in = datetime.datetime.strptime(check_in_str, "%Y-%m-%d").date()
        else:
            check_in = booking.check_in
        if check_out_str:
            check_out = datetime.datetime.strptime(check_out_str, "%Y-%m-%d").date()
        else:
            check_out = booking.check_out
        if check_out <= check_in:
            print("Дата виїзду повинна бути пізніше дати заїзду.")
            return
        booking.check_in = check_in
        booking.check_out = check_out
    except ValueError:
        print("Невірний формат дати.")
        return

    session.commit()
    print("Бронювання оновлено.\n")

def delete_booking(session):
    view_bookings(session)
    booking_id = int(input("Введіть ID бронювання для видалення: "))
    booking = session.query(Booking).get(booking_id)
    if not booking:
        print("Бронювання не знайдено.\n")
        return
    # Після видалення бронювання оновлюємо статус кімнати (якщо потрібно)
    room = session.query(Room).get(booking.room_id)
    if room:
        room.status = RoomStatus.Вільний
    session.delete(booking)
    session.commit()
    print("Бронювання видалено.\n")

def sort_bookings_by_check_in(session):
    bookings = session.query(Booking).order_by(Booking.check_in).all()
    if not bookings:
        print("Бронювання не знайдено.\n")
        return
    for b in bookings:
        guest = session.query(Guest).get(b.guest_id)
        room = session.query(Room).get(b.room_id)
        print(f"ID: {b.id} | Гість: {guest.name if guest else 'Видалено'} | "
              f"Кімната: {room.type.type if room else 'Видалено'} | "
              f"Заїзд: {b.check_in} | Виїзд: {b.check_out} | Статус: {b.status.value}")
    print()

def booking_menu(session):
    while True:
        print("\n--- Меню бронювань ---")
        print("1. Додати бронювання")
        print("2. Переглянути всі бронювання")
        print("3. Пошук бронювання за ім'ям гостя")
        print("4. Редагувати бронювання")
        print("5. Видалити бронювання")
        print("6. Сортувати бронювання за датою заїзду")
        print("0. Назад")
        choice = input("Виберіть опцію: ")
        if choice == "1":
            add_booking(session)
        elif choice == "2":
            view_bookings(session)
        elif choice == "3":
            find_booking_by_guest(session)
        elif choice == "4":
            edit_booking(session)
        elif choice == "5":
            delete_booking(session)
        elif choice == "6":
            sort_bookings_by_check_in(session)
        elif choice == "0":
            break
        else:
            print("Невірний вибір.")

#Меню для Гість-Сервіс

def add_guest_service(session):
    # Вибір гостя
    guests = session.query(Guest).all()
    if not guests:
        print("Спочатку додайте гостей.\n")
        return
    print("Доступні гості:")
    for g in guests:
        print(f"{g.id}. {g.name}")
    try:
        guest_id = int(input("Введіть ID гостя: "))
        if not session.query(Guest).filter_by(id=guest_id).first():
            print("Гість не знайдений.")
            return
    except ValueError:
        print("Невірний формат ID.")
        return

    # Вибір послуги
    services = session.query(Service).all()
    if not services:
        print("Спочатку додайте послуги.\n")
        return
    print("Доступні послуги:")
    for s in services:
        print(f"{s.id}. {s.name}")
    try:
        service_id = int(input("Введіть ID послуги: "))
        if not session.query(Service).filter_by(id=service_id).first():
            print("Послуга не знайдена.")
            return
    except ValueError:
        print("Невірний формат ID.")
        return

    guest_service = GuestService(guest_id=guest_id, service_id=service_id)
    session.add(guest_service)
    session.commit()
    print("Послуга гостю додана.\n")

def view_guest_services(session):
    gs_list = session.query(GuestService).all()
    if not gs_list:
        print("Послуги гостей не знайдені.\n")
        return
    for gs in gs_list:
        print(f"ID: {gs.id} | Гість: {gs.guest.name if gs.guest else 'Н/д'} | Послуга: {gs.service.name if gs.service else 'Н/д'} | Дата: {gs.date}")
    print()

def find_guest_service(session):
    keyword = input("Введіть ім'я гостя або назву послуги для пошуку: ")
    gs_list = session.query(GuestService).join(Guest).join(Service).filter(
        (Guest.name.contains(keyword)) | (Service.name.contains(keyword))
    ).all()
    if not gs_list:
        print("Послуги гостей не знайдені.\n")
        return
    for gs in gs_list:
        print(f"ID: {gs.id} | Гість: {gs.guest.name if gs.guest else 'Н/д'} | Послуга: {gs.service.name if gs.service else 'Н/д'} | Дата: {gs.date}")
    print()

def edit_guest_service(session):
    try:
        gs_id = int(input("Введіть ID для редагування: "))
    except ValueError:
        print("Невірний формат ID.")
        return
    gs = session.query(GuestService).get(gs_id)
    if not gs:
        print("Запис не знайдено.\n")
        return

    # Зміна гостя
    guests = session.query(Guest).all()
    if guests:
        print("Доступні гості:")
        for g in guests:
            print(f"{g.id}. {g.name}")
        guest_input = input(f"ID гостя [{gs.guest_id}]: ")
        if guest_input:
            try:
                guest_id = int(guest_input)
                if session.query(Guest).filter_by(id=guest_id).first():
                    gs.guest_id = guest_id
                else:
                    print("Гість не знайдений. Зміна пропущена.")
            except ValueError:
                print("Невірний формат ID гостя. Зміна пропущена.")

    # Зміна послуги
    services = session.query(Service).all()
    if services:
        print("Доступні послуги:")
        for s in services:
            print(f"{s.id}. {s.name}")
        service_input = input(f"ID послуги [{gs.service_id}]: ")
        if service_input:
            try:
                service_id = int(service_input)
                if session.query(Service).filter_by(id=service_id).first():
                    gs.service_id = service_id
                else:
                    print("Послуга не знайдена. Зміна пропущена.")
            except ValueError:
                print("Невірний формат ID послуги. Зміна пропущена.")

    date_input = input(f"Дата [{gs.date}]: ")
    if date_input:
        try:
            gs.date = datetime.datetime.strptime(date_input, "%Y-%m-%d").date()
        except ValueError:
            print("Невірний формат дати. Зміна пропущена.")

    session.commit()
    print("Дані оновлено.\n")

def delete_guest_service(session):
    try:
        gs_id = int(input("Введіть ID для видалення: "))
    except ValueError:
        print("Невірний формат ID.")
        return
    gs = session.query(GuestService).get(gs_id)
    if not gs:
        print("Запис не знайдено.\n")
        return
    session.delete(gs)
    session.commit()
    print("Запис видалено.\n")

def guest_service_menu(session):
    while True:
        print("\n--- Меню послуг гостей ---")
        print("1. Додати послугу гостю")
        print("2. Переглянути послуги гостей")
        print("3. Пошук послуг гостей")
        print("4. Редагувати послугу гостю")
        print("5. Видалити послугу гостю")
        print("0. Назад")
        choice = input("Виберіть опцію: ")
        if choice == "1":
            add_guest_service(session)
        elif choice == "2":
            view_guest_services(session)
        elif choice == "3":
            find_guest_service(session)
        elif choice == "4":
            edit_guest_service(session)
        elif choice == "5":
            delete_guest_service(session)
        elif choice == "0":
            break
        else:
            print("Невірний вибір.\n")

#Меню для Оплати

def add_payment(session):
    # Отримати список оплачених бронювань
    paid_booking_ids = [p.booking_id for p in session.query(Payment.booking_id).all()]

    # Отримати список активних бронювань без оплати
    unpaid_bookings = session.query(Booking).filter(
        Booking.status == BookingStatus.Активно,
        ~Booking.id.in_(paid_booking_ids)
    ).all()

    if not unpaid_bookings:
        print("Всі активні бронювання вже оплачені.\n")
        return

    print("Бронювання, які ще не оплачені:")
    for b in unpaid_bookings:
        guest = session.query(Guest).get(b.guest_id)
        room = session.query(Room).get(b.room_id)
        print(f"ID: {b.id} | Гість: {guest.name} | Кімната: {room.type.type} | З {b.check_in} до {b.check_out}")

    while True:
        try:
            booking_id = int(input("ID бронювання: "))
        except ValueError:
            print("Невірний формат ID. Спробуйте ще раз.\n")
            continue

        booking = session.query(Booking).get(booking_id)
        if not booking:
            print("Бронювання не знайдено. Спробуйте ще раз.\n")
            continue
        break  # Вірний booking_id

    # Розрахунок вартості номера
    num_nights = (booking.check_out - booking.check_in).days
    room_cost = num_nights * booking.price_per_night

    # Розрахунок сервісів
    guest_services = session.query(GuestService).filter_by(guest_id=booking.guest_id).all()
    service_cost = 0
    for gs in guest_services:
        service = session.query(Service).get(gs.service_id)
        if service:
            service_cost += service.price

    total_amount = room_cost + service_cost

    print(f"\n Ціна за номер: {room_cost} грн")
    print(f"Ціна за сервіси: {service_cost} грн")
    print(f"Загальна сума до сплати: {total_amount} грн")

    # Введення методу оплати
    while True:
        method_input = input("Спосіб оплати (Готівка/Карта): ")
        try:
            method = PaymentMethod[method_input]
           
        except KeyError:
            print("Невірний спосіб оплати. Введіть 'Готівка' або 'Карта'.\n")
        break
    payment = Payment(
        booking_id=booking.id,
        amount=total_amount,
        date=datetime.date.today(),
        method=method
    )

    session.add(payment)
    session.commit()
    print("Оплату додано.\n")

def view_payments(session):
    payments = session.query(Payment).all()
    if not payments:
        print("Оплати не знайдені.\n")
        return
    for p in payments:
        print(f"ID: {p.id} | Бронювання ID: {p.booking_id} | Сума: {p.amount} | Дата: {p.date} | Метод: {p.method.value}")
    print()

def find_payment(session):
    # Пошук по бронюванню
    try:
        booking_id = int(input("Введіть ID бронювання для пошуку оплат: "))
    except ValueError:
        print("Невірний формат ID.")
        return
    payments = session.query(Payment).filter_by(booking_id=booking_id).all()
    if not payments:
        print("Оплати не знайдені.\n")
        return
    for p in payments:
        print(f"ID: {p.id} | Бронювання ID: {p.booking_id} | Сума: {p.amount} | Дата: {p.date} | Метод: {p.method.value}")
    print()

def edit_payment(session):
    view_payments(session)
    try:
        payment_id = int(input("Введіть ID оплати для редагування: "))
    except ValueError:
        print("Невірний формат ID.")
        return
    payment = session.query(Payment).get(payment_id)
    if not payment:
        print("Оплата не знайдена.\n")
        return

    amount_input = input(f"Сума [{payment.amount}]: ")
    if amount_input:
        try:
            payment.amount = float(amount_input)
        except ValueError:
            print("Сума має бути числом. Зміни не збережено.")
            return

    date_input = input(f"Дата [{payment.date}]: ")
    if date_input:
        try:
            payment.date = datetime.datetime.strptime(date_input, "%Y-%m-%d").date()
        except ValueError:
            print("Невірний формат дати. Зміни не збережено.")
            return

    method_input = input(f"Метод оплати [{payment.method.value}]: ")
    if method_input:
        if method_input not in [m.value for m in PaymentMethod]:
            print("Невідомий метод оплати. Зміни не збережено.")
            return
        payment.method = PaymentMethod(method_input)

    session.commit()
    print("Дані оплати оновлено.\n")

def delete_payment(session):
    view_payments(session)
    try:
        payment_id = int(input("Введіть ID оплати для видалення: "))
    except ValueError:
        print("Невірний формат ID.")
        return
    payment = session.query(Payment).get(payment_id)
    if not payment:
        print("Оплата не знайдена.\n")
        return
    session.delete(payment)
    session.commit()
    print("Оплату видалено.\n")

def payment_menu(session):
    while True:
        print("\n--- Меню оплат ---")
        print("1. Додати оплату")
        print("2. Переглянути всі оплати")
        print("3. Пошук оплат")
        print("4. Редагувати оплату")
        print("5. Видалити оплату")
        print("0. Назад")
        choice = input("Виберіть опцію: ")
        if choice == "1":
            add_payment(session)
        elif choice == "2":
            view_payments(session)
        elif choice == "3":
            find_payment(session)
        elif choice == "4":
            edit_payment(session)
        elif choice == "5":
            delete_payment(session)
        elif choice == "0":
            break
        else:
            print("Невірний вибір.\n")

# Головна функція
if __name__ == '__main__':
    main()
    