import re
from dataclasses import dataclass

UNICODE_FRACTIONS = {
    "½": "1/2", "⅓": "1/3", "⅔": "2/3", "¼": "1/4", "¾": "3/4", "⅕": "1/5", "⅖": "2/5",
    "⅗": "3/5", "⅘": "4/5", "⅙": "1/6", "⅚": "5/6", "⅛": "1/8", "⅜": "3/8", "⅝": "5/8", "⅞": "7/8",
}

WORD_NUMBERS = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "half": 0.5,
}

UNIT_ALIASES = {
    "tsp": ["teaspoons", "teaspoon", "tsps", "tsp", "ts", "t"],
    "tbsp": ["tablespoons", "tablespoon", "tbsps", "tbsp", "tbs", "tbl", "tb"],
    "cup": ["cups", "cup", "c"],
    "fl oz": ["fluid ounces", "fluid ounce", "fl. oz", "fl oz", "floz"],
    "oz": ["ounces", "ounce", "oz"],
    "lb": ["pounds", "pound", "lbs", "lb"],
    "g": ["grams", "gram", "gr", "g"],
    "kg": ["kilograms", "kilogram", "kgs", "kg"],
    "mg": ["milligrams", "milligram", "mg"],
    "ml": ["milliliters", "milliliter", "millilitres", "millilitre", "mls", "ml"],
    "l": ["liters", "liter", "litres", "litre", "l"],
    "pint": ["pints", "pint", "pt"],
    "quart": ["quarts", "quart", "qt"],
    "gallon": ["gallons", "gallon", "gal"],
    "pinch": ["pinches", "pinch"],
    "dash": ["dashes", "dash"],
    "clove": ["cloves", "clove"],
    "can": ["cans", "can"],
    "jar": ["jars", "jar"],
    "package": ["packages", "package", "packets", "packet", "pkg"],
    "stick": ["sticks", "stick"],
    "slice": ["slices", "slice"],
    "piece": ["pieces", "piece"],
    "bunch": ["bunches", "bunch"],
    "sprig": ["sprigs", "sprig"],
    "stalk": ["stalks", "stalk"],
    "head": ["heads", "head"],
    "handful": ["handfuls", "handful"],
    "inch": ["inches", "inch", "in"],
}

ALIAS_TO_UNIT = {alias: unit for unit, aliases in UNIT_ALIASES.items() for alias in aliases}
UNIT_PATTERN = "|".join(sorted((re.escape(a) for a in ALIAS_TO_UNIT), key=len, reverse=True))

NUMBER = r"\d+\s+\d+/\d+|\d+/\d+|\d*\.\d+|\d+"
QUANTITY_RE = re.compile(
    rf"^(?P<low>{NUMBER})(?:\s*(?:-|to|or)\s*(?P<high>{NUMBER}))?"
    rf"|^(?P<word>{'|'.join(WORD_NUMBERS)})\b",
    re.IGNORECASE,
)
# The lookahead stops "c" matching the start of "chopped" and "in" the start of "into".
UNIT_RE = re.compile(rf"^(?P<unit>{UNIT_PATTERN})\.?(?=[\s,()]|$)(?:\s+of\b)?", re.IGNORECASE)
# Text after a comma is a note only if it reads like prep ("diced", "finely chopped", "to taste", "about 1 cup"),
# so commas inside a name ("boneless, skinless chicken") are kept.
NOTE_START_RE = re.compile(
    r"^(\w+(ed|ly)\b|to|at|for|plus|about|or|optional|divided|cut|room|such|preferably|with|without|if|as|\d)",
    re.IGNORECASE,
)
TRAILING_NOTE_RE = re.compile(r"\s+(to taste|as needed|for serving|for garnish|optional)$", re.IGNORECASE)


@dataclass
class ParsedIngredient:
    quantity: float | None = None
    quantity_max: float | None = None
    unit: str | None = None
    name: str | None = None
    note: str | None = None


def _normalize(text: str) -> str:
    for char, fraction in UNICODE_FRACTIONS.items():
        text = re.sub(rf"(\d)\s*{char}", rf"\1 {fraction}", text)
        text = text.replace(char, fraction)
    text = text.replace("⁄", "/").replace("–", "-").replace("—", "-")
    text = re.sub(r"^[\s•*▢□◦-]+", "", text)
    text = re.sub(r"(\d)([a-zA-Z])", r"\1 \2", text)
    return re.sub(r"\s+", " ", text).strip()


def _split_parentheses(text: str) -> tuple[str, list[str]]:
    outside: list[str] = []
    groups: list[str] = []
    depth = 0
    current = ""
    for char in text:
        if char == "(":
            if depth:
                current += char
            depth += 1
        elif char == ")" and depth:
            depth -= 1
            if depth:
                current += char
            else:
                groups.append(current)
                current = ""
                outside.append(" ")
        elif depth:
            current += char
        elif char != ")":
            outside.append(char)
    if current:
        groups.append(current)
    cleaned = [g.strip(" ,;") for g in groups]
    return re.sub(r"\s+", " ", "".join(outside)).strip(), [g for g in cleaned if g]


def _to_number(token: str) -> float:
    whole = 0.0
    parts = token.split()
    if len(parts) == 2:
        whole = float(parts[0])
        token = parts[1]
    if "/" in token:
        numerator, denominator = token.split("/")
        return whole + float(numerator) / float(denominator)
    return whole + float(token)


def _match_unit(rest: str) -> tuple[str | None, str]:
    match = UNIT_RE.match(rest)
    if not match:
        return None, rest
    alias = match.group("unit")
    # Capital T is a common shorthand for tablespoon and lowercase t for teaspoon.
    if alias == "T":
        unit = "tbsp"
    elif alias == "t":
        unit = "tsp"
    else:
        unit = ALIAS_TO_UNIT[alias.lower()]
    return unit, rest[match.end():].strip()


def parse_ingredient(raw: str) -> ParsedIngredient:
    text = _normalize(raw)
    result = ParsedIngredient()
    text, notes = _split_parentheses(text)

    match = QUANTITY_RE.match(text)
    if match:
        rest = text[match.end():].strip()
        if match.group("word"):
            unit, after_unit = _match_unit(rest)
            word = match.group("word").lower()
            if word in ("a", "an") and unit is None:
                rest = text
            else:
                result.quantity = WORD_NUMBERS[word]
                result.unit, rest = unit, after_unit
        else:
            result.quantity = _to_number(match.group("low"))
            if match.group("high"):
                result.quantity_max = _to_number(match.group("high"))
            result.unit, rest = _match_unit(rest)
    else:
        rest = text

    parts = rest.split(",")
    for i in range(1, len(parts)):
        if NOTE_START_RE.match(parts[i].strip()):
            notes.append(",".join(parts[i:]).strip())
            rest = ",".join(parts[:i])
            break

    trailing = TRAILING_NOTE_RE.search(rest)
    if trailing:
        notes.insert(0, trailing.group(1))
        rest = rest[: trailing.start()]

    name = rest.strip(" ,.-")
    result.name = name or None
    note = ", ".join(n for n in notes if n)
    result.note = note or None
    return result
