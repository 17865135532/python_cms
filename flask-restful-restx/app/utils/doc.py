import logging


logger = logging.getLogger(__name__)


def gen_document_from_jsonschema(schema, name='', depth=0):
    description = schema.get('description') or schema.get('title') or ''
    text = ''
    if name:
        text += f'{name}: '
    info = []
    schema_type = schema.get('type')
    if not schema_type:
        raise ValueError(f'type is required:{name}({schema})')
    info.append(schema_type)
    if description:
        info.append(description)
    if schema.get('is_required'):
        info.append('不可为空')
    text += '，'.join(info)
    required = schema.get("required", [])
    if schema_type == 'object':
        depth += 1
        if schema.get('anyOf', []):
            for idx, item in enumerate(schema['anyOf']):
                _name = name
                item['description'] = f'第{idx+1}种格式 {item.get("description", "")}'
                item['required'] = item.get('required', [])
                item['required'].extend(required)
                item['type'] = item.get('type') or schema_type
                text += f'\n' + depth * '\t' + gen_document_from_jsonschema(item, name=_name, depth=depth+1)
            return text
        for _property, _schema in schema.get('properties', {}).items():
            try:
                _schema['is_required'] = _schema.get('is_required') or _property in required
                _name = f'{name}.{_property}' if name else _property
                text += '\n' + depth*'\t' + gen_document_from_jsonschema(_schema, name=_name, depth=depth)
            except Exception as e:
                logger.error(f"schema error: {e.args}")
        return text
    elif schema_type == 'array':
        if schema.get('minItems') is not None:
            text += f'，元素个数不少于{schema["minItems"]}'
        if schema.get('maxItems') is not None:
            text += f'，元素个数不多于{schema["maxItems"]}'
        depth += 1
        items = schema.get('items')
        if isinstance(items, dict):
            _name = f'{name}[]'
            items['required'] = items.get('required', [])
            items['required'].extend(required)
            text += '\n' + depth * '\t' + gen_document_from_jsonschema(items, name=_name, depth=depth)
        elif isinstance(items, list):
            if schema.get("additionalItems") is False:
                text += '，不含额外元素'
            for idx, _schema in enumerate(items):
                _name = f'{name}[{idx}]'
                _schema['required'] = _schema.get('required', [])
                _schema['required'].extend(required)
                text += '\n' + depth * '\t' + gen_document_from_jsonschema(_schema, name=_name, depth=depth)
            if isinstance(schema.get("additionalItems"), dict):
                _schema = schema['additionalItems']
                _name = f'{name}[]'
                _schema['required'] = _schema.get('required', [])
                _schema['required'].extend(required)
                text += '\n' + depth * '\t' + gen_document_from_jsonschema(_schema, name=_name, depth=depth)
        else:
            raise TypeError(type(items))
        return text
    elif schema_type == 'string':
        pattern = schema.get('pattern')
        if pattern is not None:
            text += f'，格式为{pattern}'
        if schema.get('is_date') is True:
            text += f'，格式为日期yyyy-MM-dd'
        if schema.get('is_number') is True:
            text += f'，数值型字符串'
        if schema.get('max_bytes_len') is not None:
            text += f'，最大字节长度为{schema["max_bytes_len"]}'
        if schema.get('format') == "date-time":
            text += f'，格式为日期时间yyyy-MM-ddTHH:mm:ssZ'
        return text
    else:
        if schema.get("min") is not None:
            text += f'，最小值{schema["min"]}'
        if schema.get("max") is not None:
            text += f'，最大值{schema["max"]}'
        return text
