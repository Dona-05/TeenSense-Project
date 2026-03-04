# --------------------------------
# SMARTER PARENTING ASSISTANT
# --------------------------------

intents = {
    "tantrum": ["tantrum", "crying", "screaming", "shouting", "meltdown"],
    "academic_stress": ["exam", "study", "marks", "stress", "pressure", "homework"],
    "anger_issue": ["angry", "anger", "temper", "irritated", "frustrated"],
    "communication_issue": ["silent", "not talking", "ignore", "avoiding", "withdrawn"]
}


def detect_intent(message):
    message = message.lower()
    scores = {}

    for intent, keywords in intents.items():
        scores[intent] = sum(keyword in message for keyword in keywords)

    best_intent = max(scores, key=scores.get)

    if scores[best_intent] == 0:
        return "general"

    return best_intent


def generate_response(intent):

    responses = {

        "tantrum": """It can be challenging when a child experiences a tantrum.
• Stay calm and avoid escalating the situation.
• Acknowledge their feelings without rewarding negative behavior.
• Offer limited choices to help them feel in control.
• Discuss the situation after they calm down.

If tantrums are frequent or intense, professional guidance may be beneficial.""",

        "academic_stress": """Academic stress is common during adolescence.
• Encourage open discussion about academic pressure.
• Focus on effort rather than just results.
• Help establish a balanced routine.
• Ensure proper rest and downtime.

If stress becomes overwhelming, consider speaking with educators or a counselor.""",

        "anger_issue": """Managing anger requires patience and consistency.
• Model calm behavior.
• Teach emotional labeling (e.g., 'I feel upset').
• Encourage healthy outlets like exercise or journaling.
• Avoid reacting harshly during emotional peaks.

Seek professional advice if anger becomes aggressive or persistent.""",

        "communication_issue": """Communication gaps can develop during adolescence.
• Create a safe and non-judgmental environment.
• Avoid forcing conversations.
• Spend relaxed, quality time together.
• Practice active listening.

If the situation continues, guided counseling may help rebuild communication.""",

        "general": """TeenSense provides general parenting guidance.
For specific or serious concerns, consulting a qualified professional is recommended.
Consistent empathy, patience, and open communication remain key."""
    }

    return responses.get(intent)


def chatbot_reply(message):
    intent = detect_intent(message)
    return generate_response(intent)