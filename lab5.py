from fastapi import FastAPI, Depends, HTTPException, Query, Path
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import List, Optional
from enum import Enum
import lab4
import datetime

Base = declarative_base()

print(dir(lab4))

app = FastAPI()

SQLALCHEMY_DATABASE_URL = "sqlite:///./hotel_management.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class HotelCreate(BaseModel):
    name: str
    city: str
    address: str

@app.post("/hotel/")
def init_hotel(hotel_data: HotelCreate, db: Session = Depends(get_db)):
    exists_hotel = db.query(Hotel).first()
    if exists_hotel:
        raise HTTPException(status_code=400, detail="Готель вже існує")

    hotel = Hotel(**hotel_data.dict())
    db.add(hotel)
    db.commit()
    db.refresh(hotel)
    return {"message": "Готель успішно додано!", "hotel_id": hotel.id}

#Меню Guest
class GuestCreate(BaseModel):
    name: str
    age: int
    phone: str
    email: EmailStr
    passport: str

class GuestUpdate(BaseModel):
    name: Optional[str]
    age: Optional[int]
    phone: Optional[str]
    email: Optional[EmailStr]
    passport: Optional[str]

class GuestOut(BaseModel):
    id: int
    name: str
    age: int
    phone: str
    email: EmailStr
    passport: str

    class Config:
        orm_mode = True

@app.post("/guest/", response_model=GuestOut)
def add_guest(guest_data: GuestCreate, db: Session = Depends(get_db)):
    guest = Guest(**guest_data.dict())
    db.add(guest)
    db.commit()
    db.refresh(guest)
    return guest

@app.get("/guest/", response_model=List[GuestOut])
def view_all_guests(db: Session = Depends(get_db)):
    return db.query(Guest).all()

@app.get("/guest/search", response_model=List[GuestOut])
def find_guest(keyword: str = Query(...), db: Session = Depends(get_db)):
    return db.query(Guest).filter(
        (Guest.name.contains(keyword)) | (Guest.phone.contains(keyword))
    ).all()

