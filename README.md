# Divina Commedia — Analisi NLP

Versione statica (Cloudflare Pages) dell’app Google Apps Script **DanteFuzzyW**.

Stessa grafica (Cinzel / IM Fell English, tema pergamena scura) e stesse funzioni:
mappa UMAP 2D/3D, ricerca fuzzy AND/OR/NOT, concordanze KWIC, frequenze/TF-IDF,
nuvola, rete lessicale, sentiment, mappe cosmologiche Inferno/Purgatorio/Paradiso.

## Locale

Apri `site/` con un server HTTP (non `file://`, i JSON vanno in fetch):

```bash
python3 -m http.server 8788 --directory site
```

Poi http://127.0.0.1:8788/

## Sorgente Apps Script

- Foglio: [DanteFuzzyW](https://docs.google.com/spreadsheets/d/1PLSOdSP93rYIkBFNVY44ANmoJ35ajqYjdoVRiznN8B4)
- Script: `1rhJVOIWG9Pl3Ha1WsSTYJ_ZOGjBuXe1LRRUql0hRsPiTk1W_aaHN94nt`
- Checkout clasp: `original/apps-script/`

Il quiz da punti selezionati resta solo su Apps Script (crea un Google Form).

## Deploy Cloudflare Pages

Progetto suggerito: `divina-commedia`  
Output directory: `site`  
Dominio di default: `divina-commedia.pages.dev`  
(opzionale) `commedia.fisica-liceo.com` o `dante.pages.dev` se libero.
