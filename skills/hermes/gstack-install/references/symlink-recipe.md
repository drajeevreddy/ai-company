# Hermes gstack Symlink Recipe

Session-specific detail for the Hermes gstack install. The `./setup --host hermes`
script exits early (Hermes is not a first-class target), so these manual steps are needed.

## Runtime dirs to create

```bash
mkdir -p ~/.hermes/skills/gstack/{bin,browse/dist,browse/bin,design/dist,gstack-upgrade,review,specialists,qa/templates,qa/references,plan-devex-review}
```

## Runtime symlinks

```bash
ln -sf ~/gstack/bin ~/.hermes/skills/gstack/bin
ln -sf ~/gstack/browse/dist ~/.hermes/skills/gstack/browse/dist
ln -sf ~/gstack/browse/bin ~/.hermes/skills/gstack/browse/bin
ln -sf ~/gstack/design/dist ~/.hermes/skills/gstack/design/dist
ln -sf ~/gstack/ETHOS.md ~/.hermes/skills/gstack/ETHOS.md
ln -sf ~/gstack/review/checklist.md ~/.hermes/skills/gstack/review/checklist.md
ln -sf ~/gstack/review/TODOS-format.md ~/.hermes/skills/gstack/review/TODOS-format.md
ln -sf ~/gstack/review/specialists ~/.hermes/skills/gstack/review/specialists
ln -sf ~/gstack/qa/templates ~/.hermes/skills/gstack/qa/templates
ln -sf ~/gstack/qa/references ~/.hermes/skills/gstack/qa/references
ln -sf ~/gstack/plan-devex-review/dx-hall-of-fame.md ~/.hermes/skills/gstack/plan-devex-review/dx-hall-of-fame.md
ln -sf ~/gstack/gstack-upgrade/SKILL.md ~/.hermes/skills/gstack/gstack-upgrade/SKILL.md
```

## Skill directory symlinks

```bash
for d in ~/gstack/.hermes/skills/gstack-*/; do
  name=$(basename "$d")
  target="$HOME/.hermes/skills/$name"
  [ -L "$target" ] || [ ! -e "$target" ] && ln -sf "$d" "$target"
done
```

## Common failure mode

Missing `bin/` or `browse/dist/` symlinks — skills that reference `$SKILL_ROOT/review/design-checklist.md` will fail silently without them.
