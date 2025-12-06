# Test Status Summary

## Expected Files Created

The following scenarios had expected files created from actual outputs:

1. **couple_of stories_with_acceptance_criteria** - Created expected files
2. **different_story_types_story_graph** - Created expected files  
3. **incomplete_with_estimates_story_graph** - Created expected files
4. **multiple_epics_features_test** - Created expected files
5. **nested_workflow** - Created expected files
6. **optional_vs_sequential_story_graph** - Created expected files
7. **render_sync_render_complex** - Created expected files
8. **simple_story_graph** - Created expected files
9. **single_epic_story_graph** - Created expected files
10. **sync_render_with_layout** - Created expected files
11. **with_increments_story_graph** - Created expected files

## Test Results

- **Passed**: 1 test (multiple_users_story_graph)
- **Failed**: 11 tests
- **Total**: 12 tests

## Common Failure Pattern

Most tests are failing because:
- **rendered2 extracted JSON doesn't match expected JSON**

This suggests that when extracting JSON from the second render (with layout applied), there may be differences from the original input JSON. This could be due to:
1. Layout data affecting the extraction
2. Round-trip conversion differences
3. Test assertions being too strict

## Next Steps

1. Investigate why rendered2 extracted JSON differs from expected
2. Determine if differences are acceptable (layout-related) or need fixing
3. Update test assertions if needed to account for acceptable differences
4. Fix any actual bugs in the render/sync/extract cycle




















































