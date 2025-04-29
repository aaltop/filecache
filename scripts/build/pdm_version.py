from pdm.backend.hooks.version import SCMVersion

def format_version(version: SCMVersion) -> str:
    if version.distance is None:
        return str(version.version)
    else:
        raise TypeError("Version distance should be None; create a tag for the commit")