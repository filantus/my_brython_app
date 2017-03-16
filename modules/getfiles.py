import os
import json
import hashlib
import datetime

def md5_for_file(path, block_size=256*128):
    '''
    Block size directly depends on the block size of your filesystem
    to avoid performances issues
    Here I have blocks of 4096 octets (Default NTFS)
    '''
    md5 = hashlib.md5()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(block_size), b''):
             md5.update(chunk)

    return md5.hexdigest()


def get_file_stat(f, skip_md5=True):
    if os.path.exists(f):        
        metafile = {
            'name': f.rsplit('/', 1)[-1],
            'ext': os.path.splitext(f)[1][1:],
            'size': os.stat(f).st_size,
            'is_dir': os.path.isdir(f),
            'created': datetime.datetime.fromtimestamp(os.stat(f).st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            # 'md5': md5_for_file(f) if not skip_md5 else None,
        }

        return metafile
    else:
        print('%s - file not exists' % f)

def get_dir_files_data(path='./'):
    files_data = []
    for i in os.listdir(path):
        files_data.append(get_file_stat(path+'/'+i))
    return json.dumps(files_data)

def process_files(directory, func):
    for f in os.listdir(directory):
        path = directory+'/'+f

        if not os.path.isdir(path):
            func(path)
        else:
            process_files(path, func)