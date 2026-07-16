# Fiche orale express : inférence causale

## Pitch de 60 à 90 secondes

Nous étudions l'effet moyen d'une session ayant lieu durant le week-end, plutôt qu'en semaine, sur la probabilité qu'elle se termine par un achat. `Weekend` est l'exposition et `Revenue` est un indicateur binaire d'achat, pas un montant de revenu. Pour éviter un grave problème de recouvrement lié aux jours commerciaux spéciaux, l'analyse principale porte sur les 11 079 sessions pour lesquelles `SpecialDay = 0`.

Le DAG de travail conduit à ajuster sur le mois, le type de visiteur, la région, le système d'exploitation, le navigateur et le type de trafic. Les variables de navigation et `PageValues` sont exclues parce qu'elles peuvent être postérieures à l'exposition, médiatrices, colliders ou sources de fuite d'information. Nous estimons l'effet par standardisation, IPW et surtout AIPW, avec une validation croisée en cinq plis.

L'estimation AIPW principale correspond à une hausse de 1,506 point de pourcentage, avec un intervalle de confiance à 95 % de −0,176 à 3,188 points. L'équilibre observé après pondération est bon, mais l'intervalle contient zéro et le résultat varie lorsque `TrafficType` est exclu. La conclusion correcte est donc celle d'une association ajustée positive, compatible avec un faible effet causal sous des hypothèses fortes, mais qui ne constitue pas une preuve d'effet causal.

## Chiffres à connaître

- Jeu complet : 12 330 sessions, 1 908 achats, soit 15,47 %.
- Population principale : 11 079 sessions avec `SpecialDay = 0`.
- Répartition principale : 8 371 sessions en semaine et 2 708 le week-end.
- Différence brute : +2,026 points ; IC à 95 % [0,378 ; 3,674].
- Standardisation : +1,384 point ; IC bootstrap [−0,317 ; 2,984].
- IPW de Hájek : +1,444 point ; IC [−0,256 ; 3,143].
- AIPW principale : +1,506 point ; IC [−0,176 ; 3,188].
- Moyennes potentielles AIPW : 17,67 % le week-end contre 16,16 % en semaine.
- SMD maximal : 0,268 avant pondération et 0,040 après ; aucune indicatrice au-dessus de 0,10 après pondération.
- Sans `TrafficType` : +2,233 points ; IC [0,535 ; 3,931].
- E-value du point : 1,412 ; E-value de la borne la plus proche du nul : 1,000.

## Concepts à expliquer simplement

**Estimand.** Quantité causale précise recherchée : ici, la différence moyenne de probabilité d'achat entre le week-end et la semaine parmi les sessions hors jours spéciaux.

**DAG.** Représentation des hypothèses causales formulées avant l'estimation. Il sert surtout à choisir les variables d'ajustement et à éviter les ajustements nuisibles.

**Score de propension.** Probabilité estimée qu'une session ait lieu le week-end, compte tenu des covariables. Il sert à vérifier le recouvrement et à pondérer les observations.

**Positivité.** Pour chaque profil analysé, il doit exister une probabilité strictement positive d'observer chacune des deux expositions. Les valeurs non nulles de `SpecialDay` violaient presque structurellement cette condition.

**IPW.** Cette méthode repondère les sessions afin de rendre les groupes du week-end et de la semaine plus comparables sur les covariables observées.

**AIPW.** Cette méthode combine un modèle du traitement et un modèle du résultat. L'estimateur est dit doublement robuste si au moins un des deux modèles est correctement spécifié, mais il ne corrige pas la présence d'un confondeur non mesuré.

**Cross-fitting.** Les prédictions de nuisance d'une observation sont produites par des modèles entraînés sans cette observation, ce qui limite le surajustement.

**FCI et PAG.** FCI recherche des indépendances conditionnelles tout en autorisant des confondeurs latents. Le PAG obtenu représente une classe de graphes compatibles, et non un DAG causal certain.

**Intervalle de confiance.** Ensemble de valeurs compatibles avec les données et la méthode. Ici, il contient zéro : on ne peut pas exclure l'absence d'effet.

## Questions pièges et réponses

### Pourquoi appeler `Weekend` un traitement ?

Nous parlons plus exactement d'une exposition calendaire. L'intervention hypothétique consiste à déplacer une session déjà existante vers le week-end, dans le même mois et à profil comparable. Il ne s'agit pas d'une variable randomisée.

### Pourquoi restreindre l'analyse à `SpecialDay = 0` ?

