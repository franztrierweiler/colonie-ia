# Prompts pour Assets Graphiques - Colonie-IA

## Textures de Planètes

Les textures de planètes sont générées procéduralement par le script `scripts/generate-planets.py`.

```bash
python scripts/generate-planets.py
```

Génère 48 textures (8 par type × 6 types) dans `frontend/public/planets/`.

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
