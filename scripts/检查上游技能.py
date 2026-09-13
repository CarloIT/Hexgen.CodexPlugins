#!/usr/bin/env python3
"""只读核验本地快照并检查 Grill Me 上游变化；0=一致，2=有更新，1=失败。"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import quote
from urllib.request import Request, urlopen


PLUGIN_ROOT = Path(__file__).resolve().parents[1] / 'plugins/hexgen-productivity'
REPOSITORY = 'https://github.com/mattpocock/skills'
API = 'https://api.github.com/repos/mattpocock/skills'
DIRECTORIES = ['skills/productivity/grill-me/', 'skills/productivity/grilling/']


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def blob_sha1(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def read_local(plugin_root, relative):
    path = PurePosixPath(relative)
    if path.is_absolute() or '..' in path.parts or '\\' in relative or ':' in relative:
        raise ValueError(f'非法本地相对路径：{relative}')
    target = (plugin_root / relative).resolve()
    if not target.is_relative_to(plugin_root.resolve()):
        raise ValueError(f'本地路径越界：{relative}')
    return target.read_bytes()


def validate_local(plugin_root, lock):
    if lock.get('schemaVersion') != 1 or lock.get('repository') != REPOSITORY:
        raise ValueError('不支持的来源记录或仓库。')
    if lock.get('directories') != DIRECTORIES:
        raise ValueError('跟踪目录与已审核范围不一致。')
    if not re.fullmatch(r'[0-9a-f]{40}', lock.get('commit', '')):
        raise ValueError('采用的 commit 必须为完整 SHA。')
    files = lock['files']
    paths = [entry['upstreamPath'] for entry in files]
    locals_ = [entry['localPath'] for entry in files]
    if len(paths) != len(set(paths)) or len(locals_) != len(set(locals_)):
        raise ValueError('来源记录存在重复文件。')
    required = {directory + 'SKILL.md' for directory in DIRECTORIES} | {'LICENSE'}
    if not required.issubset(paths):
        raise ValueError('缺少入口、追问规则或许可证的来源记录。')
    for entry in files:
        path = entry['upstreamPath']
        if path != 'LICENSE' and not any(path.startswith(prefix) for prefix in DIRECTORIES):
            raise ValueError(f'上游文件不属于跟踪范围：{path}')
        data = read_local(plugin_root, entry['localPath'])
        if sha256(data) != entry['sha256'] or blob_sha1(data) != entry['gitBlobSha1']:
            raise ValueError(f'本地上游快照已改变：{entry["localPath"]}')
    single = lock['single']
    if single['localPath'] != 'skills/grill-me-single/SKILL.md':
        raise ValueError('Single 来源记录指向了其它文件。')
    if sha256(read_local(plugin_root, single['localPath'])) != single['sha256']:
        raise ValueError('Grill Me Single 与已记录的固定版本不一致。')


def fetch_json(url):
    request = Request(url, headers={'User-Agent': 'Hexgen-CodexPlugins', 'Accept': 'application/vnd.github+json'})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def check_upstream(lock, ref, fetch=fetch_json):
    head = fetch(f'{API}/commits/{quote(ref, safe="")}')
    commit = head['sha']
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('GitHub 返回了无效 commit。')
    # 固定解析后的 commit，避免 main 在两次请求间变化。
    tree = fetch(f'{API}/git/trees/{commit}?recursive=1')
    if tree.get('truncated') is not False:
        raise ValueError('GitHub 文件树不完整，不能判断为无更新。')
    remote = {}
    for entry in tree['tree']:
        path = entry['path']
        if path != 'LICENSE' and not any(path.startswith(prefix) for prefix in DIRECTORIES):
            continue
        if entry['type'] == 'tree':
            continue
        if entry['type'] != 'blob' or entry.get('mode') not in ('100644', '100755'):
            raise ValueError(f'上游出现需人工审查的文件类型：{path}')
        remote[path] = entry['sha']
    local = {entry['upstreamPath']: entry['gitBlobSha1'] for entry in lock['files']}
    changes = []
    for path in sorted(local.keys() | remote.keys()):
        if path not in local:
            status = 'added'
        elif path not in remote:
            status = 'removed'
        elif local[path] != remote[path]:
            status = 'modified'
        else:
            continue
        changes.append({'path': path, 'status': status})
    return {
        'status': 'update_available' if changes else 'up_to_date',
        'adoptedCommit': lock['commit'], 'checkedCommit': commit, 'ref': ref,
        'changes': changes,
        'compareUrl': f'{REPOSITORY}/compare/{lock["commit"]}...{commit}',
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true', help='只核验本地快照和 Single，不联网')
    parser.add_argument('--ref', help='检查指定上游分支、标签或 commit；默认使用来源记录的 ref')
    parser.add_argument('--json', action='store_true', help='输出 JSON，供其它工具消费')
    args = parser.parse_args(argv)
    try:
        lock = json.loads((PLUGIN_ROOT / '上游来源.json').read_text(encoding='utf-8'))
        validate_local(PLUGIN_ROOT, lock)
        result = {'status': 'local_verified', 'adoptedCommit': lock['commit']}
        if not args.offline:
            result = check_upstream(lock, args.ref or lock['ref'])
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.offline:
            print('PASS: 上游快照与固定 Single 均匹配来源记录。未检查远程更新。')
        else:
            print(f'{result["status"]}: {result["checkedCommit"]}')
            for change in result['changes']:
                print(f'  {change["status"]}: {change["path"]}')
            print(result['compareUrl'])
        return 2 if result['status'] == 'update_available' else 0
    except Exception as error:
        if args.json:
            print(json.dumps({'status': 'error', 'message': str(error)}, ensure_ascii=False))
        else:
            print(f'FAIL: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
