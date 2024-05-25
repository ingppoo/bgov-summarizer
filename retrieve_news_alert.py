import os
import base64
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def get_email_text(msg):
    """Extracts the body of the email message."""
    parts = msg['payload'].get('parts', [])
    if not parts:
        data = msg['payload']['body']['data']
        byte_code = base64.urlsafe_b64decode(data.encode('ASCII'))
        text = byte_code.decode('UTF-8')
        return text
    else:
        for part in parts:
            if part['mimeType'] == 'text/plain':
                data = part['body']['data']
                byte_code = base64.urlsafe_b64decode(data.encode('ASCII'))
                text = byte_code.decode('UTF-8')
                return text
            elif part['mimeType'] == 'text/html':
                data = part['body']['data']
                byte_code = base64.urlsafe_b64decode(data.encode('ASCII'))
                html = byte_code.decode('UTF-8')
                soup = BeautifulSoup(html, 'html.parser')
                return soup.get_text()

    return ""

def get_emails(service, days=7, query='from:"New York Times" subject:"The Morning"'):
    date_days_ago = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')
    query = f'{query} after:{date_days_ago}'
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    email_list = []

    if not messages:
        print('No messages found.')
    else:
        # print('Messages:')
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            msg_text = get_email_text(msg)
            email_list.append(msg_text)
            # print(f"Message text: {msg_text}")

    return email_list

def extract_specific_content(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Extract content from "content-title" class
    content_title_elements = soup.find_all(class_='content-title')
    content_title_text = ' '.join([elem.get_text() for elem in content_title_elements])

    # Extract content from "news-rsf-news-body" class
    news_body_elements = soup.find_all(class_='news-rsf-news-body')
    news_body_text = ' '.join([elem.get_text() for elem in news_body_elements])

    return {'title': content_title_text.strip(),
            'content': news_body_text.strip()}

def format_emails(emails):
    articles = []

    for article in emails:
        content = extract_specific_content(article)
        if content['content'] != "":
            articles.append(content)

    print(f'Total {len(articles)} news articles have been retrieved.')

    return articles

def main():
    service = authenticate_gmail()
    emails = get_emails(service)
    print("Retrieved Emails:", emails)

if __name__ == '__main__':
    main()