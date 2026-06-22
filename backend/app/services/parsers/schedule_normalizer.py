from app.services.parsers.day_mapper import normalize_day

def normalize_rows(dataframe, mapping):
    rows = []

    for _, row in dataframe.iterrows():
        rows.append(
            {
                "activity": str(row[mapping["activity"]]).strip(),
                "day": normalize_day(row[mapping["day"]]),
                "start": row[mapping["start"]],
                "end": row[mapping["end"]]
            }
        )

    return rows