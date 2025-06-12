import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Lab4 import Base  # твій файл з моделями
from Lab4 import (Hotel, Guest, RoomType, Room, Service, GuestService,
                  Position, Staff, Booking, Payment, RoomStatus, BookingStatus, PaymentMethod)
import datetime

# Підключення до БД
engine = create_engine('sqlite:///hotel\hotel_management.db')
Session = sessionmaker(bind=engine)
session = Session()

# Створення таблиць
Base.metadata.create_all(engine)

# Головне меню Streamlit
st.set_page_config(page_title="Система управління готелем", layout="wide")
st.title("🏨 Система управління готелем")

menu = st.sidebar.selectbox("Оберіть розділ:", [
    "Головна",
    "Ініціалізувати готель",
    "Меню гостей",
    "Меню типів кімнат",
    "Меню кімнат",
    "Меню посад",
    "Меню персоналу",
    "Меню послуг",
    "Меню бронювань",
    "Меню послуг гостей",
    "Меню оплат"
])

# Обробка вибору меню
if menu == "Головна":
    st.subheader("Ласкаво просимо до системи управління готелем!")
    st.markdown("Виберіть опцію з меню зліва для початку роботи.")

elif menu == "Ініціалізувати готель":
    st.subheader("Ініціалізувати готель")
    name = st.text_input("Назва готелю")
    city = st.text_input("Місто")
    address = st.text_input("Адреса")
    if st.button("Зберегти"):
        new_hotel = Hotel(name=name, city=city, address=address)
        session.add(new_hotel)
        session.commit()
        st.success("Готель успішно збережено!")

elif menu == "Меню гостей":
    st.subheader("👤 Меню гостей")

    tab1, tab2, tab3, tab4 = st.tabs(["➕ Додати", "📋 Переглянути", "🔍 Пошук", "⚙️ Редагувати / Видалити"])

    # ➕ Додавання гостя
    with tab1:
        with st.form("add_guest_form"):
            name = st.text_input("ПІБ гостя")
            age = st.number_input("Вік", min_value=0, max_value=120, step=1)
            phone = st.text_input("Телефон")
            email = st.text_input("Email")
            passport = st.text_input("Номер паспорта")
            submitted = st.form_submit_button("Додати")
            if submitted:
                guest = Guest(name=name, age=age, phone=phone, email=email, passport=passport)
                session.add(guest)
                session.commit()
                st.success("✅ Гість доданий успішно")

    # 📋 Перегляд усіх гостей + сортування
    with tab2:
        sort = st.checkbox("Сортувати за віком", value=False)
        guests = session.query(Guest).order_by(Guest.age if sort else Guest.id).all()
        if guests:
            for g in guests:
                st.markdown(f"""
                **ID:** {g.id} | **ПІБ:** {g.name} | **Вік:** {g.age}  
                📞 {g.phone} | ✉️ {g.email} | 🆔 {g.passport}
                ---""")
        else:
            st.info("Гостей не знайдено.")

    # 🔍 Пошук гостей
    with tab3:
        keyword = st.text_input("Пошук за ПІБ або телефоном")
        if keyword:
            results = session.query(Guest).filter(
                (Guest.name.contains(keyword)) | (Guest.phone.contains(keyword))
            ).all()
            if results:
                for g in results:
                    st.markdown(f"""
                    **ID:** {g.id} | **ПІБ:** {g.name} | **Вік:** {g.age}  
                    📞 {g.phone} | ✉️ {g.email} | 🆔 {g.passport}
                    ---""")
            else:
                st.warning("Гостей не знайдено.")

    # ⚙️ Редагування та видалення
    with tab4:
        guests = session.query(Guest).all()
        guest_ids = {f"{g.id} - {g.name}": g.id for g in guests}
        selected = st.selectbox("Оберіть гостя для редагування/видалення", list(guest_ids.keys()))
        guest_id = guest_ids[selected]
        guest = session.query(Guest).get(guest_id)

        with st.form("edit_guest_form"):
            new_name = st.text_input("ПІБ", guest.name)
            new_age = st.number_input("Вік", 0, 120, guest.age)
            new_phone = st.text_input("Телефон", guest.phone)
            new_email = st.text_input("Email", guest.email)
            new_passport = st.text_input("Паспорт", guest.passport)
            submitted = st.form_submit_button("Оновити")
            if submitted:
                guest.name = new_name
                guest.age = new_age
                guest.phone = new_phone
                guest.email = new_email
                guest.passport = new_passport
                session.commit()
                st.success("✅ Дані оновлено")

        if st.button("🗑️ Видалити цього гостя"):
            session.delete(guest)
            session.commit()
            st.success("🗑️ Гість видалений")
            st.experimental_rerun()

