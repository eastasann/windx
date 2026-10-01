#!/usr/bin/env python3
"""Sync Issue labels and state into GitHub Projects (v2) fields.

Implements DD-0001 Implementation Plan #10 (decisions DP-5 and DP-6), and is written to be
independent of who owns the project — see ADR-0004.

    python3 scripts/project_sync.py --self-test          # offline: validate the mapping logic
    python3 scripts/project_sync.py --dry-run            # print what would change
    python3 scripts/project_sync.py --issue 12           # sync one Issue
    python3 scripts/project_sync.py --pr 34              # sync the Issues a PR closes
    python3 scripts/project_sync.py --issue 12 --event labeled

Configuration (environment, usually repository variables):
    PROJECT_OWNER        the user or organisation login that owns the project
    PROJECT_OWNER_TYPE   "user" or "organization"
    PROJECT_NUMBER       the number in the project URL
    GITHUB_REPOSITORY    "owner/repo" (set automatically inside Actions)
    PROJECTS_TOKEN       the credential (see below)

Why not GITHUB_TOKEN: it cannot operate on Projects v2 for either ownership type. The
`repository-projects` entry under a workflow's `permissions:` key applies to classic
projects only. Supply PROJECTS_TOKEN instead:

    organisation-owned  a GitHub App installation token
                        (organisation "Projects: read and write"; repository Projects
                        permission is not sufficient) -- GitHub's recommendation
    user-owned          a classic PAT with the `project` scope
                        (a fine-grained PAT cannot obtain Projects permission for a
                        personal account)

The full matrix and sources are in DD-0001 Appendix A-3.
No third-party dependencies: GraphQL goes over urllib.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

GRAPHQL_URL = "https://api.github.com/graphql"
OWNER_TYPES = ("user", "organization")

# A label maps to a Status value. The first match in this order wins, so that a more
# advanced state is not overwritten by a label left behind from an earlier stage.
LABEL_TO_STATUS = [
    ("agent/wip", "In Progress"),
    ("agent/ready", "Ready"),
    ("agent/blocked", "Inbox"),
    ("stage/g3-release", "In Review"),
    ("stage/g2-build", "In Progress"),
    ("stage/g1-design", "Designing"),
    ("stage/g0-problem", "Triaged"),
]

STAGE_TO_FIELD = {
    "stage/g0-problem": "G0",
    "stage/g1-design": "G1",
    "stage/g2-build": "G2",
    "stage/g3-release": "G3",
}

SIZE_TO_FIELD = {
    "size/xs": "XS", "size/s": "S", "size/m": "M", "size/l": "L", "size/xl": "XL",
}


class ConfigError(RuntimeError):
    pass


# --- Pure mapping logic (no network; covered by --self-test) -----------------

def status_for(labels: list[str], *, state: str, state_reason: str | None,
               has_open_pr: bool) -> str:
    """Decide the Status field value for an Issue."""
    if state == "closed":
        return "Dropped" if (state_reason or "").lower() == "not_planned" else "Done"
    if has_open_pr:
        return "In Review"
    for label, status in LABEL_TO_STATUS:
        if label in labels:
            return status
    return "Inbox"


def fields_for(labels: list[str]) -> dict[str, str]:
    """Decide the single-select field values derived purely from labels."""
    fields: dict[str, str] = {}
    for label in labels:
        if label in STAGE_TO_FIELD:
            fields["Stage"] = STAGE_TO_FIELD[label]
        if label in SIZE_TO_FIELD:
            fields["Size"] = SIZE_TO_FIELD[label]
    return fields


def project_query(owner_type: str) -> str:
    """The lookup query. This is the only place ownership type matters (ADR-0004)."""
    if owner_type not in OWNER_TYPES:
        raise ConfigError(
            f"PROJECT_OWNER_TYPE must be one of {OWNER_TYPES}; got {owner_type!r}"
        )
    return """
    query($owner: String!, $number: Int!) {
      %s(login: $owner) {
        projectV2(number: $number) {
          id
          title
          fields(first: 50) {
            nodes {
              ... on ProjectV2SingleSelectField {
                id name options { id name }
              }
              ... on ProjectV2FieldCommon { id name }
            }
          }
        }
      }
    }
    """ % owner_type


def owner_root(owner_type: str) -> str:
    return owner_type


# --- GraphQL plumbing -------------------------------------------------------

def graphql(token: str, query: str, variables: dict) -> dict:
    payload = json.dumps({"query": query, "variables": variables}).encode()
    request = urllib.request.Request(
        GRAPHQL_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "windx-project-sync",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"GraphQL HTTP {exc.code}: {detail}") from exc
    if body.get("errors"):
        messages = "; ".join(e.get("message", "?") for e in body["errors"])
        if "Resource not accessible by integration" in messages:
            messages += (
                "\n  PROJECTS_TOKEN lacks Projects write permission. For an organisation"
                " project the GitHub App needs organisation 'Projects: read and write';"
                " for a user project use a classic PAT with the 'project' scope."
                " See DD-0001 Appendix A-3."
            )
        raise RuntimeError(f"GraphQL error: {messages}")
    return body["data"]


ISSUE_QUERY = """
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    issue(number: $number) {
      id
      title
      state
      stateReason
      labels(first: 50) { nodes { name } }
      closedByPullRequestsReferences(first: 10, includeClosedPrs: false) {
        nodes { state }
      }
    }
  }
}
"""

PR_QUERY = """
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      number
      closingIssuesReferences(first: 10) { nodes { number } }
    }
  }
}
"""

ADD_ITEM = """
mutation($project: ID!, $content: ID!) {
  addProjectV2ItemById(input: {projectId: $project, contentId: $content}) {
    item { id }
  }
}
"""

SET_SELECT = """
mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $project, itemId: $item, fieldId: $field,
    value: {singleSelectOptionId: $option}
  }) { projectV2Item { id } }
}
"""


def resolve_option(field: dict, value: str) -> str:
    for option in field.get("options", []):
        if option["name"].lower() == value.lower():
            return option["id"]
    available = ", ".join(o["name"] for o in field.get("options", []))
    raise RuntimeError(
        f"field {field['name']!r} has no option {value!r} (available: {available}). "
        "Add it in the Project UI -- see docs/process/09-setup-checklist.md"
    )


# --- Self-test (offline) ----------------------------------------------------

def self_test() -> int:
    """Validate the mapping and query construction without touching the network."""
    checks: list[tuple[str, bool]] = []

    checks.append(("closed -> Done",
                   status_for([], state="closed", state_reason="completed", has_open_pr=False) == "Done"))
    checks.append(("closed not_planned -> Dropped",
                   status_for([], state="closed", state_reason="not_planned", has_open_pr=False) == "Dropped"))
    checks.append(("open PR wins over labels",
                   status_for(["agent/ready"], state="open", state_reason=None, has_open_pr=True) == "In Review"))
    checks.append(("agent/ready -> Ready",
                   status_for(["agent/ready"], state="open", state_reason=None, has_open_pr=False) == "Ready"))
    checks.append(("agent/wip beats agent/ready",
                   status_for(["agent/ready", "agent/wip"], state="open", state_reason=None,
                              has_open_pr=False) == "In Progress"))
    checks.append(("no labels -> Inbox",
                   status_for([], state="open", state_reason=None, has_open_pr=False) == "Inbox"))
    checks.append(("stage/g1 -> Designing",
                   status_for(["stage/g1-design"], state="open", state_reason=None,
                              has_open_pr=False) == "Designing"))
    checks.append(("stage and size map to fields",
                   fields_for(["stage/g2-build", "size/m", "type/task"]) == {"Stage": "G2", "Size": "M"}))
    checks.append(("no mappable labels -> no fields", fields_for(["type/bug"]) == {}))

    for owner_type in OWNER_TYPES:
        query = project_query(owner_type)
        checks.append((f"{owner_type} query names the right root",
                       f"{owner_type}(login: $owner)" in query and "projectV2(number: $number)" in query))

    try:
        project_query("team")
        checks.append(("an invalid owner type is rejected", False))
    except ConfigError:
        checks.append(("an invalid owner type is rejected", True))

    # The PR path must ask for the Issues a PR closes, so a PR event can set "In Review".
    checks.append(("the PR query requests closingIssuesReferences",
                   "closingIssuesReferences" in PR_QUERY and "pullRequest(number: $number)" in PR_QUERY))
    checks.append(("the Issue query asks only for open linked PRs",
                   "includeClosedPrs: false" in ISSUE_QUERY))

    # Every Status value the mapping can produce must be a documented option.
    documented = {"Inbox", "Triaged", "Designing", "Ready", "In Progress", "In Review", "Done", "Dropped"}
    produced = {status for _, status in LABEL_TO_STATUS} | {"Inbox", "In Review", "Done", "Dropped"}
    checks.append(("every produced Status is a documented option", produced <= documented))

    failed = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    print(f"\nself-test: {len(checks) - len(failed)}/{len(checks)} passed")
    if failed:
        return 1
    print("OK")
    return 0


# --- Main -------------------------------------------------------------------

def require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConfigError(
            f"{name} is not set. See docs/process/09-setup-checklist.md section 2-3."
        )
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--issue", type=int, default=None, help="the Issue number to sync")
    parser.add_argument("--pr", type=int, default=None,
                        help="a PR number; syncs every Issue it closes")
    parser.add_argument("--event", default=None, help="the triggering event name (logged only)")
    parser.add_argument("--dry-run", action="store_true", help="resolve and print, but do not mutate")
    parser.add_argument("--self-test", action="store_true", help="validate the mapping offline")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    try:
        owner_type = require("PROJECT_OWNER_TYPE").lower()
        project_owner = require("PROJECT_OWNER")
        project_number = int(require("PROJECT_NUMBER"))
        query = project_query(owner_type)
    except ConfigError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    except ValueError:
        print("ERROR PROJECT_NUMBER must be an integer", file=sys.stderr)
        return 2

    if args.issue is None and args.pr is None:
        print("ERROR one of --issue or --pr is required (or use --self-test)", file=sys.stderr)
        return 2
    if args.issue is not None and args.pr is not None:
        print("ERROR pass either --issue or --pr, not both", file=sys.stderr)
        return 2

    target = f"issue #{args.issue}" if args.issue is not None else f"pr #{args.pr}"
    if args.dry_run and not os.environ.get("PROJECTS_TOKEN"):
        print(f"project: {owner_type}/{project_owner} #{project_number}")
        print(f"target:  {target}" + (f" (event: {args.event})" if args.event else ""))
        print("PROJECTS_TOKEN is unset, so nothing was resolved against the API.")
        print("The mapping logic is covered by --self-test.")
        return 0

    try:
        token = require("PROJECTS_TOKEN")
        repo_full = require("GITHUB_REPOSITORY")
    except ConfigError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    repo_owner, _, repo_name = repo_full.partition("/")

    data = graphql(token, query, {"owner": project_owner, "number": project_number})
    project = (data.get(owner_root(owner_type)) or {}).get("projectV2")
    if not project:
        print(
            f"ERROR project #{project_number} not found under {owner_type} {project_owner!r}. "
            "Check PROJECT_OWNER_TYPE -- a user-owned project is not visible via the "
            "organization root, and vice versa.",
            file=sys.stderr,
        )
        return 1
    fields = {f["name"]: f for f in project["fields"]["nodes"] if f.get("name")}

    if args.pr is not None:
        pr_data = graphql(token, PR_QUERY,
                          {"owner": repo_owner, "repo": repo_name, "number": args.pr})
        pull = (pr_data.get("repository") or {}).get("pullRequest")
        if not pull:
            print(f"ERROR pull request #{args.pr} not found in {repo_full}", file=sys.stderr)
            return 1
        numbers = [n["number"] for n in pull["closingIssuesReferences"]["nodes"]]
        if not numbers:
            print(f"pr #{args.pr} closes no Issue; nothing to sync.")
            return 0
        print(f"pr #{args.pr} closes: {', '.join('#' + str(n) for n in numbers)}")
    else:
        numbers = [args.issue]

    failures = 0
    for number in numbers:
        try:
            sync_issue(token, project, fields, repo_owner, repo_name, number,
                       owner_type, project_owner, project_number, args)
        except (RuntimeError, ConfigError) as exc:
            print(f"ERROR issue #{number}: {exc}", file=sys.stderr)
            failures += 1
    if failures:
        return 1
    print("OK")
    return 0


def sync_issue(token, project, fields, repo_owner, repo_name, number,
               owner_type, project_owner, project_number, args) -> None:
    """Resolve one Issue's desired field values and apply them."""
    issue_data = graphql(token, ISSUE_QUERY,
                         {"owner": repo_owner, "repo": repo_name, "number": number})
    issue = (issue_data.get("repository") or {}).get("issue")
    if not issue:
        raise RuntimeError(f"issue #{number} not found in {repo_owner}/{repo_name}")

    labels = [n["name"] for n in issue["labels"]["nodes"]]
    has_open_pr = any(
        n["state"] == "OPEN" for n in issue["closedByPullRequestsReferences"]["nodes"]
    )
    desired = {"Status": status_for(labels, state=issue["state"].lower(),
                                   state_reason=issue.get("stateReason"),
                                   has_open_pr=has_open_pr)}
    desired.update(fields_for(labels))

    print(f"project: {project['title']} ({owner_type}/{project_owner} #{project_number})")
    print(f"issue:   #{number} {issue['title']!r}" + (f" (event: {args.event})" if args.event else ""))
    print(f"labels:  {', '.join(labels) or '(none)'}")
    for name, value in desired.items():
        print(f"  {name} -> {value}")

    if args.dry_run:
        print("  --dry-run: nothing was changed.")
        return

    item_id = graphql(token, ADD_ITEM,
                      {"project": project["id"], "content": issue["id"]})[
        "addProjectV2ItemById"]["item"]["id"]

    for name, value in desired.items():
        field = fields.get(name)
        if field is None:
            print(f"  skip {name}: the project has no such field "
                  "(see docs/process/09-setup-checklist.md section 2-1)")
            continue
        if "options" not in field:
            print(f"  skip {name}: not a single-select field")
            continue
        graphql(token, SET_SELECT, {
            "project": project["id"], "item": item_id,
            "field": field["id"], "option": resolve_option(field, value),
        })
        print(f"  set {name} = {value}")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, ConfigError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        sys.exit(1)
