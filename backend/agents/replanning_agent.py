import json
from typing import Dict, List, Any

from llm_service import generate_response

REPLANNING_SYSTEM_PROMPT = """
You are a highly intelligent study-replanning assistant.
You will be provided with:
1. The student's current weekly study schedule (JSON).
2. The details of a study session they just missed or failed to complete.

Your task is to intelligently handle this missed session without blindly moving it to the next day.

Step 1 — Analyze importance of the missed session:
- Is it preparation for an upcoming class (e.g. next day)?
- Is there a nearby assessment or deadline?
- Is it a core/foundational topic?
- Or is it just general revision?

Step 2 — Decide the best action based on importance:
- High importance: reschedule soon (e.g., next available day or earliest slot).
- Medium importance: reschedule but not necessarily next day, or merge with an existing session of the same module.
- Low importance: optionally skip OR push to later in the week to avoid overloading the schedule.

Step 3 — Apply minimal changes:
- Do NOT regenerate the full weekly plan.
- Only adjust what is exactly necessary to accommodate the change.
- Keep the timetable stable and realistic.
- Avoid creating overloaded days. 
- Respect existing constraints (classes, commitments, study limits).
- Keep behavior practical and human-like.
- Prioritize academic urgency over perfect scheduling.

Return ONLY valid JSON with this exact schema:
{
  "patched_timetable": [ ... complete updated schedule array ... ],
  "explanation": "A short, one-sentence UI message explaining the change (e.g. 'Session merged with Thursday slot', or 'Skipped due to low priority').",
  "is_rescheduled": true
}
If the session is entirely skipped because of low priority and no new timeslot is found, return "is_rescheduled": false.
Do not output any markdown formatting, only raw JSON.
""".strip()

def evaluate_and_replan(
    current_timetable: List[Dict[str, Any]],
    missed_session: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Evaluates a missed session and returns a patched timetable.
    """
    prompt = f"""
Current Timetable:
{json.dumps(current_timetable, indent=2)}

Missed Session:
Module: {missed_session.get('module_name')}
Original Date/Time: {missed_session.get('actual_start')} to {missed_session.get('actual_end')}
Planned Duration: {missed_session.get('planned_duration_mins')} minutes

Please output the updated timetable JSON.
"""
    content_blocks = [{"text": prompt}]
    
    try:
        response_text = generate_response(
            content_blocks,
            system_prompt=REPLANNING_SYSTEM_PROMPT,
            max_tokens=4000
        )
        
        # Clean up possible markdown wrappers
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        result = json.loads(text.strip())
        print(f"[ReplanningAgent] Replanning successful. is_rescheduled={result.get('is_rescheduled')}, explanation={result.get('explanation')}")
        print(f"[ReplanningAgent] Original timetable had {len(current_timetable)} sessions, patched has {len(result.get('patched_timetable', []))} sessions")
        return result
    except Exception as e:
        print(f"[ReplanningAgent] Replanning failed: {e}")
        return {"is_rescheduled": False, "explanation": "Replanning failed due to an error.", "patched_timetable": current_timetable}
