from panda3d.core import ConfigVariableString

log_level = ConfigVariableString("default-directnotify-level", "warning")
log_level.setStringValue("info")