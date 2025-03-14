import os

from app.utils.logging_utilities import setup_logging

logger = setup_logging()


def get_project_workspace():
    """Retrieve the DEEP_DIVE_WORKSPACE environment variable or create a default workspace."""
    # Attempt to get the environment variable
    workspace = os.getenv('DEEP_DIVE_WORKSPACE')
    if workspace:
        # Check if the provided directory exists
        if not os.path.isdir(workspace):
            raise FileNotFoundError(f"The specified workspace directory does not exist: {workspace}")
        logger.info(f"Using provided workspace at: {workspace}")
    else:
        # If not found, create the default workspace directory
        home_dir = os.path.expanduser('~')
        workspace = os.path.join(home_dir, '.deep-dive', 'workspace')
        try:
            os.makedirs(workspace, exist_ok=True)
            logger.info(f"DEEP_DIVE_WORKSPACE not set. Created default workspace at: {workspace}")
        except OSError as e:
            logger.error(f"Failed to create workspace directory at {workspace}: {e}")
            raise
    return workspace