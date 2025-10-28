# Delivery Approve

Approve and continue the delivery pipeline to the next step.

## Usage
```
/delivery-approve <feature>
```

## Parameters
- `<feature>` - Feature name (required)

## Example
```
/delivery-approve user-api
/delivery-approve sample
```

## What it does
- Approves the current human-in-the-loop step
- Moves pipeline to next phase
- Continues execution

---

```bash
python features/delivery\ pipeline/delivery-pipeline.py approve --feature <feature>
``` 