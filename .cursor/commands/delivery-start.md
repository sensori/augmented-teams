# Delivery Start

Start development phase with feature requirements.

Part of **DELIVERY Phase** (continues after delivery-init).

## Usage
```
/delivery-start <prompt-text...>
```

## Parameters
- `<prompt-text>` - Feature requirements/description (can be multiple words)

## Example
```
/delivery-start Create REST API for user management
/delivery-start Build payment processing system
/delivery-start Add authentication with JWT
```

## Steps in Delivery Phase
1. **INIT_STRUCTURE** - Creates feature directory structure
2. **INIT_CONFIG** - Generates feature-config.yaml
3. **INIT_FILES** - Creates code scaffolds (main.py, test.py)
4. **PROMPT_INPUT** - Records feature requirements ← You are here
5. **SCAFFOLD_SUGGEST** - AI suggests test structure
6. **SCAFFOLD_REVIEW** - Human reviews suggestions

## What it does
1. Takes prompt text as feature requirements
2. Records prompt in pipeline state
3. AI suggests test structure from requirements
4. Prepares for scaffold review

---

```bash
python features/delivery\ pipeline/delivery-pipeline.py run --feature <feature-name> --prompt "<prompt-text>"
```

