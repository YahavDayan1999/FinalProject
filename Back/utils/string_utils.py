


def is_valid_israeli_id(client_id):
    client_id = str(client_id)
    if len(client_id) != 9 or not client_id.isdigit():
        return False
    checksum = sum(
        sum(divmod(int(d) * (2 if i % 2 else 1), 10))
        for i, d in enumerate(client_id)
    )
    return checksum % 10 == 0

