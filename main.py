def addition(a, b):
    return a + b

def SumAndProduct(a, b):
    c = addition(a, b)
    return a * b + c

def MainFunction(a, b):
    c = addition(a, b)
    d = SumAndProduct(a, b)
    return addition(c, d)

def decorator_wraper(max_repeats=20):
    def decorator(function):
        def wrap_function(max_repeating=max_repeats, *args, **kwargs):
            print(f"max_repeating = {max_repeating}")
            repeat = 0
            while repeat < max_repeating:
                try:
                    return function(*args, **kwargs)
                except Exception:
                    pass
        return wrap_function
    return decorator


@decorator_wraper(5)
def decorate_me_with_argument():
    print('decorate_me_with_argument')


@decorator_wraper()
def decorate_me_with_default():
    print('decorate_me_with_default')


decorate_me_with_argument()  # max_repeating = 5
decorate_me_with_default()  # max_repeating = 20
decorate_me_with_argument(3)  # max_repeating = 3
decorate_me_with_default(8)  # max_repeating = 8

def all_together(x, y, z=1, indent=True, spaces=4, **options):
    print("> fonction2 ", "(", x,",",y,")")
    print("<",addition(x,y))
    print("> SumAndProduct", "(", x, ",", y, ")")
    print("<", SumAndProduct(x, y))
    print("     > fonction2 ", "(", x, ",", y, ")")
    print("     <", addition(x, y))

