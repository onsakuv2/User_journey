#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

API_VERSION = "7.1"
DEFAULT_FIELDS = [
    "System.Id",
    "System.WorkItemType",
    "System.Title",
    "System.State",
    "System.Parent",
]


class AzureBoardsError(Exception):
    pass


@dataclass
class AzureContext:
    organization: str
    project: str
    pat: str


def normalize_title(title: str) -> str:
    return " ".join(title.strip().lower().split())


def build_auth_header(pat: str) -> str:
    token = base64.b64encode(f":{pat}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def resolve_context(args) -> AzureContext:
    organization = args.organization or os.getenv("AZURE_DEVOPS_ORG")
    project = args.project or os.getenv("AZURE_DEVOPS_PROJECT")
    pat = args.pat or os.getenv("AZURE_DEVOPS_PAT")

    missing = []
    if not organization:
        missing.append("organization")
    if not project:
        missing.append("project")
    if not pat:
        missing.append("pat")
    if missing:
        raise AzureBoardsError(
            "Missing Azure Boards settings: " + ", ".join(missing) + ". "
            "Provide flags or environment variables AZURE_DEVOPS_ORG, AZURE_DEVOPS_PROJECT, AZURE_DEVOPS_PAT."
        )

    return AzureContext(organization=organization.rstrip("/"), project=project, pat=pat)


def request_json(context: AzureContext, method: str, url: str, payload=None, content_type="application/json"):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8") if content_type == "application/json" else payload

    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Authorization", build_auth_header(context.pat))
    request.add_header("Accept", "application/json")
    if payload is not None:
        request.add_header("Content-Type", content_type)

    try:
        with urllib.request.urlopen(request) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise AzureBoardsError(f"HTTP {error.code} calling Azure Boards: {details}") from error
    except urllib.error.URLError as error:
        raise AzureBoardsError(f"Unable to reach Azure Boards: {error}") from error


def wiql_url(context: AzureContext) -> str:
    project = urllib.parse.quote(context.project, safe="")
    return f"{context.organization}/{project}/_apis/wit/wiql?api-version={API_VERSION}"


def work_items_url(context: AzureContext, ids) -> str:
    joined_ids = ",".join(str(item_id) for item_id in ids)
    fields = ",".join(DEFAULT_FIELDS)
    return (
        f"{context.organization}/_apis/wit/workitems?ids={joined_ids}"
        f"&fields={urllib.parse.quote(fields, safe=',')}&api-version={API_VERSION}"
    )


def work_item_type_url(context: AzureContext, work_item_type: str) -> str:
    project = urllib.parse.quote(context.project, safe="")
    item_type = urllib.parse.quote(work_item_type, safe="")
    return f"{context.organization}/{project}/_apis/wit/workitems/${item_type}?api-version={API_VERSION}"


def work_item_url(context: AzureContext, work_item_id: int) -> str:
    return f"{context.organization}/_apis/wit/workitems/{work_item_id}?api-version={API_VERSION}"


def query_work_items(context: AzureContext, wiql: str):
    result = request_json(context, "POST", wiql_url(context), {"query": wiql})
    ids = [item["id"] for item in result.get("workItems", [])]
    if not ids:
        return {"ids": [], "work_items": []}
    details = request_json(context, "GET", work_items_url(context, ids))
    return {"ids": ids, "work_items": details.get("value", [])}


def get_work_items(context: AzureContext, ids):
    if not ids:
        return {"work_items": []}
    details = request_json(context, "GET", work_items_url(context, ids))
    return {"work_items": details.get("value", [])}


def create_work_item(context: AzureContext, work_item_type: str, title: str, description: str | None = None):
    operations = [
        {"op": "add", "path": "/fields/System.Title", "value": title},
    ]
    if description:
        operations.append({"op": "add", "path": "/fields/System.Description", "value": description})
    return request_json(
        context,
        "POST",
        work_item_type_url(context, work_item_type),
        payload=json.dumps(operations).encode("utf-8"),
        content_type="application/json-patch+json",
    )


def link_child_to_parent(context: AzureContext, child_id: int, parent_id: int):
    payload = [
        {
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "System.LinkTypes.Hierarchy-Reverse",
                "url": work_item_url(context, parent_id),
            },
        }
    ]
    return request_json(
        context,
        "PATCH",
        work_item_url(context, child_id),
        payload=json.dumps(payload).encode("utf-8"),
        content_type="application/json-patch+json",
    )


