import secrets
import string
import random

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
    
    lower_case = string.ascii_lowercase
    upper_case = string.ascii_uppercase
    digits = string.digits
    symbols = string.punctuation

    if exclude_ambiguous:
        AMBIGUOUS = set("0Oo1lI")

        lower_case = ''.join(c for c in string.ascii_lowercase if c not in AMBIGUOUS)
        upper_case = ''.join(c for c in string.ascii_uppercase if c not in AMBIGUOUS)
        digits = ''.join(c for c in string.digits if c not in AMBIGUOUS)
        symbols = string.punctuation
    
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
    
    if length.isdigit():
        length = int(length)

        if length < 8:
            strength = "Weak"
        elif length < 12:
            strength = "Medium"
        else:
            strength = "Strong"
        
        try:
            password = password_generator(length, exclude_ambiguous)
            print(f"The generated password is : {password}")
            print(f"The password strength is : {strength}")
        except ValueError as e:
            print(e)

    else:
        print("Enter a valid number")

    print("\n" + "==================================")

if __name__ == "__main__":
    main()