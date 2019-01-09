#!/usr/bin/python
# (c) 2019, Whitney Champion <whitney.ellis.champion@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
module: graylog_streams
short_description: Communicate with the Graylog API to manage streams
description:
    - The Graylog streams module manages Graylog streams
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
      - Action to take against stream API.
    required: false
    default: list
    choices: [ create, create_rule, update, update_rule, delete, delete_rule, list, query_streams ]
  title:
    description:
      - Stream title.
    required: false
    default: None
  description:
    description:
      - Stream description.
    required: false
    default: None
  matching_type:
    description:
      - Matching type for the stream rules.
    required: false
    default: None
  remove_matches_from_default_stream:
    description:
      - Remove matches from default stream, true or false.
    required: false
    default: False
  stream_name:
    description:
      - Stream name to use with the query_streams action.
    required: false
    default: None
  field:
    description:
      - Field name for the stream rule to check.
    required: false
    default: None
  type:
    description:
      - Rule type for the stream rule: 1 (match exactly), 2 (match regular expression), 3 (greater than), 4 (smaller than), 5 (field presence), 6 (contain), 7 (always match).
    required: false
    default: None
  value:
    description:
      - Value to check rule against.
    required: false
    default: None
  inverted:
    description:
      - Invert rule (must not match value).
    required: false
    default: False
