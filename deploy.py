import os
import sys
from huggingface_hub import HfApi, login

def main():
    print("=" * 45)
    print("      AgroMed AI - Hugging Face Deployer")
    print("=" * 45)
    
    # Read Hugging Face token from command-line arguments or ask user
    token = ""
    if len(sys.argv) > 1:
        token = sys.argv[1].strip()
    
    if not token:
        token = input("Enter your Hugging Face Write Token: ").strip()
        
    if not token:
        print("[ERROR] Hugging Face Write Token is required to proceed.")
        sys.exit(1)
        
    try:
        # Log in to Hugging Face
        print("\n[INFO] Authenticating with Hugging Face...")
        login(token=token)
        print("[SUCCESS] Logged in successfully!")
        
        # Instantiate HfApi and fetch username
        api = HfApi()
        user_info = api.whoami()
        username = user_info['name']
        print(f"[INFO] Hugging Face User: {username}")
        
        # Ask for Space Name (default is agromed-ai)
        space_name = input("\nEnter Space Name (default: agromed-ai): ").strip()
        if not space_name:
            space_name = "agromed-ai"
        
        repo_id = f"{username}/{space_name}"
        print(f"[INFO] Target Space: {repo_id}")
        
        # Create Repository with Docker SDK
        print(f"\n[INFO] Initializing Space repository '{repo_id}' with Docker SDK...")
        api.create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="docker",
            private=False,
            exist_ok=True
        )
        print("[SUCCESS] Repository initialized/verified.")
        
        # Define ignore patterns to avoid uploading large node_modules and local data
        ignore = [
            "node_modules",
            "node_modules/*",
            ".git",
            ".git/*",
            "backend/data/*",
            "backend/agrovet.db", # Deploy clean/initialize on startup
            "backend/__pycache__",
            "backend/__pycache__/*",
            "*.pdf",
            "generate_*.py",
            "deploy.py"
        ]
        
        # Uploading workspace contents to Hugging Face Space
        print(f"\n[INFO] Uploading workspace contents to '{repo_id}' (excluding node_modules)...")
        api.upload_folder(
            folder_path=".",
            repo_id=repo_id,
            repo_type="space",
            ignore_patterns=ignore
        )
        
        print("\n" + "=" * 45)
        print("            DEPLOYMENT COMPLETE!")
        print("=" * 45)
        print("Your application is building on Hugging Face Spaces.")
        print(f"It will be accessible shortly at:")
        print(f"👉 https://huggingface.co/spaces/{repo_id}")
        print("=" * 45)
        
    except Exception as e:
        print(f"\n[ERROR] An error occurred during deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
