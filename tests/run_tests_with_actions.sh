#!/bin/bash
# File: run_tests_with_actions.sh

# Create logs directory if it doesn't exist
mkdir -p test_logs

# Get the next log file number
NEXT_NUM=1
if ls test_logs/test-output-*.txt 1> /dev/null 2>&1; then
    LAST_FILE=$(ls -1 test_logs/test-output-*.txt | sort -V | tail -n 1)
    LAST_NUM=$(echo $LAST_FILE | grep -o '[0-9]\+' | tail -n 1)
    NEXT_NUM=$((LAST_NUM + 1))
fi

# Output file
OUTPUT_FILE="test_logs/test-output-${NEXT_NUM}.txt"

# Run tests and capture output
{
    echo "# Test run $NEXT_NUM - $(date)"
    echo "# Command: $@"
    echo ""
    
    # Run the actual test command
    $@
    
    echo ""
    echo "# End of test run $NEXT_NUM - $(date)"
} 2>&1 | tee "$OUTPUT_FILE"

echo "Test output saved to $OUTPUT_FILE"

# Generate action items
python generate_action_items.py
echo "Action items generated in test_action_items.md"

# Optional: Display action items
echo ""
echo "=== ACTION ITEMS SUMMARY ==="
grep "^###" test_action_items.md
# Display the action items file
cat test_action_items.md
