def pcall(func):
    try:
        args = func()

        if type(args) == tuple:
            return True, *args

        return True, args
    except Exception as e:
        return False, e


def ungay_anson():
    print("anson gay")
    print("ungaying...")
    print("done!")

    return "ungayed"


print(pcall(ungay_anson))