"""

EXAMPLES = '''
# List streams
- graylog_streams:
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"

# Get stream from stream name query_streams
- graylog_streams:
    action: query_streams
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    stream_name: "test_stream"
  register: stream

# List single stream by ID
- graylog_streams:
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    stream_id: "{{ stream.json.id }}"

# Create stream
- graylog_streams:
    action: create
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    title: "Client XYZ"
    description: "Windows and IIS logs"
    matching_type: "AND"
    remove_matches_from_default_stream: False
    rules:
      - "{\"field\":\"message\",\"type\":\"6\",\"value\":\"test\",\"inverted\":true,\"description\":\"testrule\"}"

# Update stream
- graylog_streams:
    action: update
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    stream_id: "{{ stream.json.id }}"
    remove_matches_from_default_stream: True

# Create stream rule
- graylog_streams:
    action: create_rule
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    stream_id: "{{ stream.json.id }}"
    description: "Windows Security Logs"
    field: "winlogbeat_log_name"
    type: "1"
    value: "Security"
    inverted: False

# Update stream rule
- graylog_streams:
    action: update_rule
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    stream_id: "{{ stream.json.id }}"
    rule_id: "{{ rule.json.id }}"
    description: "Windows Security and Application Logs"

# Delete stream rule
- graylog_streams:
    action: delete_rule
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    stream_id: "{{ stream.json.id }}"
    rule_id: "{{ rule.json.id }}"

# Delete stream
- graylog_streams:
    action: delete
    endpoint: "graylog.mydomain.com"
    graylog_user: "username"
    graylog_password: "password"
    stream_id: "{{ stream.json.id }}"
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

def create(module,base_url,api_token,title,description,remove_matches_from_default_stream,matching_type,rules,default_index_set_id):

    headers = '{ "Content-Type": "application/json", "X-Requested-By": "Graylog API", "Accept": "application/json", "Authorization": "Basic %s" }' % (api_token)

    url = base_url

    payload = {}

    if title is not None:
        payload['title'] = title
    if description is not None:
        payload['description'] = description
    if remove_matches_from_default_stream is not None:
        payload['remove_matches_from_default_stream'] = remove_matches_from_default_stream
    if matching_type is not None:
        payload['matching_type'] = matching_type
    if rules is not None:
        payload['rules'] = rules
    if default_index_set_id is not "":
        payload['index_set_id'] = default_index_set_id

    response, info = fetch_url(module=module, url=url, headers=json.loads(headers), method='POST', data=module.jsonify(payload))

    if info['status'] != 201:
        module.fail_json(msg="Fail: %s" % (info['msg']))

    try:
        content = response.read()
    except AttributeError:
        content = info.pop('body', '')

    return info['status'], info['msg'], content, url

def create_rule(module,base_url,api_token,stream_id,field,type,value,inverted,description):

    headers = '{ "Content-Type": "application/json", "X-Requested-By": "Graylog API", "Accept": "application/json", "Authorization": "Basic %s" }' % (api_token)

    url = base_url+"/%s/rules" % (stream_id)

    payload = {}

    if field is not None:
        payload['field'] = field
    if type is not None:
        payload['type'] = type
    if value is not None:
        payload['value'] = value
    if inverted is not None:
        payload['inverted'] = inverted
    if description is not None:
        payload['description'] = description

    response, info = fetch_url(module=module, url=url, headers=json.loads(headers), method='POST', data=module.jsonify(payload))

    if info['status'] != 201:
        module.fail_json(msg="Fail: %s" % (info['msg']))

    try:
        content = response.read()
    except AttributeError:
        content = info.pop('body', '')

    return info['status'], info['msg'], content, url

def update(module,base_url,api_token,stream_id,title,description,remove_matches_from_default_stream,matching_type,rules):

    headers = '{ "Content-Type": "application/json", "X-Requested-By": "Graylog API", "Accept": "application/json", "Authorization": "Basic %s" }' % (api_token)

    url = base_url+"/%s" % (stream_id)

    payload = {}

    if title is not None:
        payload['title'] = title
    if description is not None:
        payload['description'] = description
    if remove_matches_from_default_stream is not None:
        payload['remove_matches_from_default_stream'] = remove_matches_from_default_stream
    if matching_type is not None:
        payload['matching_type'] = matching_type
    if rules is not None:
        payload['rules'] = rules

    response, info = fetch_url(module=module, url=url, headers=json.loads(headers), method='PUT', data=module.jsonify(payload))

    if info['status'] != 200:
        module.fail_json(msg="Fail: %s" % (info['msg']))

    try:
        content = response.read()
    except AttributeError:
        content = info.pop('body', '')

    return info['status'], info['msg'], content, url

def update_rule(module,base_url,api_token,stream_id,rule_id,field,type,value,inverted,description):

    headers = '{ "Content-Type": "application/json", "X-Requested-By": "Graylog API", "Accept": "application/json", "Authorization": "Basic %s" }' % (api_token)

    url = base_url+"/%s/rules/%s" % (stream_id,rule_id)

    payload = {}

    if field is not None:
        payload['field'] = field
    if type is not None:
        payload['type'] = type
    if value is not None:
        payload['value'] = value
    if inverted is not None:
        payload['inverted'] = inverted
    if description is not None:
        payload['description'] = description

    response, info = fetch_url(module=module, url=url, headers=json.loads(headers), method='PUT', data=module.jsonify(payload))

    if info['status'] != 200:
        module.fail_json(msg="Fail: %s" % (info['msg']))

    try:
        content = response.read()
    except AttributeError:
        content = info.pop('body', '')

    return info['status'], info['msg'], content, url

def delete(module,base_url,api_token,stream_id):

    headers = '{ "Content-Type": "application/json", "X-Requested-By": "Graylog API", "Accept": "application/json", "Authorization": "Basic %s" }' % (api_token)

    url = base_url+"/%s" % (stream_id)

    response, info = fetch_url(module=module, url=url, headers=json.loads(headers), method='DELETE')

    if info['status'] != 204:
        module.fail_json(msg="Fail: %s" % (info['msg']))

    try:
        content = response.read()
    except AttributeError:
        content = info.pop('body', '')

    return info['status'], info['msg'], content, url

def delete_rule(module,base_url,api_token,stream_id,rule_id):

    headers = '{ "Content-Type": "application/json", "X-Requested-By": "Graylog API", "Accept": "application/json", "Authorization": "Basic %s" }' % (api_token)

    url = base_url+"/%s/rules/%s" % (stream_id,rule_id)

    response, info = fetch_url(module=module, url=url, headers=json.loads(headers), method='DELETE')

    if info['status'] != 204:
        module.fail_json(msg="Fail: %s" % (info['msg']))

    try:
        content = response.read()
    except AttributeError:
        content = info.pop('body', '')

    return info['status'], info['msg'], content, url

def list(module,base_url,api_token,stream_id):

    headers = '{ "Content-Type": "application/json", "X-Requested-By": "Graylog API", "Accept": "application/json", "Authorization": "Basic %s" }' % (api_token)

    if stream_id is not None:
        url = base_url+"/%s" % (stream_id)
    else:
        url = base_url

    response, info = fetch_url(module=module, url=url, headers=json.loads(headers), method='GET')

    if info['status'] != 200:
        module.fail_json(msg="Fail: %s" % (info['msg']))

    try:
        content = response.read()
    except AttributeError:
        content = info.pop('body', '')

    return info['status'], info['msg'], content, url

def query_streams(module,base_url,api_token,stream_name):

    headers = '{ "Content-Type": "application/json", "X-Requested-By": "Graylog API", "Accept": "application/json", "Authorization": "Basic %s" }' % (api_token)

    url = base_url

    response, info = fetch_url(module=module, url=url, headers=json.loads(headers), method='GET')

    if info['status'] != 200:
        module.fail_json(msg="Fail: %s" % (info['msg']))

    try:
        content = response.read()
        streams = json.loads(content)
    except AttributeError:
        content = info.pop('body', '')

    stream_id = ""
    if streams is not None:

        i = 0
        while i < len(streams['streams']):
            stream = streams['streams'][i]
            if stream_name == stream['title']:
                 stream_id = stream['id']
                 break
            i += 1

    return stream_id

def default_index_set(module,endpoint,base_url,api_token):

    headers = '{ "Content-Type": "application/json", "X-Requested-By": "Graylog API", "Accept": "application/json", "Authorization": "Basic %s" }' % (api_token)

    url = "https://%s/api/system/indices/index_sets?skip=0&limit=0&stats=false" % (endpoint)

    response, info = fetch_url(module=module, url=url, headers=json.loads(headers), method='GET')

    if info['status'] != 200:
        module.fail_json(msg="Fail: %s" % (info['msg']))

    try:
        content = response.read()
        indices = json.loads(content)
    except AttributeError:
        content = info.pop('body', '')

    default_index_set_id = ""
    if indices is not None:
        default_index_set_id = indices['index_sets'][0]['id']

    return default_index_set_id

def get_token(module,endpoint,username,password):

    headers = '{ "Content-Type": "application/json", "X-Requested-By": "Graylog API", "Accept": "application/json" }'

    url = "https://%s/api/system/sessions" % (endpoint)

    payload = {}
    payload['username'] = username
    payload['password'] = password
    payload['host'] = endpoint

    response, info = fetch_url(module=module, url=url, headers=json.loads(headers), method='POST', data=module.jsonify(payload))

    if info['status'] != 200:
        module.fail_json(msg="Fail: %s" % (info['msg']))

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
            action         = dict(type='str', required=False, default='list', choices=['create', 'create_rule', 'update', 'update_rule', 'delete', 'delete_rule', 'list', 'query_streams']),
            stream_id     = dict(type='str', default=None),
            stream_name     = dict(type='str', default=None),
            rule_id     = dict(type='str', default=None),
            title     = dict(type='str', default=None),
            field     = dict(type='str', default=None),
            type     = dict(type='int', default=1),
            value     = dict(type='str', default=None),
            inverted     = dict(type='bool', default=False),
            description       = dict(type='str', default=None),
            remove_matches_from_default_stream       = dict(type='bool', default=False),
            matching_type       = dict(type='str', default=None),
            rules       = dict(type='list', default=None)
        )
    )

    endpoint = module.params['endpoint']
    graylog_user = module.params['graylog_user']
    graylog_password = module.params['graylog_password']
    action = module.params['action']
    stream_id = module.params['stream_id']
    stream_name = module.params['stream_name']
    rule_id = module.params['rule_id']
    title = module.params['title']
    field = module.params['field']
    type = module.params['type']
    value = module.params['value']
    inverted = module.params['inverted']
    description = module.params['description']
    remove_matches_from_default_stream = module.params['remove_matches_from_default_stream']
    matching_type = module.params['matching_type']
    rules = module.params['rules']

    base_url = "https://%s/api/streams" % (endpoint)

    api_token = get_token(module,endpoint,graylog_user,graylog_password)

    if action == "create":
        default_index_set_id = default_index_set(module,endpoint,base_url,api_token)
        status, message, content, url = create(module,base_url,api_token,title,description,remove_matches_from_default_stream,matching_type,rules,default_index_set_id)
    elif action == "create_rule":
        status, message, content, url = create_rule(module,base_url,api_token,stream_id,field,type,value,inverted,description)
    elif action == "update":
        status, message, content, url = update(module,base_url,api_token,stream_id,title,description,remove_matches_from_default_stream,matching_type,rules)
    elif action == "update_rule":
        status, message, content, url = update_rule(module,base_url,api_token,stream_id,rule_id,field,type,value,inverted,description)
    elif action == "delete":
        status, message, content, url = delete(module,base_url,api_token,stream_id)
    elif action == "delete_rule":
        status, message, content, url = delete_rule(module,base_url,api_token,stream_id,rule_id)
    elif action == "list":
        status, message, content, url = list(module,base_url,api_token,stream_id)
    elif action == "query_streams":
        stream_id = query_streams(module,base_url,api_token,stream_name)
        status, message, content, url = list(module,base_url,api_token,stream_id)

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
import base64
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()
