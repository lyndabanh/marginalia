def isbn10_to_isbn13(isbn10: str) -> str:
    digits = "978" + isbn10[:9]
    total = sum(
        int(d) * (1 if i % 2 == 0 else 3)
        for i, d in enumerate(digits)
    )
    check = (10 - (total % 10)) % 10
    return digits + str(check)