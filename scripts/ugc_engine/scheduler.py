"""Content schedule and copy library for the Pupper social engine."""
from datetime import datetime

SCHEDULE = {
    0: "ugc",                   # Monday
    1: "voiceover_tip",         # Tuesday
    2: "ugc",                   # Wednesday
    3: "product_story",         # Thursday
    4: "relatable_reel",        # Friday
    5: "ingredient_spotlight",  # Saturday
    6: "social_proof",          # Sunday
}

# Dog health tips — hook + voiceover body + caption
TIPS = [
    {
        "hook": "The silent joint crisis no one tells you about",
        "body": "Your dog's joints start breaking down at age five — and most owners don't catch it until it's painful. The good news? Daily omega-3 support maintains cartilage before damage sets in. Pupper's formula is designed exactly for this.",
        "caption": "Don't wait until they're limping 🐾 Link in bio. #doghealth #dogsupplements #dogjoints #pupper #dogsofinstagram",
        "search": "dog running playing",
    },
    {
        "hook": "Why your dog's gut controls everything",
        "body": "Eighty percent of your dog's immune system lives in their gut. Most commercial kibble destroys that balance over time. Pupper Probiotic restores the good bacteria your dog needs to thrive — better digestion, less shedding, calmer behavior.",
        "caption": "The supplement change that made everything better 🐾 #dogmom #doghealth #dogprobiotics #pupper",
        "search": "happy dog owner",
    },
    {
        "hook": "Your senior dog isn't slowing down — they're in pain",
        "body": "That afternoon nap habit your older dog picked up? It's often early-stage joint inflammation, not just aging. Pupper's glucosamine complex has shown real improvement in mobility within thirty days. Your senior dog deserves to feel young again.",
        "caption": "Senior dogs deserve so much better 🐾 #seniordogs #dogjoints #doghealth #pupper",
        "search": "senior dog happy",
    },
    {
        "hook": "What your dog's dull coat is actually telling you",
        "body": "A dull, dry coat is one of the first signs of omega-3 deficiency. It's not the shampoo — it's what's happening inside. Daily fish oil restores shine in as little as three weeks. Pupper sources from wild-caught Alaskan salmon. Nothing else.",
        "caption": "The glow-up was an inside job 🐾 #dogcoat #doghealth #dogsupplements #pupper",
        "search": "beautiful dog coat",
    },
    {
        "hook": "The one thing most dog parents get wrong with supplements",
        "body": "Dogs absorb nutrients up to forty percent better when supplements are given with food. Timing matters more than most people realize. Mix Pupper into your dog's morning meal and you'll see results faster — it's that simple.",
        "caption": "Small habit, big results 🐾 #dogparent #dogtips #dogsupplements #pupper",
        "search": "dog eating food",
    },
    {
        "hook": "Why is my dog so anxious — and it's not what you think",
        "body": "Anxiety in dogs is often a nutrient deficiency, not a behavior problem. Magnesium and B-vitamins regulate the canine nervous system. Pupper's calming blend addresses the root cause instead of just masking the symptoms.",
        "caption": "This changed everything for my anxious pup 🐾 #anxiousdog #doghealth #calmingdog #pupper",
        "search": "calm relaxed dog",
    },
    {
        "hook": "The math every dog owner needs to hear",
        "body": "The average vet bill for joint issues is over eight hundred dollars. Prevention with Pupper costs about one dollar and thirty cents a day. That's not a supplement — that's an investment in your dog's quality of life. The math writes itself.",
        "caption": "Prevention > treatment. Always. 🐾 #doghealth #dogsupplements #dogmom #pupper",
        "search": "dog owner happy",
    },
]

