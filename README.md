# Zwembaden in Nederland
In deze _repository_ kijken we naar privézwembaden in Nederland. Door de analyse van satellietbeeld uit het [Satellietdataportaal van de Rijksoverheid](https://www.satellietdataportaal.nl/). Informatie over publieke zwembaden halen we uit [Overpass](https://overpass-turbo.eu/). 

Deze repository is gemaakt in het kader van een cursus van het Fonds Bijzondere Journalistieke projecten.

## Benodigdheden
Al deze code is geschreven in Python, gebruik een moderne versie en een versiemanager als `venv` of `conda` om de benodigde libraries te installeren. Een moderne computer is fijn, omdat de AI-analyse aardig wat rekenkracht kost. 

## Scripts
- `get_satellite_url.py` creëert een url waarmee je de juiste data in het Rijksdataportaal kunt vinden. Hier heb je wel een account voor nodig, als je materiaal wilt downloaden zal de site je om een inlog vragen. 
- `tile_satellite_file.py` neemt een gedownload `tiff`-bestand uit het portaal en knipt het op in kleine stukjes. Hiermee kun je je model trainen (in een tool als [Teachable Machine](https://teachablemachine.withgoogle.com/)). 
- `detect_swimming_pools.py` kun je vervolgens gebruiken om zwembaden te vinden in je geknipte bestanden. Let op: hiervoor moet je wel een model-bestand hebben, en je moet je originele bestand al hebben opgeknipt! 

## Tips
- Laad de tif-bestanden, en je uiteindelijke `geojson` met de gevonden zwembaden in in [Qgis](https://qgis.org/) zodat je kunt controleren of het model naar behoren functioneert.
- De originele beelden en modellen staan niet in deze _repo_, omdat die bestanden veel te groot zijn.

## TODO
- De resultaten van het model afzetten tegen publieke zwembaden zodat die niet mee worden genomen.