elif menu == "Меню типів кімнат":
    st.subheader("🏨 Меню типів кімнат")

    tab1, tab2, tab3, tab4 = st.tabs(["➕ Додати", "📋 Переглянути / Сортувати", "🔍 Пошук", "⚙️ Редагувати / Видалити"])

    # ➕ Додавання типу кімнати
    with tab1:
        with st.form("add_room_type_form"):
            room_type = st.selectbox("Тип кімнати", ["Стандарт", "Люкс", "Апартаменти"])
            submitted = st.form_submit_button("Додати")

            if submitted:
                if room_type.lower() == "стандарт":
                    price, max_guests = 50, 2
                elif room_type.lower() == "люкс":
                    price, max_guests = 150, 4
                elif room_type.lower() == "апартаменти":
                    price, max_guests = 300, 6
                else:
                    st.error("❌ Невідомий тип кімнати.")
                    st.stop()

                rt = RoomType(type=room_type, price=price, max_guests=max_guests)
                session.add(rt)
                session.commit()
                st.success("✅ Тип кімнати додано.")

    # 📋 Перегляд усіх + сортування
    with tab2:
        sort_by = st.radio("Сортувати за:", ["ID", "Ціна", "Макс. гостей"], horizontal=True)
        if sort_by == "Ціна":
            room_types = session.query(RoomType).order_by(RoomType.price).all()
        elif sort_by == "Макс. гостей":
            room_types = session.query(RoomType).order_by(RoomType.max_guests).all()
        else:
            room_types = session.query(RoomType).order_by(RoomType.id).all()

        if room_types:
            for t in room_types:
                st.markdown(f"""
                **ID:** {t.id} | **Тип:** {t.type}  
                💰 {t.price} / ніч | 👥 Макс. гостей: {t.max_guests}
                ---""")
        else:
            st.info("Типи кімнат не знайдені.")

    # 🔍 Пошук типу
    with tab3:
        keyword = st.text_input("Введіть тип кімнати для пошуку")
        if keyword:
            results = session.query(RoomType).filter(RoomType.type.ilike(f"%{keyword}%")).all()
            if results:
                for t in results:
                    st.markdown(f"""
                    **ID:** {t.id} | **Тип:** {t.type}  
                    💰 {t.price} / ніч | 👥 Макс. гостей: {t.max_guests}
                    ---""")
            else:
                st.warning("❌ Нічого не знайдено.")

    # ⚙️ Редагування / видалення
    with tab4:
        all_types = session.query(RoomType).all()
        if all_types:
            options = {f"{t.id} - {t.type}": t.id for t in all_types}
            selected = st.selectbox("Оберіть тип для редагування або видалення", list(options.keys()))
            selected_id = options[selected]
            rt = session.query(RoomType).get(selected_id)

            with st.form("edit_room_type_form"):
                new_type = st.text_input("Тип", rt.type)
                new_price = st.number_input("Ціна", value=rt.price, min_value=0.0)
                new_max_guests = st.number_input("Макс. гостей", value=rt.max_guests, min_value=1)
                update_btn = st.form_submit_button("Оновити")

                if update_btn:
                    rt.type = new_type
                    rt.price = new_price
                    rt.max_guests = new_max_guests
                    session.commit()
                    st.success("✅ Дані оновлено")

            if st.button("🗑️ Видалити цей тип кімнати"):
                session.delete(rt)
                session.commit()
                st.success("🗑️ Тип кімнати видалено")
                st.experimental_rerun()
        else:
            st.info("Типи кімнат не знайдені.")

