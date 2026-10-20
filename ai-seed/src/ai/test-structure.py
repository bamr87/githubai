#!/usr/bin/env python3
"""
AI Engine Structure Test - Validates AI/ML backend architecture
Path: Structure Validation → Component Check → Readiness Report
"""

import os
import sys
import json
from pathlib import Path

def validate_ai_structure():
    """Path: AI structure validation"""
    current_dir = Path(__file__).parent
    
    required_files = [
        'main.py',
        'requirements.txt'
    ]
    
    missing_files = []
    validation_score = 0
    
    for file_name in required_files:
        file_path = current_dir / file_name
        if file_path.exists():
            validation_score += 1
        else:
            missing_files.append(file_name)
    
    return {
        'score': validation_score,
        'total': len(required_files),
        'missing': missing_files,
        'is_ready': len(missing_files) == 0
    }

def validate_python_dependencies():
    """Path: Python dependencies validation"""
    requirements_path = Path(__file__).parent / 'requirements.txt'
    
    if not requirements_path.exists():
        return {'is_valid': False, 'reason': 'requirements.txt not found'}
    
    try:
        with open(requirements_path, 'r') as f:
            requirements = f.read().strip().split('\n')
        
        required_packages = ['flask', 'flask-cors']
        present_packages = [line.split('==')[0].split('>=')[0].strip() 
                          for line in requirements if line.strip()]
        
        missing_packages = [pkg for pkg in required_packages 
                          if pkg not in present_packages]
        
        return {
            'is_valid': len(missing_packages) == 0,
            'missing': missing_packages,
            'total_packages': len(present_packages),
            'packages': present_packages
        }
        
    except Exception as e:
        return {'is_valid': False, 'reason': f'Error reading requirements: {str(e)}'}

def validate_python_syntax():
    """Path: Python syntax validation"""
    current_dir = Path(__file__).parent
    main_py = current_dir / 'main.py'
    
    if not main_py.exists():
        return {'is_valid': False, 'reason': 'main.py not found'}
    
    try:
        with open(main_py, 'r') as f:
            code = f.read()
        
        # Basic syntax check by compiling
        compile(code, str(main_py), 'exec')
        return {'is_valid': True}
        
    except SyntaxError as e:
        return {'is_valid': False, 'reason': f'Syntax error: {str(e)}'}
    except Exception as e:
        return {'is_valid': False, 'reason': f'Validation error: {str(e)}'}

def main():
    """Path: Main validation execution"""
    print('🧠 AI-Seed AI Engine Structure Validation')
    print('==========================================')
    
    # Validate file structure
    structure_result = validate_ai_structure()
    print(f"📁 File Structure: {structure_result['score']}/{structure_result['total']} files present")
    
    if structure_result['missing']:
        print(f"❌ Missing files: {', '.join(structure_result['missing'])}")
    else:
        print('✅ All required files present')
    
    # Validate dependencies
    deps_result = validate_python_dependencies()
    if deps_result['is_valid']:
        print('✅ Dependencies correctly configured')
        print(f"✅ Total packages: {deps_result['total_packages']}")
        print(f"✅ Required packages: {', '.join(deps_result.get('packages', []))}")
    else:
        error_msg = deps_result.get('reason', f"Missing packages: {', '.join(deps_result.get('missing', []))}")
        print(f"❌ Dependencies issue: {error_msg}")
    
    # Validate Python syntax
    syntax_result = validate_python_syntax()
    if syntax_result['is_valid']:
        print('✅ Python syntax validation passed')
    else:
        print(f"❌ Python syntax issue: {syntax_result['reason']}")
    
    # Final readiness check
    is_ready = (structure_result['is_ready'] and 
                deps_result['is_valid'] and 
                syntax_result['is_valid'])
    
    print('')
    print(f"🚀 AI Engine Readiness: {'READY' if is_ready else 'NOT READY'}")
    
    if is_ready:
        print('✨ AI Engine structure validated and ready for container deployment!')
        print('AI engine structure validation ready')
    else:
        print('⚠️  Some components need attention before deployment')
        sys.exit(1)

if __name__ == '__main__':
    main()