# # =============================================================================
# FILE:               Paris_Interractive_Map_01_03.py
# AUTHOR:             Aris Dimitracopoulos
# CREATION DATE:      2026-02-08
# DESCRIPTION:        This code creates an interactive map of Paris powered by 
#                     Folium & Pandas, based on suggestions and opinions by 
#                     the GOAT himself (Aris). 
# VERSION UPDATES:    Adds places as a category
# LAST MODIFIED BY Aris Dimitracopoulos ON THE 2026-02-08
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
m = folium.Map(location=[48.8566, 2.3522], zoom_start=13, tiles="cartodbpositron")

# 3. CONFIGURATION DES CATÉGORIES
config_categories = {
    'Friperie': {'couleur': 'purple', 'icon': 'shopping-bag'},
    'Resto': {'couleur': 'orange', 'icon': 'cutlery'},
    'Musee': {'couleur': 'blue', 'icon': 'university'},
    'Bar': {'couleur': 'darkred', 'icon': 'glass'},
    'Boulangerie': {'couleur': 'green', 'icon': 'birthday-cake'},
    'Endroit': {'couleur': 'darkgreen', 'icon': 'tree'}  # <--- NOUVEAU (Parcs, rues, spots...)
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
groupe_complet = folium.FeatureGroup(name="--- TOUT AFFICHER ---", show=True).add_to(m)
groupes_cat = {}

# On parcourt les catégories présentes dans le CSV
for cat in df['categorie'].unique():
    groupes_cat[cat] = folium.FeatureGroup(name=cat, show=False).add_to(m)

# 5. Ajout des marqueurs
for index, lieu in df.iterrows():
    # Récupération de la config (si la catégorie n'existe pas, icône par défaut 'map-marker' grise)
    conf = config_categories.get(lieu['categorie'], {'couleur': 'gray', 'icon': 'map-marker'})
    est_fait = str(lieu['statut']).lower() == 'fait'
    
    # Étoiles
    stars_html = generer_html_etoiles(lieu['note'])
    
    # Avis
    avis_text = ""
    if 'avis' in df.columns and pd.notna(lieu['avis']):
        avis_text = f"<br><div style='margin-top:8px; padding-top:8px; border-top:1px solid #eee;'><b>L'avis du GOAT :</b> <i>{lieu['avis']}</i></div>"
    
    # Popup HTML
    html_popup = f"""
    <div style='font-family: sans-serif; min-width: 220px;'>
        <h4 style='margin-bottom:0px;'>{lieu['nom']}</h4>
        <small style='color:gray;'>{lieu['categorie']}</small><br>
        <div style='margin-top:5px; margin-bottom:5px;'>{stars_html}</div>
        <p style='margin:0;'>{lieu['description']}</p>
        {avis_text}
    </div>
    """
    
    # Création du Marker
    tooltip_simple = f"{lieu['nom']} ({lieu['note']})"
    
    def create_marker(lieu_data, config, fait):
        return folium.Marker(
            location=[lieu_data['latitude'], lieu_data['longitude']],
            popup=folium.Popup(html_popup, max_width=300),
            tooltip=lieu_data['nom'],
            icon=folium.Icon(color=config['couleur'], icon=config['icon'], prefix='fa'),
            opacity=0.5 if fait else 1.0
        )

    # Ajout aux groupes
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
    layer=search_layer, geom_type="Point", placeholder="Chercher une pépite...",
    collapsed=False, search_label="name", search_zoom=17
).add_to(m)

# 7. LÉGENDE FIXE
legende_html = """
<div style="
    position: fixed; 
    bottom: 30px; left: 30px; width: 230px; 
    z-index:9999; font-size:12px;
    background-color: white; opacity: 0.9;
    padding: 10px; border: 2px solid grey; border-radius: 5px;
    font-family: sans-serif; box-shadow: 3px 3px 5px rgba(0,0,0,0.3);
    ">
    <h5 style="margin-top:0; text-align:center;">Légende des Notes (GOAT)</h5>
    <div style="margin-bottom:5px;">⭐ <b>5.0 :</b> Immanquable</div>
    <div style="margin-bottom:5px;">⭐ <b>4.0 :</b> Si dans le quartier</div>
    <div style="margin-bottom:5px;">⭐ <b>3.0 :</b> Normal sans plus</div>
    <div style="margin-bottom:5px;">⭐ <b>2.0 :</b> Si pas d'alternative</div>
    <div>⭐ <b>1.0 :</b> À éviter</div>
</div>
"""
m.get_root().html.add_child(folium.Element(legende_html))

# Options
LocateControl(auto_start=False, flyTo=True).add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

m.save("carte_paris_complete.html")
print("Carte générée ! 'Endroit' ajouté avec succès (icône arbre 🌳).")