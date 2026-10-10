import pytest

from app.services.ingredients import ParsedIngredient, parse_ingredient


def p(quantity=None, quantity_max=None, unit=None, name=None, note=None) -> ParsedIngredient:
    return ParsedIngredient(quantity, quantity_max, unit, name, note)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2 cups flour", p(2, unit="cup", name="flour")),
        ("1 cup sugar", p(1, unit="cup", name="sugar")),
        ("1/2 tsp salt", p(0.5, unit="tsp", name="salt")),
        ("1 1/2 cups milk", p(1.5, unit="cup", name="milk")),
        ("½ cup butter", p(0.5, unit="cup", name="butter")),
        ("1½ cups water", p(1.5, unit="cup", name="water")),
        ("1 ½ cups all-purpose flour, sifted", p(1.5, unit="cup", name="all-purpose flour", note="sifted")),
        ("¾ teaspoon baking soda", p(0.75, unit="tsp", name="baking soda")),
        ("1⁄4 cup honey", p(0.25, unit="cup", name="honey")),
        ("0.5 kg potatoes", p(0.5, unit="kg", name="potatoes")),
        (".25 cup oil", p(0.25, unit="cup", name="oil")),
        ("2-3 cloves garlic, minced", p(2, 3, "clove", "garlic", "minced")),
        ("2 – 3 tablespoons olive oil", p(2, 3, "tbsp", "olive oil")),
        ("1 to 2 tsp chili flakes", p(1, 2, "tsp", "chili flakes")),
        ("3 Tbsp. soy sauce", p(3, unit="tbsp", name="soy sauce")),
        ("2 T sugar", p(2, unit="tbsp", name="sugar")),
        ("2 t vanilla", p(2, unit="tsp", name="vanilla")),
        ("200g dark chocolate", p(200, unit="g", name="dark chocolate")),
        ("500 ml chicken stock", p(500, unit="ml", name="chicken stock")),
        ("8 fl oz cream", p(8, unit="fl oz", name="cream")),
        ("16 oz pasta", p(16, unit="oz", name="pasta")),
        ("1 lb ground beef", p(1, unit="lb", name="ground beef")),
        ("2 pounds chicken thighs", p(2, unit="lb", name="chicken thighs")),
        ("2 cups of rice", p(2, unit="cup", name="rice")),
        ("1 (14 oz) can diced tomatoes", p(1, unit="can", name="diced tomatoes", note="14 oz")),
        ("2 (8-ounce) packages cream cheese, softened", p(2, unit="package", name="cream cheese", note="8-ounce, softened")),
        ("1 cup (240ml) milk", p(1, unit="cup", name="milk", note="240 ml")),
        ("3 large eggs", p(3, name="large eggs")),
        ("2 medium onions, diced", p(2, name="medium onions", note="diced")),
        ("1 lemon", p(1, name="lemon")),
        ("4 c chopped spinach", p(4, unit="cup", name="chopped spinach")),
        ("1 inch ginger, grated", p(1, unit="inch", name="ginger", note="grated")),
        ("1 bunch cilantro", p(1, unit="bunch", name="cilantro")),
        ("a pinch of salt", p(1, unit="pinch", name="salt")),
        ("two cloves garlic", p(2, unit="clove", name="garlic")),
        ("salt to taste", p(name="salt", note="to taste")),
        ("Salt and pepper, to taste", p(name="Salt and pepper", note="to taste")),
        ("fresh parsley for garnish", p(name="fresh parsley", note="for garnish")),
        ("1 tbsp sesame seeds (optional)", p(1, unit="tbsp", name="sesame seeds", note="optional")),
        ("Juice of 1 lemon", p(name="Juice of 1 lemon")),
        ("an onion", p(name="an onion")),
        ("• 1 cup broth", p(1, unit="cup", name="broth")),
        ("▢ 2 tbsp butter", p(2, unit="tbsp", name="butter")),
        ("1 cup  rolled   oats", p(1, unit="cup", name="rolled oats")),
        ("3 cups water, divided", p(3, unit="cup", name="water", note="divided")),
        ("1 lb. boneless, skinless chicken breast", p(1, unit="lb", name="boneless, skinless chicken breast")),
        ("1 lb boneless, skinless chicken thighs, cut into cubes", p(1, unit="lb", name="boneless, skinless chicken thighs", note="cut into cubes")),
        ("1 yellow onion, diced ($0.32)", p(1, name="yellow onion", note="$0.32, diced")),
        ("1 onion, about 1 cup", p(1, name="onion", note="about 1 cup")),
        ("2 tbsp butter, at room temperature", p(2, unit="tbsp", name="butter", note="at room temperature")),
        ("1 cup parsley, finely chopped", p(1, unit="cup", name="parsley", note="finely chopped")),
        ("2 carrots, peeled and cut into 1-inch pieces", p(2, name="carrots", note="peeled and cut into 1-inch pieces")),
    ],
)
def test_parse_ingredient(raw: str, expected: ParsedIngredient) -> None:
    assert parse_ingredient(raw) == expected


def test_one_third_is_close_enough() -> None:
    assert parse_ingredient("1/3 cup milk").quantity == pytest.approx(0.3333, abs=1e-3)


def test_unit_prefix_inside_a_word_is_not_a_unit() -> None:
    result = parse_ingredient("2 chopped onions")
    assert result.unit is None
    assert result.name == "chopped onions"


def test_empty_line() -> None:
    assert parse_ingredient("   ") == p()
