"""schedules a message to send in slack

Example:
    source .env; \
    pipenv run python main.py schedule_msg \
            --to "#break-time" \
            --at "May 9, 2021, 2:39PM" \
            "i scheduled this message in the past and i'm test sending it to you"

You'll need to get some API keys from me if you want to use this.
"""

import os

import typing as ty

from argparse import ArgumentParser
from datetime import datetime, timedelta
from dateutil.parser import parse
from pprint import PrettyPrinter

# github.com/slackapi/python-slack-sdk
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


pp = PrettyPrinter(indent=2)


TOKEN = lambda: os.environ.get('SLACK_BOT_USER_TOKEN')


def print_users(members: ty.List[dict]):
    u = sorted(
        map(lambda u: (u['id'], u['name'], u['profile']['display_name'], u['profile']['real_name']),
            members),
        key=lambda u: u[1]

    )
    print('id, name, display_name, real_name')
    pp.pprint(u)
    print('id, name, display_name, real_name')


def list_users(_args):
    client = WebClient(token=TOKEN())
    resp = client.users_list()
    print_users(resp['members'])


def msg_payload_from_args(args):
    dt = parse(args.at)
    print(f'parsed "{args.at}" as "{dt.isoformat()}", with tzinfo="{dt.tzinfo}"')
    schedule_timestamp = int(dt.timestamp())

    return dict(
        channel=args.to,
        text=' '.join(args.msg),
        post_at=schedule_timestamp,
        as_user=True,
    )


def print_schedule_result(result):
    dt = datetime.fromtimestamp(result['post_at'])
    print(f'scheduled to send message "{result["message"]["text"]}" at "{dt.isoformat()}"')


def schedule_msg(args):
    client = WebClient(token=TOKEN())

    try:
        result = client.chat_scheduleMessage(**msg_payload_from_args(args))
        print_schedule_result(result)
    except SlackApiError as e:
        print('Error listing users message: {}'.format(e))



def main():
    parser = ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers()

    list_users_parser = subparsers.add_parser('list_users', help='list users in your slack workspace')
    list_users_parser.set_defaults(func=list_users)

    schedule_msg_parser = subparsers.add_parser('schedule_msg', help='schedule a message to send to a user or channel')
    schedule_msg_parser.add_argument('--to', type=str, required=True, help="user id or channel name to send message to. to find user_id you're trying to hit, use list_users cmnd. if sending to a channel, format it '#channel-name'")
    schedule_msg_parser.add_argument('--at', type=str, required=True, help='when to send message; try to be specific and USE YOUR OWN TIMEZONE')
    schedule_msg_parser.add_argument('msg', type=str, nargs='+', help='the message')
    schedule_msg_parser.set_defaults(func=schedule_msg)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()

