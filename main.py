def __manual_launch(command_line: str = None) -> None:
    from system.app import App
    App.init(command_line)
    App.start()


if __name__ == '__main__':
    __manual_launch()
