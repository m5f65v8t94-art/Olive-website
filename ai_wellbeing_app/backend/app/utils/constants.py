"""
Application constants, crisis resources, non-clinical disclaimers, mode definitions, and realistic study notes templates.
"""

NON_CLINICAL_DISCLAIMER = (
    "Olive is a judgment-free medium to help you reflect, not a doctor or therapist. "
    "In urgent distress, connect to real-world support below."
)

GET_HELP_PRIVATELY_GUIDANCE = {
    "title": "Get Help (Privately)",
    "subtitle": "Confidential, respectful real-world support services when you need help beyond this website.",
    "trusted_adult_notice": (
        "You're not expected to handle everything on your own. If you can, consider talking to a trusted adult — such as a parent, guardian, teacher, school counsellor, or another adult you feel safe with. You can also use the resources below for additional support."
    ),
    "confidentiality_note": (
        "You can also ask the counsellor or support service what their confidentiality policy is and what information they may need to share with someone else before you tell them anything personal. Confidentiality rules can vary depending on the service and situation."
    ),
    "services": [
        {
            "id": "tele_manas",
            "name": "Tele-MANAS",
            "category": "Mental Health & Emotional Support",
            "description": "Comprehensive, 24/7 mental-health counseling by trained mental health professionals in multiple Indian languages.",
            "phone": "14416",
            "alt_phone": "1800-89-14416",
            "display_phone": "14416 / 1800-89-14416",
            "whatsapp": None,
            "availability": "24/7, Toll-Free",
            "call_link": "tel:14416",
            "alt_call_link": "tel:18008914416",
            "badge": "24/7 Toll-Free"
        },
        {
            "id": "childline",
            "name": "Child Helpline",
            "category": "Children & Teenagers",
            "description": "Dedicated 24/7 emergency outreach, protection, and supportive guidance for children and teenagers.",
            "phone": "1098",
            "alt_phone": None,
            "display_phone": "1098",
            "whatsapp": None,
            "availability": "24/7, Free for Youth",
            "call_link": "tel:1098",
            "badge": "24/7 Youth Helpline"
        },
        {
            "id": "meri_trustline",
            "name": "Meri Trustline",
            "category": "Online Safety & Cyberbullying",
            "description": "Specialized, confidential support for young people facing online safety issues, cyberbullying, digital threats, harassment, or harmful personal content online.",
            "phone": "6363 17 6363",
            "alt_phone": None,
            "display_phone": "6363 17 6363",
            "whatsapp": "6363 17 6363",
            "availability": "9 AM - 6 PM (Mon-Sat)",
            "call_link": "tel:+916363176363",
            "whatsapp_link": "https://wa.me/916363176363?text=Hi%2C%20I%20need%20some%20help%20and%20support%20regarding%20an%20online%20safety%20issue.",
            "badge": "Call & WhatsApp"
        },
        {
            "id": "cyber_crime",
            "name": "National Cyber Crime Helpline",
            "category": "Cybercrime & Online Harassment",
            "description": "Government helpline to report cybercrime, financial fraud, hacking, or serious online stalking and exploitation.",
            "phone": "1930",
            "alt_phone": None,
            "display_phone": "1930",
            "whatsapp": None,
            "availability": "24/7, National Helpline",
            "call_link": "tel:1930",
            "badge": "Cybercrime Portal"
        },
        {
            "id": "emergency_112",
            "name": "Emergency Services",
            "category": "Immediate Physical Danger",
            "description": "National emergency single-number support for police, medical ambulance, or fire assistance when someone is in immediate danger.",
            "phone": "112",
            "alt_phone": None,
            "display_phone": "112",
            "whatsapp": None,
            "availability": "24/7, Immediate Response",
            "call_link": "tel:112",
            "badge": "Emergency (112)"
        }
    ]
}

