from app.exceptions.common import AppError, NotFoundError


class UserNotFoundError(NotFoundError):
    pass


class SpecialistNotFoundError(NotFoundError):
    pass


class SpecialistInactiveError(AppError):
    pass


class ServiceNotFoundError(NotFoundError):
    pass


class ServiceInactiveError(AppError):
    pass


class ServiceNotAvailableError(AppError):
    pass


class AppointmentOutsideWorkingHoursError(AppError):
    pass


class AppointmentAlreadyOccupiedError(AppError):
    pass


class AppointmentNotFoundError(NotFoundError):
    pass


class AppointmentCannotBeCancelledError(AppError):
    pass


class AppointmentCannotBeConfirmedError(AppError):
    pass


class AppointmentCannotBeCompletedError(AppError):
    pass