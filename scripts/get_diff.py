import os
import pathlib
import re
import json
import subprocess

# Folder containing Terraform files — override via TERRAFORM_PATH env var
TERRAFORM_FOLDER = os.environ.get("TERRAFORM_PATH", "infra/terraform/aws")

# Determine base ref: use GITHUB_BASE_REF in CI, fall back to main locally
base_branch = os.environ.get("GITHUB_BASE_REF", "main")
base_ref = f"origin/{base_branch}"

# Ensure the base ref exists (in case of shallow clone or local run)
subprocess.run(["git", "fetch", "origin", base_branch], capture_output=True)

print(f"Diffing against: {base_ref}")

# Parse resource blocks from Terraform content.
# Returns a dict of {resource_type: [list of full block strings]}
def parse_resource_blocks(content):
    blocks = {}
    # Match resource "aws_type" "name" { ... } — handles nested braces
    pattern = re.compile(r'resource\s+"(aws_[a-z0-9_]+)"\s+"([^"]+)"\s*\{', re.MULTILINE)
    for match in pattern.finditer(content):
        resource_type = match.group(1)
        start = match.start()
        # Walk forward to find the matching closing brace
        depth = 0
        i = content.index('{', start)
        while i < len(content):
            if content[i] == '{':
                depth += 1
            elif content[i] == '}':
                depth -= 1
                if depth == 0:
                    block = content[start:i+1]
                    blocks.setdefault(resource_type, []).append(block)
                    break
            i += 1
    return blocks

# Step 1: Get all changed files vs base branch
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

resources_added_or_modified = set()
resources_deleted = set()

for line in diff_result:
    parts = line.split("\t", 1)
    if len(parts) != 2:
        continue
    status, filepath = parts[0], parts[1]

    if status == "D":
        # File deleted — all resources in it are deleted
        result = subprocess.run(
            ["git", "show", f"{base_ref}:{filepath}"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            old_blocks = parse_resource_blocks(result.stdout)
            for rtype in old_blocks:
                resources_deleted.add(rtype)
                print(f"Deleted file {filepath}: {rtype}")
    else:
        path = pathlib.Path(filepath)
        if not path.exists():
            continue

        new_content = path.read_text()
        new_blocks = parse_resource_blocks(new_content)

        # Get old version from base ref
        old_result = subprocess.run(
            ["git", "show", f"{base_ref}:{filepath}"],
            capture_output=True, text=True
        )
        if old_result.returncode != 0:
            # File is new — all resources are added
            for rtype in new_blocks:
                resources_added_or_modified.add(rtype)
                print(f"New file {filepath}: {rtype}")
        else:
            old_blocks = parse_resource_blocks(old_result.stdout)

            # Resources in new but not in old (by type+content) = added/modified
            for rtype, new_block_list in new_blocks.items():
                old_block_list = old_blocks.get(rtype, [])
                # Normalize whitespace for comparison
                new_normalized = sorted(re.sub(r'\s+', ' ', b).strip() for b in new_block_list)
                old_normalized = sorted(re.sub(r'\s+', ' ', b).strip() for b in old_block_list)
                if new_normalized != old_normalized:
                    resources_added_or_modified.add(rtype)
                    print(f"Modified {filepath}: {rtype}")

            # Resources in old but not in new = deleted
            for rtype in old_blocks:
                if rtype not in new_blocks:
                    resources_deleted.add(rtype)
                    print(f"Removed from {filepath}: {rtype}")

# Untracked new files — all resources are new
for filepath in untracked:
    path = pathlib.Path(filepath)
    if path.exists():
        try:
            new_blocks = parse_resource_blocks(path.read_text())
            for rtype in new_blocks:
                resources_added_or_modified.add(rtype)
                print(f"Untracked {filepath}: {rtype}")
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
print("Parsed Terraform diff saved to diff.json")
