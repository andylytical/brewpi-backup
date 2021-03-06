#!/usr/bin/env python3

import pathlib
import json
import re
import datetime
import string
import urllib
import pprint
import os
import textwrap
import math

# Only grab data for columns matching this regular expression
COLS_REGEX = re.compile( 'Time|Temp|Set|SG' )
#COLS_REGEX = re.compile( 'Time|BeerTemp|BeerSet|SG' )

HOME = pathlib.Path( os.environ['HOME'] )
DATADIR = pathlib.Path( '/var/www/html/data' )
HTML_TEMPLATE = HOME/'brewpi-backup/brewlog.html.tmpl'


class myTemplate( string.Template ):
    delimiter = '___'


class jscode( object ):
    ''' A regular python string that will return without quotes when
        formatted with __repr__
    '''
    def __init__( self, rawstr ):
        self.line = rawstr

    def __str__( self ):
        return str( self.line )

    __repr__ = __str__


def safe_filename( rawfn ):
    return urllib.parse.unquote_plus( rawfn )


def mk_lcdparts( src ):
    fmt = '{:^22}'
    lcdtext = 'BrewPi brewlog for {}'.format( src )
    lcdparts = [''] * 4
    for i,v in enumerate( textwrap.wrap( lcdtext, width=22, max_lines=4 ) ):
        lcdparts[i] = fmt.format( v )
    return lcdparts


def get_jsonfiles():
    ''' Return a dict with format 
        { <BREWDIR>: { 
                       'JSONFILES': [ /brewdir/file1.json, /brewdir/file2.json, ... ],
                       'LAST_UPDATE': datetime.datetime,
                     },
          ...
        }
    '''
    data = {}
    for p in DATADIR.iterdir():
        if p.is_dir() and p.name != 'profiles':
            data[ p ] = { 'JSONFILES': [], 'LAST_UPDATE': datetime.datetime.min, }
            for f in p.iterdir():
                if f.is_file() and f.suffix == '.json':
                    data[ p ][ 'JSONFILES' ].append( f )
                    mtime = datetime.datetime.fromtimestamp( f.stat().st_mtime )
                    if mtime > data[ p ][ 'LAST_UPDATE' ]:
                        data[ p ][ 'LAST_UPDATE' ] = mtime
    return data


def j2py( elem, typ ):
    ''' Convert a json value into a native python datatype
    '''
    val = None
    if elem:
        rawval = elem[ 'v' ]
        if typ == 'datetime':
            val = jscode( 'new ' + rawval )
        elif typ == 'number':
            val = rawval
        elif typ == 'string':
            val = rawval
        else:
            raise UserWarning( "Unknown type '{}' from json".format( typ ) )
    return val


def py2js( val ):
    ''' Convert Python None type to javascript null type
    '''
    if isinstance( val, dict ):
        return { k: py2js( v ) for k,v in val.items() }
    elif isinstance( val, list ):
        return [ py2js( v ) for v in val ]
    if val is None:
        return jscode( 'null' )
    else:
        return val


def filter_empty_cols( data ):
    ''' Remove columns of data in which there is no value present in any row.
        PARAMS:
            data - dict - of the form { 'labels': list,
                                        'values': list of lists 
                                      }
        RETURN:
            cleandata - dict with same format as above but with empty cols removed
        Note: labels are excluded from checking for empty values,
              but will be filtered based on data from the remaining values (rows)
    '''
    cols_with_data = []
    for ary in data[ 'values' ]:
        for i, elem in enumerate( ary ):
            if elem is not None:
                cols_with_data.append( i )
    valid_cols = set( sorted( cols_with_data ) )
    cleanhdrs = [ data[ 'labels' ][ i ] for i in valid_cols ]
    cleanrows = []
    for ary in data[ 'values' ]:
        cleanrows.append( [ ary[i] for i in valid_cols ] )
    return { 'labels': cleanhdrs, 'values': cleanrows }



def parse_jsonfile( jpath ):
    with jpath.open() as fp:
        data = json.load( fp )
    col_nums = [ k for k,v in enumerate( data['cols'] ) if COLS_REGEX.search( v['id'] ) ]
    labels = [ data[ 'cols' ][ i ][ 'id' ] for i in col_nums ]
    rows = []
    for row in data[ 'rows' ]:
        values = []
        for i in col_nums:
            elem = row['c'][i]
            typ = data[ 'cols' ][ i ][ 'type' ]
            values.append( j2py( elem, typ ) )
        rows.append( values )
    return ( labels, rows )


