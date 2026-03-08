# # =============================================================================
# FILE:               Paris_Interractive_Map_01_04.py
# AUTHOR:             Aris Dimitracopoulos
# CREATION DATE:      2026-02-08
# DESCRIPTION:        This code creates an interactive map of Paris powered by 
#                     Folium & Pandas, based on suggestions and opinions by 
#                     the GOAT himself (Aris). 
# VERSION UPDATES:    Minimize legends for better readability on mobile phone
# LAST MODIFIED BY Aris Dimitracopoulos ON THE 2026-02-14
# =============================================================================

import folium
import pandas as pd
from folium.plugins import Search, LocateControl

# 1. Chargement des données
try:
    df = pd.read_csv('Adresses_Paris.csv')
    if 'note' not in df.columns:
        df['note'] = 0.0
except FileNotFoundError:
    print("Erreur : Le fichier 'Adresses_Paris.csv' est introuvable.")
    exit()

# 2. Création de la carte
# On désactive le contrôle du zoom par défaut pour gagner de la place (on zoome avec les doigts)
m = folium.Map(location=[48.8566, 2.3522], zoom_start=13, tiles="cartodbpositron", zoom_control=False)

# 3. CONFIGURATION DES CATÉGORIES
config_categories = {
    'Friperie': {'couleur': 'purple', 'icon': 'shopping-bag'},
    'Resto': {'couleur': 'orange', 'icon': 'cutlery'},
    'Musee': {'couleur': 'blue', 'icon': 'university'},
    'Bar': {'couleur': 'darkred', 'icon': 'glass'},
    'Boulangerie': {'couleur': 'green', 'icon': 'birthday-cake'},
    'Endroit': {'couleur': 'darkgreen', 'icon': 'tree'},
    'Magasin': {'couleur': 'turquoise', 'icon': 'shop'},
}

# --- FONCTION : GÉNÉRATEUR D'ÉTOILES ---
def generer_html_etoiles(note):
    try:
        score = float(note)
    except:
        score = 0.0
    percent = (score / 5) * 100
    html = f"""
    <div style="position: relative; display: inline-block; font-size: 18px; color: #d3d3d3;">
        ★★★★★
        <div style="position: absolute; top: 0; left: 0; width: {percent}%; overflow: hidden; color: #f1c40f; white-space: nowrap;">
            ★★★★★
        </div>
    </div>
    <span style="font-size: 12px; color: gray; margin-left: 5px;">({score}/5)</span>
    """
    return html

# 4. Création des Groupes
groupe_complet = folium.FeatureGroup(name="Tout Afficher", show=True).add_to(m)
groupes_cat = {}

for cat in df['categorie'].unique():
    groupes_cat[cat] = folium.FeatureGroup(name=cat, show=False).add_to(m)

# 5. Ajout des marqueurs
for index, lieu in df.iterrows():
    conf = config_categories.get(lieu['categorie'], {'couleur': 'gray', 'icon': 'map-marker'})
    est_fait = str(lieu['statut']).lower() == 'fait'
    stars_html = generer_html_etoiles(lieu['note'])
    
    avis_text = ""
    if 'avis' in df.columns and pd.notna(lieu['avis']):
        avis_text = f"<br><div style='margin-top:8px; padding-top:8px; border-top:1px solid #eee;'><b>L'avis du GOAT :</b> <i>{lieu['avis']}</i></div>"
    
    html_popup = f"""
    <div style='font-family: sans-serif; min-width: 220px;'>
        <h4 style='margin-bottom:0px;'>{lieu['nom']}</h4>
        <small style='color:gray;'>{lieu['categorie']}</small><br>
        <div style='margin-top:5px; margin-bottom:5px;'>{stars_html}</div>
        <p style='margin:0;'>{lieu['description']}</p>
        {avis_text}
    </div>
    """
    
    # Fonction locale pour créer le marqueur (évite la répétition)
    def create_marker(lieu_data, config, fait):
        return folium.Marker(
            location=[lieu_data['latitude'], lieu_data['longitude']],
            popup=folium.Popup(html_popup, max_width=300),
            tooltip=lieu_data['nom'],
            icon=folium.Icon(color=config['couleur'], icon=config['icon'], prefix='fa'),
            opacity=0.5 if fait else 1.0
        )

    create_marker(lieu, conf, est_fait).add_to(groupes_cat[lieu['categorie']])
    create_marker(lieu, conf, est_fait).add_to(groupe_complet)

