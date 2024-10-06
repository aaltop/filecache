import string



def pascal_to_snake_case(word):

    upper = string.ascii_uppercase
    no_first = word[1:]
    for letter in upper:
        no_first = no_first.replace(letter, "_"+letter.lower())

    return word[0].lower()+no_first