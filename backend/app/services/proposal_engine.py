from app.services.availability_matrix_service import (build_matrix)

def required_slots(duration_minutes):
    return (duration_minutes + 29) // 30

def find_candidates(matrix, min_people, slots_needed):
    candidates = []

    for day in matrix:
        times = list(matrix[day].keys())

        for i in range(len(times)):
            valid = True
            score = 0

            for j in range(slots_needed):
                if (i + j >= len(times)):
                    valid = False
                    break

                current_slot = (times[i + j])
                available = (matrix[day][current_slot])

                if (available < min_people):
                    valid = False
                    break

                score += available

            if valid:
                candidates.append(
                    {
                        "day": day,
                        "start": times[i],
                        "score": score
                    }
                )

    return candidates