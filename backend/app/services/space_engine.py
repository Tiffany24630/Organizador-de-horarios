from app.models.space_reservation import SpaceReservation

def apply_space_restrictions(matrix: dict, reservations: list[SpaceReservation]):
    for reservation in reservations:
        day = reservation.day_of_week.value
        start = reservation.start_time.strftime("%H:%M")
        end = reservation.end_time.strftime("%H:%M")

        for slot in matrix[day]:
            if start <= slot < end:
                matrix[day][slot] = 0

    return matrix