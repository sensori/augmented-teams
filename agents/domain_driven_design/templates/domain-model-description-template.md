# Domain Model Description: {solution_name}

**File Name**: `{solution_name_slug}-domain-model-description.md`
**Location**: `{solution_folder}/docs/domain/shaping/{solution_name_slug}-domain-model-description.md`

## Solution Purpose
{solution_purpose}

---

## Domain Model Descriptions

{domain_model_descriptions}

Each description should:
- Use natural language that domain experts understand
- Explain what each concept represents in the business domain
- Describe relationships and constraints between concepts
- Use examples to illustrate domain concepts

### Example Format

A **Program** represents all program information maintained by OSAP for each Educational Institution.

Students enrolled in a Program do not have Eligibility to apply for specific Funding Instruments.

Funding Instruments Eligibility for a Program is determined by the Educational Institution providing the Program. Each Program has a set of Program Costs that are either Fixed, Flexible or Student Centric.

A Program may be defined by a Student when making an Application for a specific Course. This will set the type of Program Cost to Student Centric.

The resulting Student Centric Program would be associated with the Student and the Application that created it.

---

## Source Material

{source_material}















