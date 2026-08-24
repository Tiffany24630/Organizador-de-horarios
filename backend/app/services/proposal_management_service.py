from app.models.accepted_schedule import AcceptedSchedule
from app.models.proposal_history import ProposalHistory
from app.models.enums import ProposalStatus
from app.models.activity import Activity
from app.models.time_block import TimeBlock

def accept_proposal(proposal, db):
    if proposal.status == ProposalStatus.ACCEPTED:
        return proposal.accepted_schedule

    proposal.status = ProposalStatus.ACCEPTED

    accepted = AcceptedSchedule(proposal_id=proposal.id_schedule)

    db.add(accepted)

    history = ProposalHistory(proposal_id=proposal.id_schedule, action="ACCEPTED")

    db.add(history)

    # An accepted proposal becomes a normal calendar activity for every selected
    # participant, so it remains visible and editable in each personal schedule.
    for participant in proposal.group.participants:
        activity = Activity(
            person_id=participant.person_id,
            name=proposal.group.name,
            type="GROUP_EVENT",
            description=f"Actividad grupal aceptada: {proposal.name}",
        )
        db.add(activity)
        db.flush()
        for session in proposal.sessions:
            db.add(TimeBlock(
                activity_id=activity.id_activity,
                day_of_week=session.day_of_week,
                start_time=session.start_time,
                end_time=session.end_time,
            ))
    db.commit()

    return accepted

def reject_proposal(proposal, db):
    proposal.status = ProposalStatus.REJECTED

    history = ProposalHistory(proposal_id=proposal.id_schedule, action="REJECTED")

    db.add(history)
    db.commit()
