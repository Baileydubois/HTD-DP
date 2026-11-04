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

## HDR-0005 — Validation fonctionnelle Machine Builder V1 et DR

**Date :** 2026-10-30

**Statut :** Approuvée

### Décision

Machine Builder V1 est validé sur HTD Edge : création réelle de `lab_obs_stride` en intention `observe`, GET et PATCH, filtrage Observer, magasin YAML `0640`, sauvegarde DR réelle COMPLETE/SUCCESS du 30 octobre 2026 à 14:47:47 EDT, manifeste SHA-256 12/12, restauration isolée hors production.

Le texte de référence est `docs/HTD_MACHINE_BUILDER_V1.md` dans le dépôt HTD-EDGE, ID `htd_machine_builder_v1_functional_dr_validated`. Cette entrée enregistre l'approbation. Elle n'en recopie pas le détail.

Cette validation n'autorise pas :

- une restauration complète en production ;
- le contrôle physique ;
- l'installation PWA ;
- un nouveau cycle DR ;
- le contact PLC.

La prochaine priorité enregistrée est la reprise de l'acquisition Allen-Bradley réelle, lecture seule, cinq tags CompactLogix 1769-L16ER-BB1B, en conservant la chaîne déjà développée et validée hors ligne. Ce n'est pas une autorisation d'implémentation ni de communication industrielle. Une étape ultérieure distincte est requise.

HDR-0002 demeure. L'architecture produit et HDR-0004 ne sont pas modifiées.

### Justification

L'approbation humaine du 30 octobre 2026 ne doit pas rester seulement dans une conversation. Le journal conserve la décision et renvoie au document.

## HDR-0006 — Checkpoint réseau Edge Option B, trois NIC physiques

**Date :** 2026-10-31

**Statut :** Approuvée

**ID :** `htd_edge_network_option_b_three_physical_nics_validated_v1`

### Décision

Le réseau industriel Option B de HTD Edge est enregistré comme checkpoint Master. La configuration permanente suivante a été validée le 31 octobre 2026, RESULT=PASS à 19:15:24 EDT, retour arrière désarmé.

- CLIENT : `enp0s31f6` — `192.168.1.124/24`
- STRIDE : `enx9c69d340b5bf` — `192.168.50.1/24`
- PLC : `enx9c69d3be1405` — `192.168.123.250/24`
- MAC PLC : `9c:69:d3:be:14:05`
- CompactLogix raccordé en Ethernet direct, lien 100 Mb/s Full Duplex
- `systemd-networkd` : trois interfaces configurées
- Netplan PLC permanent : `/etc/netplan/60-htd-plc-enx9c69d3be1405.yaml`

Cette entrée enregistre l'état réseau validé. Pendant cette validation, aucun ping, aucune session CIP, aucune lecture de tags et aucune écriture PLC n'ont été effectués.

Cette validation n'autorise pas :

- un ping vers le CompactLogix ;
- une session CIP ou une ouverture TCP `192.168.123.24:44818` ;
- une lecture de tags ;
- une écriture PLC ;
- un changement de mode automate ;
- le déploiement d'un service PLC ;
- une modification Machine Builder, Observer ou Points.

Une autorisation humaine ultérieure, distincte de ce checkpoint, reste exigée pour le premier contact d'identité CIP.

HDR-0002 demeure. HDR-0005 n'est pas modifiée. L'architecture produit et HDR-0004 ne sont pas modifiées.

### Justification

La validation humaine du réseau Option B du 31 octobre 2026 ne doit pas rester seulement dans une conversation. Le journal conserve le checkpoint et ses limites.

## HDR-0007 — Checkpoint d'identification CIP réelle CompactLogix

**Date :** 2026-11-01

**Statut :** Approuvée

**ID :** `htd_ab_compactlogix_real_identity_validated_v1`

### Décision

