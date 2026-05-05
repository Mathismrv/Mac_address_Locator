'''
#@MetaDataStart
#@DetailDescriptionStart
#This script allows you to find the tunnel associated with a given MAC address in a VOSS/Fabric Engine network
#@DetailDescriptionEnd
#@SectionStart (description = Mac address Locator)
#    @VariableFieldLabel (
#        description = Enter MAC,
#        type = string,
#        required = yes,
#        name = userInput_MAC_Address,
#    )#@SectionEnd
#@SectionStart (description = Debug)
#    @VariableFieldLabel (
#        description = Debug,
#        type = string,
#        required = no,
#        validValues = [Enable, Disable],
#        name = userInputDebug,
#    )#@SectionEnd
#@MetaDataEnd
'''

import re
# Initialisation du framework XIQSE de Thibault Chevalleraud
from XIQSE import XIQSE
ctx = XIQSE(emc_cli, emc_nbi, emc_results, emc_vars)
def execute_cli_command(command):
    '''
    Executes une commande CLI simple et retourne la réponse brute.

    exemple:
    command="enable"
    print(execute_cli_command(command))

    '''
    output = ctx.CLI.sendCommandShow(command)
    return output

def ask_debug():
    '''
    Regarde si l'utilisateur veut un debug
    :return: retourne True ou False en fonction de ce que veut l'utilisateur
    '''
    user_input_debug =emc_vars['userInputDebug']
    if user_input_debug=="Enable":
        return True
    elif user_input_debug =="Disable" :
        return False

def parse_mac_table_response(raw_response, mac_address):
    '''
    Cette fonction sert a verifier si l'adresse MAC recherchée
    est présente dans la réponse brute de la commande CLI.
    :param raw_response: Réponse brute de la commande CLI
    :param mac_address: Notre Mac address cible
    :return: retourne la ligne ou est trouvée la mac address
    '''
    for line in raw_response.splitlines():
        if mac_address in line:
            return line
    return

def get_tunnel(line):
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

def execute_graphql(query_string):
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

def get_switch_ip(graphql_response, switch_name):
    '''
    Cette fonction sert a extraire l'IP du switch à partir de la réponse GraphQL en fonction du nom du switch.
    :param graphql_response: Reponse GraphQL sous forme de string
    :param switch_name: Nom du switch
    return: IP du switch ou message d'erreur si le switch n'est pas trouvé
    '''
    try:
        response= graphql_response['network'] ['devices']
        for device in response:
            if device['sysName'] == switch_name:
                return device['ip']
        return
    except KeyError as e:
        print("KeyError lors de l'extraction de l'IP du switch: " + str(e))
        return "Error: Key not found in GraphQL response"

def is_local(line) :
    '''
    La fonction permet de verifie si la ligne de la table mac fournit est bien en local ou non.
    :param line: Ligne de la table MAC ou est trouvée notre adresse MAC cible
    :return: return 1 ou 0 et affiche un message de succes ou d'erreur en fonction du resultat
    '''
    parts = line.split()
    try:
        if parts[4] == "NON-LOCAL":
            better_print("La mac address n est pas en local sur ce switch")
            return 0
        if parts[4] == "LOCAL":
            better_print("Trouvee, la MAC address : "+ parts[2] +" est en local sur le switch : "+get_switch_prompt()+ ", et connecte sur le port: " + clean_port(parts[3]))
            return 1
    except IndexError:
        print("Format inattendu pour la ligne: " + line)
        return -1


def get_switch_prompt():
    '''
    Cette fonction n'envoie rien pour simuler une pression sur la touche "entrée"
    et ainsi recuperer le prompt du switch. Elle est utilisee dans la fonction Islocal.
    :return: le prompt du switch
    '''
    result = ctx.emc_cli.send("")
    if result.isSuccess():
        raw_output = result.getOutput()
        lines = raw_output.splitlines()
        if lines:
            prompt=lines[-1].strip()
            prompt = prompt.replace(":1>", "").strip()
            return prompt

    return "prompt non trouvé"

def clean_port(port):
    '''
    Fonction qui sert a nettoyer la sortie du port pour n'afficher que le port
    :param port: port a nettoyé
    :return: port tout propre
    '''
    if (":" in port):
        port=port.split(":")
        return port[1]
    if ("-" in port):
        port=port.split("-")
        return port[1]
    return port

