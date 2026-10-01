import secrets
import string
import random
import math

def character_sets(exclude_ambiguous = False):
    lower_case = string.ascii_lowercase
    upper_case = string.ascii_uppercase
    digits = string.digits
    symbols = string.punctuation

    if exclude_ambiguous:
        AMBIGUOUS = set("0Oo1lI")

        lower_case = ''.join(c for c in lower_case if c not in AMBIGUOUS)
        upper_case = ''.join(c for c in upper_case if c not in AMBIGUOUS)
        digits = ''.join(c for c in digits if c not in AMBIGUOUS)

    return lower_case, upper_case, digits, symbols

def password_entropy(length, exclude_ambiguous = False):
    """
    Entropy in bits: length * log2(charset size). Slightly overstated, since
    the first four characters are each drawn from a single class.
    """
    charset_size = len(''.join(character_sets(exclude_ambiguous)))
    return length * math.log2(charset_size)

def password_strength(entropy):
    if entropy < 50:
        return "Weak"
    elif entropy < 75:
        return "Medium"
    else:
        return "Strong"

def password_generator(length, exclude_ambiguous = False):

    """
    Generate a cryptographically secure password.

    Guarantees at least:
    - 1 lowercase character
    - 1 uppercase character
    - 1 digit
    - 1 symbol

    Excludes ambiguous characters:
    0 O o 1 l I
    """

    if length < 4:
        raise ValueError("Password length must be at least 4")
    
    lower_case, upper_case, digits, symbols = character_sets(exclude_ambiguous)

    characters = lower_case + upper_case + digits + symbols

    password = [
        secrets.choice(lower_case),
        secrets.choice(upper_case),
        secrets.choice(digits),
        secrets.choice(symbols)
    ]

    password.extend(
        secrets.choice(characters)
        for _ in range(length - 4)
    )

    random.SystemRandom().shuffle(password)

    return ''.join(password)


def main(length = None, exclude_ambiguous = False):
    
    print("==================================")
    print("\n" + "--------PASSWORD GENERATOR--------")
    print("==================================")
    if length == None:
        exclude_ambiguous = False
        
        length = input("Enter the length of character : ")
        amb = input("Exclude ambiguous characters (0 O o 1 l I)? (y/n): ")

        exclude_ambiguous = amb.lower() == "y"

        # input() returns a string; the CLI path already passes an int
        if not length.isdigit():
            print("Enter a valid number")
            print("\n" + "==================================")
            return

        length = int(length)

    try:
        password = password_generator(length, exclude_ambiguous)
        entropy = password_entropy(length, exclude_ambiguous)
        print(f"The generated password is : {password}")
        print(f"The password strength is : {password_strength(entropy)} ({entropy:.0f} bits of entropy)")
    except ValueError as e:
        print(e)

    print("\n" + "==================================")

if __name__ == "__main__":
    main()