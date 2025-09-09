import asyncio
from backend.autonomy import AutonomyManager
from backend.collaboration import CollaborationHub


def test_ask_clarifications_generates_three_questions_and_broadcasts():
    hub = CollaborationHub()
    events = []

    async def listener(event_type, payload):
        events.append((event_type, payload))

    hub.subscribe(listener)
    mgr = AutonomyManager(collaboration=hub)

    questions = asyncio.run(mgr.ask_clarifications("build a web app"))

    assert len(questions) == 3
    types = [e[0] for e in events]
    assert types[0] == "user_query"
    assert types.count("clarifying_question") == 3


def test_record_clarification_answers_broadcasts_and_signals_complete():
    hub = CollaborationHub()
    events = []

    async def listener(event_type, payload):
        events.append((event_type, payload))

    hub.subscribe(listener)
    mgr = AutonomyManager(collaboration=hub)

    asyncio.run(mgr.record_clarification_answers(["ans1", "ans2", "ans3"]))

    types = [e[0] for e in events]
    assert types.count("clarification_answer") == 3
    assert types[-1] == "clarifications_complete"
