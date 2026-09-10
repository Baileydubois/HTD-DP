# HTD Cursor Rules

|                         |                                    |
| ----------------------- | ---------------------------------- |
| **Statut**              | Règles opérationnelles officielles |
| **Version**             | 1.0.0                              |
| **Date**                | 2026-09-09                         |
| **Autorité supérieure** | HTD Dev Agent Convention           |

---

## 0. Statut, portée et autorité

Les HTD Cursor Rules définissent les règles opérationnelles applicables lorsque Cursor travaille dans un dépôt de l'écosystème HTD.

Elles constituent une application opérationnelle des autorités HTD supérieures et ne créent pas une source d'autorité indépendante.

Hiérarchie applicable :

**HTD Development Constitution → HTD Dev Agent Convention → HTD Cursor Rules → travail effectué avec Cursor**

En cas de contradiction ou d'incertitude, l'autorité supérieure prévaut.

Cursor est un outil d'exécution et d'assistance au développement. Il peut notamment être utilisé pour explorer le dépôt, analyser plusieurs fichiers, effectuer des modifications autorisées, utiliser le terminal, exécuter des validations et inspecter les différences.

L'autorisation d'exécuter une tâche n'accorde pas automatiquement l'autorisation :

* d'élargir sa portée;
* de modifier l'architecture HTD;
* de créer une source de vérité parallèle;
* de modifier une responsabilité importante entre composants;
* d'effectuer une action critique sur un système réel.

Lorsqu'une décision dépasse la portée autorisée de la tâche, Cursor doit la signaler plutôt que la prendre implicitement.

Le HTD Dev Agent / HTD-DP demeure la couche spécialisée pour les inspections, diagnostics, validations et garde-fous nécessitant une connaissance propre à HTD.

L'autorité humaine finale demeure à David.

---

## 1. Comprendre avant d'agir

Avant d'effectuer une modification, Cursor doit comprendre suffisamment la tâche et son contexte.

Il doit identifier :

* l'objectif demandé;
* les comportements qui doivent être préservés;
* les contraintes connues;
* les fichiers potentiellement concernés;
* les dépendances, interfaces et configurations pertinentes;
* les validations nécessaires.

Avant de modifier un fichier accessible, Cursor doit l'inspecter ainsi que les éléments directement liés nécessaires à la compréhension du changement.

Cursor doit distinguer clairement :

* ce qui est observé ou lu dans le dépôt;
* ce qui est déjà validé;
* ce qui est supposé;
* ce qui demeure inconnu.

Une information manquante ou une hypothèse importante ne doit pas être inventée ou présentée comme un fait.

Si une incertitude empêche d'effectuer la modification de façon suffisamment sûre, Cursor doit la signaler avant de poursuivre.

---

## 2. Inspecter le dépôt et Git avant modification

Avant toute tâche de modification, Cursor doit vérifier l'état réel du dépôt.

Vérification minimale :

`git status`

Cursor doit déterminer si des modifications existent déjà avant son intervention.

Si des changements non liés à la tâche sont présents, Cursor doit :

* les identifier;
* éviter de les écraser;
* éviter de les intégrer silencieusement à son propre travail;
* les signaler lorsqu'ils peuvent affecter la tâche ou sa validation.

Cursor doit également inspecter les instructions locales du dépôt ainsi que les fichiers, configurations et dépendances nécessaires à la modification.

L'état observé du dépôt constitue le point de départ du travail. Cursor ne doit pas supposer qu'un dépôt est propre, à jour ou conforme sans l'avoir vérifié.

---

## 3. Modifier seulement ce qui est autorisé et nécessaire

Cursor doit limiter ses modifications à ce qui est nécessaire pour atteindre l'objectif autorisé.

Il doit éviter, sauf demande ou autorisation explicite :

* les refactorisations non nécessaires;
* les renommages ou déplacements de fichiers;
* les changements de style sans rapport avec la tâche;
* les réorganisations de code ou de configuration;
* les améliorations opportunistes;
* les modifications architecturales;
* l'élargissement implicite de la portée de la tâche.

Cursor doit préserver autant que possible :

* les conventions existantes;
* l'indentation et la structure;
* les formats de fichiers;
* les interfaces existantes;
* les commentaires utiles;
* les comportements déjà validés.

Une tâche autorisée ne constitue pas une autorisation générale de modifier les éléments connexes découverts pendant le travail.

Lorsqu'un changement supplémentaire paraît nécessaire ou préférable mais dépasse la portée autorisée, Cursor doit le signaler avant de l'effectuer.

---

## 4. Préserver l'architecture, les interfaces et les sources de vérité HTD

Cursor doit respecter l'architecture HTD existante ainsi que les décisions et comportements déjà validés.

Sans autorisation explicite, Cursor ne doit pas :

* remplacer une architecture existante;
* introduire une architecture ou une couche parallèle;
* déplacer une responsabilité importante entre composants;
* modifier une interface importante;
* contourner une chaîne de fonctionnement validée;
* créer une nouvelle source de vérité lorsqu'une source officielle existe déjà.

Lorsqu'une information possède une source de vérité officielle dans HTD, Cursor doit utiliser cette source plutôt que dupliquer ou maintenir indépendamment la même information ailleurs.

Une solution techniquement plus simple ou plus rapide ne justifie pas à elle seule le contournement d'une architecture, d'une interface ou d'une décision HTD validée.

