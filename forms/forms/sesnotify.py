import boto3
from botocore.exceptions import ClientError
import markdownify
import os

CHARSET = "UTF-8"

TEST_EMAIL_RECIPIENT = os.getenv("TEST_EMAIL_RECIPIENT")

class SESNotifier:
    
    def __init__(self, region:str = '', access_key_id: str = '', access_key_secret: str = '', email_name:str='', email_address:str='') -> None:
        self.sender = "{0} <{1}>".format(email_name, email_address)
        self.client = boto3.client('ses', region_name=region, aws_access_key_id=access_key_id, aws_secret_access_key=access_key_secret)

    def SendEmail(self, recipients: list[str], subject, bodyhtml, bodytext):
        if TEST_EMAIL_RECIPIENT != None and TEST_EMAIL_RECIPIENT != "":
            recipients = [TEST_EMAIL_RECIPIENT]
        try:
            self.client.send_email(
                Destination={
                    'ToAddresses': 
                        recipients,
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': bodyhtml,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': bodytext,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': subject,
                    },
                },
                Source=self.sender,
            )
            return
        except ClientError as e: 
            print(e)   
            return e 
        