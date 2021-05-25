#!/usr/bin/env python

from Google import Create_Service
import base64
import re
import uploader
import os

CLIENT_FILE='client.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']

service = Create_Service(CLIENT_FILE,API_NAME,API_VERSION,SCOPES)

#about my gmail information
#service.users().getProfile(userId='me').execute()

#need to be completed gmail labels
pbm_label_id = 'Label_4899090031194194311'
claims_label_id = 'Label_3714798389628113853'
#completed
pbm_completed_label_id ='Label_6762915334295495346'
claims_completed_label_id = 'Label_3024528762162722106'

base_file_path = '/mnt/c/Users/tnicola/My Documents/Scripts/gmailBatchFetcher/'

def search_messages_for_ids(service, label):
    try:
        #searching for the label of PBM/Insurance claims. returns {id and thread}
        # search_id = service.users().messages().list(userId='me', q=f'label:{search_string}').execute()
        search_id = service.users().messages().list(userId='me', labelIds=f'{label}').execute()

        #for testing individual labels
        #search_id = service.users().messages().list(userId='me', labelIds='Label_3714798389628113853').execute()

        # searches for label names/ids
        # labelsList = service.users().labels().list(userId='me').execute()

        #get id
        # messages_list = search_id['messages']
        
        messages_list = search_id.get('messages')

        #blank list to put each id into
        final_list_ids = []

        #estimate of the amount
        result_amount = search_id['resultSizeEstimate']
        if result_amount > 0:
            for ids in messages_list:
                final_list_ids.append(ids['id'])
            return final_list_ids
        else: 
            print('No emails found')
            empty_array = []
            return empty_array
            
    except:
        print('An error occured: %s')
    
pbm_email_list = search_messages_for_ids(service, pbm_label_id)
insurance_claims_email_list = search_messages_for_ids(service, claims_label_id)


def get_subject_data(service, msg_ids, type):
    if (len(msg_ids) == 0):
        print('No emails to find IDS in: {type}' )
        return
    else: 
        f = open(f'{base_file_path}/temp_logs/{type}.txt', "w+")                    
        f.write('ID'+ '\n')
        print('Log file created')

        for id in msg_ids:

            # creating log file to upload in data loader
            try:
                #raw_message and content_nonsense are all fancy and not understandable. google'd how to translate to plain text...
                raw_message = service.users().messages().get(userId ='me', id=f'{id}', format='full').execute()

                # Get the right body data item (this part was my Heureka-moment as there are several 'data' keys)
                content_nonsense = raw_message['payload']['parts'][0]['parts'][1]['body']['data']

                # Encode and now readable
                msg_body = base64.urlsafe_b64decode(content_nonsense).decode('utf-8')

                #finds and stores all 18 digits SF ids into an array. 
                salesforce_id_regex = re.findall("[a-zA-Z0-9]{18}", msg_body) 

                #creating set to not have duplicate SF ids
                salesforce_ids_set = set()
            
                if (len(salesforce_id_regex) > 0):
                    #write each Id to the file
                    for sfIds in salesforce_id_regex:
                        salesforce_ids_set.add(sfIds)
                else:
                    print('no SF id in message')

                # writing unique id in file
                for uniqueIds in salesforce_ids_set:
                    f.write(uniqueIds+ '\n')

                # setting up the correct labels to be added/removed
                if(type == 'pbm'):
                    changing_labels = {'removeLabelIds': [f'{pbm_label_id}'], 'addLabelIds': [f'{pbm_completed_label_id}']}
                else:
                    changing_labels = {'removeLabelIds': [f'{claims_label_id}'], 'addLabelIds': [f'{claims_completed_label_id}']}

                # sending the call to change the labels
                service.users().messages().modify(userId='me', id=f'{id}', body=changing_labels).execute()

            except Exception as e:
                print('An error occured: ' + e)
        f.close()

        os.rename(base_file_path + 'temp_logs/' + type + '.txt', f"{base_file_path}upload_logs/{type}.csv")


        print('completed the ' + type)


get_subject_data(service, pbm_email_list, 'pbm')
get_subject_data(service, insurance_claims_email_list, 'claims')

uploader.doc_path_checking()