import argh
import panda_main


def main(no_ui: bool = None):
    panda_main.run_app()


if __name__ == '__main__':
    argh.dispatch_command(main)