L'identification CIP réelle du CompactLogix 1769-L16ER-BB1B est enregistrée comme checkpoint Master. Le deuxième essai, RESULT=PASS, a été effectué le 1er novembre 2026, horodatage `2026-11-02T01:57:36.761769Z`, une seule tentative, session fermée.

- Source : `192.168.123.250`, interface `enx9c69d3be1405`
- CompactLogix : `192.168.123.24:44818`
- Bibliothèque : `pycomm3==1.2.16`
- Identité confirmée : vendor `1`, product type `14`, product code `153`, révision `33.14`, série `60e1bf5b`
- Journal : `/home/hydrotech/htd-plc-sim-lab/essai-2/identity-observe/observation.json`
- SHA256 : `7c39444c476073a023af8af9fb5cd055ffc6beda6c75306ea8c78f49edc0baf5`
- Premier essai `REFUSEE` / `identite_ambigue` conservé, SHA256 `dce22ac36b865ec17e1cf2a00a1d4e9c93efb176c9823d316bb8c854fbf79494`

Cette entrée enregistre l'identité observée et comparée. Elle n'autorise pas :

- une lecture réelle des cinq tags ;
- une écriture PLC ;
- un changement de mode automate ;
- une publication HTD Points ;
- un service d'acquisition régulier ;
- un contact CIP supplémentaire.

Une autorisation humaine ultérieure, distincte de ce checkpoint, reste exigée pour la première lecture réelle des cinq tags.

HDR-0002 demeure. HDR-0005 n'est pas modifiée. HDR-0006 n'est pas modifiée. L'architecture produit et HDR-0004 ne sont pas modifiées.

### Justification

La validation humaine de l'identité CIP du 1er novembre 2026 ne doit pas rester seulement dans une conversation. Le journal conserve le checkpoint, ses preuves et ses limites.

## HDR-0008 — Checkpoint de première lecture réelle de cinq tags CompactLogix

**Date :** 2026-11-01

**Statut :** Approuvée

**ID :** `htd_ab_compactlogix_five_tags_real_read_validated_v1`

### Décision

La première acquisition ponctuelle réelle des cinq tags du CompactLogix 1769-L16ER-BB1B, programme `HTD_PLC_SIM_V1`, est enregistrée comme checkpoint Master. L'essai, RESULT=PASS, a été effectué le 1er novembre 2026 à 21:35 HNE, horodatage d'acquisition `2026-11-02T02:35:44Z`, une seule session, une seule tentative, fermeture confirmée.

- Source : `192.168.123.250`, interface `enx9c69d3be1405`
- CompactLogix : `192.168.123.24:44818`
- Identité CIP conforme : vendor `1`, product type `14`, product code `153`, révision `33.14`, série `60e1bf5b`
- `HTD_Pression` REAL = `79.0`, quality `good`
- `HTD_Temperature` REAL = `44.5`, quality `good`
- `HTD_Debit` REAL = `28.0`, quality `good`
- `HTD_Pompe_Run` BOOL = `true`, quality `good`
- `HTD_Defaut` BOOL = `true`, quality `good`
- Journal : `/home/hydrotech/htd-plc-sim-lab/tag-observe/observation.json`
- SHA256 : `46d9640e366f16815b9114a062631fe0e445cb77fc86cd088bae6df56f2e8029`

Ces valeurs proviennent de tags internes du programme `HTD_PLC_SIM_V1`. Elles ne prouvent pas un capteur ou un actionneur physique.

Cette entrée enregistre la lecture ponctuelle observée. Elle n'autorise pas :

- une écriture PLC ;
- un changement de mode automate ;
- une commande physique ;
- un service d'acquisition régulier ;
- une publication HTD Points ou Observer ;
- un contact CIP supplémentaire.

Une autorisation humaine ultérieure, distincte de ce checkpoint, reste exigée pour toute nouvelle communication industrielle.

