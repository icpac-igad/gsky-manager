#!/bin/bash

{% for layer in layers %}
/ingest_data.sh {{ layer.shard_name }} {{ layer.container_full_path }}
{% endfor %}