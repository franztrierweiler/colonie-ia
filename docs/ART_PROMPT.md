# Prompts pour Assets Graphiques - Colonie-IA

## Planche de Textures de Planètes

### Prompt pour Mistral AI - Sprite Sheet Planètes

```
Create a sprite sheet of 12 different planet textures arranged in a 4x3 grid.
Each planet should be a perfect circle on a transparent or pure black background (#000000).
Style: Spaceward Ho! retro 1990s game aesthetic, vibrant colors, slightly cartoonish but detailed.

Grid layout (4 columns x 3 rows):

Row 1 (Habitable planets):
1. Earth-like planet: blue oceans, green/brown continents, white clouds, vibrant
2. Ocean world: almost entirely deep blue water, small islands, tropical feel
3. Desert planet: Mars-like orange/red, canyons, dust storms, dried riverbeds
4. Ice planet: white/light blue, frozen oceans, glaciers, snowstorms

Row 2 (Hostile planets):
5. Volcanic planet: dark surface with bright orange/red lava rivers and eruptions
6. Toxic planet: sickly green/yellow atmosphere, purple clouds, poisonous look
7. Barren rocky: gray moon-like surface, many craters, no atmosphere
8. Scorched planet: blackened surface, glowing cracks, extreme heat damage

Row 3 (Special planets):
9. Gas giant type A: Jupiter-like bands, orange/brown/white stripes, great storm
10. Gas giant type B: Saturn-like, pale yellow/beige bands, subtle rings hint
11. Mineral-rich asteroid: metallic gray/silver, crystalline formations, valuable look
12. Mysterious unexplored: shrouded in fog/clouds, hints of surface, enigmatic

Technical requirements:
- Total image size: 1024x768 pixels (each planet ~256x256 in its cell)
- Pure black (#000000) or transparent background between planets
- Each planet perfectly circular with consistent size (~200px diameter)
- Good spacing between planets for easy slicing
- Consistent lighting (light source from top-left)
- Visible surface details: craters, continents, clouds, atmospheric effects
- Semi-realistic but stylized (not photorealistic, not too cartoonish)
- Each planet should look distinct and recognizable at small sizes (32-64px)

Style references:
- Spaceward Ho! game planets
- Master of Orion planet styles
- Vibrant but not neon colors
- Subtle shading for 3D sphere effect
```

### Variante compacte

```
Sprite sheet, 4x3 grid of 12 cartoon planets on black background, retro 1990s space game style like Spaceward Ho!. Include: Earth-like, ocean, desert, ice, volcanic, toxic, barren, scorched, 2 gas giants, asteroid, mysterious foggy. Each planet circular ~200px, total 1024x768, vibrant colors, visible surface details, consistent lighting from top-left.
```

### Instructions de découpage

Une fois l'image générée, elle sera découpée en 12 textures individuelles :
- Colonnes : 4 (256px chacune)
- Lignes : 3 (256px chacune)
- Chaque texture sera sauvegardée dans `/frontend/public/planets/`

### Nommage des fichiers après découpage

```
planet-earthlike.png
planet-ocean.png
planet-desert.png
planet-ice.png
planet-volcanic.png
planet-toxic.png
planet-barren.png
planet-scorched.png
planet-gasgiant-a.png
planet-gasgiant-b.png
planet-asteroid.png
planet-mysterious.png
```

---

## Logo Principal (Page de Login)

### Prompt pour Mistral AI

```
Create a game logo featuring a colorful cartoon planet wearing a Napoleonic bicorne hat.
The style should be inspired by the 1990s game "Spaceward Ho!" - vibrant colors,
slightly cartoonish, playful but not childish, with a retro sci-fi feel.

The planet should be:
- Spherical with visible continents or terrain features
- Warm earth-like colors (blues, greens, browns)
- Wearing a classic black Napoleonic bicorne hat with gold trim and a tricolor cockade
- The hat should be tilted at a jaunty, confident angle
- Slight shading to give depth

Background:
- Simple starfield or transparent background
- No text in the image

Style references:
- Spaceward Ho! game aesthetic (1990s Mac/PC strategy game)
- Cartoon/vector art style
- Bold outlines
- Saturated colors
- Slightly humorous tone

Technical requirements:
- High resolution (at least 512x512, ideally 1024x1024)
- Square format suitable for a login page hero image
- Clean edges suitable for web use
```

### Variante simplifiée

```
A cartoon planet with a black Napoleonic bicorne hat, Spaceward Ho! retro game style,
vibrant colors, starfield background, 1990s video game aesthetic, vector art,
playful and humorous, high resolution logo
```

### Mots-clés à ajuster si nécessaire

- Plus rétro : ajouter "pixel art", "16-bit era", "dithering"
- Plus moderne : ajouter "flat design", "minimalist", "vector illustration"
- Plus dramatique : ajouter "epic lighting", "space nebula background"
- Plus humoristique : ajouter "googly eyes on planet", "smirking expression"
