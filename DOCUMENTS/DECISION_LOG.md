# HTD Decision Log

## HDR-0001 — Adoption de HTD Development Platform

**Date :** 2026-08-07

**Statut :** Approuvée

### Décision

HTD Development Platform (HTD-DP) est adoptée comme plateforme officielle définissant les méthodes, les règles, les processus, les outils et les connaissances utilisés pour développer durablement l'écosystème HTD.

Le document `MASTER/HTD_DEVELOPMENT_CONSTITUTION.md` constitue la Constitution officielle de HTD-DP.

La table des matières validée du Master est adoptée comme architecture de référence initiale.

**Note de référence — 2026-10-25 :** la formulation d'origine citait `MASTER_DEVELOPMENT_PLATFORM.md`. Ce fichier n'a pas été trouvé dans le dépôt. La référence est corrigée vers le document constitutionnel réel. Le sens de la décision du 2026-08-07 n'est pas modifié.

### Justification

Le développement de HTD devient suffisamment important pour nécessiter un environnement structuré, traçable et indépendant des outils particuliers.

HTD-DP doit permettre :

- d'améliorer continuellement la façon de développer ;
- de protéger les composants validés ;
- de réduire la dette technique ;
- de favoriser la réutilisation ;
- de conserver et transmettre les connaissances ;
- de permettre la collaboration entre développeurs humains et agents IA.

### Principe directeur

Les outils évoluent. Les principes de développement HTD demeurent.

## HDR-0002 — Recentrage temporaire du HTD Dev Agent V1 pour HTD #0

**Statut :** Adopté  
**Priorité :** HTD #0 — Érablière 2027  
**Date :** 2026-09-04

### Contexte

Le développement du HTD Dev Agent V1 avait été amorcé comme composante de HTD Development Platform.

La priorité immédiate de Hydro Tech Dubois est maintenant la réalisation de HTD #0 — Érablière 2027, avec comme objectif de disposer d'un système opérationnel pour la saison acéricole 2027.

Le développement du Dev Agent ne doit donc pas devenir un projet autonome qui retarde la réalisation de HTD Edge, HTD Remote ou HTD Core.

### Décision

Le développement du HTD Dev Agent V1 est temporairement recentré sur la création d'un agent minimal, fiable et immédiatement utile pour accélérer le développement de HTD Edge.

Le Dev Agent doit être développé uniquement jusqu'au seuil où il procure un gain de temps réel dans le travail quotidien sur HTD #0.

Dès que ce seuil est atteint, son développement général est mis sur pause et l'agent est utilisé directement pour poursuivre HTD Edge.

Les nouvelles capacités seront ensuite ajoutées uniquement lorsqu'un besoin réel rencontré pendant le développement de HTD les justifie.

### Critère de décision

Toute nouvelle fonction envisagée pour le Dev Agent doit répondre à la question suivante :

> « Est-ce que cette fonction nous fera gagner suffisamment de temps pendant le développement de HTD #0 pour justifier le temps nécessaire à la développer maintenant? »

Si oui :

**[DEV AGENT — NÉCESSAIRE MAINTENANT]**

Si non :

