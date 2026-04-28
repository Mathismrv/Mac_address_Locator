# MAC_address_Locator
Ce script a pour but de localiser une adresse MAC dans une fabric ExtremeCloudIQ en utilisant le SDK Python de Thibault Chevalleraud. 
Le script interroge les tables MAC des switchs de la fabric pour trouver une adresse MAC cible et retourne le nom du switch et le port où elle est connectée.

## Installation
1. Télécharger XIQSE-SDK de Thibault Chevalleraud sur son GitHub : [www.github.com/TChevalleraud/XIQSE-SDK-Python]
2. Exécuter les commandes données dans le README de Thibault pour installer le SDK et ses dépendances.
3. Télécharger le projet MAC_address_Locator sur votre machine.
4. Ajouter à vos scripts dans ExtremeCloudIQ le script `MAC_address_Locator.py` (dans l'onglet Task).
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

### `main()`
Fonction principale du script qui coordonne les actions (appels CLI, requêtes GraphQL, changements de switch) pour localiser la MAC cible.