def entry_to_correct_format(user_input):
    '''
    Nettoie l'entrée MAC de tous les symboles, vérifie qu'il reste 12 caractères hexadécimaux,
    et les colle au format "xx:xx:xx:xx:xx:xx".
    Accepte n'importe quel format du moment qu'il y a 12 caractères hexadécimaux valides.
    :param user_input: L'adresse MAC entrée par l'utilisateur
    :return: L'adresse MAC au format "xx:xx:xx:xx:xx:xx" ou l'entrée d'origine si invalide.
    '''
    if user_input is None:
        return user_input

    s = str(user_input).strip().lower()
    hexchars = re.sub(r'[^0-9a-f]', '', s)
    if len(hexchars) == 12:
        return ':'.join(hexchars[i:i+2]for i in range(0, len(hexchars),2))
    print("Erreur: entree MAC invalide "+ user_input +". Format attendu doit comporter 12 characteres hexa.")
    return None

def better_print(string):
    '''
    Fonction qui permet une meilleur lisibilite dans le terminal de ExtremeCLound
    :param String: une chaine de charactere qui va etre rendu plus lisible
    '''
    print("="*100 )
    print(string)
    print("="*100)


def main():
    user_input_debug=ask_debug()
    mac_cible = emc_vars['userInput_MAC_Address']
    if user_input_debug :
        print("Mac a chercher : " +mac_cible)
    mac_cible=entry_to_correct_format(mac_cible)
    if mac_cible is None: return

    print("="*100)
    print("RESULTAT TOUT EN BAS DU TERMINAL")
    print("Debut de la recherche :")
    print("="*100)


    jump_limit=5
    jump =0
    while jump < jump_limit :
        command = "show vlan mac-address-entry mac " + mac_cible
        raw_response = execute_cli_command(command)
        #On demande au switch de nous afficher la ligne de la table MAC ou est trouvée notre adresse MAC cible
        if raw_response is None or "error" in raw_response.lower():
            better_print("Pas de response ou erreur lors de l execution de la commande CLI: " + str(raw_response))
            return

        result = parse_mac_table_response(raw_response, mac_cible)
        #On verifie que la ligne est trouvée sinon on affiche un message d'erreur
        if result is None:
            better_print("MAC address pas trouvee dans la table MAC du switch actuel")
            return
        if user_input_debug :
            print("Resultat de la ligne ou la MAC a ete trouve : "+result)

        tunnel_info = get_tunnel(result)
        #si on a pas d'erreur alors on recupere le tunnel associé à la ligne de la table MAC ou est trouvée notre adresse MAC cible
        #si la adresse est vu en local on affiche un message de succes
        if (user_input_debug) :
            print("Info du tunnel trouve : "+ tunnel_info)
        if tunnel_info == "LOCAL" :
            break
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

        graphql_response = execute_graphql(raw_query)
        #on execute notre commande

        if graphql_response:
            switch_ip = get_switch_ip(graphql_response, tunnel_info)
            #on recupere l'IP du switch via son sysName (qui est dans tunnel_info)
            if user_input_debug :
                print("L'ip du switch trouve est : " + switch_ip)
            if switch_ip is None:
                better_print("Impossible de recuperer l'IP du switch " + str(tunnel_info) + " depuis la response GraphQL")
                return
                #si la fonction ne retourne rien on verifie et on l'affiche une erreur
            else:
                print("Connection au switch: " + switch_ip)
                ctx.close()#On ferme la connexion au switch actuel pour eviter que la session reste ouverte
                ctx.setIpAddress(switch_ip) #on change l'IP du switch dans le framework pour se connecter au nouveau switch
                emc_cli.connect() #on se connecte au nouveau switch
                jump += 1
        else:
            better_print("La response GraphQL est vide")
            return
    new_command= "sh i-sid mac-address-entry mac "+ mac_cible
    #On execute une nouvelle commande qui affiche si les addresses MAC sont en local
    # ou pas sur ce switch et sur quel port
    nouvelle_reponse_brute = execute_cli_command(new_command)
    #on recupere la response brute de la commande
    nouveau_resultat = parse_mac_table_response(nouvelle_reponse_brute, mac_cible)
    #on verifie que la ligne est trouvée
    if nouveau_resultat is None:
        parts = result.split()
        status = parts[1]
        port = clean_port(parts[3])
        better_print("La MAC address " + mac_cible + " (Status: " + status + ") est en local sur le switch : " + get_switch_prompt() + ", port : " + port + ". (Non presente dans I-SID, probablement une adresse du switch)")
        return
    if user_input_debug :
        print("La MAC a ete trouve sur cette ligne : "+nouveau_resultat)
    is_local(nouveau_resultat)
    #on verifie si la mac address est en local ou pas sur ce switch
    print("Nombre de saut effectue :" + str(jump))

main()