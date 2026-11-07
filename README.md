# TrouveMonAlternance
Site statique (GitHub Pages) : offres d'alternance réelles (API France Travail), compétences demandées calculées sur ces offres.

## Mise en route
1. Crée un compte sur https://francetravail.io, crée une application et active l'API « Offres d'emploi v2 ». Récupère l'identifiant client et la clé secrète.
2. Dépôt GitHub → Settings → Secrets and variables → Actions → ajoute `FT_CLIENT_ID` et `FT_CLIENT_SECRET`.
3. Settings → Actions → General → Workflow permissions : « Read and write permissions ».
4. Onglet Actions → « Mise à jour des offres » → Run workflow (puis automatique chaque jour).
5. Settings → Pages → Deploy from a branch → `main` / root.
