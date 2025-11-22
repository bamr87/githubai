#!/bin/bash

# Simulate version bumping locally

# Get current version
CURRENT_VERSION=$(cat VERSION)
echo "Current version: $CURRENT_VERSION"

# Check for version tag in the last commit message
COMMIT_MSG=$(git log -1 --pretty=%B)
echo "Last commit message: $COMMIT_MSG"

# Determine version bump type
if echo "$COMMIT_MSG" | grep -q '\[major\]'; then
  BUMP_TYPE="major"
elif echo "$COMMIT_MSG" | grep -q '\[minor\]'; then
  BUMP_TYPE="minor"
else
  BUMP_TYPE="patch"
fi

echo "Bump type: $BUMP_TYPE"

# Calculate new version
if [ "$BUMP_TYPE" == "major" ]; then
  MAJOR=$(echo $CURRENT_VERSION | cut -d. -f1)
  NEW_VERSION="$((MAJOR+1)).0.0"
elif [ "$BUMP_TYPE" == "minor" ]; then
  MAJOR=$(echo $CURRENT_VERSION | cut -d. -f1)
  MINOR=$(echo $CURRENT_VERSION | cut -d. -f2)
  NEW_VERSION="$MAJOR.$((MINOR+1)).0"
else
  MAJOR=$(echo $CURRENT_VERSION | cut -d. -f1)
  MINOR=$(echo $CURRENT_VERSION | cut -d. -f2)
  PATCH=$(echo $CURRENT_VERSION | cut -d. -f3)
  NEW_VERSION="$MAJOR.$MINOR.$((PATCH+1))"
fi

echo "New version would be: $NEW_VERSION"

# Update VERSION file (comment out to just preview)
# echo $NEW_VERSION > VERSION

# Update Python package version (comment out to just preview)
# sed -i "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" src/githubai/__init__.py

echo "To actually update the files, uncomment the last two commands in the script"
