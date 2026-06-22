from datetime import datetime
from app.models.accepted_schedule import AcceptedSchedule
from app.models.proposal_history import ProposalHistory
from app.models.enums import ProposalStatus
from app.models.proposal_history import ProposalHistory
from app.models.enums import ProposalStatus

def accept_proposal(proposal, db):
    proposal.status = ProposalStatus.ACCEPTED

    accepted = AcceptedSchedule(proposal_id=proposal.id_schedule)

    db.add(accepted)

    history = ProposalHistory(proposal_id=proposal.id_schedule, action="ACCEPTED")

    db.add(history)
    db.commit()

    return accepted

def reject_proposal(proposal, db):
    proposal.status = ProposalStatus.REJECTED

    history = ProposalHistory(proposal_id=proposal.id_schedule, action="REJECTED")

    db.add(history)
    db.commit()