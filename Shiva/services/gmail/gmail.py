from dataclasses import dataclass
from googleapiclient.discovery import build
from apiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools
from email.mime.text import MIMEText
import base64
import inspect
from typing import Dict
import os
import os.path
from pathlib import Path


@dataclass
class Gmail:
    scope : str = ''

    VERSION = '1.0.0'
    API_VERSION = '1.7.4'
    PATH = Path(os.path.dirname(os.path.abspath(__file__)))
    # From https://developers.google.com/gmail/api/auth/scopes :
    SCOPES = {
        'readonly' : (
            'https://www.googleapis.com/auth/gmail.readonly',
            'Read all resources and their metadata—no write operations.'
        ),
        'compose' : (
            'https://www.googleapis.com/auth/gmail.compose',
            'Create, read, update, and delete drafts. Send messages and drafts.'
        ),
        'send' : (
            'https://www.googleapis.com/auth/gmail.send',
            'Send messages only. No read or modify privileges on mailbox.'
        ),
        'insert' : (
            'https://www.googleapis.com/auth/gmail.insert',
            'Insert and import messages only.'
        ),
        'labels' : (
            'https://www.googleapis.com/auth/gmail.labels',
            'Create, read, update, and delete labels only.'
        ),
        'modify' : (
            'https://www.googleapis.com/auth/gmail.modify',
            'All read/write operations except immediate, permanent deletion of threads and messages, bypassing Trash.'
        ),
        'metadata' : (
            'https://www.googleapis.com/auth/gmail.metadata',
            'Read resources metadata including labels, history records, and email message headers, but not the message body or attachments.'
        ),
        'basic' : (
            'https://www.googleapis.com/auth/gmail.settings.basic',
            'Manage basic mail settings.'
        ),
        'sharing' : (
            'https://www.googleapis.com/auth/gmail.settings.sharing',
            'Manage sensitive mail settings, including forwarding rules and aliases.'
        ),
        'all' : (
            'https://mail.google.com/',
            'Full access to the account, including permanent deletion of threads and messages.'
        )
    }


    def requirements(self) -> None:
        '''Display the requirements to use the service

               :return: None
        '''
        print('You must install google-api-python-client and oauth2client modules.')
        print('> pip3 install --upgrade google-api-python-client oauth2client')
        print('You must active Gmail API on https://console.developers.google.com.')
        print('You must download the client_secret_xxxxxx.apps.googleusercontent.com.json file and copy it in the services/gmail folder (give the name as secretJson parameter in the init() method).')


    def changeScope(self, scope : str, storageFile : str ='token.json') -> None:
        '''Change the scope and delete the storage file to enable the
           modification

               :scope: Key associated to SCOPES

               :return: None
        '''
        if os.path.isfile(Gmail.PATH / storageFile):
            os.remove(Gmail.PATH / storageFile)
        self.scope = scope


    def init(self, scope : str = 'modify', storageFile : str ='token.json', secretJson : str = 'client_secret.json') -> None:
        '''Initialization of the API

               :scope: Name of the scope as specified in SCOPES
               :storageFile: Name of the storage file
               :secretJson: Name of the JSON file containing access key

               :return: None
        '''
        if self.scope != '':
            scope = self.scope
        store = file.Storage(Gmail.PATH / storageFile)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(Gmail.PATH / secretJson, Gmail.SCOPES['modify'][0])
            creds = tools.run_flow(flow, store)
        self.gmailService = build('gmail', 'v1', http=creds.authorize(Http()))


    def help(self, subject : str) -> None:
        '''Display help on the 'subject' parameter

               :return: None
        '''
        subject = subject.upper()
        if subject.startswith('SCOPE'):
            print('Help on scope values :')
            print('-' * 22)
            for scopeName in Gmail.SCOPES:
                print(f'- {scopeName}')
                print(f'  value : {Gmail.SCOPES[scopeName][0]}')
                print(f'  description : {Gmail.SCOPES[scopeName][1]}')


    def expose(self) -> None:
        """Display the API list of functions
    
               :return: None
        """
        currentModule = __import__(__name__).gmail.gmail
        for name, obj in inspect.getmembers(currentModule.Gmail, inspect.isfunction):
            if obj.__name__ == 'build' or obj.__name__.startswith('__'):
                continue
            print('***')
            print(f'Function {obj.__name__}(', end='')
            arguments = ''
            rtype = ''
            for arg in obj.__annotations__:
                if arg == 'return':
                    rtype = obj.__annotations__[arg]
                    continue
                if not arguments is '':
                    arguments += ', '
                arguments += f'{arg} : {obj.__annotations__[arg]}'
            print(f'{arguments})', end='')
            if rtype == '': 
                print(' -> not specified')
            else:
                print(f' -> {rtype}')
            if obj.__doc__ is None:
                print('Documentation unavailable')
            else:
                print(obj.__doc__)
            print()


    def createMessage(self, sender : str, to : str, subject : str, message_text : str) -> Dict[str, str]:
        '''Create a MIME text message ready to use as message parameter in the send-message() function
    
               :return: A dictionary containing the MIME text message (key 'raw')
        '''
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}


    def sendMessage(self, fromUser : str, to : str, subject : str, message : str, idSender : str = 'me') -> Dict[str, str]:
        ''' Send an email
  
            :fromUser: Sender email adress
            :to: Receiver email address
            :subject: Subject of the email
            :message: Body of the email
            :idSender: Gmail identifier of the sender
   
            :return: Information on the email sent
        '''
        try:
            mail = self.createMessage(fromUser, to, subject, message)
            message = (self.gmailService.users().messages().send(userId=idSender, body=mail).execute())
            return message
        except errors.HttpError as error:
            print(f'An error occurred: {error}')
