'''
#@MetaDataStart
#@DetailDescriptionStart
#This script allows you to find the tunnel associated with a given MAC address in a VOSS/Fabric Engine network
#@DetailDescriptionEnd
#@SectionStart (description = \"Mac address Locator\")
#    @VariableFieldLabel (
#        description = \"Enter MAC\",
#        type = string,
#        required = yes,
#        name = userInput_MAC_Address,
#    )#@SectionEnd
#@MetaDataEnd
'''

import sys
import re
# Initialisation du framework XIQSE de Thibault Chevalleraud
from XIQSE import XIQSE
ctx = XIQSE(emc_cli, emc_nbi, emc_results, emc_vars)
def ExecuteCLICommand(command):
    '''
    Executes une commande CLI simple et retourne la réponse brute.

    exemple:
    command="enable"
    print(execute_cli_command(command))

    '''
    output = ctx.CLI.sendCommandShow(command)
    return output


def ParseMacTableResponse(raw_response, mac_address):
    '''
    Cette fonction sert a verifier si l'adresse MAC recherchée
    est présente dans la réponse brute de la commande CLI.
    :param raw_response: Reponse brute de la commande CLI
    :param mac_address: Notre Mac address cible
    :return: retourne la ligne ou est trouvée la mac address
    '''
    for line in raw_response.splitlines():
        if mac_address in line:
            return line
    return

def getTunnel(line):
    '''
    La fonction permet de recuperer le tunnel associé à la ligne de la table MAC ou est trouvée notre adresse MAC cible.
    Et verifie si l'adresse mac est en local sur le premier switch interrogé
    :param line: ligne de la table MAC ou est trouvée notre adresse MAC cible
    :return: Le nom du switch de la colonne tunnel ou bien gagné la mac est local et on renvoie le nom du switch+le port
    '''
    parts = line.split()
    if len(parts) < 6:
        return "Unable to parse tunnel from line: " + line
    if parts[5] == "-":
        return "LOCAL"
    return parts[5]

def ExecuteGraphQL(query_string):
    '''
    Execute une requete GraphQL brute et retourne la réponse.
    :param query_string: Requete GraphQL sous forme de string
    :return: Reponse de la requete GraphQL
     exemple:
    raw_query = \'''
        query {
            network {
                devices {
                    ip
                    sysName
                }
            }
        }
    \'''
    raw_response = execute_cli_command(query_string)
    print("GraphQL response: " + str(raw_response))

    '''
    try :
        return ctx.GraphQL.nbiQuery({'json': query_string}, returnKeyError=True)
    except Exception as e:
        print("Error executing GraphQL query: " + str(e))
        return None

def getSwitchIP(GraphQl_response, Switch_Name):
    '''
    Cette fonction sert a extraire l'IP du switch à partir de la réponse GraphQL en fonction du nom du switch.
    :param GraphQl_response: Reponse GraphQL sous forme de string
    :param Switch_Name: Nom du switch
    return: IP du switch ou message d'erreur si le switch n'est pas trouvé
    '''
    try:
        reponse= GraphQl_response['network'] ['devices']
        for device in reponse:
            if device['sysName'] == Switch_Name:
                return device['ip']
        return
    except KeyError as e:
        print("KeyError lors de l'extraction de l'IP du switch: " + str(e))
        return "Error: Key not found in GraphQL response"


def IsLocal(line) :
    '''
    La fonction permet de verifie si la ligne de la table mac fournit est bien en local ou non.
    :param line: Ligne de la table MAC ou est trouvée notre adresse MAC cible
    :return: return 1 ou 0 et affiche un message de succes ou d'erreur en fonction du resultat
    '''
    parts = line.split()
    try:
        if parts[4] == "NON-LOCAL":
            print("La mac address n est pas en local sur ce switch")
            return 0
        if parts[4] == "LOCAL":
            print("Gagne, la MAC address : "+ parts[2] +" est en local sur le switch : "+getSwitchPrompt()+ ", et sur le port: " + parts[3])
            return 1
    except IndexError:
        print("Format inattendu pour la ligne: " + line)
        return -1


