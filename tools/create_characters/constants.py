DATA_DIR = 'data/generated_actor_templates'

HEADER = """from src.models import ActorTemplate

{response}"""

PROMPT_TEMPLATE = """Please generate a profile based on an individual one might encounter in the United States. To be used for a background character.
Ensure the character is unique, reflecting the rich tapestry of American life. Ensure diversity in backgrounds, cultures, professions, and personalities, so the character feels unique and provides broad representation. Please incorporate flaws and character defects.
Please minimize repeated data and ensure that the character has a mix of positive and negative qualities. Each data point in the profile should provide new context.

{names_prompt}

{custom_prompt}

Here is the declaration for the ActorTemplate class. Use it to generate the data for each character profile.
### Start ActorTemplate Declaration ###
{actor_template_declaration}
### End ActorTemplate Declaration ###

Response Format Instructions: {format_instructions}
"""

PROMPT_FORMAT_INSTRUCTIONS = """Create an instance of an ActorTemplate class. It should look something like this:
john = ActorTemplate(
    # ...values go here
)

Guidelines:
- ONLY CREATE ONE INSTANCE OF THE ActorTemplate CLASS.
- Do not provide a last name for actors. Only first name. (IE 'Sarah' not 'Sarah Smith')
- ONLY respond with the generated data in the correct format for a python file. DO NOT INCLUDE ANYTHING ELSE.
- You MUST generate at least the [min] items for each Field but can generate 1 or 2 additional items when applicable.
- Ensure you put elements of a list on a new line. (Follow the example given in the ActorTemplate declaration)

Example of how to format a value (notice the spacing, tabs, and new lines):
background=[
        'Raised in the affluent part of Manhattan.',
        'Parents were high-powered NYC attorneys.',
        'Sent to a boarding school in Europe due to unruly behavior.',
        'Expelled from three Ivy League universities.'
    ],
"""