HDR-0002 demeure. HDR-0005 n'est pas modifiée. HDR-0006 n'est pas modifiée. HDR-0007 n'est pas modifiée. L'architecture produit et HDR-0004 ne sont pas modifiées.

### Justification

La validation humaine de la première lecture réelle des cinq tags du 1er novembre 2026 ne doit pas rester seulement dans une conversation. Le journal conserve le checkpoint, ses preuves et ses limites.

## HDR-0009 — Checkpoint d'acquisition Allen-Bradley réelle bornée CompactLogix

**Date :** 2026-11-02

**Statut :** Approuvée

**ID :** `htd_ab_compactlogix_bounded_real_acquisition_validated_v1`

### Décision

L'acquisition Allen-Bradley réelle bornée du CompactLogix 1769-L16ER-BB1B, programme `HTD_PLC_SIM_V1`, est enregistrée comme checkpoint Master. Le deuxième essai borné, RESULT=PASS, a été effectué le 2 novembre 2026 à 21:37 HNE, horodatage d'acquisition `2026-11-03T02:37:38Z`, dans le répertoire distinct `bounded-real-2`.

- Source : `192.168.123.250`, interface `enx9c69d3be1405`
- CompactLogix : `192.168.123.24:44818`
- Identité CIP conforme : vendor `1`, product type `14`, product code `153`, révision `33.14`, série `60e1bf5b`
- Cycles tentés : `5` ; cycles réussis : `5`
- Durée : `4,049` secondes ; arrêt : `limite_cycles`
- Sessions fermées ; permis consommé ; grant fermé ; variables d'autorisation désarmées
- `HTD_Pression` REAL = `73.0`, quality `good`
- `HTD_Temperature` REAL = `21.5`, quality `good`
- `HTD_Debit` REAL = `16.0`, quality `good`
- `HTD_Pompe_Run` BOOL = `true`, quality `good`
- `HTD_Defaut` BOOL = `false`, quality `good`
- Journal : `/home/hydrotech/htd-plc-sim-lab/bounded-real-2/`
- Rapport SHA256 : `67267e97e4df1d42b5570470d8e799a7241fbbf1ce3876aac626e4753a89cfbb`
- Premier essai borné `bounded-real-1` (FAIL, cinq `identite_ambigue`) conservé intégralement

Ces valeurs proviennent de tags internes du programme `HTD_PLC_SIM_V1`. Elles ne prouvent pas un capteur ou un actionneur physique.

Cette entrée enregistre une acquisition bornée validée, limitée à cinq cycles ou trente secondes. Elle n'autorise pas :

- un service d'acquisition permanent ;
- une preuve de reconnexion après panne réelle ;
- une écriture PLC ;
- un changement de mode automate ;
- une commande physique ;
- une publication HTD Points ou Observer de production ;
- un contact CIP supplémentaire.

Une autorisation humaine ultérieure, distincte de ce checkpoint, reste exigée pour toute nouvelle communication industrielle.

HDR-0002 demeure. HDR-0005 n'est pas modifiée. HDR-0006 n'est pas modifiée. HDR-0007 n'est pas modifiée. HDR-0008 n'est pas modifiée. L'architecture produit et HDR-0004 ne sont pas modifiées.

### Justification

La validation humaine du deuxième essai réel borné du 2 novembre 2026 ne doit pas rester seulement dans une conversation. Le journal conserve le checkpoint, ses preuves et ses limites.

## HDR-0010 — Checkpoint d'intégration catalogue 13 Points et raccordement resolver Allen-Bradley

**Date :** 2026-11-03

**Statut :** Approuvée

**ID :** `htd_edge_ab_points_production_catalog_resolver_integration_v1`

### Décision

L'intégration en production du catalogue HTD Points à 13 Points et le raccordement du resolver actif au chemin PLC Allen-Bradley dédié sont enregistrés comme checkpoint Master. La validation finale hors CIP a été confirmée le 3 novembre 2026 (HNE), avec `FINAL_VALIDATION_PASS` et journal d'installation `DROPIN_INSTALL_PASS` sous `/home/hydrotech/htd-plc-sim-lab/points13-dropin-install-20261103T232619Z/`.

