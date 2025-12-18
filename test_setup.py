import sys
from pathlib import Path

def check_imports():
    """Check if all imports work."""
    print("Checking imports...")
    try:
        from dnd.core.config import Settings
        from dnd.core.models import GameState, Character, NPC
        # core runtime aliases (refactored public API)
        from dnd.core.engine import AegisEngine
        from dnd.core.memory import VaultManager
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def check_config():
    """Check configuration."""
    print("\nChecking configuration...")
    try:
        from dnd.core.config import Config
        Config.ensure_directories()
        print(f"✓ Log directory: {Config.LOG_DIR}")
        print(f"✓ Session DB: {Config.SESSION_DB}")
        
        try:
            Config.validate()
            print("✓ Configuration valid (API key set)")
        except ValueError as e:
            print(f"⚠ Configuration warning: {e}")
            print("  (This is okay if you're just testing imports)")
        
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def check_directories():
    """Check that directories exist."""
    print("\nChecking directories...")
    from dnd.core.config import Config
    
    dirs = [Config.LOG_DIR, Config.BASE_DIR]
    all_exist = True
    
    for dir_path in dirs:
        if dir_path.exists():
            print(f"✓ {dir_path}")
        else:
            print(f"✗ {dir_path} (will be created on first run)")
            all_exist = False
    
    return True  # Not critical

def main():
    """Run all checks."""
    print("=" * 50)
    print("D&D Simulation Setup Verification")
    print("=" * 50)
    
    results = []
    results.append(("Imports", check_imports()))
    results.append(("Configuration", check_config()))
    results.append(("Directories", check_directories()))
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✓ All checks passed! You're ready to go.")
        print("\nNext steps:")
        print("  1. Set OPENAI_API_KEY in .env file")
        print("  2. Run: python main.py new --players 2")
        return 0
    else:
        print("\n⚠ Some checks failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

