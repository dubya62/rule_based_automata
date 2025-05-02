

TESTING = 0
DEBUG = 1

def dbg(message):
    if DEBUG:
        print(message)


def panic(message):
    print(message)
    if not TESTING:
        exit(1)