ACTOR_TEMPLATE_DECLARATION = '''
name: str = Field()

qualities: List[str] = Field("The three most important qualities about their personality and behaviour", [3], ['Focused', 'Rude', 'Intense'])

essence: List[str] = Field(
    "A one-sentence overview that tries to capture the character's personality and behavior expectations. Exclude career and other personal information.",
    """Liam is an ambitious go-getter with a sharp wit, admired for his strategic thinking but sometimes feared for his uncompromising standards."""
)

profile: List[str] = Field(
    "A short paragraph that tries to capture the character's personality and behavior expectations. Include their age, gender, ethnicity, and sexual preference. Exclude career and other personal information.",
    """Charvi, a 29-year-old Asian female, is known for her fervent advocacy in the workplace. Her dedication to her career and her fiery approach to diversity make her a formidable presence, balancing professional ambition with a personal passion for social issues."""
)

autobiography: Optional[str] = Field("A short bio written in the voice of the character.",
    """Hi there, I'm Sarah, a Cincinnati native driven by curiosity.
    My journey led me to Northwestern University, where I dove headfirst into the wonders of learning.
    Numbers always intrigued me, and I've earned a reputation as a quick learner, even if I've been known to trust a little too easily.
    Life has its ways of teaching us, right? <br/><br/> As for my outlook, I tend to see the world through an optimistic and progressive lens.
    Religion isn't my cup of tea; I prefer forging my own path. Family time is my anchor, especially with my parents.
    On the court, I'm a basketball enthusiast, and off the court, you'll find me engrossed in a podcast.
    I'm the outgoing one who spices life up with some punny jokes.
    But when it comes to motivation, well, let's just say I'm a work in progress.
    Procrastination, apathy, and inconsistency may pop up, but they're all part of my unique journey.
    <br/><br/> So, here I am, navigating life's twists and turns, with a smile and a thirst for what's next.')"""
)

behaviours=Behaviours(
    # THE CHARACTER MUST HAVE 5 POSITIVE BEHAVIOURS and 5 NEGATIVE BEHAVIOURS. Exclude specific career information.
    professional: Optional[str] = Field(
        "Adherence or indifference to professional standards.",
        ["Joe consistently upholds formal etiquette and corporate acumen.", "Joe neglects professional decorum, often appearing disheveled and unprepared."]
    )
    negotiation: Optional[str] = Field(
        "Skilled or underhanded in deal-making.",
        ["Emily skillfully navigates negotiations to achieve win-win outcomes.", "Emily uses manipulation to sway negotiations in her favor, disregarding fairness."]
    )
    social: Optional[str] = Field(
        "Charismatic or awkward in social settings.",
        ["Mike shines in social settings, making everyone feel included.", "Mike lacks social cues, often monopolizing conversations or making others uncomfortable."]
    )
    relational: Optional[str] = Field(
        "Capable or inept at relationship building.",
        ["Sandra fosters trust and cooperation in her relationships.", "Sandra burns bridges, using relationships solely for personal gain."]
    )
    diplomatic: Optional[str] = Field(
        "Graceful or clumsy in sensitive interactions.",
        ["Raj handles sensitive issues with grace, defusing tensions.", "Raj is blunt and often offends others when attempting to resolve sensitive matters."]
    )
    strategic: Optional[str] = Field(
        "Insightful or shortsighted in planning.",
        ["Alex anticipates future challenges and plans accordingly.", "Alex's lack of foresight leads to repeated crises and last-minute scrambles."]
    )
    dominance: Optional[str] = Field(
        "Confident leadership or overbearing control.",
        ["Patricia leads with confidence, inspiring her team.", "Patricia's domineering style stifles her team and breeds resentment."]
    )
    adversarial: Optional[str] = Field(
        "Challenging with integrity or with hostility.",
        ["Jordan engages in debates with respect, strengthening arguments.", "Jordan's argumentative nature turns every discussion into a bitter confrontation."]
    )
    confrontational: Optional[str] = Field(
        "Constructively direct or aggressively confrontational.",
        ["Chris addresses issues directly, promoting clear communication.", "Chris's confrontational approach often escalates conflicts unnecessarily."]
    )
    supportive: Optional[str] = Field(
        "Empathetically supportive or suffocatingly intrusive.",
        ["Taylor's support empowers others to overcome challenges.", "Taylor's overbearing sympathy often feels intrusive and disempowering."]
    )
),

identity=Identity(
    age: Optional[str] = Field("Age in years.", [18-90], ['35'])
    gender: Optional[str] = Field("Their gender", ['Female', 'Male', 'Non-binary'])
    sexual: Optional[str] = Field("Their preference", ['Heterosexual', 'Bi-sexual', 'Gay'])
    ethnicity: Optional[str] = Field("Their ethnicity", ['White', 'Black', 'Native American'])
),

traits=Traits(
    # EACH TRAIT MUS INCLUDE AT LEAST 1 NEGATIVE TRAIT. DO NOT QUANTIFY ANY TRAITS (IE 'Occasionally'). FAVOR 1 WORD VALUES.
    intellect: List[str] = Field("Intellectual traits", [3], ['Strategic', 'Perfectionist', 'Gullible'])
    emotion: List[str] = Field("Emotional traits", [3], ['Compassionate', 'Anxious', 'Depressed'])
    charisma: List[str] = Field("Charisma traits", [3], ['Charming', 'Offensive humor', 'Smug'])
    attitude: List[str] = Field("Attitude traits", [3], ['Determined', 'Impatient', 'Procrastinator'])
),

socioeconomic=Socioeconomic(
    education: Optional[str] = Field("Highest level of education.", ['M.S. Computer Science, MIT'])
    career: Optional[str] = Field("Their career field or interest", ['Lawyer', 'Fry cook', 'Bank Manager'])
    financial: Optional[str] = Field("Their class / financial status", ['Low-Income', 'Middle Class', 'New Money'])
    home: Optional[str] = Field("Living conditions.", ['Apartment in NYC with fiance'])
),

ideology=Ideology(
    religion: Optional[str] = Field("Their view of the world", ['Agnostic', 'Catholic', 'Muslim'])
    alignment: Optional[str] = Field("Their social views", ['Progressive', 'Conservative'])
    outlook: Optional[str] = Field("Their view of the world", ['Optimistic', 'Pessimistic', 'Apathetic'])
    party: Optional[str] = Field("Their political party alignment", ['Democrat', 'Green Party', 'Conservative', 'None'])
),

communication=Communication(
    vocab: Optional[str] = Field("Words complexity.", ['Verbose'])
    tone: Optional[str] = Field("Speaking/writing attitude/style.", ['Casual'])
    profanity: Optional[str] = Field("Swear/slang frequency.", ['Frequent'])
    dialect: Optional[str] = Field("Regional/social accent.", ['Southern'])
    lingo: Optional[str] = Field("Age group-specific slang.", ['Millennial'])
    jargon: Optional[str] = Field("Specialized terminology.", ['Medical'])
),

preferences=Preferences(
    loves: List[str] = Field("Things they love.", [7], ['Vintage Cars', 'French Films', 'Classical Music', 'Podcasts', 'Road Trips', 'Dogs', 'Minimalist Art'])
    hates: List[str] = Field("Things they hate.", [7], ['Fast Food', 'Reality TV', 'Video Games', 'Romantic Novels', 'Heavy Metal Music', 'Country Music', 'Social Media'])
    listening_preferences: List[str] = Field("Auditory likes", [4], ['Jazz', 'Led Zeppelin', 'True crime podcasts', 'Audiobooks'])
    reading_preferences: List[str] = Field("Reading likes", [4], ['Historical fiction', 'Scientific Journals', 'John Grisham', 'Biographies'])
    watching_preferences: List[str] = Field("Viewing likes", [4], ['News', 'Christopher Nolan', 'Korean dramas', 'Friends'])
    activity_preferences: List[str] = Field("Activity likes", [4], ['Running', 'Painting', 'Birdwatching', 'Guitar'])
    culinary_preferences: List[str] = Field("Food & drink likes", [4], ['Sushi lover', 'Hates spicy', 'Black coffee', 'Nut allergy'])
    travel_preferences: List[str] = Field("Travel likes", [4], ['Mountains', 'Historical Sites', 'Avoids cold', 'Camping enthusiast'])
),

expression=Expression(
    verbal_mannerisms: List[str] = Field("Text quirks.", [4], ['Uses "Umm" often', 'Says "Thumbs up!" to celebrate', 'Frequently uses "Indeed!"', 'Uses "Darling" to address friends'])
    humor: List[str] = Field("Type of humor they appreciate", [3], ['Uses Sarcasm when frustrated', 'Prefers dark humor and jokes about non-PC or taboo topics', 'Is often self-deprecating'])
    topics: List[str] = Field("Favorite topics.", [3], ['Astronomy: Calms anxiety by reflecting on the universe's vastness.', 'World History: Enjoys drawing parallels between historical events and current affairs.', 'Tech Innovations: Stays inspired by the ever-evolving capabilities of technology.'])
    pet_peeves: List[str] = Field("Annoyances.", [3], ['People who chew loudly', 'Gossiping', 'People who are late'])
    triggers: List[str] = Field("Topics/situations provoking strong emotional responses.", [3], ['Discussing personal finances', 'Racism', 'Climate change deniers'])
),

values=Values(
    beliefs: List[str] = Field("Fundamental beliefs.", [2], ['Everyone deserves a second chance', 'Hard work always pays off'])
    principles: List[str] = Field("Guiding principles.", [3], ['Loyalty', 'Authenticity', 'Respect'])
    influences: List[str] = Field("Major influences", [4], ['"The Glass Castle" by Jeanette Walls', 'Emma Watson', 'The Louvre Museum', '"The Office"', 'David Attenborough'], NEVER:Elon Musk. Please get creative!)
    dilemmas: List[str] = Field("Moral conflicts.", [2], ['Choosing personal gain vs collective good.', 'Personal life vs work life'])
    motivations: List[str] = Field("What drives this character?", [2], ['Curiosity', 'Drive for personal success'])
),

background=Background(
    hometown: Optional[str] = Field("Place of birth/upbringing.", ['Brooklyn, NY'])
    heritage: Optional[str] = Field("Their family origins", ['Scottish', 'Nigerian', 'Korean'])
    nationality: Optional[str] = Field("Where they have citizenship", ['American', 'Canadian', 'Mexican'])
    history: List[str] = Field("Key background facts", [5], ['Small town upbringing', 'Middle-class', 'Raised by single mother', '3 younger siblings', 'Moved to city for college'])
    experiences: List[str] = Field("Formative events", [2], ['Studying abroad in Paris', 'Natural disaster survivor'])
    roots: List[str] = Field("Cultural influences", [2], ['Raised in a collectivist society, valuing community over individual achievements.', 'Shaped by the discipline and structure of military school upbringing.'])
    challenges: List[str] = Field("Challenging decisions", [2], ['Career vs family', 'Leaving home country', 'Reporting friend for crime'])
),

memories=Memories(
    fond_memories: List[str] = Field("Warm recollections.", [3], ['Summers painting at Grandma’s cottage', 'Winning a school science competition', 'First date with Chris at a jazz café'])
    traumatic_memories: List[str] = Field("Distressing past events.", [3], ['Witnessing a severe car accident', 'Public humiliation during a college presentation', 'Sudden passing of a close friend abroad'])
    failures: List[str] = Field("Past failures", [3], ['Failed business', 'Broken engagement', 'Lost race for mayor'])
    achievements: List[str] = Field("Successes", [3], ['Published author', 'Saved someones life', 'Won a national competition'])
),

goals=Goals(
    short_term_goals: List[str] = Field("Short-term goals", [3], ['Save for trip', 'Learn to dance', 'Write a novel'])
    long_term_goals: List[str] = Field("Life objectives", [3], ['Start a family', 'Establish a business', 'Publish an Art History book'])
),

skills=Skills(
    formal_skills: List[str] = Field("Formal skills", [3], ['Advanced math', 'Piano', 'Carpentry'])
    informal_skills: List[str] = Field("Informal skills", [3], ['Cooking pasta sauce from grandmother', 'Self-taught guitar', 'Language learning'])
),

relationships=Relationships(
    family: List[str] = Field("Key family connections", [5], [
        'Mother, Linda - Early Guiding Force, Close bond', 
        'Grandmother, Shae - Renowned Painter, Inspirational', 
        'Brother, Alex - Financial Analyst, Estranged over inheritance', 
        'Fiance, Chris - Software Engineer, Childhood Friends turned lovers',
        'Cousin, Riley - Travel Blogger, Adventurous bonding during summer vacations'
    ])
    acquaintances: List[str] = Field("Key connections", [5], [
        'Best Friend, Jamie - Journalist, Bonded since college',
        'Colleague, Jane - Astrophysicist, Shares similar interests', 
        'Rival, James - Marketing Manager, Challenging work relationship', 
        'Mentor, Prof. Harold - Literature Professor, Shaped literary interests in high school',
        'Neighbor, Morgan - Florist, Friendly weekend chats and plant advice'
    ])
),

routine=Routine(
    weekday_routine: List[str] = Field("Typical workday", ['Morning coffee', 'Commute to work', 'Office tasks', 'Evening workout', 'Cook dinner', 'Watch TV''])
    weekend_routine: List[str] = Field("Typical day off", ['Sleep in', 'Brunch with friends', 'Grocery shopping', 'Visit a local park', 'Movie night at home', 'Read a book'])
    breaking_routine: List[str] = Field("Interruptions of routine", ['Visits family in China every Christmas', 'Goes camping twice a year'])
),

internal=Internal(
    secrets: List[str] = Field("Hidden info.", [3], ['In love with best friend but its not mutual', 'Mom is fighting cancer', 'Struggles with anxiety'])
    fears: List[str] = Field("Fears & anxieties", [3], ['Flying', 'Public speaking'', 'Aging'])
    dreams: List[str] = Field("Hopes and desires.", [3], ['Visit Japan', 'Write a book', 'Own a vineyard'])
    regrets: List[str] = Field("Past regrets or missed opportunities.", [3], ['Not traveling when younger', 'Not pursuing a career in art', 'Not reconnecting with estranged mother'])
),

physical=Physical(
    appearance: List[str] = Field("Physical attributes", [7], ['Petite', 'Black Hair', 'Light Skin', 'Brown Eyes', 'Button Nose', 'Sleek Hair', 'Clean cut'])
    fashion: List[str] = Field("Fashion style", [3], ['Always in Heels', 'Designer Glasses', 'Bohemian', 'Classic', 'Sporty', 'Casual chic'])
    health: List[str] = Field("Physical/mental state.", [2], ['Fit', 'Diabetes'])
),

image=Image(
    color_palette: List[str] = Field("Three color that captures various facets of their personality, energy, and aura. Vary use of analogous, complementary and triadic palettes, saturation and value.", ['Deep Blue', 'Emerald Green', 'Radiant Gold'])
    image_description: Optional[str] = Field("Image description. Use the color_palette colors, one for the background, one for their clothing, and one for their accent piece. The environment should be energetic. Specify a location typical of profile pic, like on vacation or in a social setting. Have them doing something. Describe their expression, the Time of Day, if we are inside out outdoors.", """Tall 30-something Indian woman with medium skin, brown eyes, and curly brown hair. She's dressed in an Emerald Green business casual attire against a Deep Blue backdrop. A Radiant Gold scarf flows elegantly around her neck. Discussing animatedly with colleagues at a tech conference. Engaging smile on her face. Late afternoon. Indoor. Background showcases the buzz of a bustling tech event."""])
    image_prompt: Optional[str] = Field(
        description="Used to generate the image of the person. Format exactly like [preamble] + [name] + [image_description]. Copy the preamble exactly without changing it. Copy the exact image_description without changing it. preamble='/imagine prompt:oil painting. digital painting. closeup headshot. detailed face. messy splotchy abstract background.'",
    )
),
'''