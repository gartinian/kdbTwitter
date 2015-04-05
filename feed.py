#!/usr/bin/python

import base64
import hashlib
import hmac
import json
import kdb # From https://bitbucket.org/halotis/qpy/overview
import os
import pprint
import time
import urllib
import urllib2

# Fill out these values with your own keys & secrets.
# They can be obtained from dev.twitter.com
AUTH_DICTIONARY = { 
    'oauth_consumer_key'        : 
        'YOUR KEY HERE',
    'oauth_consumer_secret'     : 
        'YOUR SECRET HERE',
    'oauth_token'               : 
        'YOUR TOKEN HERE',
    'oauth_access_token_secret' : 
        'YOUR KEY HERE' }

class Oauth:
    # Implements authorization as described here:
    # https://dev.twitter.com/oauth/overview/authorizing-requests

    def __init__(self, auth_dict):

        self.url = "https://stream.twitter.com/1.1/statuses/sample.json"
        self.consumer_secret     = auth_dict['oauth_consumer_secret']
        self.access_token_secret = auth_dict['oauth_access_token_secret']

        self.oauth_dict = {
            'oauth_consumer_key'     : auth_dict['oauth_consumer_key'],
            'oauth_nonce'            : self.getNonce(),
            'oauth_signature_method' : 'HMAC-SHA1',
            'oauth_timestamp'        : self.getTimestamp(),
            'oauth_token'            : auth_dict['oauth_token'],
            'oauth_version'          : '1.0',
            'oauth_signature'        : None }

        self.oauth_dict['oauth_signature'] = self.getSignature()
       
    # END def __init__

    def __str__(self):
        toPrint = ""
        for k,v in sorted(self.oauth_dict.iteritems()):
            toPrint += k + ':\t' + v + '\n'
        return toPrint
    # END __str__

    def getNonce(self):
        return base64.b64encode(str(os.urandom(32)))

    def getTimestamp(self):
        return str(int(time.time()))

    def getSigBaseComponent(self, key, value):
        return key + '=' + pctEncode(value)
        
    def getSigBase(self):
        base = ""

        sigDict = {(k,v) for k,v in self.oauth_dict.iteritems() 
                                                     if k != 'oauth_signature'}

        for k,v in sorted(sigDict):
            base += self.getSigBaseComponent(k,v) + '&'

        # Remove trailing ampersand
        base = base[:-1]

        return 'GET' + '&' + \
                   pctEncode(self.url) + '&' + \
                   pctEncode(base)
    # END getSigBase

    def getSigKey(self):
        return pctEncode(self.consumer_secret) + '&' + \
                   pctEncode(self.access_token_secret)
    # END getSigKey

    def getSignature(self):
        sigBase = self.getSigBase()
        sigKey  = self.getSigKey()
        return hmac.new(sigKey, sigBase, hashlib.sha1).digest().encode("base64")
    # END getSignature

    def formAuthorization(self):
       auth = "OAuth "
       for k,v in sorted(self.oauth_dict.iteritems()):
           auth += k + '=' + '\"' + pctEncode(v) + '\"' + ', '

       auth = auth[:-2]
       return auth
    # END formAuthorization

# END class Oauth

def pctEncode(x): return urllib.quote(x, '')

def rxStream(oauth):
    request = urllib2.Request(oauth.url)
    request.add_header("Authorization", oauth.formAuthorization())
    return urllib2.urlopen(request)
# END rxStream

def formTable(t):
    ts  = str(t['timestamp_ms'])
    sn  = str(t['user']['screen_name'])
    # Many tweets are not in ASCII format.  Ignore those characters,
    # then escape single-quotes and double-quotes
    txt = t['text'].encode('ascii', 'ignore') \
                   .replace('\\', '\\\\').replace('"', '\\"') \
                   .replace('\n', ' ')

    cmd = '([] ' + \
              'timestamp_ms:enlist  ' + ts  +  ';' + \
              'screen_name :enlist "' + sn  + '";' + \
              'tweet       :enlist "' + txt + '")'

    return cmd
# END formTable

def main():
    # OAUTH object, which builds the http authorization header
    OAUTH = Oauth(AUTH_DICTIONARY)

    # Initiate a connection to kdb on port 3000
    conn = kdb.q('localhost', 3000, '')

    # Clear tweets table.  Remove this line if you would like the 
    # table to persiste when restarted
    conn.k('tweets:();')

    # The rxStream function initiates the http stream with the 
    # correct authentication.  The tweet object represents a single
    # tweet
    for tweet in rxStream(OAUTH):
        # Convert tweet to JSON format
        t = json.loads(tweet)

        # Only process tweets (there are some outputs from the 
        # http stream that are not tweets
        if "created_at" in t.keys():
            # Uncomment this line to see entire JSON output
            #pprint.pprint(t, width=2)
            # Form a q-formatted table
            table = formTable(t)

            # Append tweet to the 'tweets' table in kdb
            conn.k('.u.upd[`tweets;' + table + ']')

        # END if 'created_at'
    # END for tweet...
# END main

main()
