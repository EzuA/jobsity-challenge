import sys
import json

import requests


def slack_send_alert(
    webhook_url: str, title: str, message: str, icon_emoji: str
) -> None:
    """Generic function to send alert messages to a given Slack channel URL.
    Do not use this method as a log to print random messages. Be sure to only
    use it to send real alerts, for example in case of errors or warnings.
    """
    slack_data = {
        "username": "NotificationBot",
        "icon_emoji": icon_emoji,
        "attachments": [
            {
                "color": "#9733EE",
                "fields": [
                    {
                        "title": title,
                        "value": message,
                        "short": "false",
                    }
                ],
            }
        ],
    }
    byte_length = str(sys.getsizeof(slack_data))
    headers = {"Content-Type": "application/json", "Content-Length": byte_length}
    response = requests.post(webhook_url, data=json.dumps(slack_data), headers=headers)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