elif menu == "Меню кімнат":
    st.subheader("🛏️ Меню кімнат")

    tab1, tab2, tab3 = st.tabs(["➕ Додати", "📋 Переглянути", "⚙️ Редагувати / Видалити"])

    # Отримання всіх типів кімнат
    room_types = session.query(RoomType).all()
    type_dict = {f"{t.type} (ID {t.id})": t.id for t in room_types}
    status_options = {status.name: status.value for status in RoomStatus}

    # ➕ Додавання
    with tab1:
        if not room_types:
            st.warning("⚠️ Спочатку додайте хоча б один тип кімнати.")
        else:
            with st.form("add_room_form"):
                selected_type = st.selectbox("Тип кімнати", list(type_dict.keys()))
                selected_status = st.selectbox("Статус", list(status_options.keys()))
                submitted = st.form_submit_button("Додати кімнату")

                if submitted:
                    type_id = type_dict[selected_type]
                    room_type = session.query(RoomType).get(type_id)
                    new_room = Room(
                        type_id=type_id,
                        status=RoomStatus[selected_status],
                        price_per_night=room_type.price
                    )
                    session.add(new_room)
                    session.commit()
                    st.success("✅ Кімната додана!")

    # 📋 Перегляд
    with tab2:
        rooms = session.query(Room).all()
        if rooms:
            for r in rooms:
                st.markdown(f"""
                **ID:** {r.id} | **Тип:** {r.type.type}  
                📊 Статус: {r.status.value} | 💵 Ціна: {r.price_per_night}
                ---""")
        else:
            st.info("Немає доданих кімнат.")

    # ⚙️ Редагування / видалення
    with tab3:
        all_rooms = session.query(Room).all()
        if all_rooms:
            options = {f"Кімната {r.id} ({r.type.type})": r.id for r in all_rooms}
            selected = st.selectbox("Оберіть кімнату для редагування або видалення", list(options.keys()))
            room_id = options[selected]
            room = session.query(Room).get(room_id)

            with st.form("edit_room_form"):
                new_type = st.selectbox("Тип", list(type_dict.keys()), index=list(type_dict.values()).index(room.type_id))
                new_status = st.selectbox("Статус", list(status_options.keys()), index=list(status_options.values()).index(room.status.value))
                new_price = st.number_input("Ціна за ніч", value=room.price_per_night, min_value=0.0)

                update_btn = st.form_submit_button("Оновити")
                if update_btn:
                    room.type_id = type_dict[new_type]
                    room.status = RoomStatus[new_status]
                    room.price_per_night = new_price
                    session.commit()
                    st.success("✅ Кімната оновлена!")

            if st.button("🗑️ Видалити цю кімнату"):
                session.delete(room)
                session.commit()
                st.success("🗑️ Кімната видалена")
                st.experimental_rerun()
        else:
            st.info("Кімнати не знайдені.")

elif menu == "Меню посад":
    st.subheader("🏢 Меню посад")

    # Отримуємо всі посади для відображення і вибору
    positions = session.query(Position).all()
    pos_dict = {f"{p.title} (ID {p.id})": p.id for p in positions}

    tab_add, tab_view, tab_edit = st.tabs(["➕ Додати", "📋 Переглянути / Пошук", "⚙️ Редагувати / Видалити"])

    # ➕ Додати
    with tab_add:
        with st.form("add_position_form"):
            title = st.text_input("Назва посади")
            level = st.text_input("Рівень")
            department = st.text_input("Відділ")
            submitted = st.form_submit_button("Додати посаду")

            if submitted:
                if title.strip() == "" or level.strip() == "" or department.strip() == "":
                    st.error("Будь ласка, заповніть всі поля.")
                else:
                    new_pos = Position(title=title.strip(), level=level.strip(), department=department.strip())
                    session.add(new_pos)
                    session.commit()
                    st.success("✅ Посаду додано.")
                    st.rerun()

    # 📋 Перегляд / Пошук
    with tab_view:
        keyword = st.text_input("Пошук за назвою або відділом")
        if keyword:
            filtered = session.query(Position).filter(
                (Position.title.ilike(f"%{keyword}%")) | (Position.department.ilike(f"%{keyword}%"))
            ).all()
        else:
            filtered = positions

        if filtered:
            for p in filtered:
                st.markdown(f"**ID:** {p.id} | **Назва:** {p.title} | **Рівень:** {p.level} | **Відділ:** {p.department}")
        else:
            st.info("Посади не знайдені.")

    # ⚙️ Редагування / Видалення
    with tab_edit:
        if not positions:
            st.info("Посади відсутні.")
        else:
            selected_pos = st.selectbox("Оберіть посаду", list(pos_dict.keys()))
            pos_id = pos_dict[selected_pos]
            pos = session.query(Position).get(pos_id)

            with st.form("edit_position_form"):
                new_title = st.text_input("Назва", value=pos.title)
                new_level = st.text_input("Рівень", value=pos.level)
                new_department = st.text_input("Відділ", value=pos.department)
                update_btn = st.form_submit_button("Оновити")

                if update_btn:
                    pos.title = new_title.strip() or pos.title
                    pos.level = new_level.strip() or pos.level
                    pos.department = new_department.strip() or pos.department
                    session.commit()
                    st.success("✅ Посаду оновлено.")
                    st.experimental_rerun()

            if st.button("🗑️ Видалити цю посаду"):
                session.delete(pos)
                session.commit()
                st.success("🗑️ Посаду видалено.")
                st.experimental_rerun()

