from pdm.backend.hooks.version import SCMVersion


def format_version(version: SCMVersion) -> str:
    return str(version.version)
