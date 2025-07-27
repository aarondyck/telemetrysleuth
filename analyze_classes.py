import os
import ast
import astroid
import re

def extract_classes_and_references(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Use ast for more robust parsing
        try:
            module = ast.parse(content)
        except SyntaxError:
            print(f"Syntax error in {file_path}. Skipping detailed analysis.")
            return [], []
        
        # Find defined classes
        defined_classes = [
            node.name for node in ast.walk(module) 
            if isinstance(node, ast.ClassDef)
        ]
        
        # Find referenced classes (simple string-based approach)
        referenced_classes = re.findall(r'\b[A-Z][a-zA-Z0-9_]*\b', content)
        referenced_classes = list(set(referenced_classes) - set(defined_classes))
        
        return defined_classes, referenced_classes
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return [], []

def analyze_project(directory):
    project_analysis = {}
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                defined, referenced = extract_classes_and_references(file_path)
                
                if defined or referenced:
                    relative_path = os.path.relpath(file_path, directory)
                    project_analysis[relative_path] = {
                        'defined_classes': defined,
                        'referenced_classes': referenced
                    }
    
    return project_analysis

if __name__ == '__main__':
    analysis = analyze_project('.')
    
    with open('structure.MD', 'a', encoding='utf-8') as f:
        for file, data in analysis.items():
            f.write(f"\n### {file}\n")
            if data['defined_classes']:
                f.write("**Defined Classes:**\n")
                for cls in data['defined_classes']:
                    f.write(f"- {cls}\n")
            
            if data['referenced_classes']:
                f.write("**Referenced Classes:**\n")
                for cls in data['referenced_classes']:
                    f.write(f"- {cls}\n")
        
        # Analyze cross-referencing
        all_defined = set()
        all_referenced = set()
        for data in analysis.values():
            all_defined.update(data['defined_classes'])
            all_referenced.update(data['referenced_classes'])
        
        f.write("\n## Unresolved Class References\n")
        
        unreferenced_classes = all_defined - all_referenced
        if unreferenced_classes:
            f.write("### Defined but Not Referenced Classes:\n")
            for cls in unreferenced_classes:
                f.write(f"- {cls}\n")
        
        undefined_references = all_referenced - all_defined
        if undefined_references:
            f.write("### Referenced but Not Defined Classes:\n")
            for cls in undefined_references:
                f.write(f"- {cls}\n")