elif menu == "Меню персоналу":
    st.subheader("👥 Меню персоналу")

    positions = session.query(Position).all()
    pos_dict = {f"{p.title} (ID {p.id})": p.id for p in positions}

    hotel = session.query(Hotel).first()
    if not hotel:
        st.warning("Спочатку ініціалізуйте готель.")
    else:
        staff_list = session.query(Staff).all()
        staff_dict = {f"{s.name} (ID {s.id})": s.id for s in staff_list}

        tab_add, tab_view, tab_edit = st.tabs(["➕ Додати", "📋 Переглянути / Пошук", "⚙️ Редагувати / Видалити"])

        # ➕ Додати
        with tab_add:
            with st.form("add_staff_form"):
                name = st.text_input("Ім'я працівника")
                if positions:
                    position_name = st.selectbox("Оберіть посаду", list(pos_dict.keys()))
                    position_id = pos_dict.get(position_name)
                else:
                    st.info("Спочатку додайте посади.")
                    position_id = None
                phone = st.text_input("Телефон")
                salary = st.text_input("Зарплата")
                submitted = st.form_submit_button("Додати працівника")

                if submitted:
                    if not (name and position_id and phone and salary):
                        st.error("Будь ласка, заповніть усі поля.")
                    else:
                        try:
                            salary_float = float(salary)
                            new_staff = Staff(
                                name=name.strip(),
                                position_id=position_id,
                                phone=phone.strip(),
                                salary=salary_float,
                                hotel_id=hotel.id,
                            )
                            session.add(new_staff)
                            session.commit()
                            st.success("✅ Працівника додано.")
                            st.rerun()
                        except ValueError:
                            st.error("Зарплата має бути числом.")

        # 📋 Перегляд / Пошук
        with tab_view:
            keyword = st.text_input("Пошук за ім'ям або телефоном")
            if keyword:
                filtered = session.query(Staff).filter(
                    (Staff.name.ilike(f"%{keyword}%")) | (Staff.phone.ilike(f"%{keyword}%"))
                ).all()
            else:
                filtered = staff_list

            if filtered:
                for s in filtered:
                    pos_title = s.position.title if s.position else "Не вказана"
                    st.markdown(
                        f"**ID:** {s.id} | **Ім'я:** {s.name} | **Посада:** {pos_title} | "
                        f"**Телефон:** {s.phone} | **Зарплата:** {s.salary}"
                    )
            else:
                st.info("Працівника не знайдено.")

        # ⚙️ Редагувати / Видалити
        with tab_edit:
            if not staff_list:
                st.info("Працівники відсутні.")
            else:
                selected_staff = st.selectbox("Оберіть працівника", list(staff_dict.keys()))
                staff_id = staff_dict[selected_staff]
                staff = session.query(Staff).get(staff_id)

                with st.form("edit_staff_form"):
                    new_name = st.text_input("Ім'я", value=staff.name)
                    if positions:
                        pos_name = next((k for k, v in pos_dict.items() if v == staff.position_id), None)
                        new_position_name = st.selectbox("Посада", list(pos_dict.keys()), index=list(pos_dict.keys()).index(pos_name) if pos_name else 0)
                        new_position_id = pos_dict.get(new_position_name)
                    else:
                        new_position_id = None
                    new_phone = st.text_input("Телефон", value=staff.phone)
                    new_salary = st.text_input("Зарплата", value=str(staff.salary))
                    update_btn = st.form_submit_button("Оновити")

                    if update_btn:
                        if not (new_name and new_position_id and new_phone and new_salary):
                            st.error("Будь ласка, заповніть усі поля.")
                        else:
                            try:
                                staff.name = new_name.strip()
                                staff.position_id = new_position_id
                                staff.phone = new_phone.strip()
                                staff.salary = float(new_salary)
                                session.commit()
                                st.success("✅ Працівника оновлено.")
                                st.experimental_rerun()
                            except ValueError:
                                st.error("Зарплата має бути числом.")

                if st.button("🗑️ Видалити працівника"):
                    session.delete(staff)
                    session.commit()
                    st.success("🗑️ Працівника видалено.")
                    st.experimental_rerun()

