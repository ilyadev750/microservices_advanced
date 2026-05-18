from fastapi import HTTPException


class BookingException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(BookingException):
    detail = "Объект не найден"


class AllRoomsAreBookedException(BookingException):
    detail = "Не осталось свободных номеров"


class UserAlreadyExistsException(BookingException):
    detail = "Пользователь уже существует"


class DateFromMoreDateToException(BookingException):
    detail = "Время заезда в отель меньше или равно времени выезда"


class HotelNotExistException(BookingException):
    detail = "Отель с выбранным id не существует"


class RoomNotExistException(BookingException):
    detail = "Номер с выбранным id не существует"


class BaseHTTPException(HTTPException):
    status_code = 500
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class HotelNotExistHTTPException(BaseHTTPException):
    status_code = 404
    detail = 'Отель не найден!'


class HotelHasRoomsHTTPException(BaseHTTPException):
    status_code = 409
    detail = 'Нельзя удалить отель, пока у него есть номера!'


class RoomNotExistHTTPException(BaseHTTPException):
    status_code = 404
    detail = 'Комната не найдена!'


class DateFromMoreDateToHTTPException(BaseHTTPException):
    status_code = 400
    detail = 'Дата заезда не может быть меньше или равна, чем дата выезда'


class DatesAreBusyHTTPException(BaseHTTPException):
    status_code = 409
    detail = 'Невозможно забронировать номер на выбранные даты!'


class ErrorTokenHTTPException(BaseHTTPException):
    status_code = 401
    detail = 'Неверный токен'