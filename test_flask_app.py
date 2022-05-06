from flask import Flask, redirect, request
import requests
import pkce
import random
import string
import json
import csv
import os
import sys
from datetime import datetime, timedelta

file_dir = os.path.dirname(__file__)

app = Flask(__name__)


# Create a basic password generator for the state key
def passwordGenerator(length):

    length = int(length)
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits
    symbols = string.punctuation
    all = lower + upper + num + symbols
    temp = random.sample(all, length)
    password = "".join(temp)
    return password


# Get a value inputted and convert it to the specified type
def valueConverter(value, type):

    if type == "integer":
        int_value = int(value)
        return int_value
    elif type == "boolean":
        bool_value = bool(int(value))
        return bool_value
    elif type == "array":
        set_value = value.split(', ')
        return set_value
    else:
        return value


# Load in a csv that contains the Etsy listing details and convert them
# Into a dictionary as a payload for requests.post
def getDraftPayload():

    csv_data = []
    file = f"{file_dir}/.csv"
    with open(file, newline='', encoding='utf8') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            csv_data.append(row)

    payload = {}
    i = 0
    for row in csv_data:
        this_csv_row = csv_data[i]

        key = this_csv_row[0]
        value = valueConverter(this_csv_row[1], this_csv_row[2])

        payload[key] = value

        i += 1

    return payload


# variables
authCode = ""
response_type = "code"
redirect_uri = "/redirection"
scope = 'listings_w'
# scope = 'listings_r'
client_id = ""
client_secret = ""
state = passwordGenerator(20)
code_verifier = pkce.generate_code_verifier(length=128)
code_challenge = pkce.get_code_challenge(code_verifier)
code_challenge_method = "S256"
shop_id = ""
access_token = ""
listing_id = ""

original_token = f"{file_dir}/original_token.json"
mod_time = datetime.fromtimestamp(os.path.getmtime(original_token))
current_time = datetime.now()
tokenUrl = 'https://api.etsy.com/v3/public/oauth/token'


# Get the auth code and authenticate with Etsy
@app.route("/oauth")
def oauth():

    payload = {
        'response_type': response_type,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'client_id': client_id,
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': code_challenge_method,
    }

    # Check first if there is a local original access_token file.
    if os.path.exists(original_token) and (current_time - mod_time) > timedelta(hours=1) and not (current_time - mod_time) >= timedelta(days=90):

        with open(original_token, "r") as json_file:

            token_data = json.load(json_file)
            # Pull out the refresh token
            refresh_token = token_data['refresh_token']

        payload_refresh = {
            'grant_type': 'refresh_token',
            'client_id': client_id,
            'refresh_token': refresh_token,
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # send the refresh token post request
        response = requests.post(tokenUrl, data=payload_refresh, headers=headers)

        if response.status_code == requests.codes.ok:
            tokenData = response.json()
            global access_token

            # Create a local file to store the access_token 
            with open(original_token, "w") as output_file:
                json.dump(tokenData, output_file)

            access_token = tokenData['access_token']
           
            return redirect("http://localhost:5000/draft")
        else:
            return "No Good"

    elif not os.path.exists(original_token) or (current_time - mod_time) >= timedelta(days=90):
        # Since the modification date of the token file is more than 90 days OR
        # The file doesn't exist then get a new access_token with a refresh_token
        url = requests.get('https://www.etsy.com/oauth/connect', params=payload)
        return redirect(f"{url.url}")

    else:
        # Here is the case where the token file is still pretty young (within 1 hour of creating it)
        # so we will just use the same access_token otherwise we will have to make a new one
        # or annoy Etsy some more for an access token.
        if os.path.exists(original_token):
            with open(original_token, "r") as json_file:

                token_data = json.load(json_file)
                # pull out the access_token from the data
                access_token = token_data['access_token']

            return redirect("http://localhost:5000/draft")
        else:
            return "There was an error reading the token file"


# Pass in the auth code and generate the access_token as save it as a variable by requesting
# an access token via POST method
@app.route("/redirection")
def redirection():

    global authCode
    authCode = request.args.get("code")
    payload_auth = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'code': authCode,
        'code_verifier': code_verifier,
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(tokenUrl, data=payload_auth, headers=headers)

    if response.status_code == requests.codes.ok:
        tokenData = response.json()
        global access_token
        os.remove(original_token)
        # Create a local file to store the access_token 
        with open(original_token, "w") as output_file:
            json.dump(tokenData, output_file)

        access_token = tokenData['access_token']
        
        return redirect("/draft")
    else:
        return "No Good"

# This is an automation for posting up the draft posting to Etsy MAIN CAKE
@app.route("/draft")
def draft():

    url = f"https://openapi.etsy.com/v3/application/shops/{shop_id}/listings"

    headers = {
        'x-api-key': client_id,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    payload = getDraftPayload()

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 201:
        draft_data = response.json()
        global listing_id
        listing_id = draft_data["listing_id"]
        return redirect("images")
    else:
        return "Something went wrong"


@app.route("/images")
def images():

    directory = f"{file_dir}/etsy_listing_images"

    headers = {
        'x-api-key': client_id,
        'Authorization': f'Bearer {access_token}',
    }

    url = f"https://openapi.etsy.com/v3/application/shops/{shop_id}/listings/{listing_id}/images"

    for file_name in os.listdir(directory):

        payload = {}

        file_path = os.path.join(os.path.abspath(directory), file_name)

        with open(file_path, "rb") as this_image:
            payload['image'] = this_image
            response = requests.post(url, files=payload, headers=headers)

    if response.status_code == 201:
        data = response.json()
        return json.dumps(data)
    else:
        return json.dumps(response.json())