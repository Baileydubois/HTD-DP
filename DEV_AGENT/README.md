# HTD Dev Agent V1

## Statut

**Phase actuelle : développement minimal orienté HTD #0**

**Première cible opérationnelle : HTD Edge**

Le HTD Dev Agent V1 est un outil de développement local destiné à accélérer le travail sur les projets de l'écosystème Hydro Tech Dubois.

Sa priorité immédiate est de devenir suffisamment fiable et utile pour participer au développement de :

**HTD #0 — Érablière 2027**

Le Dev Agent n'est pas développé comme un produit autonome.

Il doit devenir un multiplicateur de vitesse pour le développement de HTD.

---

## Objectif minimal

La première version utile du Dev Agent doit être capable d'assister un cycle de développement de la forme :

**Comprendre → Modifier → Comparer → Valider → Vérifier → Préparer**

Concrètement, l'agent doit pouvoir :

1. comprendre la structure d'un dépôt HTD;
2. lire les fichiers nécessaires avant de proposer une modification;
3. identifier les fichiers réellement concernés par une tâche;
4. effectuer des modifications précises et limitées;
5. conserver les formats et indentations existants;
6. présenter les différences produites;
7. exécuter les validations ou tests appropriés;
8. vérifier l'état Git du dépôt;
9. préparer proprement les changements pour validation humaine;
10. documenter les modifications importantes lorsque nécessaire.

---

## Première cible : HTD Edge

La première utilisation réelle du Dev Agent sera le développement de HTD Edge.

Le Dev Agent doit travailler à partir de l'état réel et de l'architecture existante du projet.

Il ne doit pas reconstruire ou remplacer une architecture existante simplement parce qu'une autre approche semble possible.

Avant toute modification importante, il doit comprendre les fichiers, services, dépendances et comportements concernés.

Les domaines de travail pourront notamment comprendre :

- services;
- configuration;
- API;
- runtime;
- logique;
- points universels;
- interface;
- tests;
- documentation;
- déploiement.

---

## Règles fondamentales

### 1. Comprendre avant de modifier

L'agent doit lire et comprendre suffisamment le contexte concerné avant de modifier un fichier.

Il ne doit pas supposer l'existence d'une architecture, d'un fichier, d'un service ou d'un comportement sans l'avoir vérifié lorsque cette information est accessible.

### 2. Modifier le minimum nécessaire

Une tâche doit produire les changements les plus limités permettant d'atteindre l'objectif.

Les refactorisations, réorganisations ou améliorations non demandées doivent être évitées.

### 3. Préserver l'existant

Le Dev Agent doit respecter :

- l'architecture existante;
- les formats;
- les indentations;
- les conventions;
- les interfaces;
- les comportements déjà validés.

Une modification structurante nécessite une instruction ou une validation humaine explicite.

### 4. Montrer ce qui change

Les changements doivent pouvoir être inspectés avant d'être considérés comme terminés.

Le Dev Agent doit utiliser les mécanismes de comparaison appropriés, notamment `git diff` lorsque le projet est sous Git.

### 5. Valider après modification

Une modification ne doit pas être considérée comme correcte uniquement parce qu'elle a été écrite.

Lorsque des tests, validations syntaxiques, commandes de diagnostic ou autres vérifications pertinentes existent, ils doivent être utilisés.

### 6. Git demeure contrôlé

Le Dev Agent peut utiliser Git pour inspecter et préparer le travail.

Il doit notamment pouvoir utiliser :

- `git status`;
- `git diff`;
- `git diff --staged`;
- les commandes de consultation nécessaires.

Le Dev Agent ne doit pas effectuer automatiquement un `git push`.

Les commits officiels doivent demeurer sous validation humaine.

### 7. Signaler les incertitudes

Lorsqu'une information nécessaire est inconnue ou qu'une modification présente un risque significatif, l'agent doit le signaler plutôt que transformer une supposition en fait.

---

## Limite de développement actuelle

Toute nouvelle capacité envisagée doit répondre à la question :

**« Est-ce que cette fonction nous fera gagner suffisamment de temps pendant le développement de HTD #0 pour justifier le temps nécessaire à la développer maintenant? »**

Si oui :

**[DEV AGENT — NÉCESSAIRE MAINTENANT]**

Si non :

**[DEV AGENT — APRÈS HTD #0]**

---

## Après HTD #0

Les capacités suivantes ne font pas partie de la cible minimale actuelle sauf si un besoin réel les rend nécessaires :

- autonomie avancée;
- orchestration complexe;
- systèmes multi-agents;
- interface utilisateur perfectionnée;
- automatisation généralisée;
- intelligence supplémentaire non nécessaire;
- fonctions destinées à commercialiser le Dev Agent;
- fonctions spécifiques à HTD Remote ou HTD Core qui ne sont pas encore nécessaires.

Ces capacités ne sont pas abandonnées.

Elles sont reportées.

---

## Condition de passage en utilisation réelle

Le développement général du Dev Agent doit être mis sur pause dès qu'il est capable de soutenir efficacement une première tâche réelle sur HTD Edge selon le cycle :

**Comprendre les fichiers concernés → appliquer une modification précise → présenter le diff → exécuter les validations → vérifier Git → présenter le résultat pour validation humaine.**

À partir de ce seuil, les améliorations du Dev Agent doivent principalement être guidées par les besoins réellement rencontrés pendant le développement de HTD.

---

## Principe directeur

**Ne pas développer l'outil pour développer l'outil.**

**Le HTD Dev Agent doit devenir un multiplicateur de vitesse pour HTD.**