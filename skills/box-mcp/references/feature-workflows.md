<!--
owner: Box Developer Relations
last_verified: 2026-09-15
assumptions: Hosted Box MCP tool catalog; runtime discovery is authoritative
sources:
  - https://developer.box.com/guides/box-mcp/tools/
-->

# Feature Workflows

Use runtime discovery and the current Box tool catalog for exact input schemas. Tool availability can differ by enterprise and client.

| Intent | Start with | Then |
| --- | --- | --- |
| Browse content | `list_folder_content_by_folder_id` | `get_file_details` or `get_folder_details` |
| Find content | `search_files_keyword`, `search_folders_by_name`, or `search_files_metadata` | confirm details and ID |
| Read a document | `get_file_details` | `get_file_content` or `get_file_preview` only as needed |
| Create or move content | relevant file/folder write tool | read destination and moved item |
| Work with metadata | `list_metadata_templates`, `get_metadata_template_schema` | metadata read/write tool exposed at runtime |
| Change access | `list_item_collaborations` | confirm audience and role, then collaboration/shared-link tool |
| Ask or extract with Box AI | single-file, multi-file, hub Q&A, or extract tool matching the request | validate sources and requested fields |
| Work with Hubs | `list_hubs`, `get_hub_details`, `get_hub_items` | confirmed hub write tool if needed |
| Generate documents | `list_docgen_templates`, `get_docgen_template_by_id` | confirm data and destination, then create the batch |

## Selection rules

- Search broadly only to identify candidates; retrieve content narrowly after the user or evidence selects the relevant items.
- Prefer standard extraction. Use an enhanced, higher-cost extraction tool only when requested or justified and confirmed.
- Treat shared links, collaborations, and hub membership as access-sensitive changes.
- For generated documents, validate template, input keys, output count, and destination before creating a batch.
- Temporary upload/download URL tools work only when the agent can perform the separate network transfer and required domains are allowed.
- When a documented tool is absent, follow [feature availability and entitlements](box-feature-availability-and-entitlements.md); do not substitute an invented name.

After any mutation, fetch the affected item, collaboration, hub, or batch and compare the observed state with the request.