# Relatable text-on-screen reels — no voiceover, music-driven
RELATABLE_MOMENTS = [
    {
        "lines": [
            "When your dog refuses their food",
            "unless it has Pupper on it 😭",
            "they trained ME.",
        ],
        "caption": "The dog knows what they want 😭 #dogmom #dogsofinstagram #puppersupplements #doglife",
        "search": "cute dog begging",
    },
    {
        "lines": [
            "Me: I'll spend $200 on dog supplements",
            "Also me: can't afford coffee ☕",
            "Worth it.",
        ],
        "caption": "Dog tax is real and I have zero regrets #dogparent #dogsupplements #pupper #doglife",
        "search": "dog and owner cuddling",
    },
    {
        "lines": [
            "Day 1 of Pupper: skeptical 🤔",
            "Day 30 of Pupper:",
            "my dog is running circles around me 🐾",
        ],
        "caption": "30 days is all it takes. Don't sleep on this 🐾 #doghealth #dogsupplements #pupper",
        "search": "dog running playing energetic",
    },
    {
        "lines": [
            "POV: your 9-year-old dog",
            "runs to the door like they're 2 🐾",
            "Pupper joint support hits different.",
        ],
        "caption": "Senior dogs deserve to feel young again 🐾 #seniordogs #dogjoints #pupper",
        "search": "senior dog playing",
    },
    {
        "lines": [
            "Things I didn't expect to say:",
            "'The dog gets his vitamins before breakfast'",
            "Here we are.",
        ],
        "caption": "Dog parents understand 😂 #doglife #dogmom #dogvitamins #pupper",
        "search": "dog morning routine",
    },
]

# Ingredient spotlights — hero ingredient education with science
INGREDIENTS = [
    {
        "name": "Omega-3 Fish Oil",
        "benefit": "Joints. Coat. Brain. Heart. One ingredient — four systems.",
        "fact": "Clinical studies show 73% reduction in joint inflammation with daily omega-3 supplementation in dogs.",
        "cta": "Pupper Omega-3. Wild-caught Alaskan salmon. Zero fillers.",
        "script_context": "omega-3 fish oil benefits for dogs, joint support, coat health, sourced from wild-caught salmon",
        "search": "dog healthy shiny coat",
    },
    {
        "name": "Glucosamine",
        "benefit": "The building block your dog's cartilage is running out of.",
        "fact": "Dogs naturally produce glucosamine — but production drops by 50% after age six.",
        "cta": "Pupper Joint Support. What time takes, we give back.",
        "script_context": "glucosamine for dogs, cartilage support, joint health, aging dogs",
        "search": "dog jumping running",
    },
    {
        "name": "Probiotics",
        "benefit": "10 billion CFU per serving. Your dog's gut, fully restored.",
        "fact": "A balanced gut microbiome reduces allergies, anxiety, and inflammation — all at once.",
        "cta": "Pupper Probiotic. Clinically studied strains. Zero junk.",
        "script_context": "probiotics for dogs, gut health, immunity, digestion, anxiety reduction",
        "search": "happy healthy dog",
    },
    {
        "name": "Turmeric + Black Pepper",
        "benefit": "Nature's most powerful anti-inflammatory pairing.",
        "fact": "Piperine in black pepper increases curcumin absorption by 2,000% — the ratio matters.",
        "cta": "Pupper's formula gets this exactly right.",
        "script_context": "turmeric and black pepper for dogs, anti-inflammatory, curcumin bioavailability",
        "search": "dog outdoor active",
    },
]

# Social proof testimonial scenarios
SOCIAL_PROOF_SCENARIOS = [
    {
        "product_type": "joint supplement",
        "angle": "senior dog mobility transformation after 30 days",
        "search": "senior dog running playing",
    },
    {
        "product_type": "omega-3",
        "angle": "coat transformation and increased energy in 3 weeks",
        "search": "dog shiny coat happy",
    },
    {
        "product_type": "probiotic",
        "angle": "digestion improvement and reduced anxiety",
        "search": "calm happy dog",
    },
    {
        "product_type": "multivitamin",
        "angle": "overall energy and vitality improvement in adult dog",
        "search": "energetic playful dog",
    },
]


def today_content_type() -> str:
    return SCHEDULE[datetime.utcnow().weekday()]


def get_tip() -> dict:
    day = datetime.utcnow().timetuple().tm_yday
    return TIPS[day % len(TIPS)]


def get_relatable_moment() -> dict:
    day = datetime.utcnow().timetuple().tm_yday
    return RELATABLE_MOMENTS[day % len(RELATABLE_MOMENTS)]


def get_ingredient() -> dict:
    day = datetime.utcnow().timetuple().tm_yday
    return INGREDIENTS[day % len(INGREDIENTS)]


def get_social_proof_scenario() -> dict:
    day = datetime.utcnow().timetuple().tm_yday
    return SOCIAL_PROOF_SCENARIOS[day % len(SOCIAL_PROOF_SCENARIOS)]
