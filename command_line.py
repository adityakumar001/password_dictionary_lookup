import sys, hashlib
import string
import os
import numpy as np

usage = "Usages:\n\t\tpython command_line.py <hash_file> B <pattern_switch> <password_length> [algorithm_used]\n" \
        "\t\tpython command_line.py <hash_file> D <dictionary_file> [algorithm_used]\n" \
        "\tpattern_switch :-\n" \
        "\t\ta : All allowed characters\n" \
        "\t\tu  : only uppercase\n" \
        "\t\tl  : only lower case\n" \
        "\t\td  : only digits\n" \
        "\t\ts  : only symbols\n" \
        "\t\tul : both upper and lower case\n" \
        "\t\tad : alphanumeric characters\n" \
        "\t\tls : lowercase and symbols\n" \
        "\t\tld : lowercase and digits\n" \
        "\t\tus : uppercase and symbols\n" \
        "\t\tud : uppercase and digits\n" \
        "\t\tds : digits and symbols"


def get_lookup_chars(char_switch):
    if char_switch == 'a':
        return list(string.printable.rstrip(string.whitespace))
    elif char_switch == 'u':
        return list(string.ascii_uppercase)
    elif char_switch == 'l':
        return list(string.ascii_lowercase)
    elif char_switch == 'd':
        return list(string.digits)
    elif char_switch == 's':
        return list(string.punctuation)
    elif char_switch == 'ul':
        return list(string.ascii_letters)
    elif char_switch == 'ad':
        return list(string.ascii_letters + string.digits)
    elif char_switch == 'ls':
        return list(string.ascii_lowercase + string.punctuation)
    elif char_switch == 'ld':
        return list(string.ascii_uppercase + string.punctuation)
    elif char_switch == 'us':
        return list(string.ascii_uppercase + string.punctuation)
    elif char_switch == 'ud':
        return list(string.ascii_uppercase + string.digits)
    elif char_switch == 'ds':
        return list(string.digits + string.punctuation)
    else:
        print(usage)
        sys.exit()


def get_words(starts, length, chars):
    words = []
    if length == 1:
        for char_ in chars:
            words.append(starts + char_)
        return words

    for i in range(len(chars)):
        for word in get_words(chars[i], length - 1, chars):
            words.append(starts + word)

    return words


def hash_word(password, hash_algorithm):
    implementation = getattr(hashlib, hash_algorithm)
    result = implementation(password.encode())
    if hash_algorithm == 'shake_128':
        return result.hexdigest(127)
    elif hash_algorithm == 'shake_256':
        return result.hexdigest(255)
    else:
        return result.hexdigest()


def main(mode, hash_file, hash_algorithm="sha1", **kwargs):
    hashes = np.loadtxt(hash_file, delimiter="\n", dtype=np.string_, encoding="latin-1").astype(str)
    hasher = np.vectorize(hash_word)
    if mode == 'D':
        passwords = np.loadtxt(kwargs["dictionary"], delimiter="\n", dtype=np.str,
                               encoding="latin-1")
        password_hashes = hasher(passwords, hash_algorithm)
        for hash_ in hashes:
            for i in range(len(password_hashes)):
                if hash_ == password_hashes[i]:
                    print(str(passwords[i]) + " : " + password_hashes[i])
    if mode == "B":
        chars = get_lookup_chars(kwargs["pattern"])
        length_ = kwargs["length"] - 1
        for char_ in chars:
            words = np.array(get_words(char_, length_, chars))
            word_hashes = hasher(words, hash_algorithm)
            for hash_ in hashes:
                for i in range(len(words)):
                    if hash_ == word_hashes[i]:
                        print(hash_ + " : " + words[i])


if __name__ == "__main__":

    try:
        hash_file = sys.argv[1]
        mode = sys.argv[2]

        if not os.path.exists(hash_file):
            print("\nEnter a valid hash file path !!!\n")
            print(usage)
            sys.exit()

        if mode == "B":
            pattern = sys.argv[3]
            length = int(sys.argv[4])
            if len(sys.argv) == 5:
                main(mode, hash_file, pattern=pattern, length=length)
            else:
                algorithm = sys.argv[5]
                main(mode, hash_file, algorithm, pattern=pattern, length=length)

        elif mode == "D":
            dictionary = sys.argv[3]
            if not os.path.exists(dictionary):
                print("\nEnter a valid dictionary file path !!!\n")
                print(usage)
                sys.exit()
            if len(sys.argv) == 4:
                main(mode, hash_file, dictionary=dictionary)
            else:
                algorithm = sys.argv[4]
                main(mode, hash_file, algorithm, dictionary=dictionary)

    except ValueError as v:
        print(v.__str__())
        print("The second argument must be a positive number...")
        print(usage)

    except IndexError as e:
        print(e.__str__())
        print("No arguments provided...")
        print(usage)
        sys.exit()