Faits validés :

- Catalogue actif `/opt/htd/core/config/points.yaml` : 13 Points ; SHA256 `ecd3ed6e7ec227adcd16be51077018cf6f81e72df30f12c4db9606a1e943613d`
- Huit Points STRIDE préservés, qualité `good` via `/api/points` ; `motor_current` source `ai3`
- Cinq Points Allen-Bradley configurés (`ab:bench_l16/HTD_*`) : qualité `unavailable`, provenance `state_absent` ; fichier `/home/hydrotech/htd-plc-sim-lab/ab-acquire/plc_state.json` absent
- Service `htd-point-resolver` : `active` ; environnement chargé `HTD_PLC_STATE_PATH=/home/hydrotech/htd-plc-sim-lab/ab-acquire/plc_state.json` et `HTD_PLC_STALE_SEC=5`
- Drop-in `/etc/systemd/system/htd-point-resolver.service.d/ab-plc-state.conf` : contenu limité à ces deux variables ; SHA256 `7c5b211df975529f14805578e802dbfd8098f8e65ffa64d4a41608a58da51364`
- Service `htd-ab-acquire` : `disabled` / `inactive` ; aucune acquisition CIP continue validée dans ce checkpoint
- Sauvegarde catalogue 8 Points et artefacts : `/home/hydrotech/htd-plc-sim-lab/backups/points13-deploy-20261103T050040Z/` (SHA catalogue avant `189ea592873be1a02538b1cf55a8579daaa3966e50a7c8f19ffee87a943a9aad`)
- `/api/points` : `status=ok`, 13 Points
- Services de contrôle physique observés actifs sans redémarrage lors de la validation finale : `htd-runtime`, `htd-runtime-bridge`, `htd-do-apply`, `htd-action`, `htd-io`
- `/var/www/html` : mtime inchangé lors des contrôles de déploiement ; aucun changement Observer enregistré dans ce checkpoint
- Aucune écriture PLC ni commande physique dans ce checkpoint

Cette entrée n'autorise pas :

- le démarrage ou l'activation de `htd-ab-acquire` ;
- une acquisition CIP régulière ou continue ;
- une écriture PLC ou une commande physique ;
- un changement réseau, Netplan, plafond F_FIT V1.3 ou SessionChannel ;
- une modification Machine Builder ;
- une modification d'Observer.

Une autorisation humaine ultérieure, distincte de ce checkpoint, reste exigée pour toute acquisition Allen-Bradley réelle régulière.

HDR-0002 demeure. HDR-0005 n'est pas modifiée. HDR-0006 n'est pas modifiée. HDR-0007 n'est pas modifiée. HDR-0008 n'est pas modifiée. HDR-0009 n'est pas modifiée. L'architecture produit et HDR-0004 ne sont pas modifiées.

### Justification

La validation humaine du raccordement catalogue 13 Points et resolver du 3 novembre 2026 ne doit pas rester seulement dans une conversation. Le journal conserve le checkpoint, ses preuves et ses limites.

## HDR-0011 — Checkpoint d'essai supervisé réel bout en bout vers HTD Points

**Date :** 2026-11-03

**Statut :** Approuvée

**ID :** `htd_ab_supervised_real_end_to_end_points_validated_v1`

### Décision

Le premier essai supervisé réel Allen-Bradley de bout en bout, avec publication vers le chemin HTD Points déjà raccordé (HDR-0010), est enregistré comme checkpoint Master. L'essai unique `supervised-real-1`, RESULT=PASS, a été effectué le 3 novembre 2026 (HNE), horodatages UTC `2026-11-04T02:12:20Z` à `2026-11-04T02:12:24Z`.

Faits validés :

