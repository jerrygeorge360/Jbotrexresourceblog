import requests


def subscribe_user(email, use_group_email, api_key):
    resp = requests.post(f"https://api.mailgun.net/v3/lists/{use_group_email}/members", auth=("api", api_key),
                         data={"subscribed": True, "email": email})
    return resp