def parse_jsondata( jsonlist ):
    ''' jsonlist is a list of json filepaths
        Returns a dict with format:
            { 'labels': [ ... ],
              'values': [ [...], [...], ... ],
            }
        INPUT:
            jsonlist - list of pathlib.Path's to json files
    '''
    thisdata = { 'values': [] }
    for jsonfile in sorted( jsonlist ):
        hdrs, rows = parse_jsonfile( jsonfile )
        if 'labels' not in thisdata:
            thisdata[ 'labels' ] = hdrs
        if len( hdrs ) != len( thisdata[ 'labels' ] ):
            raise UserWarning( "mismatched labels in file: '{}'".format( jsonfile ) )
        thisdata[ 'values' ].extend( rows )
    cleandata = filter_empty_cols( thisdata )
    return cleandata


def mk_dygraph( data ):
    ''' data formated as: { 'labels': [...], 
                            'values': [ [...], [...], ...  ] }
    '''
    COLOR_MAP = { 'BeerTemp': 'rgb(41, 170, 41)',   #green
                  'BeerSet': 'rgb(240, 100, 100)',  #pink?
                  'FridgeTemp': 'rgb(89, 184, 255)', #light blue
                  'FridgeSet': 'rgb(255, 161, 76)',  #orange
                  'RoomTemp': 'rgb(128,128,128)',     #grey
                  'RedTemp': 'red',
                  'RedSG': 'red',
                  'GreenTemp': 'lime',
                  'GreenSG': 'lime',
                  'BlackTemp': 'black',
                  'BlackSG': 'black',
                  'PurpleTemp': 'purple',
                  'PurpleSG': 'purple',
                  'OrangeTemp': 'orange',
                  'OrangeSG': 'orange',
                  'BlueTemp': 'darkblue',
                  'BlueSG': 'darkblue',
                  'YellowTemp': 'yellow',
                  'YellowSG': 'yellow',
                  'PinkTemp':  'orchid',
                  'PinkSG': 'orchid',
                }
    SG_details = { 'axis': 'y2', 'strokePattern': [ 7, 3 ] }
    SG_labels = [ 'RedSG', 'GreenSG', 'PurpleSG', 'BlackSG', 
                  'OrangeSG', 'BlueSG', 'YellowSG', 'PinkSG' ]
    series_opts = { k: SG_details for k in SG_labels }
    opts = {
        'legend': 'always',
        'labels': data[ 'labels' ],
        'colors': [ COLOR_MAP[ k ] for k in data[ 'labels' ][ 1: ] ],
        'labelsDiv': jscode( "document.getElementById('curr-beer-chart-controls')" ),
        'labelsSeparateLines': jscode( 'true' ),
        'series': series_opts,
        'ylabel': 'Temperature (C)',
        'y2label': 'Gravity (SG)',
        'axes': { 
            'y': { 'valueFormatter': jscode( 'tempFormat' ),
                 },
            'y2': { 'valueRange': [ 0.990, jscode( 'null' ) ],
                    'valueFormatter': jscode( 'gravityFormat' ),
                    'axisLabelFormatter': jscode( 'gravityFormat' ),
                  },
        },
        'highlightCircleSize': 2,
        'highlightSeriesOpts': {
            'strokeWidth': 1.5,
            'strokeBorderWidth': 1,
            'highlightCircleSize': 5,
        },
    }
    return '{},\n{},\n{}\n{}'.format(
        jscode( 'var beerChart = new Dygraph( document.getElementById("curr-beer-chart")' ),
        data[ 'values' ],
        pprint.pformat( opts ),
        jscode( ');' ) )


def sg2plato( SG ):
    cube = 135.997 * SG * SG * SG
    square = 630.272 * SG * SG
    single = 1111.14 * SG
    scalar = 616.868
    return cube - square + single - scalar


def calc_fermentation_rate( jsondata ):
    ''' Create table of fermentation data
        INPUT: jsondata - dict with format:
                          { 'labels': [ ... ],
                            'values': [ [...], [...], ... ],
                          }
        OUTPUT: dict with format:
            { 'labels': [ ... ],
              'values': [ [...], [...], ... ], ]
            }
            WHERE labels is a list of headers
            AND   values is a list of lists wherein each sublist has values matching
                  the headers given in labels
    '''
    pprint.pprint( jsondata[ 'labels' ] )
    time_col = 0 #time is always the first column
    regx = re.compile( 'SG' )
    col_nums = [ k for k,v in enumerate( jsondata[ 'labels' ] ) if regx.search( v ) ]
    col_names = [ jsondata[ 'labels' ][ i ] for i in col_nums ]
    gravity_data = {}
    for row in jsondata[ 'values' ]:
        rawtime = row[ time_col ] #looks like "new Date(2017,3,29,18,59,42)"
