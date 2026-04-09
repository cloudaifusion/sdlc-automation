import os
import pathlib
import re
import json
import subprocess

# Folder containing Terraform files
TERRAFORM_FOLDER = "infra/terraform/aws"

# Determine base ref: use GITHUB_BASE_REF in CI, fall back to main locally
base_branch = os.environ.get("GITHUB_BASE_REF", "main")
base_ref = f"origin/{base_branch}"

# Ensure the base ref exists (in case of shallow clone or local run)
subprocess.run(["git", "fetch", "origin", base_branch], capture_output=True)

print(f"Diffing against: {base_ref}")

# Step 1: Get all changed files vs base branch (catches staged, unstaged, deleted)
diff_result = subprocess.run(
    ["git", "diff", "--name-status", base_ref, "--", TERRAFORM_FOLDER],
    capture_output=True,
    text=True
).stdout.splitlines()

# Also pick up untracked new files not yet staged
untracked = subprocess.run(
    ["git", "ls-files", "--others", "--exclude-standard", TERRAFORM_FOLDER],
    capture_output=True,
    text=True
).stdout.splitlines()

# Step 2: Parse each file for aws_* resources (high-level only)
resource_pattern = re.compile(r'aws_[a-z_]+')
resources_added_or_modified = set()
resources_deleted = set()

for line in diff_result:
    parts = line.split("\t", 1)
    if len(parts) != 2:
        continue
    status, filepath = parts[0], parts[1]

    if status == "D":
        # Read content from base ref since the file may no longer exist on disk
        result = subprocess.run(
            ["git", "show", f"{base_ref}:{filepath}"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            found = resource_pattern.findall(result.stdout)
            if found:
                resources_deleted.update(found)
                print(f"Deleted {filepath}: {found}")
    else:
        path = pathlib.Path(filepath)
        if path.exists():
            try:
                text = path.read_text()
                found = resource_pattern.findall(text)
                if found:
                    resources_added_or_modified.update(found)
                    print(f"Modified/added {filepath}: {found}")
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

for filepath in untracked:
    path = pathlib.Path(filepath)
    if path.exists():
        try:
            text = path.read_text()
            found = resource_pattern.findall(text)
            if found:
                resources_added_or_modified.update(found)
                print(f"Untracked {filepath}: {found}")
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

print(f"Added/modified resources: {resources_added_or_modified}")
print(f"Deleted resources: {resources_deleted}")

# Step 3: Save to JSON
output = {
    "resources_added_or_modified": list(resources_added_or_modified),
    "resources_deleted": list(resources_deleted),
}
pathlib.Path("diff.json").write_text(json.dumps(output, indent=2))
print("Parsed high-level Terraform diff saved to diff.json")