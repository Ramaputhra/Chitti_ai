import os
import ast
import json

def analyze_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content, filename=filepath)
    except Exception as e:
        return []

    classes = []
    
    # Very basic import extraction for the whole file
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            class_info = {
                "file": filepath,
                "name": node.name,
                "bases": [b.id for b in node.bases if isinstance(b, ast.Name)],
                "methods": [],
                "pass_count": 0,
                "not_implemented_count": 0,
                "todo_count": 0,
                "constant_returns": 0,
                "imports": imports
            }
            
            for item in node.body:
                if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                    class_info["methods"].append(item.name)
                    for stmt in ast.walk(item):
                        if isinstance(stmt, ast.Pass):
                            class_info["pass_count"] += 1
                        if isinstance(stmt, ast.Raise):
                            if isinstance(stmt.exc, ast.Name) and stmt.exc.id == 'NotImplementedError':
                                class_info["not_implemented_count"] += 1
                            elif isinstance(stmt.exc, ast.Call) and isinstance(stmt.exc.func, ast.Name) and stmt.exc.func.id == 'NotImplementedError':
                                class_info["not_implemented_count"] += 1
                        if isinstance(stmt, ast.Return):
                            if isinstance(stmt.value, ast.Constant):
                                class_info["constant_returns"] += 1
                            elif isinstance(stmt.value, ast.Dict) or isinstance(stmt.value, ast.List):
                                class_info["constant_returns"] += 1
                                
            class_info["todo_count"] = content.count("TODO")
            
            classes.append(class_info)
            
    return classes

def main():
    root_dir = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\desktop"
    all_classes = []
    
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith('.py'):
                filepath = os.path.join(dirpath, f)
                all_classes.extend(analyze_file(filepath))
                
    output_path = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\audit_facts.json"
    
    with open(output_path, 'w', encoding='utf-8') as out:
        json.dump(all_classes, out, indent=2)

if __name__ == "__main__":
    main()
