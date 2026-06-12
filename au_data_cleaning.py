import pandas as pd
import re

# ==========================================
# CONFIGURATION (Easy to update)
# ==========================================
INPUT_FILE = 'real_estate_leads.csv'
OUTPUT_FILE = 'melbourne_pm_leads_cleaned.csv'

# 1️⃣ Melbourne & Greater Metro Suburbs
# Add or remove suburbs here. Case doesn't matter (code auto-lowers it)
MELBOURNE_SUBURBS = {
    'melbourne', 'south yarra', 'carlton', 'richmond', 'north melbourne',
    'fitzroy', 'collingwood', 'south melbourne', 'essendon', 'docklands',
    'southbank', 'point cook', 'hawthorn', 'malvern', 'toorak', 'brunswick',
    'albert park', 'caulfield north', 'surrey hills', 'west melbourne',
    'cremorne', 'frankston', 'seaford', 'carrum downs', 'langwarrin',
    'mount eliza', 'sunbury', 'werribee', 'hoppers crossing', 'williams landing',
    'truganina', 'tarneit', 'manor lakes', 'dandenong', 'keysborough',
    'noble park', 'doveton', 'melton', 'cobblebank', 'melton south', 'melton west',
    'weir views', 'caroline springs', 'epping', 'thomastown', 'lalor',
    'south morang', 'wollert', 'mernda', 'mill park', 'mickleham', 'kalkallo',
    'coolaroo', 'roxburgh park', 'campbellfield', 'somerton', 'pakenham',
    'officer', 'beaconsfield', 'gembrook', 'cranbourne', 'cranbourne east',
    'cranbourne west', 'cranbourne north', 'dingley village', 'lyndhurst',
    'narre warren', 'hallam', 'chelsea heights', 'berwick', 'wheelers hill',
    'mulgrave', 'glen waverley', 'box hill', 'camberwell', 'kew', 'prahran',
    'st kilda', 'elwood', 'elsternwick', 'brighton', 'caulfield', 'moonee ponds',
    'ascot vale', 'maribyrnong', 'footscray', 'yarraville', 'williamstown',
    'altona', 'laverton', 'deer park', 'sunshine', 'braybrook', 'st albans',
    'keilor', 'taylors lakes', 'delahey', 'mount duneed', 'grovedale', 'belmont'
}

# 2️⃣ Property Management Keyword Pattern
# Matches: "Property Management", "PM", "Strata", "Rental", "Real Estate", "Leasing", etc.
# Remove "real\s*estate" if you want to EXCLUDE general sales-only agencies
PM_KEYWORDS = re.compile(
    r'(property\s*management|property\s*managers?|\spm\s|strata\s*management|rental\s*management|'
    r'asset\s*management|leasing|property\s*group|real\s*estate|owners?\s*corp|'
    r'body\s*corporate|rentals?|letting)',
    re.IGNORECASE
)

# ==========================================
# PROCESSING LOGIC
# ==========================================
# Load data
df = pd.read_csv(INPUT_FILE)

# Filter functions
def is_melbourne(city):
    if pd.isna(city): return False
    return str(city).strip().lower() in MELBOURNE_SUBURBS

def has_pm_service(name):
    if pd.isna(name): return False
    return bool(PM_KEYWORDS.search(str(name)))

# Apply location filter
df = df[df['City'].apply(is_melbourne)]

# Apply service keyword filter
df = df[df['Business Name'].apply(has_pm_service)]

# Remove duplicates (keeps only 1 row per website domain to avoid double-contacting)
df = df.drop_duplicates(subset=['Root Domain'], keep='first')

# Reset index & save
df = df.reset_index(drop=True)
df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Successfully cleaned & saved {len(df)} qualified leads to '{OUTPUT_FILE}'")