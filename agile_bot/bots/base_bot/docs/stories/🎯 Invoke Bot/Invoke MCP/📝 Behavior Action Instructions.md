# 📝 Behavior Action Instructions

**Navigation:** [📋 Story Map](../../story-map.txt) | [Story Graph](../../story-graph.json)

**Epic:** Invoke MCP Bot Server  
**Feature:** Invoke Bot Tool

**User:** Bot Behavior  
**Sequential Order:** 2  
**Story Type:** system

## Story Description

Action method loads and merges instructions from base_actions and behavior-specific locations so that compiled instructions can be returned for injection into AI Chat.

## Acceptance Criteria

- **WHEN** Action method is invoked
- **THEN** Action loads instructions from base_actions and behavior-specific locations
- **AND** Instructions are merged and returned

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Base and behavior-specific instructions exist
```

## Scenarios

### Scenario: Action loads and merges instructions

**Steps:**
```gherkin
Given Base and behavior-specific instructions exist
When Action method is invoked
Then Instructions are loaded from both locations and merged
And Instructions merged from both sources
```

## Source Material

**Generated from:** Story "Behavior Action Instructions" in story graph  
**Date:** 2025-12-05  
**Context:** Foundational story for loading and merging instructions from base_actions and behavior-specific locations