CONVERSATION_MODES = {
    "just_listen": {
        "id": "just_listen",
        "title": "Just Listen",
        "icon": "headphones",
        "short_description": "Listen and validate without rushing into solutions or advice.",
        "prompt_guideline": (
            "You are in 'Just Listen' mode. Your primary role is to be a warm, compassionate, "
            "and patient confidant (a supportive 'cool older sister'). Validate the user's emotions, show deep empathy, and mirror their feelings. "
            "DO NOT jump to problem-solving, DO NOT offer unsolicited advice, and DO NOT diagnose. "
            "Respond directly to what they said, and ask gentle follow-up questions when appropriate."
        )
    },
    "give_me_advice": {
        "id": "give_me_advice",
        "title": "Give Me Advice",
        "icon": "lightbulb",
        "short_description": "Practical, healthy suggestions specifically relevant to the user's situation.",
        "prompt_guideline": (
            "You are in 'Give Me Advice' mode. Offer gentle, realistic, and practical coping techniques "
            "tailored directly to their exact problem (never generic lists). "
            "Frame suggestions warmly as options they can try, never as medical prescriptions. "
            "Never diagnose or claim to know what is medically 'wrong'."
        )
    },
    "help_me_understand": {
        "id": "help_me_understand",
        "title": "Help Me Understand",
        "icon": "search",
        "short_description": "Explore and reflect on feelings without diagnostic labels.",
        "prompt_guideline": (
            "You are in 'Help Me Understand' mode. Help the user gently unpack, explore, and organize their "
            "thoughts and emotions. Ask reflective, open-ended questions. Avoid psychological jargon or diagnostic labels. "
            "Help them understand why they might feel this way without labeling or diagnosing."
        )
    },
    "help_me_tell_someone": {
        "id": "help_me_tell_someone",
        "title": "Help Me Tell Someone",
        "icon": "mail",
        "short_description": "Draft a message starter for someone in your life you trust.",
        "prompt_guideline": (
            "You are in 'Help Me Tell Someone' mode. Assist the user in putting their feelings into natural words. "
            "Help them draft natural, honest messages or conversation starters tailored for a parent, teacher, "
            "school counselor, trusted friend, or adult. Offer different tones (casual, direct, gentle)."
        )
    }
}

CRISIS_RESOURCES = [
    {
        "name": "Tele-MANAS",
        "description": "24/7 mental-health counseling support by government healthcare professionals.",
        "phone": "14416 / 1800-89-14416",
        "text": None,
        "website": "https://telemanas.mohfw.gov.in",
        "availability": "24/7, Toll-Free"
    },
    {
        "name": "Child Helpline",
        "description": "24/7 emergency phone outreach service for children and teenagers.",
        "phone": "1098",
        "text": None,
        "website": "https://wcd.nic.in",
        "availability": "24/7, Free for Youth"
    },
    {
        "name": "Meri Trustline",
        "description": "Specialized support for online safety, cyberbullying, and digital harassment.",
        "phone": "6363 17 6363",
        "text": "WhatsApp 6363 17 6363",
        "website": "https://meritrustline.com",
        "availability": "Mon-Sat (Call & WhatsApp)"
    },
    {
        "name": "National Cyber Crime Helpline",
        "description": "National portal for reporting cybercrime, harassment, and digital fraud.",
        "phone": "1930",
        "text": None,
        "website": "https://cybercrime.gov.in",
        "availability": "24/7"
    },
    {
        "name": "National Emergency Services",
        "description": "Single-number emergency support for immediate physical danger, police, or ambulance.",
        "phone": "112",
        "text": None,
        "website": None,
        "availability": "24/7"
    }
]

IMMEDIATE_DANGER_KEYWORDS = [
    "not sure i can keep myself safe", "cant keep myself safe", "can't keep myself safe",
    "cannot keep myself safe", "unable to keep myself safe", "not safe tonight",
    "not sure i'll make it through the night", "not sure ill make it through the night",
    "unsafe with myself", "can't stay safe", "cant stay safe", "cannot stay safe",
    "going to end it tonight", "kill myself tonight", "take my life tonight",
    "have a plan to die", "going to overdose", "about to hurt myself", "about to do it",
    "about to end my life", "saying goodbye forever", "goodbye forever",
    "don't trust myself tonight", "dont trust myself tonight", "can't promise i'll stay safe",
    "cant promise ill stay safe", "can't promise to stay safe", "right now i want to end it"
]

