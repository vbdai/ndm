import argparse
import sys
import hashlib
import hmac
import binascii
from datetime import datetime
import requests
from requests.structures import CaseInsensitiveDict
import os
#### to fix proxy issue - from  ####
import ssl
os.environ['http_proxy'] = 'http://127.0.0.1:3128'
os.environ['ftp_proxy'] = 'ftp://127.0.0.1:3128'
os.environ['https_proxy'] = 'http://127.0.0.1:3128'
os.environ['no_proxy'] = '127.0.0.*,*.huawei.com,localhost'
os.environ['cntlm_proxy'] = '127.0.0.1:3128'
os.environ['SSL_CERT_DIR'] = '/etc/ssl/certs'
ssl._create_default_https_context = ssl._create_unverified_context
#####


def upload_and_link(args):
    yourAccessKeyID = "OX7DJQEABPAFUDEUEROA"
    yourSecretAccessKeyID = 'IGk3DNyYAa43RV9JmCACr77901EgneI3pNEXe6r5'
    Bucket_Name = "ndam"
    Region = "cn-north-4"
    FileName = args.filename  # "test_batch0_pred.jpg"
    #file_path = args.filepath
    # Generating the Signature
    IS_PYTHON2 = sys.version_info.major == 2 or sys.version < '3'
    httpMethod = "PUT"
    contentType = ""  # "application/xml"
    # "date" is the time when the request was actually generated
    date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    canonicalizedHeaders = ""  # "x-obs-acl:private"
    CanonicalizedResource = "/"+Bucket_Name+"/"+FileName
    canonical_string = httpMethod + "\n" + "\n" + contentType + "\n" + \
        date + "\n" + canonicalizedHeaders + CanonicalizedResource
    if IS_PYTHON2:
        hashed = hmac.new(yourSecretAccessKeyID,
                          canonical_string, hashlib.sha1)
        encode_canonical = binascii.b2a_base64(hashed.digest())[:-1]
    else:
        hashed = hmac.new(yourSecretAccessKeyID.encode(
            'UTF-8'), canonical_string.encode('UTF-8'), hashlib.sha1)
        encode_canonical = binascii.b2a_base64(
            hashed.digest())[:-1].decode('UTF-8')

    url = "http://"+Bucket_Name+".obs."+Region+".myhuaweicloud.com/"+FileName
    print(url)
    headers = CaseInsensitiveDict()
    headers["Date"] = date
    headers["Authorization"] = "OBS " + \
        yourAccessKeyID + ":" + encode_canonical

    resp_test = requests.get(url)
    print(url)
    print(resp_test.status_code)

    proxies = {'http': 'http://127.0.0.1:3128',
               'https': 'https://127.0.0.1:3128', 'ftp': 'ftp://127.0.0.1:3128'}
    resp = requests.put(url, headers=headers, data=open(
        FileName, 'rb'), proxies=proxies, verify=False)

    print(resp.status_code)
    DirectDownloadLink = None
    if resp.status_code == 200:
        DirectDownloadLink = "https://"+Bucket_Name + \
            ".obs."+Region+".myhuaweicloud.com/"+FileName
        print(DirectDownloadLink)
    else:
        print('Uploading failed!')
        print(resp.headers)
    return DirectDownloadLink


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload Arguments')
    parser.add_argument('--filename', type=str, help='data filename')
    args = parser.parse_args()
    uploaded_link = upload_and_link(args)
