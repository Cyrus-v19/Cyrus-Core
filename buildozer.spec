[app]
title = cyrus
package.name = cyrus
package.domain = org.samuel
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.3
requirements = python3,kivy,plyer,requests,pyjnius
android.permissions = INTERNET,RECORD_AUDIO
android.accept_sdk_license = True
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
