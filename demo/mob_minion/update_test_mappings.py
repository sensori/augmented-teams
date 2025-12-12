"""Update story graph with test mappings"""
import json

# Load story graph
with open('docs/stories/story-graph.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Test class mappings (exact story names in PascalCase)
test_class_mappings = {
    "Select Multiple Tokens": "TestSelectMultipleTokens",
    "Group Tokens Into Mob": "TestGroupTokensIntoMob",
    "Display Mob Creation Confirmation": "TestDisplayMobCreationConfirmation",
    "Click Mob Token To Command": "TestClickMobTokenToCommand",
    "Determine Target From Strategy": "TestDetermineTargetFromStrategy",
    "Execute Attack Action": "TestExecuteAttackAction"
}

# Test method mappings (scenario names in snake_case)
test_method_mappings = {
    "Game Master selects multiple tokens successfully": "test_game_master_selects_multiple_tokens_successfully",
    "Game Master selects zero tokens": "test_game_master_selects_zero_tokens",
    "Game Master groups tokens into mob successfully": "test_game_master_groups_tokens_into_mob_successfully",
    "Game Master confirms mob creation": "test_game_master_confirms_mob_creation",
    "Game Master cancels mob creation": "test_game_master_cancels_mob_creation",
    "Game Master clicks mob token to command mob": "test_game_master_clicks_mob_token_to_command_mob",
    "Game Master clicks token not belonging to mob": "test_game_master_clicks_token_not_belonging_to_mob",
    "System determines target using assigned strategy": "test_system_determines_target_using_assigned_strategy",
    "System uses default strategy when no strategy assigned": "test_system_uses_default_strategy_when_no_strategy_assigned",
    "System executes attack for all minions in mob": "test_system_executes_attack_for_all_minions_in_mob"
}

# Update story graph
epic = data['epics'][0]

for sub_epic in epic['sub_epics']:
    for group in sub_epic.get('story_groups', []):
        for story in group.get('stories', []):
            story_name = story['name']
            
            # Add test_class if mapping exists
            if story_name in test_class_mappings:
                story['test_class'] = test_class_mappings[story_name]
            
            # Add test_method to scenarios
            for scenario in story.get('scenarios', []):
                scenario_name = scenario['name']
                if scenario_name in test_method_mappings:
                    scenario['test_method'] = test_method_mappings[scenario_name]

# Save updated story graph
with open('docs/stories/story-graph.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Updated story graph with test mappings")

