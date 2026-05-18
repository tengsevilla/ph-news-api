# Pure data — no imports. Keyword dicts used by nlp.py for rule-based classification.

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "politics": [
        "senate", "congress", "house of representatives", "president", "senator",
        "representative", "election", "bill", "ordinance", "pork barrel",
        "cha-cha", "charter change", "impeach", "resign", "recall", "campaign",
        "partido", "comelec", "proclamation", "executive order",
    ],
    "economy": [
        "peso", "inflation", "gdp", "bsp", "bangko sentral", "budget", "tax",
        "tariff", "smuggling", "boi", "neda", "economic", "trade", "import",
        "export", "privatization", "interest rate", "foreign investment",
        "remittance", "poverty", "unemployment", "fiscal", "deficit",
    ],
    "health": [
        "hospital", "health", "disease", "outbreak", "dengue", "covid",
        "tuberculosis", "doh", "philhealth", "vaccine", "medicine", "doctor",
        "nurse", "pandemic", "malnutrition", "mental health", "dialysis",
    ],
    "weather": [
        "typhoon", "bagyo", "flood", "baha", "earthquake", "lindol",
        "eruption", "pagasa", "storm signal", "low pressure area", "monsoon",
        "habagat", "amihan",
    ],
    "crime": [
        "killed", "murder", "robbery", "kidnapping", "drug bust", "shabu",
        "arrested", "graft", "corruption", "plunder", "syndicate", "carnapping",
        "estafa", "human trafficking",
    ],
    "education": [
        "school", "student", "teacher", "deped", "ched", "university", "college",
        "enrollment", "tuition", "k-12", "scholarship", "free tuition",
        "out of school", "literacy",
    ],
    "environment": [
        "mining", "deforestation", "pollution", "climate change", "denr",
        "protected area", "wildlife", "coral reef", "plastic waste",
        "global warming", "carbon", "mangrove", "illegal logging",
    ],
    "disaster": [
        "calamity", "relief", "evacuation", "ndrrmc", "fire", "nasunog",
        "sinunog", "landslide", "collapsed", "sinking", "explosion",
    ],
    "international": [
        "china", "united states", "us-", "asean", "united nations", "foreign",
        "diplomatic", "embassy", "west philippine sea", "territorial dispute",
        "bilateral", "treaty", "sanctions",
    ],
    "sports": [
        "basketball", "pba", "boxing", "sea games", "olympics", "athlete",
        "fiba", "uaap", "ncaa", "gold medal", "tournament",
    ],
    "technology": [
        "digital", "internet", "app", "startup", "artificial intelligence",
        "cybersecurity", "social media", "e-government", "fintech",
        "telecommunications", "5g", "dito", "globe", "smart",
    ],
    "social": [
        "ofw", "labor", "family", "community", "barangay", "lgbtq", "women",
        "child", "poverty alleviation", "social protection", "indigenous",
    ],
}

