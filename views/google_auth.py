# Copyright (C) 2020-2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

import os,json,sys
from oauthlib.oauth2 import WebApplicationClient
import requests
from flask_login import login_required, login_user, logout_user
from flask import redirect, request, url_for, abort, session
from datetime import timedelta
from pprint import pprint
import base64

from root import db,app, login_manager
from models.login_users import LoginUser
from hgsc_utils.flask.flask_utils import flash_clear_messages

login_manager.login_view = "login"

@login_manager.user_loader
def load_user(login_user_id):
    app.logger.debug("load-user: login_user_id = %d" % login_user_id)
    user = LoginUser.query.get(login_user_id)
    app.logger.debug("load-user: loaded user %s" % (str(user)))
    return user


# Register a new OAuth logine key with google at
# https://console.developers.google.com/apis/credentials?pli=1
# then select "CREATE PROJECT",
# then select "CREATE CREDENTIAL",
# then select "OAuth Client ID".
# Be sure the "configure consent screen" and select "User type == internal"


# Configuration
GOOGLE_CLIENT_ID = app.config.get("GOOGLE_CLIENT_ID",None)
GOOGLE_CLIENT_SECRET = app.config.get("GOOGLE_CLIENT_SECRET",None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
GOOGLE_AUTH_BYPASS_USER = app.config.get("GOOGLE_AUTH_BYPASS_USER",None)

# Config Validation
if (GOOGLE_CLIENT_ID is None) and (GOOGLE_AUTH_BYPASS_USER is None):
    sys.exit("config error: missing either GOOGLE_CLIENT_ID or GOOGLE_AUTH_BYPASS_USER")


# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def  google_auth_dummy_login():
    app.logger.debug("google-auth: Using Dummy Login with email: %s" % (str(GOOGLE_AUTH_BYPASS_USER)))
    u = LoginUser.query.filter_by(email=GOOGLE_AUTH_BYPASS_USER).first()
    print("Forced Google OAuth User: ", u)
    if not u:
        flash_clear_messages()
        abort(500, "config error: GOOGLE_AUTH_BYPASS_USER (%s) does not exist in the database" % (GOOGLE_AUTH_BYPASS_USER), 'danger')

    print("Forced Google OAuth User: ", u)
    login_user(u)
    flash_clear_messages()
    # We use 'state' CGI parameter instead of 'next' to get google-oauth
    # to pass it through from the login to the callback (see previous function).
    next = request.args.get('state')
    app.logger.debug("after login-OK, state->next = " + str(next))
    # is_safe_url should check if the url is safe for redirects.
    # See http://flask.pocoo.org/snippets/62/ for an example.
    if not is_safe_url(next):
        return abort(400)
    return redirect(next or url_for('index'))

@app.route("/login")
def login():
    if GOOGLE_AUTH_BYPASS_USER:
        return google_auth_dummy_login()


    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    callback_uri = request.base_url + "/callback"
    #callback_uri = callback_uri.replace("http:","https:")
    print(callback_uri)

    # Google-OAuth does not support passing additional arbitrary (like a "next=" redirection).
    # So we abuse it by using the one allowed variable "state".
    # https://stackoverflow.com/a/7722099
    # in callback() below, we'll treat 'state' as if it was 'next'.
    next = request.args.get('next')
    app.logger.debug("before LOGIN-CaLLBACK, next = " + str(next))
    # is_safe_url should check if the url is safe for redirects.
    # See http://flask.pocoo.org/snippets/62/ for an example.
    if not is_safe_url(next):
        next = None

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri= callback_uri,
        scope=["openid", "email", "profile"],
        state=next
    )

    pprint(request_uri)
    return redirect(request_uri)


from urllib.parse import urlparse, urljoin
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    auth_resp = request.url
    redirect_url = request.base_url

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=auth_resp,
        redirect_url=redirect_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    #pprint(userinfo_response.json())

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if not userinfo_response.json().get("email_verified"):
        return "User email not available or not verified by Google.", 400

    resp_json = userinfo_response.json()

    email = resp_json["email"]

    # We either have this user in our database,
    # or we create a new record for him/her.
    # Google-Auth can send us any user/email - we have no control over it.
    u = LoginUser.query.filter_by(email=email).first()
    if not u:
        u = LoginUser(email)
    u.update_from_google_auth_json(resp_json)

    # After successsful Google-OAuth login, set the session cookie
    # to "permanent/7-days expiration", to avoid annoying frequent logins.
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=7) #this only needs to be set once, but oh well...

    app.logger.debug("google-auth: login OK for user %s" % (str(u)))
    # Begin user session by logging the user in
    login_user(u)

    flash_clear_messages()

    # We use 'state' CGI parameter instead of 'next' to get google-oauth
    # to pass it through from the login to the callback (see previous function).
    next = request.args.get('state')
    app.logger.debug("after login-OK, state->next = " + str(next))
    # is_safe_url should check if the url is safe for redirects.
    # See http://flask.pocoo.org/snippets/62/ for an example.
    if not is_safe_url(next):
        return abort(400)

    return redirect(next or url_for('index'))


@app.route("/logout")
def logout():
    flash_clear_messages()
    logout_user()
    return redirect(url_for("self_serve_main"))


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()
