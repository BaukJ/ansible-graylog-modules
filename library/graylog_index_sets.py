#!/usr/bin/python
# (c) 2019, Whitney Champion <whitney.ellis.champion@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
module: graylog_index_set_sets
short_description: Communicate with the Graylog API to manage index sets
description:
    - The Graylog index sets module manages Graylog index sets
version_added: "1.0"
author: "Whitney Champion (@shortstack)"
options:
  endpoint:
    description:
      - Graylog endoint. (i.e. graylog.mydomain.com).
    required: false
    default: None
  graylog_user:
    description:
      - Graylog privileged user username.
    required: false
    default: None
  graylog_password:
    description:
      - Graylog privileged user password.
    required: false
    default: None
  action:
    description:
      - Action to take against index API.
    required: false
    default: list
    choices: [ create, update, list, delete, query_index_sets ]
  id:
    description:
      - Index id.
    required: false
    default: None
  title:
    description:
      - Title.
    required: false
    default: None
  description:
    description:
      - Description.
    required: false
    default: None
  index_prefix:
    description:
      - A unique prefix used in Elasticsearch indices belonging to this index set. The prefix must start with a letter or number, and can only contain letters, numbers, '_', '-' and '+'.
    required: false
    default: None
  index_analyzer:
    description:
      - Elasticsearch analyzer for this index set.
    required: false
    default: "standard"
  shards:
    description:
      - Number of Elasticsearch shards used per index in this index set.
    required: false
    default: 4
  replicas:
    description:
      - Number of Elasticsearch replicas used per index in this index set.
    required: false
    default: 1
  rotation_strategy_class:
    description:
      - Rotation strategy class, ex: org.graylog2.indexer.rotation.strategies.TimeBasedRotationStrategy
    required: false
    default: "org.graylog2.indexer.rotation.strategies.TimeBasedRotationStrategy"
  retention_strategy_class:
    description:
      - Retention strategy class, ex: org.graylog2.indexer.retention.strategies.DeletionRetentionStrategy
    required: false
    default: "org.graylog2.indexer.retention.strategies.DeletionRetentionStrategy"
  rotation_strategy:
    description:
      - Graylog uses multiple indices to store documents in. You can configure the strategy it uses to determine when to rotate the currently active write index. ex: { "type": "org.graylog2.indexer.rotation.strategies.TimeBasedRotationStrategyConfig", "rotation_period": "P1D" }
    required: false
    default: dict(type='org.graylog2.indexer.rotation.strategies.TimeBasedRotationStrategyConfig', rotation_period='P1D')
  retention_strategy:
    description:
      - Graylog uses a retention strategy to clean up old indices. ex: { "type": "org.graylog2.indexer.rotation.strategies.DeletionRetentionStrategyConfig", "max_number_of_indices": "14" }
    required: false
    default: dict(type='org.graylog2.indexer.retention.strategies.DeletionRetentionStrategyConfig', max_number_of_indices=14)
  index_optimization_max_num_segments:
    description:
      - Maximum number of segments per Elasticsearch index after optimization (force merge).
    required: false
    default: 1
  index_optimization_disabled:
    description:
      - Disable Elasticsearch index optimization (force merge) after rotation.
    required: false
    default: False
  writable:
    description:
      - Writable, true or false.
    required: false
    default: True
  default:
    description:
      - Default index set, true or false.
    required: false
    default: False

