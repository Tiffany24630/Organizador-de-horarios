from datetime import datetime
from datetime import timedelta
from datetime import datetime
from backend.app.models.enums import DayOfWeek
from app.services.availability_service import (get_group_people, get_busy_blocks)

def generate_time_slots(start="06:00", end="23:00"):
    slots = []

    current = datetime.strptime(start, "%H:%M")
    limit = datetime.strptime(end, "%H:%M")

    while current < limit:
        slots.append(current.strftime("%H:%M"))

        current += timedelta(minutes=10)

    return slots

def create_empty_matrix():
    matrix = {}

    slots = generate_time_slots()

    for day in DayOfWeek:
        matrix[day.value] = {}

        for slot in slots:
            matrix[day.value][slot] = 0

    return matrix

def slot_inside_block(slot, start_time, end_time):
    slot_dt = datetime.strptime(slot, "%H:%M")
    start_dt = datetime.strptime(start_time.strftime("%H:%M"), "%H:%M")
    end_dt = datetime.strptime(end_time.strftime("%H:%M"), "%H:%M")

    return (start_dt <= slot_dt < end_dt)

def build_matrix(group_id, db):
    matrix = create_empty_matrix()
    people = get_group_people(group_id, db)
    total_people = len(people)
    slots = generate_time_slots()

    for day in matrix:
        for slot in slots:
            available_count = total_people

            for person_id in people:
                blocks = get_busy_blocks(person_id, db)

                occupied = False

                for block in blocks:
                    if (block.day_of_week.value != day):
                        continue

                    if slot_inside_block(slot, block.start_time, block.end_time):
                        occupied = True
                        break

                if occupied:
                    available_count -= 1

            matrix[day][slot] = (available_count)

    return matrix