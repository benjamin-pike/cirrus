#!/bin/bash

# Allow bypassing the tests with the --no-verify flag
if [[ $1 == "--no-verify" ]]; then
    exit 0
fi

# Run tests
echo "Running tests..."
pytest
TEST_RESULT=$?

if [[ $TEST_RESULT -ne 0 ]]; then
    echo "Tests failed. Commit aborted."
    echo "To commit without running tests, use 'git commit --no-verify'."
    exit 1
else
    echo "All tests passed. Proceeding with commit."
    exit 0
fi