elif menu == "Меню послуг":
    st.subheader("🛎️ Меню послуг")

    services = session.query(Service).all()
    service_dict = {f"{s.name} (ID {s.id})": s.id for s in services}

    tab_add, tab_view, tab_edit, tab_sort = st.tabs(["➕ Додати", "📋 Переглянути / Пошук", "⚙️ Редагувати / Видалити", "🔽 Сортувати за ціною"])

    # ➕ Додати послугу
    with tab_add:
        with st.form("add_service_form"):
            name = st.text_input("Назва послуги")
            price = st.text_input("Ціна послуги")
            submitted = st.form_submit_button("Додати послугу")

            if submitted:
                if not (name and price):
                    st.error("Будь ласка, заповніть усі поля.")
                else:
                    try:
                        price_val = float(price)
                        new_service = Service(name=name.strip(), price=price_val)
                        session.add(new_service)
                        session.commit()
                        st.success("✅ Послугу додано.")
                        st.rerun()
                    except ValueError:
                        st.error("Ціна має бути числом.")

    # 📋 Переглянути / Пошук
    with tab_view:
        keyword = st.text_input("Пошук за назвою послуги")
        if keyword:
            filtered = session.query(Service).filter(Service.name.ilike(f"%{keyword}%")).all()
        else:
            filtered = services

        if filtered:
            for s in filtered:
                st.markdown(f"**ID:** {s.id} | **Назва:** {s.name} | **Ціна:** {s.price}")
        else:
            st.info("Послуги не знайдені.")

    # ⚙️ Редагувати / Видалити
    with tab_edit:
        if not services:
            st.info("Послуги відсутні.")
        else:
            selected_service = st.selectbox("Оберіть послугу", list(service_dict.keys()))
            service_id = service_dict[selected_service]
            service = session.query(Service).get(service_id)

            with st.form("edit_service_form"):
                new_name = st.text_input("Назва", value=service.name)
                new_price = st.text_input("Ціна", value=str(service.price))
                update_btn = st.form_submit_button("Оновити")

                if update_btn:
                    if not (new_name and new_price):
                        st.error("Будь ласка, заповніть усі поля.")
                    else:
                        try:
                            service.name = new_name.strip()
                            service.price = float(new_price)
                            session.commit()
                            st.success("✅ Послугу оновлено.")
                            st.experimental_rerun()
                        except ValueError:
                            st.error("Ціна має бути числом.")

            if st.button("🗑️ Видалити послугу"):
                session.delete(service)
                session.commit()
                st.success("🗑️ Послугу видалено.")
                st.experimental_rerun()

    # 🔽 Сортування за ціною
    with tab_sort:
        sorted_services = session.query(Service).order_by(Service.price).all()
        if sorted_services:
            for s in sorted_services:
                st.markdown(f"**ID:** {s.id} | **Назва:** {s.name} | **Ціна:** {s.price}")
        else:
            st.info("Послуги відсутні.")