#        pprint.pprint( rawtime )
        cleantime = str( rawtime )[9:-1]
        parts = cleantime.split( ',' )
#        pprint.pprint( parts )
        # javascript months are 0-based, python months are 1-based
        parts[1] = int( parts[1] ) + 1
        thetime = datetime.date( *( map( int, parts[0:3] ) ) )
        if thetime not in gravity_data:
            gravity_data[ thetime ] = dict( zip( col_names, [[]] * len( col_nums ) ) )
        for col in col_nums:
            colname = jsondata[ 'labels' ][ col ]
            gravity_data[ thetime ][ colname ].append( row[ col ] )
    hdrs = [ jsondata[ 'labels' ][ time_col ] ]
    for name in col_names:
        for unit in [ 'SG', 'Plato' ]:
            hdrs.extend( [ '{} {}'.format( name, unit ) ] )
    output_rows = []
    for date in sorted( gravity_data.keys() ):
        for hdr in gravity_data[date].keys():
            vals = [ x for x in gravity_data[date][hdr] if x ]
#            print( 'DATE:{} HDR:{} NUMVALS:{}'.format( date, hdr, len( vals ) ) )
#            pprint.pprint( vals )
            vmax = max( vals, default=0 )
            vmin = min( vals, default=0 )
            diff = vmax - vmin
            if vmax==0 or vmin==0:
                diff = 0
            plato = sg2plato( 1.0 + diff )
            output_rows.append( [ date.strftime( '%d-%b' ), 
                                  '{:1.4f}'.format( diff ), 
                                  '{:1.2f}'.format( plato ) ] )
    return { 'labels': hdrs, 'values': output_rows }


def dict2html_table( data ):
    table_hdrs = [ '<th>{}</th>'.format( h ) for h in data[ 'labels' ] ]
    table_rows = []
    for row in data[ 'values' ]:
        cells = [ '<td>{}</td>'.format( v ) for v in row ]
        table_rows.append( ''.join( cells ) )
    html_parts = [ '<table>' ]
    html_parts.append( '<tr>{}</tr>'.format( ''.join( table_hdrs ) ) )
    html_parts.extend( [ '<tr>{}</tr>'.format( row ) for row in table_rows ] )
    html_parts.append( '</table>' )
    return "\n".join( html_parts )


def mk_html( template_data, outfile ):
    with HTML_TEMPLATE.open() as infile:
        doc = infile.read()
    tmpl = myTemplate( doc )
    print( 'Writing file: {}'.format( outfile ) )
    with outfile.open( mode='w' ) as fh:
        fh.write( tmpl.substitute( template_data ) )


def run():
    jsonlist = get_jsonfiles()
    for dir, jsondata in jsonlist.items():
        combined_json = parse_jsondata( jsondata[ 'JSONFILES' ] )
        print( 'Brewdir: {}'.format( dir ) )
        beername = safe_filename( dir.name )
        outfn = dir.parent.joinpath( beername ).with_suffix( '.html' )
        # only create html if there is new json data
        html_mtime = datetime.datetime.min
        if outfn.exists():
            html_mtime = datetime.datetime.fromtimestamp( outfn.stat().st_mtime )
        if jsondata[ 'LAST_UPDATE' ] <= html_mtime:
            # No new changes to json data, dont create new html file
            print( 'No changes, skipping' )
            continue
        f_rate = calc_fermentation_rate( combined_json )
        f_rate_html = dict2html_table( f_rate )
        lcdparts = mk_lcdparts( beername )
        template_data = { 'BEERNAME': beername,
                          'LCD0': lcdparts[0],
                          'LCD1': lcdparts[1],
                          'LCD2': lcdparts[2],
                          'LCD3': lcdparts[3],
                          'BEERCHART': mk_dygraph( py2js( combined_json ) ),
                          'FERMENTATION_RATE': f_rate_html,
                        }
        mk_html( template_data, outfn )


if __name__ == '__main__':
    run()
