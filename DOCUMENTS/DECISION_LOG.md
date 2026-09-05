\# HTD Decision Log



\## HDR-0001 — Adoption de HTD Development Platform



\*\*Date :\*\* 2026-08-07  

\*\*Statut :\*\* Approuvée



\### Décision



HTD Development Platform (HTD-DP) est adoptée comme plateforme officielle définissant les méthodes, les règles, les processus, les outils et les connaissances utilisés pour développer durablement l'écosystème HTD.



Le document `MASTER\_DEVELOPMENT\_PLATFORM.md` constitue la Constitution officielle de HTD-DP.



La table des matières validée du Master est adoptée comme architecture de référence initiale.



\### Justification



Le développement de HTD devient suffisamment important pour nécessiter un environnement structuré, traçable et indépendant des outils particuliers.



HTD-DP doit permettre :



\- d'améliorer continuellement la façon de développer ;

\- de protéger les composants validés ;

\- de réduire la dette technique ;

\- de favoriser la réutilisation ;

\- de conserver et transmettre les connaissances ;

\- de permettre la collaboration entre développeurs humains et agents IA.



\### Principe directeur



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
