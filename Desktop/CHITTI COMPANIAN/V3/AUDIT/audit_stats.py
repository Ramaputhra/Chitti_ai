import os
from collections import defaultdict
import json

def audit_repo(path):
    stats = {
        'total_files': 0,
        'extensions': defaultdict(int),
        'directories': [],
        'tests': 0,
        'docs': 0
    }
    
    for root, dirs, files in os.walk(path):
        if '.venv' in root or '.git' in root or '__pycache__' in root or 'chitti_companion.egg-info' in root:
            continue
        
        rel_root = os.path.relpath(root, path)
        if rel_root != '.':
            stats['directories'].append(rel_root)
            
        for file in files:
            stats['total_files'] += 1
            ext = os.path.splitext(file)[1].lower()
            stats['extensions'][ext] += 1
            
            if 'test' in file.lower() or 'test' in root.lower():
                stats['tests'] += 1
            if ext in ['.md', '.txt'] or 'doc' in root.lower():
                stats['docs'] += 1
                
    return stats

if __name__ == '__main__':
    path = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3"
    stats = audit_repo(path)
    print(json.dumps(stats, indent=2))
