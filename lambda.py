import boto3
import os

print('Loading virus scanner function.')

bucket = 'ic-storage-' + os.environ['ENV_NAME']
s3 = boto3.client('s3')
db = boto3.client('dynamodb')
secret = '58B312z8F-c5aTd7e'
# version 3!!!


def lambda_handler(event, context):
    print('Let the virus scan commence! Launching InfiniCrate Advanced AI Defense')
    count = 0
    prefixes = ['dev/', 'crate/']
    for prefix in prefixes:
        for key in s3.list_objects(Bucket=bucket, Prefix=prefix)['Contents']:
            object_key = key['Key']
            if object_key.endswith('/'):
                continue
            try:
                print("Scanning {} for viruses with InfiniCrate Advanced AI Defense...".format(object_key))
                count += ai_virus_scan(object_key, s3.get_object(Bucket=bucket, Key=object_key))
            except UnicodeDecodeError as e:
                print(e)
                print('error, not utf8 encoded potential virus found')
                write_encoded_file_entry(object_key, get_object_owner(object_key))
            except Exception as e:
                print(e)
                print('Error scanning object {} from {} for viruses.'.format(object_key, bucket))

    if count > 0:
        return 'Successfully found {} viruses!'.format(count)
    return 'Superb! No viruses found!'


def get_object_owner(key):
    tag_set = s3.get_object_tagging(Bucket=bucket, Key=key)['TagSet']
    for tag in tag_set:
        if tag['Key'] == 'username':
            return tag['Value']

    return 'unknown'

def get_lines(filename, object):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', 'pdf')):
        return []
    else:
        return object['Body'].read().decode("utf-8").splitlines()

def ai_virus_scan(filename, object):
    lines = get_lines(filename, object)
    keywords = ['virus', 'вирус', 'evil', 'hack', 'illegal', 'very illegal', 'bad boi', 'evil doer', 'OR 1=1', '×0Ë×YV', secret]
    username = get_object_owner(filename)

    line_number = 1
    count = 0
    for line in lines:
        if any(map(line.__contains__, keywords)):
            print('Found a virus in {}. Saving...'.format(filename))
            write_plaintext_entry(filename, line, line_number, username)
            count += 1

        line_number += 1

    if count > 0:
        write_file_entry(filename, count, username, line_number-1)

    return count


def write_plaintext_entry(filename, line, line_number, username):
    item = {
        'filename': {'S': filename + ':' + str(line_number)},
        'bucket': {'S': bucket},
        'username': {'S': username},
        'line': {'S': line},
        'line_number': {'N': str(line_number)},
        'type': {'S': 'line text'}
    }
    write_to_db(item)


def write_file_entry(filename, count, username, total_lines):
    virus_percent = count / total_lines
    item = {
        'filename': {'S': filename},
        'bucket': {'S': bucket},
        'username': {'S': username},
        'virus_count': {'N': str(count)},
        'line_count': {'N': str(total_lines)},
        'virus_per_line': {'N': str(virus_percent)},
        'type': {'S': 'percentage'}
    }
    write_to_db(item)



def write_encoded_file_entry(filename, username):
    item = {
        'filename': {'S': filename},
        'bucket': {'S': bucket},
        'username': {'S': username},
        'virus_count': {'N': str(1)},
        'line_count': {'N': str(1)},
        'virus_per_line': {'N': str(1)},
        'type': {'S': 'percentage'}
    }
    write_to_db(item)

def write_to_db(item):
    table_name = 'ic-analytics-' + os.environ['ENV_NAME']
    try:
        db.put_item(TableName=table_name, Item=item)
        print('db updated')
    except Exception as e:
        print(e)
        print('Error writing object {} to db {}.'.format(item, table_name))  # 58B312z8F-c5aTd7e
        raise e

