import os
import pprint

from googleauthorizedservice import GoogleAuthorizedService

class SimpleGoogleDrive( object ):
    parameter_map = { 
        'drive': {
            'api_name': 'drive', 
            'api_version': 'v3', 
            'scopes': [ 'https://www.googleapis.com/auth/drive' ],
        },
        'sheets': {
            'api_name': 'sheets', 
            'api_version': 'v4', 
            'scopes': [ 'https://www.googleapis.com/auth/spreadsheets' ],
        },
    }
        

    def __init__( self, *a, **k ):
        self.drive = GoogleAuthorizedService( **(self.parameter_map[ 'drive' ]) )
        self.sheets = GoogleAuthorizedService( **(self.parameter_map[ 'sheets' ]) )


    def get_brewday_sheet( self, parent, name ):
        fmt = ('name contains {name}'
               ' mimeType = application/vnd.google-apps.spreadsheet'
               ' {parent} in parents'
               )
        query = fmt.format( name=name, parent=parent )
        results = self.drive.files().list( q=query ).execute()
        pprint.pprint( results, indent=2 )
