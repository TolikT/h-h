from settings import SLACK_BOT_TOKEN, BOT_ID
from slackclient import SlackClient
import sqlite3
import requests

slack_client = SlackClient(SLACK_BOT_TOKEN)
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    if user != 'incognito':
        response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
        if command.startswith(EXAMPLE_COMMAND):
            response = "Sure...write some more code then I can do that!"
        elif command.startswith("getorderstatus"):
            conn = sqlite3.connect("C:\db.sqlite3")
            c = conn.cursor()
            c.execute("select id from register_extuser where email='{}'".format(user))
            result = c.fetchall()[0][0]
            print result
            c.execute("select weight, type_of_goods from orders_saleorder where user_login_id='{}'".format(result))
            response = ''
            for elem in c.fetchall():
                response += "Weight is {} and type is {}\n".format(elem[0], elem[1])
            conn.close()
    else:
        response = 'no information for this user'
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                r = requests.post('https://slack.com/api/users.list', data={'token': SLACK_BOT_TOKEN})
                for member in r.json()['members']:
                    if member['id'] == output['user']:
                        user = member['profile']['email']
                if not user:
                    user = 'incognito'

                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel'], user
    return None, None, None
