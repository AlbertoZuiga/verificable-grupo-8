def extract_common_fields(response, fields):
    result = {}
    for field in fields:
        try:
            result[field] = (
                response.data.split(f'name="{field}"'.encode())[1]
                .split(b'value="')[1]
                .split(b'"')[0]
                .decode()
            )
        except IndexError:
            result[field] = None
    return result
