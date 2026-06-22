from datetime import datetime
from app.models.accepted_schedule import AcceptedSchedule
from app.models.proposal_history import ProposalHistory
from app.models.proposed_schedule import ProposedSchedule
from app.models.enums import ProposalStatus

def accept_proposal(proposal_id, db):
    proposal = db.get(ProposedSchedule, proposal_id)

    if not proposal:
        raise ValueError("Proposal not found")

    proposal.status = (ProposalStatus.ACCEPTED)
    accepted = AcceptedSchedule(proposal_id=proposal_id, accepted_at=datetime.utcnow())
    history = ProposalHistory(proposal_id=proposal_id, action="ACCEPTED", created_at=datetime.utcnow())

    db.add(accepted)
    db.add(history)
    db.commit()

    return {
        "message":
        "Proposal accepted"
    }