#!/usr/bin/python3
# -*- coding: utf-8 -*- 
import json
import os
import logging
import logs
from alma_set import Set
import requests
from re import search

TITLE = "Code civil"
FRBR_GRP_ID = "130126728"

SERVICE = "Primo_Analyse_FRBR"
URL_PROD="https://api-eu.hosted.exlibrisgroup.com/primo/v1/search?vid=33PUDB_UB_VU1&tab=default_tab&scope=catalog_pci&q=any%2Ccontains%2C{}&qInclude=facet_frbrgroupid%2Cexact%2C{}&lang=eng&offset=0&limit=200&sort=rank&pcAvailability=true&getMore=0&conVoc=true&inst=33PUDB_Ub&skipDelivery=true&disableSplitFacets=true&apikey=l8xx4d2abd05dccb426b9ee6be607bc372f9".format(TITLE,FRBR_GRP_ID)
URL_TEST="https://api-eu.hosted.exlibrisgroup.com/primo/v1/search?vid=33PUDB_UB_VU1&tab=default_tab&scope=catalog_pci&q=any%2Ccontains%2C=any,contains,Le service public du sport en Afrique noire : l'exemple du Cameroun&qInclude=facet_frbrgroupid%2Cexact%2C38651654&lang=eng&offset=0&limit=200&sort=rank&pcAvailability=true&getMore=0&conVoc=true&inst=33PUDB_Ub&skipDelivery=true&disableSplitFacets=true&apikey=l8xxef3897dc832b4355b146f7ca19cccb3e"
URL = URL_PROD

SET_NAME = "Membre Groupe FRBR_{}_{}".format(TITLE[:50],FRBR_GRP_ID)
#On initialise le logger
logs.setup_logging(name=SERVICE, level='DEBUG',log_dir=os.getenv('LOGS_PATH'))
logger = logging.getLogger(__name__)


r = requests.get(URL)
try:
    r.raise_for_status()  
except requests.exceptions.HTTPError:
    logger.error("{} :: {} :: HTTP Status: {} || Method: {} || URL: {} || Response: {}".format(URL, 
                                                                                                    SERVICE,
                                                                                                    r.status_code,
                                                                                                    r.request.method,
                                                                                                    r.url,
                                                                                                    r.text))
    exit()
reponse = json.loads(r.content.decode('utf-8'))
docs_list = reponse['docs']
# Création du set
api_key = os.getenv('PROD_NETWORK_BIB_API')
jeu = Set(apikey=api_key)
erreur, reponse = jeu.create_set(SET_NAME)
if erreur :
    logger.debug(reponse)
    exit()
dataset = reponse
logger.info("Set créé avec succès")
# for doc in docs_list :
#     primo_id = doc['pnx']['control']['recordid'][0]
#     if primo_id[0:8] == 'dedupmrg':
#         if 'k3' in doc['pnx']['frbr'] :
#             clefs_frbrK3 = doc['pnx']['frbr']['k3']
#         else : 
#             clefs_frbrK3 = ['None']
#         if 'k2' in doc['pnx']['frbr'] :
#             clefs_frbrK2 = doc['pnx']['frbr']['k2']
#         else : 
#             clefs_frbrK2 = ['None']
#         if len(clefs_frbrK2) > 1 or len(clefs_frbrK3) > 1 :
#             logger.debug("{}\n\tk3 : {}\n\tk2 : {}".format(primo_id,clefs_frbrK3,clefs_frbrK2))
logger.debug(reponse)
records_list = []
# Parcours des réponse et identification des MMSID de la NZ
for doc in docs_list :
    mmsid_list = doc['pnx']['search']['addsrcrecordid']
    for mms_id in mmsid_list :
        if search('.*04671$', mms_id):
            set_member = {"id" : mms_id}
            records_list.append(set_member)
            logger.debug(mms_id)
# Envoi des notices dans la liste
jeu.update_set(dataset,records_list,SET_NAME)
if erreur :
    logger.debug(reponse)
    exit()
logger.info("{} notices ajoutées au jeu de résultat !".format(len(records_list)))