Les autres valeurs de `SpecialDay` sont presque exclusivement observées dans un seul des deux groupes, semaine ou week-end. Ajuster directement sur cette variable aurait forcé une extrapolation sans support commun. La restriction rend la positivité plus crédible, au prix d'une population cible plus étroite.

### Pourquoi ne pas utiliser les variables de navigation ?

Elles sont mesurées pendant la session et peuvent être causées par le week-end. Les ajuster pourrait bloquer une partie de l'effet total ou ouvrir un chemin par collider. De plus, `PageValues` est liée à la valeur transactionnelle et présente un risque de fuite d'information.

### Pourquoi ajuster sur `TrafficType` ?

Dans le DAG principal, le canal d'acquisition est considéré comme défini avant l'exposition et susceptible d'influencer à la fois le moment de la visite et l'achat. Son ordre temporel reste ambigu ; c'est pourquoi son exclusion constitue une analyse de sensibilité substantielle, et non un simple choix technique.

### L'absence d'arête `Weekend`-`Revenue` dans FCI prouve-t-elle un effet nul ?

Non. Elle indique seulement qu'une indépendance conditionnelle compatible avec l'absence d'adjacence a été trouvée dans une version simplifiée et discrétisée des données. Elle ne prouve ni un ATE nul ni l'absence d'effet indirect.

### Pourquoi choisir AIPW comme résultat principal ?

Parce que cet estimateur combine le modèle de propension et le modèle du résultat, exploite le cross-fitting et fournit une estimation moins dépendante d'un seul modèle. Sa double robustesse ne remplace toutefois pas les hypothèses causales.

### Le résultat est-il statistiquement significatif ?

Non pour l'analyse principale : l'IC AIPW [−0,176 ; 3,188] contient zéro. Certaines analyses de sensibilité ont un IC positif, mais elles ne remplacent pas l'analyse prédéfinie et montrent plutôt la dépendance des résultats aux choix de modélisation.

### Peut-on recommander de concentrer les campagnes le week-end ?

Pas sur la base de cette seule analyse. Le résultat est faible, incertain et potentiellement confondu par les promotions, les prix, les produits et l'intention d'achat non observés. Une expérience randomisée ou des données temporelles plus riches seraient nécessaires.

### À quelle population le résultat s'applique-t-il ?

Aux sessions déjà existantes, hors proximité des jours commerciaux spéciaux, dans le contexte du site et de l'année observés. Il ne mesure ni l'effet sur le nombre de visites ni le chiffre d'affaires total.

### Les doublons changent-ils la conclusion ?

Non. Après suppression des 125 lignes exactement dupliquées, l'AIPW vaut +1,199 point avec un IC [−0,484 ; 2,882], ce qui conduit à la même conclusion prudente.

### La forêt aléatoire donne un IC positif ; pourquoi ne pas conclure ?

Cette analyse change les modèles de nuisance et donne +1,736 point [0,123 ; 3,348]. Une analyse de sensibilité positive ne supprime ni la variabilité entre les spécifications, ni les confondeurs non mesurés, ni le fait que l'intervalle de l'analyse principale contient zéro.

### Que signifie l'E-value de 1,412 ?

Pour ramener le point estimé vers le nul, un confondeur non mesuré associé au traitement et au résultat par des rapports de risques d'environ 1,412 chacun pourrait suffire, selon la logique de l'E-value. Comme l'intervalle contient déjà le nul, l'E-value de sa borne est 1,000 : le résultat n'est pas robuste sur le plan inférentiel.

### Que mesure `Revenue` ?

C'est un indicateur vrai ou faux qui précise si la session s'est terminée par une transaction. L'analyse porte sur une probabilité d'achat, et non sur une somme d'argent.

## Formulations à éviter

- Ne pas dire : « Le week-end augmente les achats de 1,5 %. »
- Dire : « L'estimation est de +1,5 point de pourcentage, sous les hypothèses du DAG. »
- Ne pas dire : « FCI a trouvé le vrai graphe causal. »
- Dire : « FCI fournit un PAG exploratoire compatible avec certaines indépendances observées. »
- Ne pas dire : « AIPW élimine tous les biais. »
- Dire : « AIPW protège contre la mauvaise spécification d'un des deux modèles, mais pas contre la confusion non mesurée. »
- Ne pas dire : « L'effet existe parce que le point estimé est positif. »
- Dire : « Le point estimé est positif, mais l'intervalle principal contient zéro. »
