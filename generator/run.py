import os
import sys
import requests
import subprocess
from jinja2 import Template
from dataclasses import dataclass
from caseconverter import camelcase, kebabcase, pascalcase

GET_COMMON_MODELS_URL = "https://development-api.integrationos.com/v1/public/sdk/common-models?limit=500"
OPENAPI_URL = "https://development-api.integrationos.com/v1/public/openapi"

TEMPLATE_FILE_PATH = os.path.join('generator', 'templates', 'client.py.jinja')
OUTPUT_FILE_PATH = os.path.join('src', 'integrationos', 'client.py')

@dataclass
class Resource:
    pascal_case: str
    kebab_case: str
    camel_case: str

def handle_dependencies():
    """Check if required packages are installed and install them if missing."""
    try:
        subprocess.run(
            ["datamodel-codegen", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 Installing required package: datamodel-code-generator...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "datamodel-code-generator"],
                check=True
            )
            print("✅ Installation successful!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install datamodel-code-generator: {e}")
            sys.exit(1)

def ensure_directory_exists(path: str):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"📁 Created directory: {path}")

def generate_sdk():
    try:
        print('🚀 Starting SDK generation process...')

        handle_dependencies()

        src_path = os.path.join('src', 'integrationos')
        types_path = os.path.join(src_path, 'types')

        for path in [src_path, types_path]:
            ensure_directory_exists(path)

        print('🔍 Generating models using datamodel-codegen...')
        subprocess.run([
            "datamodel-codegen",
            "--url", OPENAPI_URL,
            "--use-field-description",
            "--use-default",
            "--output", os.path.join(types_path, "models.py")
        ], check=True)
        print('✅ models.py file generated successfully.\n')

        print('🔍 Fetching resources from IntegrationOS API...')
        common_models_response = requests.get(GET_COMMON_MODELS_URL)
        common_models_response.raise_for_status()
        common_models = common_models_response.json().get('rows', [])
        primary_common_model_names = [model['name'] for model in common_models if model['primary']]
        print(f"Found {len(primary_common_model_names)} primary common models.\n")

        # Create Resource objects
        resources = [
            Resource(
                pascal_case=pascalcase(name),
                kebab_case=kebabcase(name),
                camel_case=camelcase(name)
            )
            for name in primary_common_model_names
        ]

        print('📝 Generating resource properties...')
        
        # Read the template
        with open(TEMPLATE_FILE_PATH, 'r') as f:
            template_content = f.read()

        # Create the template and render
        template = Template(template_content)
        generated_client_file = template.render(resources=resources)

        # Write the client.py file
        with open(OUTPUT_FILE_PATH, 'w') as f:
            f.write(generated_client_file)

        print('✅ client.py file generated successfully.\n')

        print('🎉 SDK generation completed successfully!')

    except requests.RequestException as error:
        print(f'❌ An error occurred while fetching data from the API: {error}')
    except subprocess.CalledProcessError as error:
        print(f'❌ An error occurred while running datamodel-codegen: {error}')
    except Exception as error:
        print(f'❌ An unexpected error occurred while generating the SDK: {error}')
        raise

if __name__ == "__main__":
    generate_sdk()
