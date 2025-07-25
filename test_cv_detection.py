#!/usr/bin/env python3
"""
Test Computer Vision Easy Apply Button Detection
Verifies that the CV system can load and process the Easy Apply button images
"""

import os
import sys

def test_cv_imports():
    """Test if computer vision libraries can be imported"""
    print("🧪 Testing Computer Vision Imports...")
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
        print(f"   Version: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
        print(f"   Version: {np.__version__}")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow imported successfully")
    except ImportError as e:
        print(f"❌ Pillow import failed: {e}")
        return False
    
    return True

def test_template_loading():
    """Test loading Easy Apply button templates"""
    print("\n🖼️ Testing Template Loading...")
    
    try:
        import cv2
        
        template_files = [
            "easy apply image1.png",
            "easy apply image2.webp"
        ]
        
        loaded_templates = 0
        
        for template_file in template_files:
            if os.path.exists(template_file):
                try:
                    # Load image
                    img = cv2.imread(template_file, cv2.IMREAD_COLOR)
                    
                    if img is not None:
                        # Convert to grayscale
                        gray_template = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        height, width = gray_template.shape
                        
                        print(f"✅ Loaded {template_file}")
                        print(f"   Dimensions: {width}x{height}")
                        print(f"   Data type: {gray_template.dtype}")
                        
                        loaded_templates += 1
                    else:
                        print(f"❌ Could not decode {template_file}")
                except Exception as e:
                    print(f"❌ Error loading {template_file}: {e}")
            else:
                print(f"⚠️ Template file not found: {template_file}")
        
        print(f"\n📊 Loaded {loaded_templates}/{len(template_files)} templates")
        return loaded_templates > 0
        
    except Exception as e:
        print(f"❌ Template loading test failed: {e}")
        return False

def test_linkedin_applier_integration():
    """Test integration with LinkedIn applier"""
    print("\n🔗 Testing LinkedIn Applier Integration...")
    
    try:
        # Import the main class
        from linkedin_job_applier import LinkedInJobApplier
        
        print("✅ LinkedInJobApplier class imported successfully")
        
        # Test profile loading
        if os.path.exists("user_profile.json"):
            try:
                applier = LinkedInJobApplier("user_profile.json")
                print("✅ User profile loaded successfully")
                
                # Test template loading
                template_count = len(applier.easy_apply_templates)
                print(f"✅ Loaded {template_count} Easy Apply templates")
                
                if template_count > 0:
                    print("✅ Computer vision system ready!")
                    return True
                else:
                    print("⚠️ No templates loaded - CV detection will be disabled")
                    return False
                    
            except Exception as e:
                print(f"❌ Error initializing applier: {e}")
                return False
        else:
            print("⚠️ user_profile.json not found")
            return False
            
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def main():
    print("🧪 Computer Vision Detection Test Suite")
    print("=" * 60)
    
    # Test 1: Import libraries
    imports_ok = test_cv_imports()
    
    # Test 2: Load templates
    templates_ok = test_template_loading()
    
    # Test 3: Integration test
    integration_ok = test_linkedin_applier_integration()
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    tests = [
        ("Computer Vision Imports", imports_ok),
        ("Template Loading", templates_ok),
        ("LinkedIn Applier Integration", integration_ok)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Computer vision system is ready.")
        print("\n🚀 You can now run the LinkedIn automation with CV detection:")
        print("   python linkedin_job_applier.py")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please fix issues before running automation.")
        
        if not imports_ok:
            print("\n💡 To fix import issues, run:")
            print("   python setup_cv_dependencies.py")
        
        if not templates_ok:
            print("\n💡 Make sure Easy Apply button images are in the current directory:")
            print("   - easy apply image1.png")
            print("   - easy apply image2.webp")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
