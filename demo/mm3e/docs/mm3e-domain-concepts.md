# M&M 3E Domain Concepts Reference

**Source**: Extracted from Heroes Handbook (demo/mm3e/HeroesHandbook.pdf)
**Date**: Thursday, November 13, 2025
**Purpose**: Core domain knowledge for character creator development

---

## Character Creation Workflow

**Order of Creation** (from handbook examples, pages 51-54):
1. **Power Level** → Sets limits and starting points (PL × 15 = total power points)
2. **Abilities** → Foundation (2 pp/rank, affects defenses & skills)
3. **Defenses** → Derived from abilities, can purchase additional ranks (1 pp/rank)
4. **Skills** → Training in specific areas (1 pp per 2 ranks, 0.5 pp/rank)
5. **Advantages** → Minor benefits (1 pp each or per rank)
6. **Powers** → Superhuman abilities (variable cost based on effects/modifiers)
7. **Complications** → Earn hero points during play
8. **Details** → Name, appearance, background

---

## Core Costs (Page 26, Basic Trait Costs table)

| Trait | Cost |
|-------|------|
| **Ability** | 2 points per rank |
| **Defense** | 1 point per rank |
| **Skill** | 1 point per 2 ranks (0.5 per rank) |
| **Advantage** | 1 point per advantage or rank |
| **Power** | ((base effect cost + extras – flaws) × rank) + flat modifiers |

---

## Power Level System

**Starting Power Points** (Page 26 table):
- Formula: **PL × 15 = Starting Power Points**
- PL 8 = 120 points (Masked Adventurers)
- **PL 10 = 150 points** (Standard Superheroes) ← DEFAULT
- PL 12 = 180 points (Big Leagues)
- PL 14 = 210 points (World-Protectors)

**Power Level Limits** (Pages 26-27):
1. **Skill Modifier**: Ability rank + Skill rank + Advantages ≤ PL + 10
2. **Attack & Effect**: Attack bonus + Effect rank ≤ PL × 2
3. **Dodge & Toughness**: Dodge + Toughness ≤ PL × 2
4. **Parry & Toughness**: Parry + Toughness ≤ PL × 2
5. **Fortitude & Will**: Fortitude + Will ≤ PL × 2

---

## The 8 Abilities (Chapter 3, Pages 108-111)

| Ability | Description | Affects |
|---------|-------------|---------|
| **Strength (STR)** | Physical power | Damage, lifting, athletics |
| **Stamina (STA)** | Endurance & health | Fortitude, Toughness (base values) |
| **Agility (AGL)** | Balance & grace | Dodge (base), Acrobatics |
| **Dexterity (DEX)** | Coordination & accuracy | Ranged attacks, fine manipulation |
| **Fighting (FGT)** | Close combat skill | Parry (base), Close Combat |
| **Intellect (INT)** | Reasoning & knowledge | Technology, Investigation |
| **Awareness (AWE)** | Perception & willpower | Will (base), Perception, Insight |
| **Presence (PRE)** | Personality & force of will | Persuasion, Intimidation, Deception |

**Rank Scale**:
- **-5 to 0**: Below average to average
- **1-2**: Above average
- **3-4**: Exceptional
- **5-7**: Peak human
- **8-12**: Superhuman
- **13-20**: Cosmic-level

**Cost**: **2 power points per rank**

---

## The 5 Defenses (Pages 108-111)

| Defense | Base Calculation | Can Purchase? | Cost |
|---------|------------------|---------------|------|
| **Dodge** | 10 + Agility | Yes | 1 pp/rank |
| **Parry** | 10 + Fighting | Yes | 1 pp/rank |
| **Fortitude** | Stamina | Yes | 1 pp/rank |
| **Will** | Awareness | Yes | 1 pp/rank |
| **Toughness** | Stamina | **NO - Only via Advantages/Powers** | N/A |

**Critical Rule**: **Toughness CANNOT be purchased directly with power points!**
- Only improved through:
  - Advantages (e.g., Defensive Roll, Protection)
  - Powers (e.g., Protection effect, Enhanced Stamina)

**Active Defenses**: Dodge, Parry (require action/awareness)
**Resistance Checks**: Fortitude, Toughness, Will (passive resistance)

---

## Skills (Chapter 4, Pages 114-131)

**Cost**: **1 power point per 2 skill ranks** (0.5 pp per rank)

**Skill Check Formula**: `d20 + Ability Rank + Skill Rank + Modifiers`

**Trained vs. Untrained**:
- **Untrained**: Can use skill with just ability modifier (skill rank = 0)
- **Trained Only**: Some skills CANNOT be used untrained (marked in handbook)
  - Examples: Expertise (specific), Technology, Treatment (surgery), Vehicles (complex)

**Linked Abilities** (key examples):
- **Acrobatics** → Agility
- **Athletics** → Strength
- **Close Combat** → Fighting
- **Deception** → Presence
- **Insight** → Awareness
- **Intimidation** → Presence
- **Investigation** → Intellect
- **Perception** → Awareness
- **Persuasion** → Presence
- **Ranged Combat** → Dexterity
- **Sleight of Hand** → Dexterity
- **Stealth** → Agility
- **Technology** → Intellect
- **Treatment** → Intellect
- **Vehicles** → Dexterity

