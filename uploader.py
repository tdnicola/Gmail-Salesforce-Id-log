#!/usr/bin/env python

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

gauth = GoogleAuth()
# Try to load saved client credentials
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")

drive = GoogleDrive(gauth)

file_list = drive.ListFile({'q': "'1LrI5olmWHkdxhMgzP59B7EWvOSLQWq2x' in parents and trashed=false"}).GetList()

document_path = r"/mnt/c/Users/tnicola/My Documents/Scripts/gmailBatchFetcher/upload_logs"

print(file_list)

def uploadFile(file_name, file_path):
    batch_records = drive.CreateFile({'title': file_name, 'parents': [{'id': '1LrI5olmWHkdxhMgzP59B7EWvOSLQWq2x'}]})
    batch_records.SetContentFile(file_path)
    # filetoupload = drive.CreateFile({'title': "I'm in a folder!.txt", 'parents': [{'id': e['id']}]})
    batch_records.Upload(param={'convert': True})

def doc_path_checking():
    for fname in os.listdir(document_path):
        log_file_path = document_path + '/' + fname
        try:
            uploadFile(fname, log_file_path)
            print('uploaded?')
        except:
            print('failed')
