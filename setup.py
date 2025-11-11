#!/usr/bin/env python3
"""
Linoroso Shopify Automation - Setup Script
Automated setup and validation of the marketing automation system
"""

import os
import sys
from pathlib import Path
import subprocess
import json
from typing import List, Tuple

class SetupAssistant:
    """Interactive setup assistant"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.checks = []
        
    def print_header(self, text: str):
        """Print formatted header"""
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70 + "\n")
    
    def print_step(self, step_num: int, text: str):
        """Print step number and description"""
        print(f"\n[Step {step_num}] {text}")
        print("-" * 70)
    
    def check_python_version(self) -> Tuple[bool, str]:
        """Check Python version"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 9:
            return True, f"Python {version.major}.{version.minor}.{version.micro} ✓"
        else:
            return False, f"Python {version.major}.{version.minor}.{version.micro} ✗ (Need 3.9+)"
    
    def check_env_file(self) -> Tuple[bool, str]:
        """Check if .env file exists"""
        env_path = self.project_root / '.env'
        if env_path.exists():
            return True, ".env file exists ✓"
        else:
            return False, ".env file missing ✗"
    
    def check_required_packages(self) -> Tuple[bool, str]:
        """Check if required packages can be imported"""
        required = ['anthropic', 'pandas', 'requests', 'loguru']
        missing = []
        
        for package in required:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        
        if not missing:
            return True, "Required packages installed ✓"
        else:
            return False, f"Missing packages: {', '.join(missing)} ✗"
    
    def check_directories(self) -> Tuple[bool, str]:
        """Check if required directories exist"""
        required_dirs = [
            'data', 'logs', 'reports', 
            'data/generated_content', 'data/social_posts'
        ]
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
        
        return True, "Directory structure created ✓"
    
    def check_api_keys(self) -> Tuple[bool, str]:
        """Check if critical API keys are configured"""
        env_path = self.project_root / '.env'
        
        if not env_path.exists():
            return False, "No .env file ✗"
        
        # Read .env file
        with open(env_path, 'r') as f:
            env_content = f.read()
        
        critical_keys = [
            'ANTHROPIC_API_KEY',
            'SHOPIFY_STORE_URL',
            'SHOPIFY_ACCESS_TOKEN'
        ]
        
        missing = []
        for key in critical_keys:
            if key not in env_content or f'{key}=your_' in env_content:
                missing.append(key)
        
        if not missing:
            return True, "API keys configured ✓"
        else:
            return False, f"Missing keys: {', '.join(missing)} ✗"
    
    def run_system_checks(self):
        """Run all system checks"""
        self.print_header("SYSTEM CHECKS")
        
        checks = [
            ("Python Version", self.check_python_version),
            ("Environment File", self.check_env_file),
            ("Required Packages", self.check_required_packages),
            ("Directory Structure", self.check_directories),
            ("API Keys", self.check_api_keys)
        ]
        
        results = []
        for check_name, check_func in checks:
            success, message = check_func()
            results.append((check_name, success, message))
            status = "✓" if success else "✗"
            print(f"{status} {check_name}: {message}")
        
        all_passed = all(r[1] for r in results)
        
        if all_passed:
            print("\n✅ All checks passed!")
        else:
            print("\n⚠️  Some checks failed. Please address the issues above.")
        
        return all_passed
    
    def install_dependencies(self):
        """Install Python dependencies"""
        self.print_step(1, "Installing Dependencies")
        
        requirements_file = self.project_root / 'requirements.txt'
        
        if not requirements_file.exists():
            print("❌ requirements.txt not found!")
            return False
        
        print("Installing packages from requirements.txt...")
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
                check=True
            )
            print("✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    
    def create_env_file(self):
        """Create .env file from template"""
        self.print_step(2, "Creating Environment Configuration")
        
        env_path = self.project_root / '.env'
        env_example_path = self.project_root / '.env.example'
        
        if env_path.exists():
            response = input("\n.env file already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Keeping existing .env file")
                return
        
        if not env_example_path.exists():
            print("❌ .env.example not found!")
            return
        
        # Copy template
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        with open(env_path, 'w') as f:
            f.write(content)
        
        print("✅ Created .env file from template")
        print("\n⚠️  IMPORTANT: Edit .env file with your actual API keys:")
        print("   - ANTHROPIC_API_KEY")
        print("   - SHOPIFY_STORE_URL")
        print("   - SHOPIFY_ACCESS_TOKEN")
    
    def configure_api_keys(self):
        """Interactive API key configuration"""
        self.print_step(3, "Configuring API Keys")
        
        print("\nLet's configure your essential API keys.")
        print("(Press Enter to skip and configure manually later)\n")
        
        # Anthropic API Key
        anthropic_key = input("Anthropic API Key: ").strip()
        
        # Shopify credentials
        shopify_url = input("Shopify Store URL (e.g., yourstore.myshopify.com): ").strip()
        shopify_token = input("Shopify Access Token: ").strip()
        
        # Update .env file
        env_path = self.project_root / '.env'
        if env_path.exists():
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            with open(env_path, 'w') as f:
                for line in lines:
                    if anthropic_key and line.startswith('ANTHROPIC_API_KEY='):
                        f.write(f'ANTHROPIC_API_KEY={anthropic_key}\n')
                    elif shopify_url and line.startswith('SHOPIFY_STORE_URL='):
                        f.write(f'SHOPIFY_STORE_URL={shopify_url}\n')
                    elif shopify_token and line.startswith('SHOPIFY_ACCESS_TOKEN='):
                        f.write(f'SHOPIFY_ACCESS_TOKEN={shopify_token}\n')
                    else:
                        f.write(line)
            
            if anthropic_key or shopify_url or shopify_token:
                print("\n✅ API keys configured!")
            else:
                print("\n⚠️  No keys entered. Please edit .env manually.")
    
    def run_test_generation(self):
        """Test content generation"""
        self.print_step(4, "Testing Content Generation")
        
        print("\nTesting Claude API connection and content generation...")
        
        try:
            # Import after ensuring packages are installed
            sys.path.insert(0, str(self.project_root))
            from src.content_generation.content_engine import ContentGenerator
            
            generator = ContentGenerator()
            
            # Generate a simple test
            print("Generating test blog post...")
            blog = generator.generate_blog_post(
                topic="Welcome to Linoroso",
                keywords=["kitchen tools", "cooking"],
                word_count=300
            )
            
            print(f"\n✅ Generated test content: {blog.title}")
            print(f"   Word count: {blog.word_count}")
            
            # Save test content
            filepath = generator.save_content(blog)
            print(f"   Saved to: {filepath}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            print("\nTroubleshooting:")
            print("1. Check your ANTHROPIC_API_KEY in .env")
            print("2. Ensure you have API credits")
            print("3. Check your internet connection")
            return False
    
    def run_full_setup(self):
        """Run complete setup process"""
        self.print_header("LINOROSO SHOPIFY AUTOMATION - SETUP")
        
        print("Welcome! This setup assistant will help you get started.\n")
        
        # Step 0: System checks
        if not self.run_system_checks():
            print("\n❌ Please resolve the issues above before continuing.")
            sys.exit(1)
        
        # Step 1: Install dependencies
        if not self.check_required_packages()[0]:
            self.install_dependencies()
        
        # Step 2: Create .env
        if not self.check_env_file()[0]:
            self.create_env_file()
        
        # Step 3: Configure keys
        if not self.check_api_keys()[0]:
            response = input("\nWould you like to configure API keys now? (Y/n): ")
            if response.lower() != 'n':
                self.configure_api_keys()
        
        # Step 4: Test generation
        response = input("\nWould you like to test content generation? (Y/n): ")
        if response.lower() != 'n':
            self.run_test_generation()
        
        # Final summary
        self.print_header("SETUP COMPLETE!")
        
        print("✅ Your Linoroso automation is ready!\n")
        print("Next steps:")
        print("1. Review generated test content in data/generated_content/")
        print("2. Run batch content generation: python scripts/batch_generate.py")
        print("3. Optimize products: python src/product_optimizer/optimizer.py")
        print("4. Start automation: python main.py --mode scheduler\n")
        print("Documentation:")
        print("• Quick Start: See QUICKSTART.md")
        print("• Full README: See README.md\n")
        print("Questions? Contact: tony@linoroso.com\n")


def main():
    """Main entry point"""
    assistant = SetupAssistant()
    
    try:
        assistant.run_full_setup()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
