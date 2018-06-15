"""
Based on the sample at:
https://developers.google.com/api-client-library/python/auth/installed-app#example
"""

import json

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from collections import namedtuple

class GoogleAuthorizedService( object ):
    client_secrets_file = 'client_secret.json'
    credentials_file = 'credentials.json'


    def __init__( self, api_name=None, api_version=None, scopes=None, **k ):
        self.credentials = None
        self.service = None
        self.api_name = api_name
        self.api_version = api_version
        self.scopes = scopes
        valid_keys = [ 'client_secrets_file',
                       'credentials_file',
                     ]
        for key in valid_keys:
            if key in k:
                setattr( self, key, k[key] )
        self._get_authenticated_service()
                

    def _get_authenticated_service( self ):
        if self.service is None:
            self._get_credentials()
            self.service = build( self.api_name, 
                                  self.api_version,
                                  credentials = self.credentials )
        

    def _get_credentials( self ):
        if self.credentials is None:
            try:
                self._credentials_from_auth_file()
            except ( FileNotFoundError ) as e:
                self._credentials_from_secrets_file()


    def _credentials_from_auth_file( self ):
        self.credentials = Credentials.from_authorized_user_file(
            self.credentials_file, scopes = self.scopes )


    def _credentials_from_secrets_file( self ):
        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, self.scopes )
        self.credentials = flow.run_console()
        self._save_credentials()


    def _save_credentials( self ):
        info = { 'refresh_token': self.credentials._refresh_token,
                 'client_id': self.credentials._client_id,
                 'client_secret': self.credentials._client_secret,
               }
        with open( self.credentials_file, 'w' ) as fp:
            json.dump( info, fp )


    def __getattr__( self, name ):
        return getattr( self.service, name )