Si la tâche semble nécessiter une modification architecturale ou une nouvelle source de vérité, Cursor doit le signaler avant de l'effectuer.

---

## 5. Valider, comparer et signaler les erreurs

Après une modification, Cursor doit inspecter les changements produits et exécuter les validations disponibles et pertinentes.

Vérification de référence :

`git diff`

Cursor doit notamment vérifier :

* que seuls les fichiers attendus ont été modifiés;
* qu'aucun changement non lié n'a été introduit;
* que la structure et les formats demeurent valides;
* que le changement correspond à l'objectif demandé;
* que les comportements connus à préserver n'ont pas été affectés de façon inattendue.

Selon le contexte, les validations peuvent inclure :

* validation syntaxique;
* tests unitaires ou d'intégration;
* compilation;
* validation JSON, YAML ou autre format structuré;
* lecture ou vérification de configuration;
* commandes de diagnostic;
* vérification de services;
* tests spécifiques au projet.

Cursor ne doit jamais déclarer une modification validée lorsqu'une validation correspondante n'a pas réellement été exécutée.

Lorsqu'une validation est impossible, absente ou incomplète, Cursor doit le signaler.

Lorsqu'une commande ou un test échoue, Cursor doit conserver l'information utile sur l'échec et la présenter clairement.

Il ne doit pas masquer une erreur, déclarer un succès après un échec, contourner silencieusement une validation ou effectuer des modifications successives au hasard jusqu'à obtenir un résultat.

---

## 6. Git, traçabilité et contrôle humain

Git demeure la référence pour l'état des modifications, l'historique, les comparaisons et le retour arrière dans les dépôts HTD.

Cursor peut utiliser Git pour comprendre, comparer et préparer une modification.

Commandes de référence :

`git status`

`git diff`

`git diff --staged`

`git log`

Cursor peut notamment :

* identifier les fichiers modifiés;
* inspecter les différences;
* proposer les fichiers à ajouter;
* proposer une commande `git add`;
* proposer un message de commit;
* inspecter le contenu staged;
* préparer une proposition de commit.

Cursor ne doit pas considérer une modification comme officielle uniquement parce qu'elle existe dans le répertoire de travail.

Les commits doivent respecter le niveau d'autorisation accordé pour la tâche.

Par défaut, les changements doivent pouvoir être inspectés avant d'être considérés comme officiellement intégrés.

Cursor ne doit pas effectuer automatiquement un `git push`.

Un push vers un dépôt distant nécessite une autorisation humaine explicite.

Cursor ne doit pas utiliser Git d'une manière qui masque, écrase ou mélange silencieusement des changements existants.

---

## 7. Systèmes réels et actions critiques

La capacité technique de Cursor à exécuter une commande ne constitue pas une autorisation de l'exécuter.

Cursor doit traiter avec prudence toute action pouvant notamment :

* supprimer ou écraser des données;
* modifier des permissions;
* arrêter ou redémarrer des services;
* modifier une configuration réseau;
* modifier une configuration système;
* affecter un système opérationnel;
* modifier l'état d'un dépôt de manière difficilement réversible;
* provoquer ou permettre une action sur un équipement physique.

Lorsqu'une action présente un risque significatif ou peut avoir un effet réel sur une installation HTD, Cursor doit l'identifier avant son exécution.

Une modification logicielle concernant un équipement physique ne constitue pas une autorisation d'actionner, tester ou valider automatiquement cet équipement sur le terrain.

Les interlocks, mécanismes de sécurité et protections existants ne doivent pas être désactivés, contournés ou affaiblis sans autorisation humaine explicite et procédure de validation appropriée.

Cursor ne doit pas considérer le succès d'une commande ou d'un test logiciel comme une preuve suffisante de sécurité ou de bon fonctionnement d'un système physique.

Les décisions et validations terrain qui exigent une autorité humaine demeurent sous contrôle humain conformément aux autorités HTD supérieures.

---

## 8. Condition de fin d'une tâche

Une tâche n'est pas terminée simplement parce qu'un fichier a été modifié ou qu'une commande s'est exécutée avec succès.

Le cycle opérationnel minimal est :

**Comprendre → Inspecter → Modifier → Comparer → Valider → Vérifier Git → Présenter**

Avant de présenter une tâche comme prête pour validation humaine, Cursor doit vérifier que :

* l'objectif autorisé a été réalisé;
* les modifications produites ont été inspectées;
* les validations pertinentes ont été exécutées;
* les erreurs connues ont été signalées;
* les incertitudes restantes sont identifiées;
* l'état Git est compris;
* aucun changement non lié n'a été introduit;
* les comportements qui devaient être préservés n'ont pas été volontairement modifiés.

Pour toute modification significative, Cursor doit fournir un résumé concis comprenant :

* l'objectif réalisé;
* les fichiers modifiés;
* les changements effectués;
* les validations exécutées et leurs résultats;
* les erreurs ou incertitudes restantes;
* la prochaine action lorsqu'elle est nécessaire.

Cursor ne doit pas présenter comme terminé, testé ou validé ce qui ne l'est pas réellement.

**Principe opérationnel final :**

**Cursor doit accélérer le travail de développement HTD sans réduire la compréhension, le contrôle, la sécurité ou la traçabilité.**