- Runtime : `run_supervised_real` ; pilote réutilisé `HtdSimLogixTags` (HDR-0009)
- Source : `192.168.123.250`, interface `enx9c69d3be1405`
- CompactLogix : `192.168.123.24:44818` ; programme `HTD_PLC_SIM_V1`
- Identité CIP conforme : vendor `1`, product type `14`, product code `153`, révision `33.14`, série `60e1bf5b` ; `identity_stop=None`
- Cycles tentés : `5` ; cycles réussis : `5` ; durée : `4,06` secondes ; arrêt : `limite_cycles`
- Publication atomique sous `/home/hydrotech/htd-plc-sim-lab/ab-acquire/plc_state.json`
- Dernières valeurs publiées : `HTD_Pression` REAL=`57.0`, `HTD_Temperature` REAL=`23.5`, `HTD_Debit` REAL=`24.0`, `HTD_Pompe_Run` BOOL=`false`, `HTD_Defaut` BOOL=`false` ; qualité fichier `good` ; ts `2026-11-04T02:12:24Z`
- `/api/points` pendant la fraîcheur : cinq Points AB (`htd_pression`, `htd_temperature`, `htd_debit`, `htd_pompe_run`, `htd_defaut`) observés `good` avec valeurs
- Après expiration `HTD_PLC_STALE_SEC=5` : les cinq Points AB observés `unavailable` (valeurs null) ; aucune preuve `reason=stale` n'est affirmée ici
- Huit Points STRIDE non perturbés ; `motor_current` source `ai3`, qualité `good`
- Permis oneshot consommé ; grant fermé ; variables `HTD_AB_SERVICE`, `HTD_AB_SERVICE_ARM`, `HTD_AB_SUPERVISED`, `HTD_AB_ENABLE_REAL` désarmées
- Session CIP fermée ; aucun processus d'acquisition restant
- Service `htd-ab-acquire` : `disabled` / `inactive` ; `ExecStart=/bin/false`
- Journal : `/home/hydrotech/htd-plc-sim-lab/supervised-real-1/essai-report.json`
- Rapport SHA256 : `545e207dc8b8993452ee963d7469eb965ed10552c3a431a30c726c8ed191a287`
- SHA256 runtime `ab_acquire_supervised.py` : `9311b9f1c56f03fa7cfe7f25bfc1bd00177d3ee268af172d007b3991e5c3c7ad`
- SHA256 pilote `ab_htd_sim_tag_driver.py` : `d6df237c2a71f78e80cb36bd1c82345937ef59f85c9b12f7c5ba2d38cc639634`

Ces valeurs proviennent de tags internes du programme `HTD_PLC_SIM_V1` sur matériel CompactLogix réel. Elles ne prouvent pas un capteur ou un actionneur physique.

Cette entrée enregistre un essai unique borné (cinq cycles ou trente secondes). Elle n'autorise pas :

- un fonctionnement continu prolongé ;
- un service d'acquisition permanent ni l'activation de `htd-ab-acquire` ;
- une écriture PLC ;
- un changement de mode automate ;
- une commande physique ;
- un changement réseau, plafond F_FIT V1.3, SessionChannel ou Observer ;
- un contact CIP supplémentaire.

Une autorisation humaine ultérieure, distincte de ce checkpoint, reste exigée pour toute nouvelle communication industrielle.

HDR-0002 demeure. HDR-0005 n'est pas modifiée. HDR-0006 n'est pas modifiée. HDR-0007 n'est pas modifiée. HDR-0008 n'est pas modifiée. HDR-0009 n'est pas modifiée. HDR-0010 n'est pas modifiée. L'architecture produit et HDR-0004 ne sont pas modifiées.

### Justification

La validation humaine du premier essai supervisé réel bout en bout vers HTD Points du 3 novembre 2026 ne doit pas rester seulement dans une conversation. Le journal conserve le checkpoint, ses preuves et ses limites.