# 6. Recherche (Invisible)
def create_geojson_features(df):
    features = []
    for _, lieu in df.iterrows():
        features.append({
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [lieu['longitude'], lieu['latitude']]},
            'properties': {'name': lieu['nom']}
        })
    return {'type': 'FeatureCollection', 'features': features}

search_layer = folium.GeoJson(
    create_geojson_features(df),
    style_function=lambda x: {'fillColor': '#00', 'color': '#00', 'opacity':0} 
).add_to(m)

Search(
    layer=search_layer, geom_type="Point", placeholder="🔍 Chercher...",
    collapsed=True, # La barre de recherche est repliée aussi !
    search_label="name", search_zoom=17
).add_to(m)

# 7. LÉGENDE INTERACTIVE (JAVASCRIPT + HTML)
# On crée un bouton qui ouvre/ferme la boîte
legende_html = """
<script>
function toggleLegende() {
    var x = document.getElementById("legende-box");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}
</script>

<div style="position: fixed; bottom: 20px; left: 10px; z-index:9999; font-family: sans-serif;">
    
    <button onclick="toggleLegende()" style="
        background-color: white; border: 2px solid grey; border-radius: 50px;
        padding: 8px 15px; font-weight: bold; cursor: pointer; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    ">
        ⭐ Légende
    </button>

    <div id="legende-box" style="
        display: none; 
        margin-bottom: 10px; width: 200px; 
        background-color: white; opacity: 0.95;
        padding: 10px; border: 1px solid grey; border-radius: 5px;
        font-size: 12px; box-shadow: 3px 3px 5px rgba(0,0,0,0.3);
    ">
        <h5 style="margin-top:0; text-align:center; border-bottom:1px solid #eee; padding-bottom:5px;">Notation GOAT</h5>
        <div style="margin-bottom:3px;">⭐ <b>5.0 :</b> Immanquable</div>
        <div style="margin-bottom:3px;">⭐ <b>4.0 :</b> Si dans le quartier</div>
        <div style="margin-bottom:3px;">⭐ <b>3.0 :</b> Normal sans plus</div>
        <div style="margin-bottom:3px;">⭐ <b>2.0 :</b> Pas ouf</div>
        <div>⭐ <b>1.0 :</b> À fuir</div>
    </div>
</div>
"""

style_css = """
<style>
    .leaflet-control-layers-overlays label:nth-child(1) { color: black; font-weight: bold; border-bottom: 1px solid #ccc; }
    .leaflet-control-layers-overlays label:nth-child(2) { color: blue; }
    .leaflet-control-layers-overlays label:nth-child(3) { color: orange; }
    .leaflet-control-layers-overlays label:nth-child(4) { color: green; }
    .leaflet-control-layers-overlays label:nth-child(5) { color: dark green; }
    .leaflet-control-layers-overlays label:nth-child(6) { color: purple; }
    .leaflet-control-layers-overlays label:nth-child(7) { color: red; }
</style>
"""

m.get_root().html.add_child(folium.Element(legende_html))
m.get_root().html.add_child(folium.Element(style_css))

# 8. Options Finales (Menu replié pour mobile)
LocateControl(auto_start=False, flyTo=True).add_to(m)

# ICI : collapsed=True rend le menu tout petit par défaut
folium.LayerControl(collapsed=True).add_to(m)

m.save("carte_paris_mobile.html")
print("Carte Mobile v9 générée ! Tout est minimisé pour ton écran.")