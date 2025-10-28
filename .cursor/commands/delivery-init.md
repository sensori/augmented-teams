# Delivery Init

Initialize feature directory structure.

Part of **DELIVERY Phase**.

## Usage
```
/delivery-init <feature-name-parts...>
```

## Parameters
- `<feature-name-parts>` - Feature name (can be multiple words/parts separated by spaces)
  - All parts are combined with dashes
  - Special characters are stripped
  - Converted to lowercase

## Example
```
/delivery-init user-api
/delivery-init example sample
/delivery-init My Great Feature
```

## Steps in Delivery Phase
1. **INIT** - Creates feature directory structure
2. **INIT_CONFIG** - Generates feature-config.yaml
3. **INIT_FILES** - Creates code scaffolds (main.py, test.py)
4. **PROMPT_INPUT** - Records feature requirements
5. **SCAFFOLD_SUGGEST** - AI suggests test structure
6. **SCAFFOLD_REVIEW** - Human reviews suggestions

## What it does
1. Combines all arguments into feature name (example-sample, my-great-feature)
2. Creates feature directory structure
3. Generates feature-config.yaml
4. Creates code scaffolds (main.py, test.py)
5. Initializes state file

---

```bash
python features/delivery\ pipeline/delivery-pipeline.py run --feature <feature-name-parts>
```
