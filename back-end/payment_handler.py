import requests
import uuid
import json

# ADD IDS AND TOKEN
SEND_PAYMENT_URL = "https://gateway-web.beta.interac.ca/publicapi/api/v2/money-requests/send"
ACCESS_ID = "CA1TAqC6v2dqXyVX"
ACCESS_TOKEN = "Bearer 03e0e0e6-3b5a-498c-b5db-61a8d6dd8b96"
API_REGISTRATION_ID = "CA1ARqc8sRsFmnsQ"

def request_payment(user,amount,paymentType):
    device_id = str(uuid.uuid4().hex)
    request_id = str(uuid.uuid4().hex)
    source_money_request_id = str(uuid.uuid4().hex)
    handle = user["email"] if paymentType == "email" else user["phone"]

    headers = {"thirdPartyAccessId":ACCESS_ID,"accessToken":ACCESS_TOKEN,"apiRegistrationId":API_REGISTRATION_ID,"requestId":request_id,"deviceId":device_id,"Accept":"application/json","Content-Type":"application/json"}

    notification_preferences = { "handle": handle, "handleType": paymentType,"active":"true"}
    requested_from = { "contactName":user["name"],"language":"en", "notificationPreferences": [notification_preferences]}
    body = { "sourceMoneyRequestId": source_money_request_id, "requestedFrom":requested_from, "amount":amount,"currency":"CAD","editableFulfillAmount": "false","supressResponderNotifications":"false", "requesterMessage":source_money_request_id,"expiryDate": "2019-03-30T16:12:12.721Z"}

    r = requests.post(SEND_PAYMENT_URL,headers=headers,data=json.dumps(body))
    
    return (source_money_request_id, "Payment Requested.")

# userOne = {"phone":"5142125431","name":"chris"}
# request_payment(userOne,"30.99","sms")