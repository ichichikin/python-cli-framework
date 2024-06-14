from main import __manual_launch


__set_globals = lambda dct: [globals().__setitem__(k, v) for k, v in dct.items()]


if __name__ == '__main__':
    __manual_launch(r'research example')  # command line arguments
