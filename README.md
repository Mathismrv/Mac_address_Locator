# MAC_address_Locator
Ce script a pour but de localiser une adresse MAC dans une fabric ExtremeCloudIQ en utilisant le SDK Python de Thibault Chevalleraud. 
Le script interroge les tables MAC des switchs de la fabric pour trouver une adresse MAC cible et retourne le nom du switch et le port où elle est connectée.

## Installation
1. Télécharger XIQSE-SDK de Thibault Chevalleraud sur son GitHub : [www.github.com/TChevalleraud/XIQSE-SDK-Python]
2. Exécuter les commandes données dans le README de Thibault pour installer le SDK et ses dépendances, il faut que le script est accés au fonction de Thibault.
3. Télécharger le projet MAC_address_Locator sur votre machine.
4. Ajouter à vos scripts dans ExtremeCloudIQ le script `MAC_address_Locator.py` (dans l'onglet Task+le bouton "Add+",), vous devez donné les droits necessaires pour que le script puisse executer des commandes CLI et GraphQL.
5. Exécuter le script sur un switch au hasard.
6. Rentrer l'adresse MAC que vous voulez localiser dans la fabric.
7. Le script va vous retourner le nom du switch et le port où est connectée votre adresse MAC cible.

## Fonctions

### `IsLocal(line)`
Cette fonction vérifie si la ligne rentrée contient le mot "LOCAL" ou "NON-LOCAL" pour déterminer si l'adresse MAC est en local sur le switch ou pas.
- **param line** : ligne de la table MAC où est trouvée notre adresse MAC cible.
- **return** : retourne 0 ou 1 et un message pour indiquer si la MAC est locale ou non.

### `ExecuteCLICommand(command)`
Exécute une commande CLI simple et retourne la réponse brute.
**Exemple :**
```python
command = "enable"
print(ExecuteCLICommand(command))
```

### `ExecuteGraphQL(query_string)`
Exécute une requête GraphQL brute et retourne la réponse.
- **param query_string** : Requête GraphQL sous forme de string.
- **return** : Réponse de la requête GraphQL.

**Exemple :**
```python
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
raw_response = ExecuteGraphQL(raw_query)
print("GraphQL response: " + str(raw_response))
```

### `getSwitchIP(GraphQl_response, Switch_Name)`
Cette fonction sert à extraire l'IP du switch à partir de la réponse GraphQL en fonction du nom du switch.
- **param GraphQl_response** : Réponse GraphQL sous forme de dictionnaire/liste.
- **param Switch_Name** : Nom du switch.
- **return** : IP du switch ou message d'erreur si le switch n'est pas trouvé.

### `getTunnel(line)`
La fonction permet de récupérer le tunnel associé à la ligne de la table MAC où est trouvée notre adresse MAC cible. Et vérifie si l'adresse MAC est en local sur le premier switch interrogé.
- **param line** : ligne de la table MAC où est trouvée notre adresse MAC cible.
- **return** : Le nom du switch de la colonne tunnel ou bien, si la MAC est locale, on renvoie le nom du switch + le port.

### `getSwitchPrompt()`
Cette fonction n'envoie rien pour simuler une pression sur la touche "entrée" et ainsi récupérer le prompt du switch. Elle est utilisée dans la fonction `IsLocal()`.
- **return** : Le prompt du switch.

### `ParseMacTableResponse(raw_response, mac_address)`
Cette fonction sert à vérifier si l'adresse MAC recherchée est présente dans la réponse brute de la commande CLI.
- **param raw_response** : Réponse brute de la commande CLI.
- **param mac_address** : Notre MAC address cible.
- **return** : retourne la ligne où est trouvée l'adresse MAC.

### `EntryToCorrectFormat(UserInput)`
Cette fonction permet de nettoyer l'adresse MAC donnée par l'utilisateur en supprimant tous symboles et en ne recuperant que les characteres qui ressemble a de l'hexadecimal et reconstruit l'adresse MAC sous le format "XX:XX:XX:XX:XX:XX"
- **param UserInput**: L'adresse MAC entrée par l'utilisateur
- **return**: L'adresse MAC formatée sous la forme "XX:XX:XX:XX:XX:XX" ou un message d'erreur si le format n'est pas accepté

### `CleanPort(port)`
Fonction qui sert a nettoyer la sortie du port pour n'afficher que le port 
- **param port**: port a nettoyé
- **return**: port tout propre

### `AskDebug()`
Regarde si l'utilisateur veut un debug 
- **return**: retourne True ou False en fonction de ce que veut l'utilisateur

### `Betterprint(String):`
Fonction qui permet une meilleur lisibilite dans le terminal de ExtremeCLound
- **param String**: une chaine de charactere qui va etre rendu plus lisible 


### `main()`
La fonction `main()` contient toute la logique pour localiser l'address MAC, voici les grosses etapes du main: 
- Elle recupere l'entrée de l'utilisateur la nettois
- Entre dans une boucle puis interroge le switch choisi au debut pour savoir s'il la connait 
- Ensuite on recupere la ligne ou notre Mac a été trouvée et on regarde si un tunnel existe
- On verifie si la MAC n'est pas deja en local sur le premier switch interrogé
- Si oui, on sort de la boucle
- Sinon on doit se connecter au switch que le tunnel affiche
- On recupere donc l'IP de ce switch via son nom recuperé par le tunnel
- On se connecte a celui-ci et on boucle 
- FIN de boucle :
- On verifie que notre MAC est bien en local
- Sinon, alors notre MAC n'est pas sur ce switch, il y a une erreur
- Si elle est en local, c'est fini, on affiche nos resultats (IP du switch, le port, et l'adresse MAC)
