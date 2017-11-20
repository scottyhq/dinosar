#!/usr/bin/env python3
'''
Sent email with link to s3 bucket where finished interferogram is stored

NOTE: localhost doesn't have mail server set up by default..
ConnectionRefusedError: [Errno 61] Connection refused
https://www.nixtutor.com/linux/send-mail-through-gmail-with-python/

For more complicated emails, including attachments see:
https://stackoverflow.com/questions/3362600/how-to-send-email-attachments

'''
#import os
import smtplib
from email.message import EmailMessage

#server = smtplib.SMTP('localhost')
sender = 'scottyhq'
receivers = ['scottyh@uw.edu']

# Plain text message
body = '''
Hi Scott, your interferogram has finished. It is stored here:
s3://interferogram

You can download it with this command:
aws s3 cp -r s3://interferogram . --recursive

'''
msg = EmailMessage()
msg['Subject'] = 'Interferogram has finished!'
msg['From'] = sender
msg['To'] = receivers
msg.set_content(body)

with smtplib.SMTP('smtp.gmail.com:587') as server:
    server.starttls()
    server.login('scottyhq','EC2004safe3')
    server.send_message(msg)

