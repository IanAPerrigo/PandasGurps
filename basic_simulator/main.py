import argh


def main(no_ui: bool = None):
    print(no_ui)
    if no_ui:
        import kivy_main
        pass
    elif not no_ui:
        import panda_main
        pass


if __name__ == '__main__':
    argh.dispatch_command(main)
