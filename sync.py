import requests
import os

# 环境变量
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
SOURCE_REPO = 'eooce/test'
TARGET_REPO = 'ansoncloud8/socks5-script'

# Headers for GitHub API
headers = {'Authorization': f'token {GITHUB_TOKEN}'}

# 获取源仓库的所有发布
releases_url = f'https://api.github.com/repos/{SOURCE_REPO}/releases'
response = requests.get(releases_url, headers=headers)
releases = response.json()

for release in releases:
    tag_name = release['tag_name']
    release_name = release['name']
    release_body = release['body']
    draft = release['draft']
    prerelease = release['prerelease']
    
    # 创建一个新的 release 在目标仓库
    create_release_url = f'https://api.github.com/repos/{TARGET_REPO}/releases'
    release_data = {
        'tag_name': tag_name,
        'name': release_name,
        'body': release_body,
        'draft': draft,
        'prerelease': prerelease
    }
    response = requests.post(create_release_url, json=release_data, headers=headers)
    new_release = response.json()
    
    # 上传资产到新的 release
    for asset in release['assets']:
        asset_url = asset['browser_download_url']
        asset_name = asset['name']
        
        # 下载资产
        asset_response = requests.get(asset_url, stream=True)
        asset_path = os.path.join('/tmp', asset_name)
        with open(asset_path, 'wb') as f:
            for chunk in asset_response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
        # 上传资产到新的 release
        upload_url = new_release['upload_url'].replace('{?name,label}', f'?name={asset_name}')
        with open(asset_path, 'rb') as f:
            headers.update({'Content-Type': 'application/octet-stream'})
            upload_response = requests.post(upload_url, headers=headers, data=f)
        
        # 删除下载的文件
        os.remove(asset_path)

# 同步标签
tags_url = f'https://api.github.com/repos/{SOURCE_REPO}/tags'
response = requests.get(tags_url, headers=headers)
tags = response.json()

for tag in tags:
    tag_name = tag['name']
    tag_sha = tag['commit']['sha']
    
    # 创建轻量级标签
    ref_url = f'https://api.github.com/repos/{TARGET_REPO}/git/refs'
    ref_data = {
        'ref': f'refs/tags/{tag_name}',
        'sha': tag_sha
    }
    response = requests.post(ref_url, json=ref_data, headers=headers)