**[DEV AGENT — APRÈS HTD #0]**

### Capacités nécessaires maintenant

Le Dev Agent minimal doit prioritairement permettre :

- la lecture et la compréhension des dépôts HTD;
- la navigation dans les fichiers et structures existantes;
- la compréhension de l'architecture avant modification;
- la modification contrôlée des fichiers;
- la conservation exacte des indentations, formats et structures;
- la génération de changements précis et limités;
- la consultation des différences avant et après modification;
- la vérification des erreurs évidentes;
- l'exécution des tests et commandes de validation appropriés;
- l'utilisation contrôlée de Git;
- la vérification de `git status`;
- la consultation des `git diff`;
- la préparation propre des commits;
- la documentation des modifications importantes.

### Première cible opérationnelle

La première cible réelle du HTD Dev Agent V1 est :

**HTD Edge**

Le Dev Agent doit travailler à partir de l'architecture et de l'état existants du projet.

Il ne doit pas reconstruire, remplacer ou modifier l'architecture HTD sans instruction explicite.

Il doit d'abord comprendre et respecter ce qui existe.

Les domaines de travail prioritaires comprennent notamment :

- services;
- configuration;
- API;
- logique;
- runtime;
- points universels;
- interface;
- tests;
- documentation;
- déploiement.

### Éléments reportés

Les fonctions ne procurant pas un gain direct suffisant pour HTD #0 sont reportées.

Cela comprend notamment, lorsque non nécessaires immédiatement :

- autonomie avancée;
- orchestration complexe;
- automatisation généralisée;
- fonctions expérimentales;
- intelligence supplémentaire non requise;
- interfaces perfectionnées;
- fonctions destinées à une commercialisation future du Dev Agent;
- développements spécifiques à HTD Remote ou HTD Core avant l'apparition d'un besoin réel.

Ces éléments ne sont pas abandonnés.

Ils sont classés :

**[APRÈS HTD #0]**

### Condition d'arrêt du développement initial

Le développement initial du HTD Dev Agent V1 doit s'arrêter temporairement dès qu'il est capable de soutenir efficacement un cycle de travail de la forme :

**Comprendre les fichiers concernés → proposer ou appliquer une modification précise → présenter le diff → exécuter les validations → vérifier Git → préparer le changement pour validation humaine.**

À partir de ce moment, le Dev Agent devient un outil de production pour HTD #0.

### Principe directeur

**« Ne pas développer l'outil pour développer l'outil. Le Dev Agent doit devenir un multiplicateur de vitesse pour HTD. »**


## HDR-0003 — Adoption de la vision HTD Edge 1.0.0

**Date :** 2026-10-21

**Statut :** Approuvée

### Décision

La vision produit de HTD Edge, version 1.0.0, est adoptée. Son texte est `docs/HTD_ARCHITECTURE_VISION.md` dans le dépôt HTD-EDGE.

Elle reste subordonnée à `docs/HTD_EDGE_ARCHITECTURE.md`, puis à `MASTER/HTD_DEVELOPMENT_CONSTITUTION.md`. En cas de contradiction, l'autorité supérieure prévaut.

Le commit `02fcec10cdcda67562ce244b069f6ceed8797544` en est la trace Git. Cette entrée enregistre l'adoption. Elle n'autorise aucune modification de code, de service, d'API, de runtime ou d'équipement.

### Justification

L'approbation humaine du 2026-10-21 ne doit pas rester seulement dans une conversation. Le journal conserve la décision et renvoie au document. Il n'en recopie pas le texte.

## HDR-0004 — Orientations produit pour le développement futur

**Date :** 2026-10-25

**Statut :** Approuvée comme orientation. Cette entrée n'est pas une autorisation d'implémentation.

### Décision

Les orientations suivantes sont approuvées pour le développement futur de HTD. Elles ne constituent ni une spécification réalisée, ni une autorisation d'implémenter, de déployer ou de modifier un équipement.

- HTD est une plateforme industrielle universelle.
- La priorité commerciale va aux solutions spécialisées de performance industrielle. Cette priorité ne rend aucun module spécialisé obligatoire pour utiliser HTD Edge.
- HTD Assistant conversationnel textuel.
- Questions prédéfinies et favoris.
- HTD Adaptive Intelligence.
- Apprentissage du fonctionnement normal des machines.
- Détection des dérives progressives.
- Remote I/O multimarque.
- HTD Control modulaire et sécurisé.

Les noms sont rappelés dans `docs/HTD_ARCHITECTURE_VISION.md` de HTD-EDGE. Cette liste n'est pas une seconde spécification.

HDR-0002 demeure en vigueur. Remote I/O, HTD Core et HTD Control ne sont pas à développer tant qu'un besoin réel ne le justifie pas et qu'ils retarderaient HTD #0. Toute évolution des restrictions de HDR-0002 exige une décision explicite. Les travaux autorisés depuis l'adoption de HDR-0002 ne sont pas annulés.

Le chemin de sorties déjà présent dans HTD Edge n'est pas redéfini comme HTD Control. HTD Adaptive Intelligence n'est pas fusionné avec Optimizer.

### Justification

Ces orientations sont conservées comme direction de développement. Leur présence dans le journal ne prouve pas qu'un fichier du dépôt les réalise.