@app.put("/guest/{guest_id}", response_model=GuestOut)
def edit_guest(guest_id: int, guest_update: GuestUpdate, db: Session = Depends(get_db)):
    guest = db.query(Guest).get(guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Гість не знайдений")
    update_data = guest_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(guest, key, value)
    db.commit()
    db.refresh(guest)
    return guest

@app.delete("/guest/{guest_id}")
def delete_guest(guest_id: int, db: Session = Depends(get_db)):
    guest = db.query(Guest).get(guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Гість не знайдений")
    db.delete(guest)
    db.commit()
    return {"message": "Гість видалений."}

@app.get("/guest/sorted_by_age", response_model=List[GuestOut])
def sort_guests_by_age(db: Session = Depends(get_db)):
    return db.query(Guest).order_by(Guest.age).all()

#Меню Room_Type

class RoomTypeCreate(BaseModel):
    type: str
    price: float
    max_guests: int

class RoomTypeUpdate(BaseModel):
    type: Optional[str]
    price: Optional[float]
    max_guests: Optional[int]

class RoomTypeOut(BaseModel):
    id: int
    type: str
    price: float
    max_guests: int

    class Config:
        orm_mode = True

# Додати тип кімнати
@app.post("/room_type/", response_model=RoomTypeOut)
def add_room_type(room_type_data: RoomTypeCreate, db: Session = Depends(get_db)):
    rt = RoomType(**room_type_data.dict())
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt

# Перегляд усіх типів кімнат
@app.get("/room_type/", response_model=List[RoomTypeOut])
def view_all_room_types(db: Session = Depends(get_db)):
    return db.query(RoomType).all()

# Пошук типу кімнати за ключовим словом у типі
@app.get("/room_type/search", response_model=List[RoomTypeOut])
def search_room_type(keyword: str = Query(...), db: Session = Depends(get_db)):
    results = db.query(RoomType).filter(RoomType.type.ilike(f"%{keyword}%")).all()
    if not results:
        raise HTTPException(status_code=404, detail="Типи кімнат не знайдені")
    return results

# Редагування типу кімнати
@app.put("/room_type/{type_id}", response_model=RoomTypeOut)
def edit_room_type(type_id: int = Path(...), room_type_update: RoomTypeUpdate = Depends(), db: Session = Depends(get_db)):
    rt = db.query(RoomType).get(type_id)
    if not rt:
        raise HTTPException(status_code=404, detail="Тип кімнати не знайдено")

    update_data = room_type_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rt, key, value)

    db.commit()
    db.refresh(rt)
    return rt

# Видалення типу кімнати
@app.delete("/room_type/{type_id}")
def delete_room_type(type_id: int = Path(...), db: Session = Depends(get_db)):
    rt = db.query(RoomType).get(type_id)
    if not rt:
        raise HTTPException(status_code=404, detail="Тип кімнати не знайдено")

    db.delete(rt)
    db.commit()
    return {"message": "Тип кімнати видалено"}

# Сортування типів кімнат
@app.get("/room_type/sort", response_model=List[RoomTypeOut])
def sort_room_types(by: str = Query("price", regex="^(price|max_guests)$"), db: Session = Depends(get_db)):
    if by == "price":
        results = db.query(RoomType).order_by(RoomType.price).all()
    else:
        results = db.query(RoomType).order_by(RoomType.max_guests).all()
    return results

#Меню для кімнат
class RoomStatus(str, Enum):
    Вільний = "Вільний"
    Зайнятий = "Зайнятий"
    На_ремонті = "На_ремонті"

# Pydantic-схеми
class RoomCreate(BaseModel):
    type_id: int
    status: RoomStatus

class RoomUpdate(BaseModel):
    type_id: Optional[int]
    status: Optional[RoomStatus]
    price_per_night: Optional[float]

class RoomOut(BaseModel):
    id: int
    type_id: int
    status: RoomStatus
    price_per_night: float
    type: Optional[str]

    class Config:
        orm_mode = True

# Додати кімнату
@app.post("/room/", response_model=RoomOut)
def add_room(room_data: RoomCreate, db: Session = Depends(get_db)):
    room_type = db.query(RoomType).get(room_data.type_id)
    if not room_type:
        raise HTTPException(status_code=404, detail="Тип кімнати не знайдено")

    room = Room(
        type_id=room_data.type_id,
        status=room_data.status,
        price_per_night=room_type.price
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

# Перегляд усіх кімнат
@app.get("/room/", response_model=List[RoomOut])
def view_all_rooms(db: Session = Depends(get_db)):
    rooms = db.query(Room).all()
    return rooms

# Редагування кімнати
@app.put("/room/{room_id}", response_model=RoomOut)
def edit_room(room_id: int, room_update: RoomUpdate, db: Session = Depends(get_db)):
    room = db.query(Room).get(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Кімната не знайдена")

    if room_update.type_id:
        room_type = db.query(RoomType).get(room_update.type_id)
        if not room_type:
            raise HTTPException(status_code=404, detail="Тип кімнати не знайдено")
        room.type_id = room_update.type_id
        # Оновлюємо ціну, якщо змінився тип
        room.price_per_night = room_type.price

    if room_update.status:
        room.status = room_update.status

    if room_update.price_per_night is not None:
        room.price_per_night = room_update.price_per_night

    db.commit()
    db.refresh(room)
    return room

# Видалення кімнати
@app.delete("/room/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).get(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Кімната не знайдена")

    db.delete(room)
    db.commit()
    return {"message": "Кімната видалена"}

# Pydantic-схеми для Position
class PositionCreate(BaseModel):
    title: str
    level: str
    department: str

class PositionUpdate(BaseModel):
    title: Optional[str]
    level: Optional[str]
    department: Optional[str]

class PositionOut(BaseModel):
    id: int
    title: str
    level: str
    department: str

    class Config:
        orm_mode = True

# Додати посаду
@app.post("/position/", response_model=PositionOut)
def add_position(pos_data: PositionCreate, db: Session = Depends(get_db)):
    pos = Position(**pos_data.dict())
    db.add(pos)
    db.commit()
    db.refresh(pos)
    return pos

# Переглянути всі посади
@app.get("/position/", response_model=List[PositionOut])
def view_positions(db: Session = Depends(get_db)):
    positions = db.query(Position).all()
    return positions

# Пошук посад за ключовим словом у title або department
@app.get("/position/search", response_model=List[PositionOut])
def find_position(keyword: str = Query(..., description="Пошук за назвою посади або відділом"), db: Session = Depends(get_db)):
    positions = db.query(Position).filter(
        (Position.title.contains(keyword)) | (Position.department.contains(keyword))
    ).all()
    if not positions:
        raise HTTPException(status_code=404, detail="Посади не знайдені")
    return positions

# Редагувати посаду
@app.put("/position/{pos_id}", response_model=PositionOut)
def edit_position(pos_id: int, pos_update: PositionUpdate, db: Session = Depends(get_db)):
    pos = db.query(Position).get(pos_id)
    if not pos:
        raise HTTPException(status_code=404, detail="Посада не знайдена")

    update_data = pos_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(pos, key, value)

    db.commit()
    db.refresh(pos)
    return pos

# Видалити посаду
@app.delete("/position/{pos_id}")
def delete_position(pos_id: int, db: Session = Depends(get_db)):
    pos = db.query(Position).get(pos_id)
    if not pos:
        raise HTTPException(status_code=404, detail="Посада не знайдена")

    db.delete(pos)
    db.commit()
    return {"message": "Посаду видалено."}

# Pydantic-схеми
class StaffCreate(BaseModel):
    name: str
    position_id: int
    phone: str
    salary: float

class StaffUpdate(BaseModel):
    name: Optional[str]
    position_id: Optional[int]
    phone: Optional[str]
    salary: Optional[float]

class StaffOut(BaseModel):
    id: int
    name: str
    position_id: int
    phone: str
    salary: float
    position_title: Optional[str] = None

    class Config:
        orm_mode = True

# Додати працівника
@app.post("/staff/", response_model=StaffOut)
def add_staff(staff_data: StaffCreate, db: Session = Depends(get_db)):
    # Перевірка позиції
    position = db.query(Position).get(staff_data.position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Посада не знайдена")
    
    # Перевірка наявності готелю (припускаємо 1 готель)
    hotel = db.query(Hotel).first()
    if not hotel:
        raise HTTPException(status_code=400, detail="Готель не ініціалізований")
    
    staff = Staff(
        name=staff_data.name,
        position_id=staff_data.position_id,
        phone=staff_data.phone,
        salary=staff_data.salary,
        hotel_id=hotel.id
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    staff.position_title = position.title
    return staff

# Переглянути всіх працівників
@app.get("/staff/", response_model=List[StaffOut])
def view_staff(db: Session = Depends(get_db)):
    staff_list = db.query(Staff).all()
    for s in staff_list:
        s.position_title = s.position.title if s.position else None
    return staff_list

# Пошук працівника по імені або телефону
@app.get("/staff/search", response_model=List[StaffOut])
def find_staff(keyword: str = Query(..., description="Пошук по імені або телефону"), db: Session = Depends(get_db)):
    staff_list = db.query(Staff).filter(
        (Staff.name.contains(keyword)) | (Staff.phone.contains(keyword))
    ).all()
    if not staff_list:
        raise HTTPException(status_code=404, detail="Персонал не знайдений")
    for s in staff_list:
        s.position_title = s.position.title if s.position else None
    return staff_list

# Редагувати працівника
@app.put("/staff/{staff_id}", response_model=StaffOut)
def edit_staff(staff_id: int, staff_update: StaffUpdate, db: Session = Depends(get_db)):
    staff = db.query(Staff).get(staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Працівник не знайдений")
    
    update_data = staff_update.dict(exclude_unset=True)
    
    # Якщо змінюємо position_id — перевіряємо існування
    if "position_id" in update_data:
        pos = db.query(Position).get(update_data["position_id"])
        if not pos:
            raise HTTPException(status_code=404, detail="Посада не знайдена")
    
    for key, value in update_data.items():
        setattr(staff, key, value)
    
    db.commit()
    db.refresh(staff)
    staff.position_title = staff.position.title if staff.position else None
    return staff

# Видалити працівника
@app.delete("/staff/{staff_id}")
def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    staff = db.query(Staff).get(staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Працівник не знайдений")
    
    db.delete(staff)
    db.commit()
    return {"message": "Працівника видалено"}
    
# Pydantic схеми для бронювання
class BookingCreate(BaseModel):
    guest_id: int
    room_id: int
    check_in: datetime.date
    check_out: datetime.date
    
class BookingStatus(str, Enum):
    Активно = "Активно"
    Скасовано = "Скасовано"
    Завершено = "Завершено"

class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    check_in: Optional[datetime.date] = None
    check_out: Optional[datetime.date] = None

class BookingRead(BaseModel):
    id: int
    guest_id: int
    guest_name: Optional[str] = None
    room_id: int
    room_type: Optional[str] = None
    check_in: datetime.date
    check_out: datetime.date
    status: BookingStatus
    price_per_night: float

    class Config:
        orm_mode = True

@app.post("/bookings/", response_model=BookingRead)
def add_booking(data: BookingCreate, db: Session = Depends(get_db)):
    # Перевірка гостя
    guest = db.query(Guest).get(data.guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Гість не знайдений")

    # Перевірка кімнати
    room = db.query(Room).get(data.room_id)
    if not room or room.status != RoomStatus.Вільний:
        raise HTTPException(status_code=400, detail="Недоступна кімната")

    # Перевірка дат
    if data.check_out <= data.check_in:
        raise HTTPException(status_code=400, detail="Дата виїзду повинна бути пізніше дати заїзду")

    # Перевірка кількості бронювань для кімнати в період
    overlapping_bookings = db.query(Booking).filter(
        Booking.room_id == data.room_id,
        Booking.status == BookingStatus.Активно,
        Booking.check_out > data.check_in,
        Booking.check_in < data.check_out
    ).count()

    max_guests = room.type.max_guests
    if overlapping_bookings >= max_guests:
        raise HTTPException(status_code=400, detail=f"Кімната вже зайнята на цей період. Макс гостей: {max_guests}")

    # Створення бронювання
    booking = Booking(
        guest_id=data.guest_id,
        room_id=data.room_id,
        check_in=data.check_in,
        check_out=data.check_out,
        status=BookingStatus.Активно,
        price_per_night=room.price_per_night
    )
    db.add(booking)

    # Оновлення статусу кімнати, якщо вона повністю зайнята
    if overlapping_bookings + 1 >= max_guests:
        room.status = RoomStatus.Зайнятий

    db.commit()
    db.refresh(booking)

    return BookingRead(
        id=booking.id,
        guest_id=guest.id,
        guest_name=guest.name,
        room_id=room.id,
        room_type=room.type.type,
        check_in=booking.check_in,
        check_out=booking.check_out,
        status=booking.status,
        price_per_night=booking.price_per_night
    )

@app.get("/bookings/", response_model=List[BookingRead])
def view_bookings(db: Session = Depends(get_db)):
    bookings = db.query(Booking).all()
    results = []
    for b in bookings:
        guest = db.query(Guest).get(b.guest_id)
        room = db.query(Room).get(b.room_id)
        results.append(BookingRead(
            id=b.id,
            guest_id=b.guest_id,
            guest_name=guest.name if guest else None,
            room_id=b.room_id,
            room_type=room.type.type if room else None,
            check_in=b.check_in,
            check_out=b.check_out,
            status=b.status,
            price_per_night=b.price_per_night
        ))
    return results

@app.get("/bookings/search/", response_model=List[BookingRead])
def find_booking_by_guest(keyword: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    guests = db.query(Guest).filter(Guest.name.contains(keyword)).all()
    if not guests:
        raise HTTPException(status_code=404, detail="Гості не знайдені")
    guest_ids = [g.id for g in guests]
    bookings = db.query(Booking).filter(Booking.guest_id.in_(guest_ids)).all()
    if not bookings:
        raise HTTPException(status_code=404, detail="Бронювання не знайдено")

    results = []
    for b in bookings:
        room = db.query(Room).get(b.room_id)
        guest = next((g for g in guests if g.id == b.guest_id), None)
        results.append(BookingRead(
            id=b.id,
            guest_id=b.guest_id,
            guest_name=guest.name if guest else None,
            room_id=b.room_id,
            room_type=room.type.type if room else None,
            check_in=b.check_in,
            check_out=b.check_out,
            status=b.status,
            price_per_night=b.price_per_night
        ))
    return results

@app.put("/bookings/{booking_id}", response_model=BookingRead)
def edit_booking(booking_id: int, data: BookingUpdate, db: Session = Depends(get_db)):
    booking = db.query(Booking).get(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Бронювання не знайдено")

    # Оновлення статусу
    if data.status:
        booking.status = data.status

    # Оновлення дат з перевіркою
    check_in = data.check_in or booking.check_in
    check_out = data.check_out or booking.check_out
    if check_out <= check_in:
        raise HTTPException(status_code=400, detail="Дата виїзду повинна бути пізніше дати заїзду")

    booking.check_in = check_in
    booking.check_out = check_out

    db.commit()
    db.refresh(booking)

    guest = db.query(Guest).get(booking.guest_id)
    room = db.query(Room).get(booking.room_id)

    return BookingRead(
        id=booking.id,
        guest_id=booking.guest_id,
        guest_name=guest.name if guest else None,
        room_id=booking.room_id,
        room_type=room.type.type if room else None,
        check_in=booking.check_in,
        check_out=booking.check_out,
        status=booking.status,
        price_per_night=booking.price_per_night
    )

@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).get(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Бронювання не знайдено")
    room = db.query(Room).get(booking.room_id)
    if room:
        room.status = RoomStatus.Вільний
    db.delete(booking)
    db.commit()
    return {"detail": "Бронювання видалено"}

@app.get("/bookings/sorted/", response_model=List[BookingRead])
def sort_bookings_by_check_in(db: Session = Depends(get_db)):
    bookings = db.query(Booking).order_by(Booking.check_in).all()
    results = []
    for b in bookings:
        guest = db.query(Guest).get(b.guest_id)
        room = db.query(Room).get(b.room_id)
        results.append(BookingRead(
            id=b.id,
            guest_id=b.guest_id,
            guest_name=guest.name if guest else None,
            room_id=b.room_id,
            room_type=room.type.type if room else None,
            check_in=b.check_in,
            check_out=b.check_out,
            status=b.status,
            price_per_night=b.price_per_night
        ))
    return results

# Pydantic схеми для валідації вхідних та вихідних даних
class ServiceCreate(BaseModel):
    name: str
    price: float

class ServiceRead(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        orm_mode = True

# Залежність для отримання сесії БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Створити нову послугу
@app.post("/services/", response_model=ServiceRead)
def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    db_service = Service(name=service.name, price=service.price)
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

# Переглянути всі послуги
@app.get("/services/", response_model=List[ServiceRead])
def read_services(db: Session = Depends(get_db)):
    services = db.query(Service).all()
    return services

# Пошук послуги за ключовим словом у назві
@app.get("/services/search/", response_model=List[ServiceRead])
def search_services(keyword: str, db: Session = Depends(get_db)):
    services = db.query(Service).filter(Service.name.contains(keyword)).all()
    return services

# Отримати послугу за ID
@app.get("/services/{service_id}", response_model=ServiceRead)
def read_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).get(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Послуга не знайдена")
    return service

# Оновити послугу
@app.put("/services/{service_id}", response_model=ServiceRead)
def update_service(service_id: int, service_data: ServiceCreate, db: Session = Depends(get_db)):
    service = db.query(Service).get(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Послуга не знайдена")
    service.name = service_data.name
    service.price = service_data.price
    db.commit()
    db.refresh(service)
    return service

# Видалити послугу
@app.delete("/services/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).get(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Послуга не знайдена")
    db.delete(service)
    db.commit()
    return {"detail": "Послугу видалено"}

# Сортування послуг за ціною (низхідне або висхідне)
@app.get("/services/sorted/", response_model=List[ServiceRead])
def sorted_services(order: str = "asc", db: Session = Depends(get_db)):
    if order == "asc":
        services = db.query(Service).order_by(Service.price.asc()).all()
    elif order == "desc":
        services = db.query(Service).order_by(Service.price.desc()).all()
    else:
        raise HTTPException(status_code=400, detail="order має бути 'asc' або 'desc'")
    return services

# Pydantic схеми
class GuestServiceCreate(BaseModel):
    guest_id: int
    service_id: int
    date: Optional[datetime.date] = None  # дата може бути необов'язковою

class GuestServiceRead(BaseModel):
    id: int
    guest_id: int
    service_id: int
    date: Optional[datetime.date]
    guest_name: Optional[str] = None
    service_name: Optional[str] = None

    class Config:
        orm_mode = True

# Залежність для сесії БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Додати послугу гостю
@app.post("/guest_services/", response_model=GuestServiceRead)
def add_guest_service(data: GuestServiceCreate, db: Session = Depends(get_db)):
    # Перевірка чи гість існує
    guest = db.query(Guest).get(data.guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Гість не знайдений")
    # Перевірка чи послуга існує
    service = db.query(Service).get(data.service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Послуга не знайдена")
    # Дата — якщо не вказана, ставимо сьогодні
    date = data.date or datetime.date.today()
    gs = GuestService(guest_id=data.guest_id, service_id=data.service_id, date=date)
    db.add(gs)
    db.commit()
    db.refresh(gs)
    # Додамо імена для зручності
    gs.guest_name = guest.name
    gs.service_name = service.name
    return gs

# Переглянути всі послуги гостей
@app.get("/guest_services/", response_model=List[GuestServiceRead])
def view_guest_services(db: Session = Depends(get_db)):
    gs_list = db.query(GuestService).all()
    # Додамо ім'я гостя та послуги у відповідь
    for gs in gs_list:
        gs.guest_name = gs.guest.name if gs.guest else None
        gs.service_name = gs.service.name if gs.service else None
    return gs_list

# Пошук по імені гостя або назві послуги
@app.get("/guest_services/search/", response_model=List[GuestServiceRead])
def find_guest_services(keyword: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    gs_list = db.query(GuestService).join(Guest).join(Service).filter(
        (Guest.name.contains(keyword)) | (Service.name.contains(keyword))
    ).all()
    for gs in gs_list:
        gs.guest_name = gs.guest.name if gs.guest else None
        gs.service_name = gs.service.name if gs.service else None
    return gs_list

# Редагувати запис гостя-сервісу
@app.put("/guest_services/{gs_id}", response_model=GuestServiceRead)
def edit_guest_service(gs_id: int, data: GuestServiceCreate, db: Session = Depends(get_db)):
    gs = db.query(GuestService).get(gs_id)
    if not gs:
        raise HTTPException(status_code=404, detail="Запис не знайдено")

    # Перевірка гостя і послуги
    guest = db.query(Guest).get(data.guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Гість не знайдений")
    service = db.query(Service).get(data.service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Послуга не знайдена")

    gs.guest_id = data.guest_id
    gs.service_id = data.service_id
    gs.date = data.date or gs.date

    db.commit()
    db.refresh(gs)
    gs.guest_name = guest.name
    gs.service_name = service.name
    return gs

# Видалити запис гостя-сервісу
@app.delete("/guest_services/{gs_id}")
def delete_guest_service(gs_id: int, db: Session = Depends(get_db)):
    gs = db.query(GuestService).get(gs_id)
    if not gs:
        raise HTTPException(status_code=404, detail="Запис не знайдено")
    db.delete(gs)
    db.commit()
    return {"detail": "Запис видалено"}

# Схема (Pydantic) для відповіді і запиту (простіша версія)

class PaymentCreate(BaseModel):
    booking_id: int
    method: str  # 'Готівка' або 'Карта'

class PaymentRead(BaseModel):
    id: int
    booking_id: int
    amount: float
    date: datetime.date
    method: str

    class Config:
        orm_mode = True


@app.post("/payments/", response_model=PaymentRead)
def add_payment(payment_in: PaymentCreate, db: Session = Depends(get_db)):

    booking = db.query(Booking).filter(Booking.id == payment_in.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронювання не знайдено")

    if booking.status != BookingStatus.Активно:
        raise HTTPException(status_code=400, detail="Оплата можлива лише для активних бронювань")

    # Перевірка чи вже є оплата для цього бронювання
    existing_payment = db.query(Payment).filter(Payment.booking_id == booking.id).first()
    if existing_payment:
        raise HTTPException(status_code=400, detail="Бронювання вже оплачено")

    # Розрахунок вартості номера
    num_nights = (booking.check_out - booking.check_in).days
    room_cost = num_nights * booking.price_per_night

    # Розрахунок сервісів
    guest_services = db.query(GuestService).filter_by(guest_id=booking.guest_id).all()
    service_cost = 0
    for gs in guest_services:
        service = db.query(Service).get(gs.service_id)
        if service:
            service_cost += service.price

    total_amount = room_cost + service_cost

    # Перевірка методу оплати
    if payment_in.method not in [m.value for m in PaymentMethod]:
        raise HTTPException(status_code=400, detail="Невірний метод оплати")

    payment = Payment(
        booking_id=booking.id,
        amount=total_amount,
        date=datetime.date.today(),
        method=PaymentMethod(payment_in.method)
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment

@app.get("/payments/", response_model=List[PaymentRead])
def view_payments(db: Session = Depends(get_db)):
    payments = db.query(Payment).all()
    return payments

@app.get("/payments/{payment_id}", response_model=PaymentRead)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Оплата не знайдена")
    return payment