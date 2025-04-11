# Automated Versioning with GitHub Actions

This repository includes a GitHub Actions workflow to automate the versioning of Python packages based on commit message tags. The workflow follows Semantic Versioning (SemVer) standards and uses `bumpversion` to manage version increments.

## How It Works

The GitHub Actions workflow is triggered on pushes to the `main` branch. It scans commit messages for specific tags to determine the type of version increment:

- `[major]`: Increments the major version.
- `[minor]`: Increments the minor version.
- `[patch]`: Increments the patch version (default if no tags are present).

The workflow then updates the version, commits the changes, tags the release in Git, and optionally publishes the new version to PyPI.

## Setup Instructions

### Prerequisites

- A GitHub repository with a Python project.
- GitHub Actions enabled for the repository.
- `bumpversion` installed in your Python environment.

### Step-by-Step Guide

1. **Create the Workflow File**:
   Add a new file named `versioning.yml` in the `.github/workflows/` directory of your repository with the following content:

   ```yaml
   name: Automated Versioning

   on:
     push:
       branches:
         - main

   jobs:
     versioning:
       runs-on: ubuntu-latest

       steps:
         - name: Checkout repository
           uses: actions/checkout@v2

         - name: Set up Python
           uses: actions/setup-python@v2
           with:
             python-version: '3.x'

         - name: Install dependencies
           run: |
             python -m pip install --upgrade pip
             pip install bumpversion

         - name: Determine version bump
           id: version-bump
           run: |
             if git log -1 --pretty=%B | grep -q '\[major\]'; then
               echo "::set-output name=version::major"
             elif git log -1 --pretty=%B | grep -q '\[minor\]'; then
               echo "::set-output name=version::minor"
             else
               echo "::set-output name=version::patch"
             fi

         - name: Bump version
           run: |
             bumpversion --current-version $(cat VERSION) ${{ steps.version-bump.outputs.version }}
             git push --follow-tags

         - name: Commit and push changes
           run: |
             git config --global user.name 'github-actions[bot]'
             git config --global user.email 'github-actions[bot]@users.noreply.github.com'
             git add .
             git commit -m "Bump version to $(cat VERSION)"
             git push

         - name: Create Git tag
           run: |
             git tag v$(cat VERSION)
             git push origin v$(cat VERSION)
   ```

2. **Configure `bumpversion`**:
   Ensure that `bumpversion` is configured in your project. Create a `.bumpversion.cfg` file in the root of your repository with the following content:

   ```ini
   [bumpversion]
   current_version = 0.1.0
   commit = True
   tag = True

   [bumpversion:file:VERSION]
   ```

3. **Add a `VERSION` File**:
   Create a `VERSION` file in the root of your repository and set the initial version:

   ```
   0.1.0
   ```

4. **Push Changes**:
   Commit and push the changes to your repository. The workflow will automatically trigger on pushes to the `main` branch and handle versioning based on commit message tags.

## Example Commit Messages

- To increment the major version:
  ```
  feat: Add new feature [major]
  ```

- To increment the minor version:
  ```
  feat: Add new feature [minor]
  ```

- To increment the patch version (default):
  ```
  fix: Fix a bug [patch]
  ```

## Conclusion

By following these instructions, you can automate the versioning of your Python packages using GitHub Actions and `bumpversion`. This will streamline your development workflow and ensure consistent version management based on Semantic Versioning standards.
