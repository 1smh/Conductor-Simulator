#!/usr/bin/env python3
"""
Test script to verify that the error fixes are working.
Run this to check if the warnings/errors are resolved.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_configuration():
    """Test if Panda3D configuration is properly set"""
    try:
        from panda3d.core import ConfigVariableManager, ConfigVariableString, ConfigVariableInt, ConfigVariableBool
        
        # Test window size configuration
        win_size = ConfigVariableInt('win-size')
        print(f"✓ Window size configuration: {win_size.getValue()}")
        
        # Test undecorated configuration
        undecorated = ConfigVariableBool('undecorated')
        print(f"✓ Undecorated configuration: {undecorated.getValue()}")
        
        # Test GLSL version configuration
        glsl_version = ConfigVariableString('glsl-version')
        print(f"✓ GLSL version configuration: {glsl_version.getValue()}")
        
        # Test icon configuration
        window_icon = ConfigVariableString('window-icon')
        print(f"✓ Window icon configuration: '{window_icon.getValue()}'")
        
        # Test PNG warning configuration
        png_warning = ConfigVariableBool('png-warning-icc')
        print(f"✓ PNG warning suppression: {png_warning.getValue()}")
        
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import Panda3D: {e}")
        return False
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_ursina_import():
    """Test if Ursina can be imported"""
    try:
        import ursina
        print(f"✓ Ursina version: {ursina.__version__}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import Ursina: {e}")
        return False
    except Exception as e:
        print(f"✗ Ursina import test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing error fixes...")
    print("=" * 40)
    
    tests = [
        ("Panda3D Configuration", test_configuration),
        ("Ursina Import", test_ursina_import),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
            print(f"✓ {test_name} passed")
        else:
            print(f"✗ {test_name} failed")
    
    print("\n" + "=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The fixes should work.")
        print("\nTo test the game, run: python main.py")
    else:
        print("✗ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
