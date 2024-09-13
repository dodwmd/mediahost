# Load environment variables from .env file
load('ext://dotenv', 'dotenv')
dotenv()

# Define the Docker Compose configuration
docker_compose('docker-compose.yml')

# Define resources for services
dc_resource('mediahost_app', resource_deps=['db', 'minio', 'nats'])
dc_resource('db', labels=['infra'])
dc_resource('minio', labels=['infra'])
dc_resource('nats', labels=['infra'])

# Custom build command for the app
docker_build(
    'mediahost_app',
    '.',
    dockerfile='Dockerfile',
    live_update=[
        sync('.', '/app'),
        run('pip install -r requirements.txt', trigger='requirements.txt'),
    ]
)

# Add labels for better organization in the Tilt UI
dc_resource('mediahost_app', labels=['app'])
dc_resource('db', labels=['infra'])
dc_resource('minio', labels=['infra'])
dc_resource('nats', labels=['infra'])
dc_resource('phpmyadmin', labels=['infra'])

# Add this line to set the PYTHONPATH
os.environ['PYTHONPATH'] = '/app'

# Set up file watching with the trigger_rebuild function
watch_file('./app')
watch_file('./requirements.txt')
watch_file('./pyproject.toml')
watch_file('./poetry.lock')

update_settings(suppress_unused_image_warnings=["mediahost_app"])
