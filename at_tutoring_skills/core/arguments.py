import argparse


def get_args() -> dict:
    # Argument parser setup
    parser = argparse.ArgumentParser(
        prog="at-tutoring-skills", description="Grader for dynamic IES practics"
    )
    parser.add_argument(
        "-u", "--url", help="RabbitMQ URL to connect", required=False, default=None
    )
    parser.add_argument(
        "-H",
        "--host",
        help="RabbitMQ host to connect",
        required=False,
        default="localhost",
    )
    parser.add_argument(
        "-p", "--port", help="RabbitMQ port to connect", required=False, default=5672
    )
    parser.add_argument(
        "-L",
        "--login",
        "-U",
        "--user",
        "--user-name",
        "--username",
        "--user_name",
        dest="login",
        help="RabbitMQ login to connect",
        required=False,
        default="guest",
    )
    parser.add_argument(
        "-P",
        "--password",
        help="RabbitMQ password to connect",
        required=False,
        default="guest",
    )
    parser.add_argument(
        "-v",
        "--virtualhost",
        "--virtual-host",
        "--virtual_host",
        dest="virtualhost",
        help="RabbitMQ virtual host to connect",
        required=False,
        default="/",
    )

    parser.add_argument(
        "-m",
        "--mode",
        dest="mode",
        help="Skills detection mode",
        required=False,
        default="kb",
        choices=['kb', 'im']
    )

    args = parser.parse_args()
    res = vars(args)
    return res
