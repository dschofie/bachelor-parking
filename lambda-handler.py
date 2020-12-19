import json
import urllib3
import datetime
import json
import string
import boto3
import os

# desiredDays are the days that you want to try and find a booking.
desiredDays = {
    datetime.date(2021, 2, 13),
    datetime.date(2021, 2, 20),
    datetime.date(2021, 2, 27),
}

# sendEmail sends emails to based on SENDER_EMAIL and RECEIVER_EMAILS
# environment variables with the desiredDays.
def sendEmail(desiredDays):
    client = boto3.client("ses")
    senderEmail = os.getenv("SENDER_EMAIL")
    # Can be comma separated to send to multiple emails.
    receiverEmail = os.getenv("RECEIVER_EMAILS")
    print("sender", senderEmail, "receiver", receiverEmail)
    try:
        response = client.send_email(
            Destination={
                "ToAddresses": [
                    receiverEmail.split(","),
                ],
            },
            Message={
                "Body": {
                    "Text": {"Data": "HI!!\n\n" + json.dumps(list(desiredDays))},
                },
                "Subject": {
                    "Data": "I found bachelor days!",
                },
            },
            Source=senderEmail,
        )

    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"])


# handler is triggered via a cloudwatch event, so we really don't care about
# the event.
def lambda_handler(event, context):
    http = urllib3.PoolManager()
    parking = http.request(
        "GET",
        "https://api.parkwhiz.com/v3_1/venues/478498/events?page=1&per_page=100&fields=event::default,event:site_url,event:availability&sort=start_time&routing_style=parkwhiz",
    )
    if parking.status != 200:
        return {
            "statusCode": parking.status,
            "body": parking.text,
        }

    # Expect a json response so that we can iterate through each day.
    desiredDaysAvailable = set()
    parkingJson = json.loads(parking.data)
    for day in parkingJson:
        dayParsed = day["start_time"].split("T")[0]
        if datetime.datetime.strptime(dayParsed, "%Y-%m-%d").date() in desiredDays:
            if day["availability"]["available"] > 0:
                desiredDaysAvailable.add(dayParsed)

    if len(desiredDaysAvailable) != 0:
        print("attempting to send email about", desiredDaysAvailable)
        sendEmail(desiredDaysAvailable)
        return {
            "statusCode": 200,
            # Convert set to list before dumping to be serializable.
            "body": json.dumps(list(desiredDaysAvailable)),
        }

    print("desired days don't work :(")
    return {
        "statusCode": 200,
    }