SUICIDE_SELF_HARM_KEYWORDS = [
    "thoughts about suicide", "thoughts of suicide", "thinking about suicide", "suicidal thoughts",
    "suicidal", "suicide", "kill myself", "killing myself", "end my life", "ending my life",
    "want to die", "wanna die", "wishing i was dead", "wish i was dead", "better off dead",
    "hurt myself", "hurting myself", "cut myself", "cutting myself", "self harm", "self-harm",
    "overdose", "slit my wrists", "bleed out", "can't go on living", "cant go on living",
    "cannot go on living", "don't want to live", "dont want to live", "hang myself",
    "take all my pills", "ending it all", "end it all"
]

SAFE_RIGHT_NOW_KEYWORDS = [
    "i'm safe right now", "im safe right now", "i am safe right now", "safe right now",
    "i'm safe", "im safe", "i am safe", "safe for now", "not in danger right now",
    "not going to do anything right now", "physically safe", "in a safe place",
    "safe at home", "i'm okay right now", "im ok right now", "safe at the moment"
]

NOT_TELLING_KEYWORDS = [
    "don't want to tell anyone", "dont want to tell anyone", "not ready to tell anyone",
    "not ready to tell someone", "don't want to tell someone", "dont want to tell someone",
    "scared to tell", "don't want my parents to know", "dont want my parents to know",
    "can't tell my parents", "cant tell my parents", "afraid to tell anyone",
    "keep it between us", "don't tell anyone", "dont tell anyone",
    "can't talk to anyone", "cant talk to anyone", "just between you and me",
    "promise not to tell", "don't tell my mom", "dont tell my mom", "don't tell my dad", "dont tell my dad"
]

SAFETY_CRISIS_KEYWORDS = list(set(SUICIDE_SELF_HARM_KEYWORDS + IMMEDIATE_DANGER_KEYWORDS + [
    "abuse", "hitting me", "touching me", "molested", "unsafe at home"
]))

DIAGNOSTIC_QUERIES = [
    "do i have depression", "do i have adhd", "do i have bipolar", "do i have bpd",
    "diagnose me", "am i depressed", "am i autistic", "am i bipolar", "what is wrong with me",
    "what mental illness do i have", "am i crazy", "is this schizophrenia", "do i have ocd"
]