def getSwitchPrompt():
    '''
    Cette fonction n'envoie rien pour simuler une pression sur la touche "entrée"
    et ainsi recuperer le prompt du switch. Elle est utilisee dans la fonction Islocal.
    :return: le prompt du switch
    '''
    result = ctx.emc_cli.send("")
    if result.isSuccess():
        raw_output = result.getOutput()
        lignes = raw_output.splitlines()
        if lignes:
            return lignes[-1].strip()
    return "Prompt non trouvé"



def main():
    MAC_cible = emc_vars['userInput_MAC_Address'].strip()
    #on recupere l'adresse MAC cible depuis les variables d'entrée de l'utilisateur
    if not re.match(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$', MAC_cible):
        print("Format invalide. Attendu: XX:XX:XX:XX:XX:XX")
        #on verifie que le format est correct
        return

    command = "show vlan mac-address-entry mac " + MAC_cible

    raw_response = ExecuteCLICommand(command)
    #On demande au switch de nous afficher la ligne de la table MAC ou est trouvée notre adresse MAC cible
    if raw_response is None or "error" in raw_response.lower():
        print("Pas de reponse ou erreur lors de l execution de la commande CLI: " + str(raw_response))
        return

    result = ParseMacTableResponse(raw_response, MAC_cible)
    #On verifie que la ligne est trouvée sinon on affiche un message d'erreur
    if result == None:
        print("MAC address pas trouvee dans la table MAC du switch " + emc_vars['deviceName'])
        return

    tunnel_info = getTunnel(result)
    #si on a pas d'erreur alors on recupere le tunnel associé à la ligne de la table MAC ou est trouvée notre adresse MAC cible
    #si la adresse est vu en local on affiche un message de succes
    if tunnel_info =="LOCAL":
        Commandbis= "sh i-sid mac-address-entry mac "+ MAC_cible
        results = ExecuteCLICommand(Commandbis)
        linebis = ParseMacTableResponse(results, MAC_cible)
        if linebis is None:
            parts = result.split()
            status = parts[1]
            port = parts[3]
            print("La MAC address " + MAC_cible + " (Status: " + status + ") est en local sur le switch : " + getSwitchPrompt() + ", port : " + port + ". (Non presente dans I-SID, probablement une adresse du switch)")
        else:
            IsLocal(linebis)
        return

    raw_query = '''
        query {
            network {
                devices {
                    ip
                    sysName
                }
            }
        }
    '''
    #requete GraphQL pour recupere la liste des IP de tous les switchs dans la fabric avec leur sysName pour recupere celui qui nous interesse

    graphql_response = ExecuteGraphQL(raw_query)
    #on execute notre commande

    if graphql_response:
        switch_ip = getSwitchIP(graphql_response, tunnel_info)
        #on recupere l'IP du switch via son sysName (qui est dans tunnel_info)
        if switch_ip==None:
            print("Impossible de recuperer l'IP du switch " + str(tunnel_info) + " depuis la reponse GraphQL")
            return
            #si la fonction retourne une erreur on verifie et on l'affiche
        else:
            print("Connection au switch: " + switch_ip)
            ctx.close()
            #on ferme la connection avec le switch initial
            ctx.setIpAddress(switch_ip)
            #on defini l'IP du Switch qu'on veut interroger
            emc_cli.connect()
            #on se connecte a celui-ci
            NewCommand= "sh i-sid mac-address-entry mac "+ MAC_cible
            #On execute une nouvelle commande qui affiche si les addresses MAC sont en local
            # ou pas sur ce switch et sur quel port
            nouvelle_reponse_brute = ExecuteCLICommand(NewCommand)
            #on recupere la reponse brute de la commande
            nouveau_resultat = ParseMacTableResponse(nouvelle_reponse_brute, MAC_cible)
            #on verifie que la ligne est trouvée
            if nouveau_resultat == None:
                print("La MAC address n'a pas ete trouvee dans la table MAC du switch " + emc_vars['deviceName'])
            else:
                IsLocal(nouveau_resultat)
                #on verifie si la mac address est en local ou pas sur ce switch et on affiche le resultat
main()