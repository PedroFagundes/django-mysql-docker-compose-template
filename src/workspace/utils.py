import uuid


def generate_random_code(length: int = 5):
    """
    Returns a random alphanumeric code with a max of 32 digits
    """

    random_code = str(uuid.uuid4())

    random_code = random_code.upper()

    random_code = random_code.replace('-', '')

    return random_code[0:length]
