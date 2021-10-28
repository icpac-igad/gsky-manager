#!/bin/bash
{% for layer in layers %}
/ingest_data.sh {{ layer.shard_name }} {{ layer.container_full_path }} "*.{{layer.file_type}}" {% if layer.use_file_pattern %} "-conf {{layer.ruleset_path}}/{{layer.name}}.json" {% endif %}
{% endfor %}