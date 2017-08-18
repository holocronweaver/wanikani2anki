class Anki:
    def generate_id():
        """Generate a 32-bit ID useful for Anki."""
        return random.randrange(1 << 30, 1 << 31)
        # return datetime.now().timestamp()