# Keyword lists per sector slug. 2+ matches = high intensity; 1 match = medium.
SECTOR_KEYWORDS: dict[str, list[str]] = {
    "farmer": [
        "farm", "farmer", "agriculture", "palay", "rice", "corn", "crop",
        "harvest", "department of agriculture", "nfa", "fertilizer",
        "irrigation", "agrarian", "agricultural",
    ],
    "fisherman": [
        "fisherman", "fishing", "fisheries", "bfar", "pangisda",
        "fishermen", "seaweed", "aquaculture",
    ],
    "miner": ["mining", "mine", "miner", "mineral", "ore", "quarry"],
    "forest_worker": [
        "forest", "logging", "timber", "reforestation", "tree planting",
    ],
    "health_worker": [
        "nurse", "doctor", "physician", "health worker", "medical staff",
        "hospital staff", "philhealth", "midwife", "barangay health worker",
    ],
    "social_worker": ["social worker", "dswd", "social welfare", "social protection"],
    "senior_citizen": [
        "senior citizen", "elderly", "pensioner", "sss pension",
        "gsis pension", "osca", "old age",
    ],
    "pwd": [
        "person with disability", "pwd", "disabled", "disability",
        "special needs", "persons with disabilities",
    ],
    "teacher": [
        "teacher", "guro", "public school teacher", "classroom",
        "deped teacher", "school faculty",
    ],
    "student": [
        "student", "pupil", "learner", "enrollment", "tuition",
        "school fees", "scholarship", "education loan",
    ],
    "labor_worker": [
        "labor", "worker", "employee", "dole", "endo", "contractual",
        "minimum wage", "wage order", "regularization", "labor union",
        "strike", "trabaho", "kasambahay law",
    ],
    "kasambahay": [
        "kasambahay", "house helper", "domestic worker", "yaya", "househelper",
    ],
    "security_guard": ["security guard", "security agency", "private security"],
    "bpo_worker": [
        "bpo", "call center", "outsourcing", "it-bpo", "contact center",
    ],
    "retail_worker": [
        "retail worker", "mall worker", "store worker", "cashier", "supermarket worker",
    ],
    "hospitality_worker": [
        "hotel worker", "restaurant worker", "tourism worker",
        "hospitality worker", "waiter", "cook",
    ],
    "driver": [
        "driver", "jeepney", "tricycle", "bus driver", "taxi driver",
        "ltfrb", "lto", "public transport", "angkas", "grab driver",
        "transport strike",
    ],
    "seafarer": [
        "seafarer", "seaman", "mariner", "maritime worker", "poea seafarer",
        "marina", "ship crew",
    ],
    "delivery_rider": [
        "delivery rider", "rider", "food delivery", "courier",
        "lalamove", "grab express",
    ],
    "business_owner": [
        "business owner", "entrepreneur", "msme", "sme", "negosyo",
        "dti", "businessmen", "small business", "enterprise",
    ],
    "vendor": [
        "vendor", "tindera", "street vendor", "palengke", "market vendor",
        "ukay-ukay", "ambulant vendor",
    ],
    "freelancer": [
        "freelancer", "gig worker", "self-employed", "independent contractor",
    ],
    "ofw": [
        "ofw", "overseas filipino", "migrant worker", "ofws",
        "remittance", "poea", "owwa",
    ],
    "government_employee": [
        "government employee", "civil servant", "csc", "public servant",
        "plantilla", "government worker",
    ],
    "barangay_official": [
        "barangay", "punong barangay", "barangay captain", "kagawad", "sk",
        "barangay official",
    ],
    "military_police": [
        "police", "pnp", "military", "afp", "soldier", "army", "navy",
        "air force", "law enforcement", "pcg",
    ],
    "engineer_architect": [
        "engineer", "architect", "engineering firm", "construction worker",
        "dpwh contractor",
    ],
    "lawyer": [
        "lawyer", "attorney", "legal counsel", "court", "judge",
        "judiciary", "bar exam", "ibp",
    ],
    "journalist": [
        "journalist", "reporter", "media worker", "press freedom",
        "nujp", "broadcaster",
    ],
    "it_tech_worker": [
        "it worker", "developer", "programmer", "software engineer",
        "tech worker", "ict worker",
    ],
    "artist_creative": [
        "artist", "actor", "musician", "performer", "creative worker",
        "entertainment", "film industry",
    ],
    "solo_parent": ["solo parent", "single parent", "single mother", "single father"],
    "informal_settler": [
        "informal settler", "urban poor", "demolition order",
        "relocation site", "nha", "socialized housing",
    ],
    "indigenous_people": [
        "indigenous", "lumad", "ancestral domain", "ncip", "tribal people",
        "ip community",
    ],
    "youth": [
        "youth", "kabataan", "teenager", "neet", "out of school youth",
        "sk", "sangguniang kabataan",
    ],
    "lgbtq": [
        "lgbtq", "lgbt", "gay", "lesbian", "transgender", "same-sex",
        "sogie", "gender equality",
    ],
    "prisoner_returnee": [
        "prisoner", "inmate", "bjmp", "bilibid", "jail", "detainee",
        "released prisoner", "parolee",
    ],
}

