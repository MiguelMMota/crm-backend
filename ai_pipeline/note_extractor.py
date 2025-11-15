"""
Note extraction module using LLM to generate structured notes from transcriptions.
"""
from .config import AIConfig


def extract_notes_from_transcription(transcription, relationships):
    """
    Extract structured notes from call transcription using LLM.

    Args:
        transcription: Full text transcription of the call
        relationships: List of Relationship objects involved in the call

    Returns:
        List of dicts with note data: [{'relationship_id': id, 'text': '...', 'importance': 7}]
    """
    try:
        if AIConfig.USE_OPENAI:
            return extract_with_gpt4(transcription, relationships)
        else:
            return extract_with_local_llm(transcription, relationships)
    except Exception as e:
        print(f"Note extraction error: {e}")
        return []


def extract_with_gpt4(transcription, relationships):
    """
    Extract notes using GPT-4.

    Args:
        transcription: Call transcription
        relationships: List of relationships

    Returns:
        List of note dicts
    """
    from openai import OpenAI

    client = OpenAI(api_key=AIConfig.OPENAI_API_KEY)

    # Build prompt
    relationship_names = [r.name for r in relationships]
    prompt = build_note_extraction_prompt(transcription, relationship_names)

    # Call GPT-4
    response = client.chat.completions.create(
        model=AIConfig.LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert at extracting important information from conversations and creating structured notes."},
            {"role": "user", "content": prompt}
        ],
        temperature=AIConfig.LLM_TEMPERATURE
    )

    # Parse response
    notes_text = response.choices[0].message.content
    return parse_notes_response(notes_text, relationships)


def extract_with_local_llm(transcription, relationships):
    """
    Extract notes using local LLM (e.g., Llama).
    This is a placeholder - actual implementation would use transformers or llama-cpp.

    Args:
        transcription: Call transcription
        relationships: List of relationships

    Returns:
        List of note dicts
    """
    # Placeholder: return simple extraction
    # TODO: Implement local LLM inference

    # For PoC, do simple keyword-based extraction
    notes = []
    for relationship in relationships:
        # Check if person's name is mentioned in transcription
        if relationship.name.lower() in transcription.lower():
            notes.append({
                'relationship_id': relationship.id,
                'text': f"Mentioned in conversation: {transcription[:200]}...",
                'importance': 5
            })

    return notes


def build_note_extraction_prompt(transcription, participant_names):
    """
    Build prompt for LLM to extract notes.

    Args:
        transcription: Call transcription
        participant_names: List of participant names

    Returns:
        Prompt string
    """
    participants_str = ", ".join(participant_names)

    prompt = f"""
You are analyzing a conversation transcript. Extract important, memorable information mentioned by or about each participant.

Participants in the call: {participants_str}

Transcript:
{transcription}

For each participant, extract:
1. Important facts they mentioned (personal updates, projects, plans, etc.)
2. Things they asked about or expressed interest in
3. Commitments or promises made
4. Any other noteworthy information

Format your response as:
PERSON: [Name]
NOTE: [Brief, clear note about something important]
IMPORTANCE: [1-10]

PERSON: [Name]
NOTE: [Another note]
IMPORTANCE: [1-10]

Only include truly important, actionable, or memorable information. Skip small talk.
"""
    return prompt


def parse_notes_response(notes_text, relationships):
    """
    Parse LLM response into structured notes.

    Args:
        notes_text: Text response from LLM
        relationships: List of Relationship objects

    Returns:
        List of note dicts
    """
    notes = []
    lines = notes_text.strip().split('\n')

    current_person = None
    current_note = None
    current_importance = 5

    for line in lines:
        line = line.strip()
        if line.startswith('PERSON:'):
            current_person = line.replace('PERSON:', '').strip()
        elif line.startswith('NOTE:'):
            current_note = line.replace('NOTE:', '').strip()
        elif line.startswith('IMPORTANCE:'):
            try:
                current_importance = int(line.replace('IMPORTANCE:', '').strip())
            except ValueError:
                current_importance = 5

            # Find matching relationship
            if current_person and current_note:
                for rel in relationships:
                    if rel.name.lower() == current_person.lower():
                        notes.append({
                            'relationship_id': rel.id,
                            'text': current_note,
                            'importance': current_importance
                        })
                        break

            # Reset
            current_person = None
            current_note = None
            current_importance = 5

    return notes
