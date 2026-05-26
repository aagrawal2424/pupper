"""Determine today's content type based on day of week."""
from datetime import datetime


SCHEDULE = {
    0: "ugc",        # Monday
    1: "tip",        # Tuesday
    2: "ugc",        # Wednesday
    3: "product",    # Thursday
    4: "ugc",        # Friday
    5: "tip",        # Saturday
    6: "product",    # Sunday
}

DOG_TIPS = [
    ("Did you know? 🐾", "Dogs absorb nutrients best when supplements are given with food."),
    ("Vet-approved tip 🐾", "Omega-3s support your dog's coat, joints, AND brain health."),
    ("Daily reminder 🐾", "Consistency is key. Same time every day = best results."),
    ("Dog parent hack 🐾", "Hide supplements in a spoonful of peanut butter. Works every time."),
    ("Science says 🐾", "Dogs with joint support supplements are more active as they age."),
    ("Pupper tip 🐾", "Always check for third-party tested supplements. Your dog deserves the best."),
    ("Did you know? 🐾", "Probiotics can reduce anxiety AND improve digestion in dogs."),
]


def today_content_type() -> str:
    return SCHEDULE[datetime.utcnow().weekday()]


def get_tip_of_the_day() -> tuple[str, str]:
    day = datetime.utcnow().timetuple().tm_yday
    tip = DOG_TIPS[day % len(DOG_TIPS)]
    return tip
