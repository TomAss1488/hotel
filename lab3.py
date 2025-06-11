
def get_guest_data():
    print("Введіть особисті дані:")
    full_name = input("ПІБ: ")
    age = input("Вік: ")
    phone = input("Номер телефону: ")
    passport = input("Номер паспорта: ")

    data = (
        f"ПІБ: {full_name}\n"
        f"Вік: {age}\n"
        f"Телефон: {phone}\n"
        f"Паспорт: {passport}\n"
        "\n"
    )
    return data
        
def get_booking_data():
    print("\nВведіть дані для бронювання:")
    room_type = input("Тип номера (Стандарт/Люкс/Апартаменти): ")
    check_in = input("Дата заїзду (рррр-мм-дд): ")
    check_out = input("Дата виїзду (рррр-мм-дд): ")

    data = (
        f"Тип номера: {room_type}\n"
        f"Дата заїзду: {check_in}\n"
        f"Дата виїзду: {check_out}\n"
        "\n"
    )
    return data


def get_payment_data():
    print("\nВведіть дані для оплати:")
    amount = input("Сума до сплати ($): ")
    method = input("Спосіб оплати (готівка/карта): ")

    data = (
        f"Сума: {amount}$\n"
        f"Спосіб оплати: {method}\n"
        "---------------------------\n"
    )
    return data

def save_to_file(data, filename):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(data)

def main():
    guest_data = get_guest_data()
    booking_data = get_booking_data()
    payment_data = get_payment_data()

    save_to_file(guest_data, "guest_data.txt")
    save_to_file(booking_data, "guest_data.txt")
    save_to_file(payment_data, "guest_data.txt")

    print("\n Всі дані успішно збережено!")

if __name__ == "__main__":
    main()