elif menu == "Меню бронювань":
    st.subheader("📅 Меню бронювань")

    guests = session.query(Guest).all()
    guest_dict = {f"{g.name} (ID {g.id})": g.id for g in guests}

    rooms = session.query(Room).filter(Room.status == RoomStatus.Вільний).all()
    room_dict = {f"Тип: {r.type.type}, Ціна: {r.price_per_night}, ID: {r.id}": r.id for r in rooms}

    tab_add, tab_view, tab_edit, tab_sort = st.tabs(["➕ Додати", "📋 Переглянути / Пошук", "⚙️ Редагувати / Видалити", "🔽 Сортувати за заїздом"])

    # ➕ Додати бронювання
    with tab_add:
        if not guests:
            st.info("Немає гостей для бронювання. Додайте гостей.")
        elif not rooms:
            st.info("Немає доступних кімнат для бронювання.")
        else:
            with st.form("add_booking_form"):
                selected_guest = st.selectbox("Оберіть гостя", list(guest_dict.keys()))
                selected_room = st.selectbox("Оберіть кімнату", list(room_dict.keys()))
                check_in_str = st.date_input("Дата заїзду", value=datetime.date.today())
                check_out_str = st.date_input("Дата виїзду", value=datetime.date.today() + datetime.timedelta(days=1))
                submitted = st.form_submit_button("Додати бронювання")

                if submitted:
                    guest_id = guest_dict[selected_guest]
                    room_id = room_dict[selected_room]

                    if check_out_str <= check_in_str:
                        st.error("Дата виїзду повинна бути пізніше дати заїзду.")
                    else:
                        # Перевірка зайнятості кімнати
                        overlapping = session.query(Booking).filter(
                            Booking.room_id == room_id,
                            Booking.status == BookingStatus.Активно,
                            Booking.check_out > check_in_str,
                            Booking.check_in < check_out_str
                        ).count()
                        room_obj = session.query(Room).get(room_id)
                        max_guests = room_obj.type.max_guests

                        if overlapping >= max_guests:
                            st.error(f"Кімната вже зайнята на цей період. Максимальна кількість гостей: {max_guests}")
                        else:
                            booking = Booking(
                                guest_id=guest_id,
                                room_id=room_id,
                                check_in=check_in_str,
                                check_out=check_out_str,
                                status=BookingStatus.Активно,
                                price_per_night=room_obj.price_per_night
                            )
                            session.add(booking)
                            if overlapping + 1 >= max_guests:
                                room_obj.status = RoomStatus.Зайнятий
                            session.commit()
                            st.success("✅ Бронювання успішно створено.")
                            st.rerun()

    # 📋 Переглянути / Пошук бронювань
    with tab_view:
        keyword = st.text_input("Пошук бронювань за ім'ям гостя")
        if keyword:
            guests_found = session.query(Guest).filter(Guest.name.ilike(f"%{keyword}%")).all()
            guest_ids = [g.id for g in guests_found]
            bookings = session.query(Booking).filter(Booking.guest_id.in_(guest_ids)).all()
        else:
            bookings = session.query(Booking).all()

        if bookings:
            for b in bookings:
                guest = session.query(Guest).get(b.guest_id)
                room = session.query(Room).get(b.room_id)
                st.markdown(
                    f"**ID:** {b.id} | Гість: {guest.name if guest else 'Видалено'} | "
                    f"Кімната: {room.type.type if room else 'Видалено'} | "
                    f"Заїзд: {b.check_in} | Виїзд: {b.check_out} | Статус: {b.status.value} | Ціна за ніч: {b.price_per_night}"
                )
        else:
            st.info("Бронювання не знайдено.")

    # ⚙️ Редагувати / Видалити бронювання
    with tab_edit:
        bookings_all = session.query(Booking).all()
        if not bookings_all:
            st.info("Бронювання відсутні.")
        else:
            booking_dict = {f"ID {b.id} | Гість ID {b.guest_id} | Кімната ID {b.room_id}": b.id for b in bookings_all}
            selected_booking_key = st.selectbox("Оберіть бронювання для редагування", list(booking_dict.keys()))
            booking_id = booking_dict[selected_booking_key]
            booking = session.query(Booking).get(booking_id)

            with st.form("edit_booking_form"):
                new_status = st.selectbox("Статус бронювання", list(BookingStatus), index=list(BookingStatus).index(booking.status))
                new_check_in = st.date_input("Дата заїзду", booking.check_in)
                new_check_out = st.date_input("Дата виїзду", booking.check_out)
                update_btn = st.form_submit_button("Оновити бронювання")

                if update_btn:
                    if new_check_out <= new_check_in:
                        st.error("Дата виїзду повинна бути пізніше дати заїзду.")
                    else:
                        booking.status = new_status
                        booking.check_in = new_check_in
                        booking.check_out = new_check_out
                        session.commit()
                        st.success("✅ Бронювання оновлено.")
                        st.experimental_rerun()

            if st.button("🗑️ Видалити бронювання"):
                room_obj = session.query(Room).get(booking.room_id)
                if room_obj:
                    room_obj.status = RoomStatus.Вільний
                session.delete(booking)
                session.commit()
                st.success("🗑️ Бронювання видалено.")
                st.experimental_rerun()

    # 🔽 Сортування бронювань за датою заїзду
    with tab_sort:
        sorted_bookings = session.query(Booking).order_by(Booking.check_in).all()
        if sorted_bookings:
            for b in sorted_bookings:
                guest = session.query(Guest).get(b.guest_id)
                room = session.query(Room).get(b.room_id)
                st.markdown(
                    f"**ID:** {b.id} | Гість: {guest.name if guest else 'Видалено'} | "
                    f"Кімната: {room.type.type if room else 'Видалено'} | "
                    f"Заїзд: {b.check_in} | Виїзд: {b.check_out} | Статус: {b.status.value}"
                )
        else:
            st.info("Бронювання не знайдено.")