"""

EXAMPLES = '''
# List index sets
- graylog_index_sets:
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"

# Create index rule
- graylog_index_sets:
    action: create_rule
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    title: "test_rule"
    description: "test"
    source: |
      rule "test_rule_domain_threat_intel"
      when
         has_field("dns_query")
      then
         let dns_query_intel = threat_intel_lookup_domain(to_string($message.dns_query), "dns_query");
         set_fields(dns_query_intel);
      end

'''

RETURN = r'''
json:
  description: The JSON response from the Graylog API
  returned: always
  type: complex
msg:
  description: The HTTP message from the request
  returned: always
  type: str
  sample: OK (unknown bytes)
status:
  description: The HTTP status code from the request
  returned: always
  type: int
  sample: 200
url:
  description: The actual URL used for the request
  returned: always
  type: str
  sample: https://www.ansible.com/
'''

def create(module,base_url,api_token,title,description,index_prefix,index_analyzer,shards,replicas,rotation_strategy_class,retention_strategy_class,rotation_strategy,retention_strategy,index_optimization_max_num_segments,index_optimization_disabled,creation_date,writable,default):

    headers = '{ "Content-Type": "application/json", "X-Requested-By": "Graylog API", "Accept": "application/json", "Authorization": "Basic %s" }' % (api_token)

    url = base_url

    payload = {}

    if title is not None:
        payload['title'] = title
    if description is not None:
        payload['description'] = description
    if index_prefix is not None:
        payload['index_prefix'] = index_prefix
    if creation_date is not None:
        payload['creation_date'] = creation_date
    if writable is not None:
        payload['writable'] = writable
    if default is not None:
        payload['default'] = default
    if index_analyzer is not None:
        payload['index_analyzer'] = index_analyzer
    if shards is not None:
        payload['shards'] = shards
    if replicas is not None:
        payload['replicas'] = replicas
    if rotation_strategy_class is not None:
        payload['rotation_strategy_class'] = rotation_strategy_class
    if retention_strategy_class is not None:
        payload['retention_strategy_class'] = retention_strategy_class
    if rotation_strategy is not None:
        payload['rotation_strategy'] = rotation_strategy
    if retention_strategy is not None:
        payload['retention_strategy'] = retention_strategy
    if index_optimization_max_num_segments is not None:
        payload['index_optimization_max_num_segments'] = index_optimization_max_num_segments
    if index_optimization_disabled is not None:
        payload['index_optimization_disabled'] = index_optimization_disabled

    response, info = fetch_url(module=module, url=url, headers=json.loads(headers), method='POST', data=module.jsonify(payload))

    if info['status'] != 200:
        module.fail_json(msg="Fail: %s" % ( "Status: "+str(info['msg']) + ", Message: " + str(info['body'])))

    try:
        content = response.read()
    except AttributeError:
        content = info.pop('body', '')

    return info['status'], info['msg'], content, url

def update(module,base_url,api_token,index_set_id,title,description,index_prefix,index_analyzer,shards,replicas,rotation_strategy_class,retention_strategy_class,rotation_strategy,retention_strategy,index_optimization_max_num_segments,index_optimization_disabled,writable,default):

    headers = '{ "Content-Type": "application/json", "X-Requested-By": "Graylog API", "Accept": "application/json", "Authorization": "Basic %s" }' % (api_token)

    url = base_url+"/%s" % (index_set_id)

    payload = {}

    if title is not None:
        payload['title'] = title
    if description is not None:
        payload['description'] = description
    if index_prefix is not None:
        payload['index_prefix'] = index_prefix
    if writable is not None:
        payload['writable'] = writable
    if default is not None:
        payload['default'] = default
    if index_analyzer is not None:
        payload['index_analyzer'] = index_analyzer
    if shards is not None:
        payload['shards'] = shards
    if replicas is not None:
        payload['replicas'] = replicas
    if rotation_strategy_class is not None:
        payload['rotation_strategy_class'] = rotation_strategy_class
    if retention_strategy_class is not None:
        payload['retention_strategy_class'] = retention_strategy_class
    if rotation_strategy is not None:
        payload['rotation_strategy'] = rotation_strategy
    if retention_strategy is not None:
        payload['retention_strategy'] = retention_strategy
    if index_optimization_max_num_segments is not None:
        payload['index_optimization_max_num_segments'] = index_optimization_max_num_segments
    if index_optimization_disabled is not None:
        payload['index_optimization_disabled'] = index_optimization_disabled

    response, info = fetch_url(module=module, url=url, headers=json.loads(headers), method='PUT', data=module.jsonify(payload))

    if info['status'] != 200:
        module.fail_json(msg="Fail: %s" % ( "Status: "+str(info['msg']) + ", Message: " + str(info['body'])))

    try:
        content = response.read()
    except AttributeError:
        content = info.pop('body', '')

    return info['status'], info['msg'], content, url

def delete(module,base_url,api_token,index_set_id):

    headers = '{ "Content-Type": "application/json", "X-Requested-By": "Graylog API", "Accept": "application/json", "Authorization": "Basic %s" }' % (api_token)

    url = base_url+"/%s" % (index_set_id)

    response, info = fetch_url(module=module, url=url, headers=json.loads(headers), method='DELETE')

    if info['status'] != 204:
        module.fail_json(msg="Fail: %s" % ( "Status: "+str(info['msg']) + ", Message: " + str(info['body'])))

    try:
        content = response.read()
    except AttributeError:
        content = info.pop('body', '')

    return info['status'], info['msg'], content, url

def list(module,base_url,api_token,index_set_id):

    headers = '{ "Content-Type": "application/json", "X-Requested-By": "Graylog API", "Accept": "application/json", "Authorization": "Basic %s" }' % (api_token)

    if index_set_id is not None:
        url = base_url+"/%s" % (index_set_id)
    else:
        url = base_url

    response, info = fetch_url(module=module, url=url, headers=json.loads(headers), method='GET')

    if info['status'] != 200:
        module.fail_json(msg="Fail: %s" % ( "Status: "+str(info['msg']) + ", Message: " + str(info['body'])))

    try:
        content = response.read()
    except AttributeError:
        content = info.pop('body', '')

    return info['status'], info['msg'], content, url

def query_index_sets(module,base_url,api_token,title):

    headers = '{ "Content-Type": "application/json", "X-Requested-By": "Graylog API", "Accept": "application/json", "Authorization": "Basic %s" }' % (api_token)

    url = base_url

    response, info = fetch_url(module=module, url=url, headers=json.loads(headers), method='GET')

    if info['status'] != 200:
        module.fail_json(msg="Fail: %s" % ( "Status: "+str(info['msg']) + ", Message: " + str(info['body'])))

    try:
        content = response.read()
        index_sets = json.loads(content)
    except AttributeError:
        content = info.pop('body', '')

    index_set_id = ""
    if index_sets is not None:

        i = 0
        while i < len(index_sets['index_sets']):
            index_set = index_sets['index_sets'][i]
            if title == index_set['title']:
                 index_set_id = index_set['id']
                 break
            i += 1

    return index_set_id

def get_token(module,endpoint,username,password):

    headers = '{ "Content-Type": "application/json", "X-Requested-By": "Graylog API", "Accept": "application/json" }'

    url = "https://%s/api/system/sessions" % (endpoint)

    payload = {}
    payload['username'] = username
    payload['password'] = password
    payload['host'] = endpoint

    response, info = fetch_url(module=module, url=url, headers=json.loads(headers), method='POST', data=module.jsonify(payload))

    if info['status'] != 200:
        module.fail_json(msg="Fail: %s" % ( "Status: "+str(info['msg']) + ", Message: " + str(info['body'])))

    try:
        content = response.read()
        session = json.loads(content)
    except AttributeError:
        content = info.pop('body', '')

    session_token = base64.b64encode(session['session_id']+":session")

    return session_token

def main():
    module = AnsibleModule(
        argument_spec = dict(
            endpoint      = dict(type='str', default=None),
            graylog_user       = dict(type='str', default=None),
            graylog_password       = dict(type='str', no_log=True),
            action         = dict(type='str', required=False, default='list', choices=['create', 'update', 'delete', 'list', 'query_index_sets']),
            title     = dict(type='str', default=None),
            description     = dict(type='str', default=None),
            index_set_id     = dict(type='str', default=None),
            index_prefix     = dict(type='str', default=None),
            index_analyzer     = dict(type='str', default="standard"),
            shards     = dict(type='int', default=4),
            replicas     = dict(type='int', default=1),
            rotation_strategy_class     = dict(type='str', default='org.graylog2.indexer.rotation.strategies.TimeBasedRotationStrategy'),
            retention_strategy_class     = dict(type='str', default='org.graylog2.indexer.retention.strategies.DeletionRetentionStrategy'),
            rotation_strategy     = dict(type='dict', default=dict(type='org.graylog2.indexer.rotation.strategies.TimeBasedRotationStrategyConfig', rotation_period='P1D')),
            retention_strategy     = dict(type='dict', default=dict(type='org.graylog2.indexer.retention.strategies.DeletionRetentionStrategyConfig', max_number_of_indices=14)),
            index_optimization_max_num_segments     = dict(type='int', default=1),
            index_optimization_disabled     = dict(type='bool', default=False),
            writable     = dict(type='bool', default=True),
            default     = dict(type='bool', default=False)
        )
    )

    endpoint = module.params['endpoint']
    graylog_user = module.params['graylog_user']
    graylog_password = module.params['graylog_password']
    action = module.params['action']
    title = module.params['title']
    index_set_id = module.params['index_set_id']
    description = module.params['description']
    index_prefix = module.params['index_prefix']
    index_analyzer = module.params['index_analyzer']
    shards = module.params['shards']
    replicas = module.params['replicas']
    rotation_strategy_class = module.params['rotation_strategy_class']
    retention_strategy_class = module.params['retention_strategy_class']
    rotation_strategy = module.params['rotation_strategy']
    retention_strategy = module.params['retention_strategy']
    index_optimization_max_num_segments = module.params['index_optimization_max_num_segments']
    index_optimization_disabled = module.params['index_optimization_disabled']
    writable = module.params['writable']
    default = module.params['default']
    creation_date = datetime.datetime.utcnow().isoformat() + 'Z'

    base_url = "https://%s/api/system/indices/index_sets" % (endpoint)

    api_token = get_token(module,endpoint,graylog_user,graylog_password)

    if action == "create":
        status, message, content, url = create(module,base_url,api_token,title,description,index_prefix,index_analyzer,shards,replicas,rotation_strategy_class,retention_strategy_class,rotation_strategy,retention_strategy,index_optimization_max_num_segments,index_optimization_disabled,creation_date,writable,default)
    elif action == "update":
        status, message, content, url = update(module,base_url,api_token,index_set_id,title,description,index_prefix,index_analyzer,shards,replicas,rotation_strategy_class,retention_strategy_class,rotation_strategy,retention_strategy,index_optimization_max_num_segments,index_optimization_disabled,writable,default)
    elif action == "delete":
        status, message, content, url = delete(module,base_url,api_token,index_set_id)
    elif action == "list":
        status, message, content, url = list(module,base_url,api_token,index_set_id)
    elif action == "query_index_sets":
        index_set_id = query_index_sets(module,base_url,api_token,title)
        status, message, content, url = list(module,base_url,api_token,index_set_id)

    uresp = {}
    content = to_text(content, encoding='UTF-8')

    try:
        js = json.loads(content)
    except ValueError, e:
        js = ""

    uresp['json'] = js
    uresp['status'] = status
    uresp['msg'] = message
    uresp['url'] = url

    module.exit_json(**uresp)

# import module snippets
import json
import datetime
import base64
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()