---

## Advantages (Chapter 5, Pages 132-142)

**Cost**: **1 power point per advantage** (or per rank for ranked advantages)

**Types**:
1. **Combat** (e.g., Power Attack, Defensive Roll, Improved Initiative)
2. **Fortune** (e.g., Luck, Seize Initiative, Ultimate Effort)
3. **General** (e.g., Equipment, Benefit, Connected)
4. **Skill** (e.g., Jack-of-all-Trades, Skill Mastery, Well-informed)

**Special**: 
- **Equipment**: 5 equipment points per rank
- **Benefit**: Various social/resource advantages (wealth, status, etc.)

---

## Powers (Chapter 6, Pages 144+)

**Effects**: Base building blocks (Damage, Protection, Flight, etc.)
- Each effect has base cost per rank
- Effects have ranks 1-20 (sometimes higher)

**Modifiers**:
- **Extras**: Increase cost per rank (+1 flat = +1 cost/rank)
- **Flaws**: Decrease cost per rank (-1 flat = -1 cost/rank)
- **Flat Modifiers**: Add/subtract fixed points (not per rank)

**Formula**: `((base cost + extras – flaws) × rank) + flat modifiers`

**Common Effects**:
- **Damage**: Offensive attack
- **Protection**: Increases Toughness
- **Flight**: Movement through air
- **Enhanced [Trait]**: Increases ability/skill/etc.
- **Immunity**: Resist specific effects
- **Regeneration**: Heal over time

---

## Character Validation Rules

**"Warn, Don't Prevent" Philosophy** (user requirement):
- Validation errors should **warn** but **never block** save operations
- Allow "illegal" characters (overspent points, violated PL caps, etc.)
- Display warnings so players know they're outside rules
- GM can decide whether to allow

**Required Minimums** (for legal character):
- Must have Power Level selected
- All 8 abilities must have values (can be 0, -1, etc.)
- All 5 defenses must be calculated
- Point totals tracked (but overspend allowed with warning)

**Power Level Caps** (must validate but not block):
1. Total points spent ≤ Starting Power Points (PL × 15)
2. Skill modifiers ≤ PL + 10
3. Attack + Effect ≤ PL × 2
4. Dodge + Toughness ≤ PL × 2
5. Parry + Toughness ≤ PL × 2
6. Fortitude + Will ≤ PL × 2

---

## Dependencies & Cascading Updates

**When Ability Changes** → Recalculate:
1. **Defense base values** (if ability affects that defense)
   - Agility → Dodge base
   - Fighting → Parry base
   - Stamina → Fortitude base, Toughness base
   - Awareness → Will base
2. **Skill bonuses** (all skills linked to that ability)
3. **Total skill modifier** (for PL cap validation)
4. **Power Level validation** (check all caps)

**When Defense Purchased Rank Changes** → Recalculate:
1. **Total defense value** (base + purchased)
2. **Power Level validation** (paired defense caps)

**When Power Level Changes** → Recalculate:
1. **Starting Power Points** (PL × 15)
2. **All PL cap validations**
3. **Validate all traits** against new limits

---

## Save/Load Philosophy

**Save Operations**:
- **Auto-save**: Every 2 minutes, non-intrusive, silent retry on failure
- **Manual save**: User-triggered, show status/confirmation
- **Create vs. Update**: Same operation (upsert), differentiated by existence check
- **Error Handling**: Never block save (warn user), allow retry

**Data Model**:
- **Single point pool**: All categories draw from same pool (Abilities, Skills, Advantages, Powers, Defenses)
- **Character state**: Includes all traits, spent points, validation warnings
- **Persistence**: Cloud storage (implementation TBD)

---

## UI Concepts

**Character Sheet Layout** (from handbook page 52):
- **Header**: Name, Identity, Power Level, Point Totals
- **Abilities Section**: 8 abilities with ranks
- **Defenses Section**: 5 defenses (base + purchased)
- **Offense Section**: Attack bonuses, damage values
- **Skills Section**: All skills with ranks and bonuses
- **Advantages Section**: List of advantages
- **Powers Section**: List of powers/effects
- **Complications Section**: Character complications
- **Equipment Section**: Gear and equipment

**Point Budget Display**:
- Total points available (PL × 15)
- Points spent by category (Abilities, Defenses, Skills, Advantages, Powers)
- Remaining unspent points
- Overspend warnings (if applicable)

---

## Glossary

- **AC**: Acceptance Criteria (story concept, not game term)
- **d20**: Twenty-sided die (core game mechanic)
- **DC**: Difficulty Class (target number for checks)
- **Effect**: Basic power building block
- **Extra**: Power modifier that increases cost
- **Flaw**: Power modifier that decreases cost
- **GM**: Gamemaster (referee/narrator)
- **PL**: Power Level (overall power scale)
- **pp**: Power Points (character creation currency)
- **Rank**: Numerical rating for traits (abilities, skills, powers, etc.)
- **Trait**: Any character attribute (ability, skill, advantage, power, defense)

---

**End of Reference**


































