import random


def generate_random_string(n=3):
    return ''.join(chr(random.randint(65, 90)) for _ in range(n))