def load_input(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_existing_index(work_items):
    index = {}
    for item in work_items:
        fields = item.get("fields", {})
        item_type = fields.get("System.WorkItemType")
        title = fields.get("System.Title")
        if item_type and title:
            index[(item_type, normalize_title(title))] = item
    return index


def collect_titles(items, titles=None):
    if titles is None:
        titles = []
    for item in items:
        titles.append((item["type"], item["title"]))
        collect_titles(item.get("children", []), titles)
    return titles


def plan_publish(existing_index, planned_items, parent_id=None, plan=None):
    if plan is None:
        plan = []

    for item in planned_items:
        key = (item["type"], normalize_title(item["title"]))
        existing = existing_index.get(key)
        action = {
            "type": item["type"],
            "title": item["title"],
            "parent_id": parent_id,
            "description": item.get("description"),
        }
        if existing:
            action["action"] = "reuse"
            action["id"] = existing["id"]
        else:
            action["action"] = "create"
        plan.append(action)

        next_parent_id = existing["id"] if existing else item["title"]
        plan_publish(existing_index, item.get("children", []), parent_id=next_parent_id, plan=plan)

    return plan


def materialize_publish_plan(context: AzureContext, plan):
    created = []
    reused = []
    linked = []
    title_to_id = {}

    for step in plan:
        if step["action"] == "reuse":
            reused.append({"id": step["id"], "title": step["title"], "type": step["type"]})
            title_to_id[step["title"]] = step["id"]
            continue

        created_item = create_work_item(context, step["type"], step["title"], step.get("description"))
        created_id = created_item["id"]
        created.append({"id": created_id, "title": step["title"], "type": step["type"]})
        title_to_id[step["title"]] = created_id

    for step in plan:
        if not step.get("parent_id"):
            continue

        child_id = step.get("id") or title_to_id.get(step["title"])
        if isinstance(step["parent_id"], int):
            parent_id = step["parent_id"]
        else:
            parent_id = title_to_id.get(step["parent_id"])

        if child_id and parent_id:
            link_child_to_parent(context, child_id, parent_id)
            linked.append({"child_id": child_id, "parent_id": parent_id})

    return {"created": created, "reused": reused, "linked": linked}


def command_query(args):
    context = resolve_context(args)
    query_text = args.wiql or Path(args.wiql_file).read_text(encoding="utf-8")
    return query_work_items(context, query_text)


def command_get(args):
    context = resolve_context(args)
    return get_work_items(context, args.ids)


def command_publish(args):
    context = resolve_context(args)
    payload = load_input(args.input)
    titles = collect_titles(payload.get("items", []))
    existing = query_work_items(
        context,
        f"SELECT [System.Id], [System.Title], [System.WorkItemType] FROM WorkItems "
        f"WHERE [System.TeamProject] = '{context.project}'"
    )
    existing_index = build_existing_index(existing.get("work_items", []))
    plan = plan_publish(existing_index, payload.get("items", []))

    result = {
        "requested_items": [{"type": item_type, "title": title} for item_type, title in titles],
        "plan": plan,
        "apply": args.apply,
    }
    if not args.apply:
        return result

    result["applied"] = materialize_publish_plan(context, plan)
    return result


def build_parser():
    parser = argparse.ArgumentParser(description="Read from and publish work items to Azure Boards.")
    parser.add_argument("--organization", help="Azure DevOps organization URL, e.g. https://dev.azure.com/my-org")
    parser.add_argument("--project", help="Azure DevOps project name")
    parser.add_argument("--pat", help="Azure DevOps personal access token")

    subparsers = parser.add_subparsers(dest="command", required=True)

    query_parser = subparsers.add_parser("query", help="Run a WIQL query and return matching work items")
    query_group = query_parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument("--wiql", help="WIQL query text")
    query_group.add_argument("--wiql-file", help="Path to a file containing WIQL")
    query_parser.set_defaults(func=command_query)

    get_parser = subparsers.add_parser("get", help="Fetch specific work items by ID")
    get_parser.add_argument("ids", nargs="+", type=int, help="Work item IDs to fetch")
    get_parser.set_defaults(func=command_get)

    publish_parser = subparsers.add_parser("publish", help="Create or reuse hierarchy from an input JSON file")
    publish_parser.add_argument("--input", required=True, help="Path to JSON input describing items and children")
    publish_parser.add_argument("--apply", action="store_true", help="Apply the publish plan instead of returning dry-run output")
    publish_parser.set_defaults(func=command_publish)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = args.func(args)
    except AzureBoardsError as error:
        print(json.dumps({"status": "error", "error": str(error)}, indent=2))
        return 1

    print(json.dumps({"status": "success", **result}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())