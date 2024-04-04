from pyparsing import (
    Word,
    alphas,
    alphanums,
    Forward,
    Group,
    infixNotation,
    printables,
    Keyword,
    Literal,
    oneOf,
    opAssoc,
)

LPAR, RPAR = map(Literal, "()")
AND = Keyword("AND")
OR = Keyword("OR")
table_name = Word(alphas, alphanums + "_")
search = Forward()
search_term = Group(
    table_name("table") + ":" + Word(printables, exclude_chars="()")("q")
)
search << infixNotation(
    search_term,
    [
        (oneOf("AND OR"), 2, opAssoc.LEFT),
    ],
)("search")


def parse_query(query: str) -> list | None:
    try:
        parsed_results = search.parseString(query)

        data = parsed_results.as_dict()["search"]
        return data
    except Exception as _:
        return None


if __name__ == "__main__":
    import sys

    input_string = sys.argv[1]
    res = parse_query(input_string)
    print(res)