STUDY_NOTES_SUBJECTS = [
    {
        "subject": "Biology",
        "topic": "Cell Structure & Organelles",
        "course": "AP / IB Biology — Unit 2: Cellular Organization",
        "last_edited": "Today at 3:42 PM",
        "breadcrumbs": ["Science", "Grade 11 Biology", "Cell Structure"],
        "summary": "Core structural components of eukaryotic and prokaryotic cells, membrane transport mechanisms, and organelle compartmentalization.",
        "sections": [
            {
                "heading": "1. Eukaryotic vs. Prokaryotic Cells",
                "content": "Prokaryotes (Bacteria, Archaea) lack membrane-bound nucleus; genetic material resides in nucleoid region. Circular plasmid DNA often present. Eukaryotes (Animals, Plants, Fungi) contain membrane-bound organelles with distinct biochemical microenvironments.",
                "bullets": [
                    "Plasma Membrane: Phospholipid bilayer with fluid mosaic model (amphipathic molecules).",
                    "Ribosomes: 70S in prokaryotes, 80S in eukaryotic cytoplasm and rough endoplasmic reticulum.",
                    "Endosymbiotic Theory: Mitochondria and Chloroplasts originated from engulfed aerobic bacteria."
                ]
            },
            {
                "heading": "2. Endomembrane System Flow",
                "content": "Nucleus (transcription to mRNA) → Rough ER (translation & peptide folding) → Transport Vesicles → Golgi Apparatus (cis face phosphorylation & glycosylation, trans face sorting) → Secretory Vesicles or Lysosomes.",
                "key_terms": ["Rough ER", "Golgi Apparatus", "Lysosome hydrolases", "Exocytosis"]
            },
            {
                "heading": "3. Mitochondria & ATP Generation",
                "content": "Inner mitochondrial membrane contains cristae to maximize surface area for electron transport chain (ETC) complexes and ATP Synthase (chemiosmosis gradient H+ across intermembrane space).",
                "formula": "C6H12O6 + 6O2 → 6CO2 + 6H2O + ~30-32 ATP"
            }
        ]
    },
    {
        "subject": "Economics",
        "topic": "Demand, Supply & Market Equilibrium",
        "course": "Intro to Microeconomics — Module 3",
        "last_edited": "Yesterday at 6:15 PM",
        "breadcrumbs": ["Social Sciences", "Economics 101", "Price Theory"],
        "summary": "Mechanisms of market price determination, determinants of demand/supply shifts, and elasticity coefficients.",
        "sections": [
            {
                "heading": "1. The Law of Demand & Substitution Effect",
                "content": "Inverse relationship between price (P) and quantity demanded (Qd), ceteris paribus. As price rises, purchasing power diminishes (Income Effect) and consumers substitute towards cheaper alternatives (Substitution Effect).",
                "bullets": [
                    "Demand Curve Shifters: Consumer income (normal vs inferior goods), prices of related goods (substitutes vs complements), tastes & preferences, future price expectations.",
                    "Movement along curve: ONLY caused by change in the good's own price."
                ]
            },
            {
                "heading": "2. Price Elasticity of Demand (PED)",
                "content": "Measures the responsiveness of quantity demanded to a change in price.",
                "formula": "PED = (% Change in Qd) / (% Change in Price) = (ΔQ / Q_avg) / (ΔP / P_avg)",
                "bullets": [
                    "|PED| > 1: Elastic (Luxury goods, many substitutes available).",
                    "|PED| < 1: Inelastic (Necessities, addictive goods, few alternatives).",
                    "|PED| = 1: Unit elastic (Total revenue is maximized)."
                ]
            },
            {
                "heading": "3. Market Equilibrium & Deadweight Loss",
                "content": "Equilibrium occurs where Qd = Qs. Price ceilings below equilibrium create shortages; price floors above equilibrium create surpluses and producer deadweight loss."
            }
        ]
    },
    {
        "subject": "Chemistry",
        "topic": "Chemical Equilibrium & Le Chatelier's Principle",
        "course": "General Chemistry II — Chapter 14",
        "last_edited": "Sep 1 at 11:20 AM",
        "breadcrumbs": ["Physical Sciences", "Chemistry", "Equilibrium"],
        "summary": "Dynamic equilibrium in reversible reactions, equilibrium constants (Kc, Kp), and stress response mechanisms.",
        "sections": [
            {
                "heading": "1. Dynamic Equilibrium Definition",
                "content": "Occurs in a closed system when the rate of the forward reaction equals the rate of the reverse reaction. Concentrations of reactants and products remain constant over time, though reactions continue simultaneously.",
                "formula": "aA + bB ⇌ cC + dD  ==>  Kc = ([C]^c * [D]^d) / ([A]^a * [B]^b)"
            },
            {
                "heading": "2. Le Chatelier's Principle Applications",
                "content": "If an external stress (concentration, temperature, pressure/volume) is applied to a system at equilibrium, the system shifts in the direction that partially offsets the stress.",
                "bullets": [
                    "Adding reactant: Shifts forward (to the right) to consume excess reactant.",
                    "Increasing pressure (decreasing volume): Shifts toward the side with fewer moles of gas.",
                    "Exothermic reaction (ΔH < 0): Increasing temperature shifts left (acts like adding product heat)."
                ]
            },
            {
                "heading": "3. Reaction Quotient (Q) vs. Equilibrium Constant (K)",
                "content": "If Q < K, forward reaction proceeds (shifts right). If Q > K, reverse reaction proceeds (shifts left). If Q = K, system is at equilibrium."
            }
        ]
    },
    {
        "subject": "History",
        "topic": "The Industrial Revolution (1760–1840)",
        "course": "World History — Era 7: Modern Transformations",
        "last_edited": "Aug 29 at 4:05 PM",
        "breadcrumbs": ["Humanities", "Modern World History", "Industrialization"],
        "summary": "Technological innovations, agrarian shift, urbanization patterns, and socioeconomic class reorganization in 18th-century Britain.",
        "sections": [
            {
                "heading": "1. Preconditions in Great Britain",
                "content": "Why Britain first? Abundant coal and iron ore deposits, capital accumulation from global trade empires, agricultural revolution producing labor surplus, stable patent laws, and insular geography with navigable waterways.",
                "bullets": [
                    "Enclosure Acts: Consolidated common land, driving rural laborers into industrial urban centers.",
                    "Steam Power: James Watt's condensation chamber innovation (1769) detached manufacturing from riverbanks."
                ]
            },
            {
                "heading": "2. Key Technological Inventions",
                "content": "Textiles led mechanization: John Kay's Flying Shuttle (1733), James Hargreaves' Spinning Jenny (1764), Richard Arkwright's Water Frame (1769), and Cartwright's Power Loom (1785).",
                "key_terms": ["Cottage Industry", "Factory System", "Urban Sprawl", "Proletariat"]
            },
            {
                "heading": "3. Socioeconomic Repercussions",
                "content": "Rapid demographic migration to Manchester, Birmingham, Leeds. Lack of sanitation infrastructure led to cholera outbreaks. Emergence of the industrial middle class (bourgeoisie) and organized labor movements (Chartism, Luddites)."
            }
        ]
    },
    {
        "subject": "Physics",
        "topic": "Newton's Laws of Motion & Classical Mechanics",
        "course": "Mechanics & Dynamics — Chapter 4",
        "last_edited": "Aug 31 at 2:10 PM",
        "breadcrumbs": ["STEM", "Physics 1", "Dynamics"],
        "summary": "Vector analysis of forces, inertia, acceleration under net force, action-reaction pairs, and friction coefficients.",
        "sections": [
            {
                "heading": "1. First & Second Laws of Motion",
                "content": "Law of Inertia: An object maintains constant velocity unless acted upon by a non-zero net external force. Second Law: Net force equals the time rate of change of momentum (F_net = m * a for constant mass).",
                "formula": "Σ F = m * a   |   F_friction = μ * N   |   p = m * v"
            },
            {
                "heading": "2. Free Body Diagrams & Inclined Planes",
                "content": "Resolution of gravitational force on angle θ: Parallel component F_parallel = m*g*sin(θ); Perpendicular component F_perp = m*g*cos(θ). Normal force N = m*g*cos(θ) on static incline.",
                "bullets": [
                    "Static Friction (μs): Maximum resistive force before motion begins (fs ≤ μs * N).",
                    "Kinetic Friction (μk): Constant resistive force during sliding motion (fk = μk * N, μk < μs)."
                ]
            },
            {
                "heading": "3. Newton's Third Law Pairs",
                "content": "For every interaction, forces occur in equal magnitude and opposite direction acting on DIFFERENT bodies. Action-reaction pairs never cancel out on a single free body diagram."
            }
        ]
    },
    {
        "subject": "Mathematics",
        "topic": "Differential Calculus & Derivatives",
        "course": "Calculus AB — Chapter 3: Differentiation",
        "last_edited": "Sep 1 at 9:45 AM",
        "breadcrumbs": ["Math", "Calculus", "Differentiation Rules"],
        "summary": "Limit definition of derivatives, product/quotient/chain rules, implicit differentiation, and tangent line equations.",
        "sections": [
            {
                "heading": "1. Definition of the Derivative",
                "content": "The derivative represents the instantaneous rate of change of a function f(x) at point x, defined geometrically as the slope of the tangent line.",
                "formula": "f'(x) = lim (h → 0) [f(x + h) - f(x)] / h"
            },
            {
                "heading": "2. Fundamental Differentiation Rules",
                "content": "Standard operational rules for computing derivatives of composite and algebraic functions without limits.",
                "bullets": [
                    "Power Rule: d/dx [x^n] = n * x^(n-1)",
                    "Product Rule: d/dx [u * v] = u' * v + u * v'",
                    "Quotient Rule: d/dx [u / v] = (u' * v - u * v') / v^2",
                    "Chain Rule: d/dx [f(g(x))] = f'(g(x)) * g'(x)"
                ]
            },
            {
                "heading": "3. Optimization & First Derivative Test",
                "content": "Set f'(x) = 0 or undefined to locate critical points. If f' changes from positive to negative, x is a local maximum. If f' changes from negative to positive, x is a local minimum."
            }
        ]
    },
    {
        "subject": "Geography",
        "topic": "Plate Tectonics & Seismic Activity",
        "course": "Physical Geography — Unit 4: Earth Systems",
        "last_edited": "Sep 2 at 1:15 PM",
        "breadcrumbs": ["Earth Sciences", "Geography 101", "Geomorphology"],
        "summary": "Lithospheric plate boundaries, subduction zones, continental drift evidence, seismic wave propagation (P and S waves), and volcanism.",
        "sections": [
            {
                "heading": "1. Plate Boundary Classifications",
                "content": "Interactions along plate margins determine seismic and volcanic hazard profiles worldwide.",
                "bullets": [
                    "Divergent Boundaries: Plates pull apart (Mid-Atlantic Ridge, East African Rift Valley), creating new oceanic crust via upwelling magma.",
                    "Convergent Boundaries: Subduction of denser oceanic crust beneath continental crust (Ring of Fire) or continental-continental collision (Himalayas).",
                    "Transform Boundaries: Lateral strike-slip faults (San Andreas Fault) generating high-magnitude shallow focus earthquakes without volcanism."
                ]
            },
            {
                "heading": "2. Seismic Wave Characteristics",
                "content": "Primary (P) waves are compressional longitudinal waves traveling through solids and liquids. Secondary (S) waves are transverse shear waves traveling only through solids, establishing Earth's liquid outer core shadow zone.",
                "formula": "Vp = √((K + 4/3 μ) / ρ)   |   Vs = √(μ / ρ)"
            }
        ]
    },
    {
        "subject": "English",
        "topic": "Narrative Structures & Motif Analysis",
        "course": "AP Literature & Composition — Module 2: Prose Analysis",
        "last_edited": "Today at 10:30 AM",
        "breadcrumbs": ["Humanities", "English Literature", "Critical Analysis"],
        "summary": "Exploration of recurring symbolic motifs, non-linear chronological sequencing, unreliable narrators, and socio-cultural subtext in modern literature.",
        "sections": [
            {
                "heading": "1. Freytag's Pyramid & Non-Linear Framing",
                "content": "Traditional dramatic arc (Exposition → Inciting Incident → Rising Action → Climax → Falling Action → Resolution) contrasted with in media res openers, epistolary frames, and stream-of-consciousness focalization.",
                "bullets": [
                    "Diegetic Levels: Intradiegetic narrators within the story world vs. extradiegetic omniscient observers.",
                    "Dramatic Irony: Discrepancy between reader omniscience and protagonist awareness.",
                    "Foil Characters: Juxtaposition designed to illuminate contrasting moral or psychological traits."
                ]
            },
            {
                "heading": "2. Symbolism vs. Leitmotif",
                "content": "A motif is a recurring thematic element (colors, weather phenomena, recurring phraseology) that accumulates symbolic resonance over the text's progression, reinforcing the core philosophical inquiry of the author.",
                "key_terms": ["Allegory", "Synecdoche", "Syntactical Pacing", "Catharsis"]
            }
        ]
    }
]