elif menu == "Меню послуг гостей":
    st.subheader("🛎️ Меню Гість-Сервіс")

    guests = session.query(Guest).all()
    guest_dict = {f"{g.name} (ID {g.id})": g.id for g in guests}

    services = session.query(Service).all()
    service_dict = {f"{s.name} (ID {s.id})": s.id for s in services}

    tab_add, tab_view, tab_search, tab_edit, tab_delete = st.tabs([
        "➕ Додати послугу гостю",
        "📋 Переглянути всі послуги",
        "🔍 Пошук послуг",
        "⚙️ Редагувати послугу",
        "🗑️ Видалити послугу"
    ])

    # ➕ Додати послугу гостю
    with tab_add:
        if not guests:
            st.info("Немає гостей. Спочатку додайте гостей.")
        elif not services:
            st.info("Немає послуг. Спочатку додайте послуги.")
        else:
            with st.form("add_guest_service_form"):
                selected_guest = st.selectbox("Оберіть гостя", list(guest_dict.keys()))
                selected_service = st.selectbox("Оберіть послугу", list(service_dict.keys()))
                submitted = st.form_submit_button("Додати послугу")

                if submitted:
                    guest_id = guest_dict[selected_guest]
                    service_id = service_dict[selected_service]

                    gs = GuestService(guest_id=guest_id, service_id=service_id)
                    session.add(gs)
                    session.commit()
                    st.success("✅ Послуга гостю додана.")
                    st.rerun()

    # 📋 Переглянути всі послуги гостей
    with tab_view:
        guest_services = session.query(GuestService).all()
        if guest_services:
            for gs in guest_services:
                st.markdown(
                    f"**ID:** {gs.id} | Гість: {getattr(gs.guest, 'name', 'Видалено') if hasattr(gs, 'guest') and gs.guest else 'Видалено'} | "
                    f"Послуга: {getattr(gs, 'service', None).name if getattr(gs, 'service', None) else 'Видалено'} "
                    #f"**ID:** {gs.id} | Гість: {gs.guest.name if gs.guest else 'Видалено'} | "
                    #f"Послуга: {gs.service.name if gs.service else 'Видалено'} | Дата: {gs.date}"
                )
        else:
            st.info("Послуги гостей не знайдені.")

    # 🔍 Пошук послуг гостей
    with tab_search:
        keyword = st.text_input("Введіть ім'я гостя або назву послуги для пошуку")
        if keyword:
            gs_list = session.query(GuestService).join(Guest).join(Service).filter(
                (Guest.name.ilike(f"%{keyword}%")) | (Service.name.ilike(f"%{keyword}%"))
            ).all()
            if gs_list:
                for gs in gs_list:
                    st.markdown(
                        f"**ID:** {gs.id} | Гість: {gs.guest.name if gs.guest else 'Видалено'} | "
                        f"Послуга: {gs.service.name if gs.service else 'Видалено'} | Дата: {gs.date}"
                    )
            else:
                st.info("Послуги гостей не знайдені за запитом.")

    # ⚙️ Редагувати послугу гостю
    with tab_edit:
        gs_all = session.query(GuestService).all()
        if not gs_all:
            st.info("Послуги гостей відсутні.")
        else:
            gs_dict = {f"ID {gs.id} | Гість ID {gs.guest_id} | Послуга ID {gs.service_id}": gs.id for gs in gs_all}
            selected_gs_key = st.selectbox("Оберіть послугу для редагування", list(gs_dict.keys()))
            gs_id = gs_dict[selected_gs_key]
            gs = session.query(GuestService).get(gs_id)

            with st.form("edit_guest_service_form"):
                new_guest = st.selectbox(
                    "Гість",
                    list(guest_dict.keys()),
                    index=list(guest_dict.values()).index(gs.guest_id) if gs.guest_id in guest_dict.values() else 0
                )
                new_service = st.selectbox(
                    "Послуга",
                    list(service_dict.keys()),
                    index=list(service_dict.values()).index(gs.service_id) if gs.service_id in service_dict.values() else 0
                )
                update_btn = st.form_submit_button("Оновити")

                if update_btn:
                    gs.guest_id = guest_dict[new_guest]
                    gs.service_id = service_dict[new_service]
                    gs.date = new_date
                    session.commit()
                    st.success("✅ Дані оновлено.")
                    st.experimental_rerun()

    # 🗑️ Видалити послугу гостю
    with tab_delete:
        gs_all = session.query(GuestService).all()
        if not gs_all:
            st.info("Послуги гостей відсутні.")
        else:
            gs_dict = {f"ID {gs.id} | Гість ID {gs.guest_id} | Послуга ID {gs.service_id}": gs.id for gs in gs_all}
            selected_gs_key = st.selectbox("Оберіть послугу для видалення", list(gs_dict.keys()))
            gs_id = gs_dict[selected_gs_key]
            gs = session.query(GuestService).get(gs_id)

            if st.button("Видалити послугу"):
                session.delete(gs)
                session.commit()
                st.success("🗑️ Послугу видалено.")
                st.experimental_rerun()