POLICY_TAG_KEYWORDS: dict[str, list[str]] = {
    "agricultural_subsidy": ["subsidy", "ayuda sa magsasaka", "farm subsidy", "fuel subsidy for farmers"],
    "land_reform": ["land reform", "carp", "dar", "agrarian reform", "land distribution"],
    "universal_healthcare": ["universal health care", "uhc", "philhealth reform", "health coverage"],
    "k12_reform": ["k-12", "k12", "senior high school", "deped curriculum"],
    "higher_education": ["ched", "state university", "free tuition", "sucs", "tertiary education"],
    "minimum_wage": ["minimum wage", "wage order", "nwpc", "wage hike", "living wage"],
    "endo_contractualization": ["endo", "contractualization", "regularization", "5-5-5 scheme"],
    "anti_corruption": ["corruption", "plunder", "graft", "ombudsman", "sandiganbayan"],
    "south_china_sea": ["west philippine sea", "south china sea", "spratlys", "scarborough shoal", "unclos"],
    "infrastructure": ["dpwh", "build build build", "road project", "bridge project", "mrt", "lrt", "subway"],
    "drug_policy": ["war on drugs", "illegal drugs", "shabu", "pdea", "drug lord", "tokhang"],
    "ofw_welfare": ["ofw protection", "poea reform", "owwa benefit", "migrant worker"],
    "disaster_preparedness": ["ndrrmc", "pagasa forecast", "disaster preparedness", "calamity fund", "early warning"],
    "public_transport": ["jeepney modernization", "ltfrb", "public transport reform", "transport strike"],
    "foreign_debt": ["foreign loan", "oda", "adb loan", "world bank loan", "imf", "foreign borrowing"],
    "tax_reform": ["train law", "create law", "tax reform", "excise tax", "bir", "customs reform"],
    "social_welfare": ["4ps", "pantawid pamilya", "dswd ayuda", "conditional cash transfer"],
    "jeepney_phaseout": ["jeepney phaseout", "jeep modernization", "puj modernization"],
}

# Keyword lists per PH region for region_primary detection
REGION_KEYWORDS: dict[str, list[str]] = {
    "NCR": [
        "metro manila", "manila", "quezon city", "makati", "pasig", "taguig",
        "mandaluyong", "pasay", "caloocan", "malabon", "navotas", "valenzuela",
        "marikina", "muntinlupa", "las piñas", "parañaque", "san juan", "pateros",
    ],
    "CAR": ["cordillera", "baguio", "benguet", "ifugao", "apayao", "abra", "kalinga"],
    "Region I - Ilocos": ["ilocos", "pangasinan", "la union", "ilocos norte", "ilocos sur", "vigan"],
    "Region II - Cagayan Valley": ["cagayan valley", "isabela", "quirino", "nueva vizcaya", "batanes", "tuguegarao"],
    "Region III - Central Luzon": ["central luzon", "bulacan", "pampanga", "tarlac", "zambales", "bataan", "nueva ecija", "aurora"],
    "Region IV-A - CALABARZON": ["calabarzon", "cavite", "laguna", "batangas", "rizal", "quezon province", "lucena"],
    "MIMAROPA": ["mimaropa", "palawan", "mindoro", "romblon", "marinduque", "puerto princesa"],
    "Region V - Bicol": ["bicol", "albay", "camarines", "sorsogon", "catanduanes", "masbate", "legazpi"],
    "Region VI - Western Visayas": ["western visayas", "iloilo", "bacolod", "negros occidental", "capiz", "aklan", "antique", "guimaras"],
    "Region VII - Central Visayas": ["central visayas", "cebu", "bohol", "negros oriental", "siquijor"],
    "Region VIII - Eastern Visayas": ["eastern visayas", "leyte", "samar", "tacloban", "biliran"],
    "Region IX - Zamboanga Peninsula": ["zamboanga", "zamboanga del norte", "zamboanga del sur", "zamboanga sibugay"],
    "Region X - Northern Mindanao": ["northern mindanao", "cagayan de oro", "bukidnon", "misamis", "lanao del norte", "camiguin"],
    "Region XI - Davao": ["davao", "davao del norte", "davao del sur", "davao oriental", "davao occidental"],
    "Region XII - SOCCSKSARGEN": ["soccsksargen", "south cotabato", "sultan kudarat", "sarangani", "general santos"],
    "Region XIII - CARAGA": ["caraga", "agusan", "surigao", "butuan"],
    "BARMM": ["bangsamoro", "maguindanao", "lanao del sur", "basilan", "sulu", "tawi-tawi", "cotabato city"],
}

# Title prefixes used to detect politician mentions via regex
POLITICIAN_TITLE_PREFIXES: list[str] = [
    "President", "Vice President", "VP",
    "Senate President", "Senate President Pro Tempore",
    "House Speaker", "Speaker",
    "Senator", "Sen.",
    "Representative", "Rep.", "Cong.",
    "Governor", "Gov.",
    "Mayor", "Vice Mayor",
    "Secretary", "Sec.",
    "Undersecretary", "Usec.",
    "Chief Justice", "Associate Justice",
    "Ombudsman",
    "General", "Police General", "Admiral", "Police Chief",
]
