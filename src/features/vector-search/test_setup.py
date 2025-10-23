#!/usr/bin/env python3
"""
Test script to verify vector search setup.
Run this to check if all components are working correctly.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (override=True prioritizes .env over system vars)
load_dotenv(override=True)

def test_imports():
    """Test if all required packages are installed"""
    print("🧪 Testing imports...")
    
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("chromadb", "ChromaDB"),
        ("openai", "OpenAI"),
        ("tiktoken", "Tiktoken"),
        ("docx", "python-docx"),
        ("openpyxl", "openpyxl"),
        ("pptx", "python-pptx"),
        ("pypdf", "pypdf"),
    ]
    
    missing = []
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - NOT INSTALLED")
            missing.append(name)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All packages installed")
    return True


def test_environment():
    """Test if environment variables are set"""
    print("\n🧪 Testing environment variables...")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    api_key = os.getenv("API_KEY")
    
    if not openai_key:
        print("  ❌ OPENAI_API_KEY not set")
        print("     Set it with: export OPENAI_API_KEY='your-key'")
        return False
    else:
        print(f"  ✅ OPENAI_API_KEY set ({len(openai_key)} chars)")
    
    if not api_key:
        print("  ⚠️  API_KEY not set (will use default 'dev-key-change-in-production')")
    else:
        print(f"  ✅ API_KEY set ({len(api_key)} chars)")
    
    return True


def test_openai_key_validity():
    """Test if OpenAI API key is valid by making a test call"""
    print("\n🧪 Testing OpenAI API key validity...")
    
    try:
        import openai
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("  ⚠️  Skipping (no API key set)")
            return True
        
        # Make a minimal test call to verify the key works
        client = openai.OpenAI(api_key=api_key)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input="test"
        )
        
        print(f"  ✅ OpenAI API key is VALID")
        print(f"     Successfully generated test embedding ({len(response.data[0].embedding)} dimensions)")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "invalid" in error_msg.lower():
            print(f"  ❌ OpenAI API key is INVALID")
            print(f"     Error: {error_msg[:100]}...")
            print(f"     Get a new key at: https://platform.openai.com/api-keys")
        else:
            print(f"  ❌ Error testing OpenAI API: {error_msg[:100]}...")
        return False


def test_document_parser():
    """Test document parser on existing files"""
    print("\n🧪 Testing document parser...")
    
    try:
        from document_parsers import DocumentParser
        
        # Find a test file
        repo_path = Path(__file__).resolve().parents[3]
        test_files = list(repo_path.glob("**/*.md"))[:1]
        
        if not test_files:
            print("  ⚠️  No test files found")
            return True
        
        test_file = test_files[0]
        result = DocumentParser.extract_text(test_file)
        
        if result['text']:
            print(f"  ✅ Successfully parsed {test_file.name}")
            print(f"     Extracted {len(result['text'])} chars")
            return True
        else:
            print(f"  ❌ Failed to extract text from {test_file.name}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_vector_search():
    """Test vector search initialization"""
    print("\n🧪 Testing vector search system...")
    
    try:
        from vector_search import VectorSearchSystem
        
        vs = VectorSearchSystem()
        print("  ✅ Vector search system initialized")
        
        stats = vs.get_stats()
        print(f"  📊 Database stats:")
        print(f"     - Total chunks: {stats.get('total_chunks', 0)}")
        print(f"     - DB path: {stats.get('vector_db_path', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_api():
    """Test API initialization"""
    print("\n🧪 Testing API...")
    
    try:
        from api import app
        
        print("  ✅ API initialized")
        print("  📚 Available endpoints:")
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = ','.join(route.methods) if route.methods else 'GET'
                print(f"     - {methods:6} {route.path}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("Vector Search Setup Test")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Environment", test_environment()))
    results.append(("OpenAI Key Validity", test_openai_key_validity()))
    results.append(("Document Parser", test_document_parser()))
    results.append(("Vector Search", test_vector_search()))
    results.append(("API", test_api()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {name}")
    
    print("="*60)
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Run: python vector_search.py index")
        print("2. Run: uvicorn api:app --reload")
        print("3. Visit: http://localhost:8000/docs")
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

