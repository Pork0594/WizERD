# Spacing Profiles

WizERD's auto-layout derives all routing and layering constants from a spacing profile. This ensures consistent, predictable results across different schemas.

## Available Profiles

### compact

```bash
wizerd generate schema.sql -o diagram.svg -w compact
```

Keeps tables closer together using smaller lane/lateral clearances. Best for:
- Quick prototypes
- Small schemas (under 20 tables)
- When you need a compact overview

### standard

```bash
wizerd generate schema.sql -o diagram.svg -w standard
```

The production default. Balanced readability without massive canvases. Best for:
- Most production use cases
- Medium schemas (20-50 tables)
- General documentation

### spacious

```bash
wizerd generate schema.sql -o diagram.svg -w spacious
```

Inflates table clearance, lane spacing, and ELK layer spacing. Best for:
- Large schemas (50+ tables)
- Team reviews
- When you need to trace complex relationships

## Comparison

| Aspect | Compact | Standard | Spacious |
|--------|---------|----------|----------|
| Table spacing | Tight | Medium | Generous |
| Lane spacing | Narrow | Medium | Wide |
| Entry margins | Small | Medium | Large |
| Canvas size | Smallest | Medium | Largest |
| Best for | Quick views | Production | Complex schemas |

## Visual Comparison

### Compact

![compact](./images/sample-spacing-compact.png)

### Standard

Uses default spacing (similar to sample-default-dark)

### Spacious

![spacious](./images/sample-spacing-spacious.png)

Notice how the relationships have more room to breathe in the spacious layout.

## How It Works

The spacing profile affects:

1. **ELK Layout Engine**
   - Layer spacing
   - Component spacing
   - Edge-to-node margins

2. **Post-processing Router**
   - Trunk offsets
   - Lane spacing
   - Entry margins

WizERD also implements a spacing feedback loop:
1. First layout pass with ELK
2. Check spacing constraints
3. If violations found: widen trunks/lanes, shrink entry zones
4. Re-run ELK with adjusted parameters
5. Repeat until constraints met or max iterations reached

This automatic adjustment handles most congestion automatically.

## Choosing a Profile

Start with `standard` for most use cases. Switch to:

- `compact` if you want smaller outputs
- `spacious` if you have many tables and relationships

You can always try multiple profiles to see which works best for your schema:

```bash
for profile in compact standard spacious; do
  wizerd generate schema.sql -o "diagram-$profile.svg" -w $profile
done
```

## Next Steps

- [Configuration](configuration.md) — Set default spacing in config
- [Examples](examples.md) — More command examples
- [CLI Reference](cli-reference.md) — Complete command reference