elif menu == "Меню оплат":
    st.subheader("💳 Меню оплат")

    tab_add, tab_view, tab_find, tab_edit, tab_delete = st.tabs([
        "➕ Додати оплату",
        "📋 Переглянути всі оплати",
        "🔍 Пошук оплат",
        "⚙️ Редагувати оплату",
        "🗑️ Видалити оплату"
    ])

    # ➕ Додати оплату
    with tab_add:
        # Отримати ID бронювань, які вже оплачено
        paid_booking_ids = [p.booking_id for p in session.query(Payment.booking_id).all()]
        # Активні бронювання без оплати
        unpaid_bookings = session.query(Booking).filter(
            Booking.status == BookingStatus.Активно,
            ~Booking.id.in_(paid_booking_ids)
        ).all()

        if not unpaid_bookings:
            st.info("Всі активні бронювання вже оплачені.")
        else:
            booking_dict = {
                f"ID {b.id} | Гість: {session.query(Guest).get(b.guest_id).name} | "
                f"Кімната: {session.query(Room).get(b.room_id).type.type} | "
                f"З {b.check_in} до {b.check_out}": b.id for b in unpaid_bookings
            }

            with st.form("add_payment_form"):
                selected_booking = st.selectbox("Оберіть бронювання для оплати", list(booking_dict.keys()))
                booking_id = booking_dict[selected_booking]
                booking = session.query(Booking).get(booking_id)

                num_nights = (booking.check_out - booking.check_in).days
                room_cost = num_nights * booking.price_per_night

                guest_services = session.query(GuestService).filter_by(guest_id=booking.guest_id).all()
                service_cost = 0
                for gs in guest_services:
                    service = session.query(Service).get(gs.service_id)
                    if service:
                        service_cost += service.price

                total_amount = room_cost + service_cost

                st.markdown(f"Ціна за номер: **{room_cost} грн**")
                st.markdown(f"Ціна за сервіси: **{service_cost} грн**")
                st.markdown(f"Загальна сума до сплати: **{total_amount} грн**")

                payment_method = st.selectbox("Спосіб оплати", [m.value for m in PaymentMethod])

                submitted = st.form_submit_button("Додати оплату")

                if submitted:
                    method_enum = PaymentMethod(payment_method)
                    payment = Payment(
                        booking_id=booking.id,
                        amount=total_amount,
                        date=datetime.date.today(),
                        method=method_enum
                    )
                    session.add(payment)
                    session.commit()
                    st.success("✅ Оплату додано.")
                    st.rerun()

    # 📋 Переглянути всі оплати
    with tab_view:
        payments = session.query(Payment).all()
        if not payments:
            st.info("Оплати не знайдені.")
        else:
            for p in payments:
                st.markdown(
                    f"**ID:** {p.id} | Бронювання ID: {p.booking_id} | "
                    f"Сума: {p.amount} грн | Дата: {p.date} | Метод: {p.method.value}"
                )

    # 🔍 Пошук оплат
    with tab_find:
        booking_id_input = st.text_input("Введіть ID бронювання для пошуку оплат")
        if booking_id_input:
            try:
                booking_id = int(booking_id_input)
                payments = session.query(Payment).filter_by(booking_id=booking_id).all()
                if payments:
                    for p in payments:
                        st.markdown(
                            f"**ID:** {p.id} | Бронювання ID: {p.booking_id} | "
                            f"Сума: {p.amount} грн | Дата: {p.date} | Метод: {p.method.value}"
                        )
                else:
                    st.info("Оплати не знайдені.")
            except ValueError:
                st.error("Невірний формат ID бронювання.")

    # ⚙️ Редагувати оплату
    with tab_edit:
        payments_all = session.query(Payment).all()
        if not payments_all:
            st.info("Оплати відсутні.")
        else:
            payment_dict = {f"ID {p.id} | Бронювання ID {p.booking_id}": p.id for p in payments_all}
            selected_payment_key = st.selectbox("Оберіть оплату для редагування", list(payment_dict.keys()))
            payment_id = payment_dict[selected_payment_key]
            payment = session.query(Payment).get(payment_id)

            with st.form("edit_payment_form"):
                new_amount = st.number_input("Сума", value=payment.amount, min_value=0.0, format="%.2f")
                new_date = st.date_input("Дата", value=payment.date)
                new_method = st.selectbox("Метод оплати", [m.value for m in PaymentMethod], index=[m for m in PaymentMethod].index(payment.method))
                update_btn = st.form_submit_button("Оновити оплату")

                if update_btn:
                    payment.amount = new_amount
                    payment.date = new_date
                    payment.method = PaymentMethod(new_method)
                    session.commit()
                    st.success("✅ Оплату оновлено.")
                    st.experimental_rerun()

    # 🗑️ Видалити оплату
    with tab_delete:
        payments_all = session.query(Payment).all()
        if not payments_all:
            st.info("Оплати відсутні.")
        else:
            payment_dict = {f"ID {p.id} | Бронювання ID {p.booking_id}": p.id for p in payments_all}
            selected_payment_key = st.selectbox("Оберіть оплату для видалення", list(payment_dict.keys()))
            payment_id = payment_dict[selected_payment_key]
            payment = session.query(Payment).get(payment_id)

            if st.button("🗑️ Видалити оплату"):
                session.delete(payment)
                session.commit()
                st.success("🗑️ Оплату видалено.")
                st.experimental_rerun()


# Закриття сесії
# session.close() — Streamlit не потребує цього напряму, сесія живе з процесом
