cp "/Applications/iStat Menus.app/Contents/Resources/Components.bundle/Contents/MacOS/Components" "/Applications/iStat Menus.app/Contents/Resources/Components.bundle/Contents/MacOS/Components_backup"
sudo tool/insert_dylib '/Applications/iStat Menus.app/Contents/Frameworks/91QiuChenly.dylib' "/Applications/iStat Menus.app/Contents/Resources/Components.bundle/Contents/MacOS/Components_backup" "/Applications/iStat Menus.app/Contents/Resources/Components.bundle/Contents/MacOS/Components"
/usr/libexec/PlistBuddy -c "Set :SMPrivilegedExecutables:com.bjango.istatmenus.installer 'identifier \\\"com.bjango.istatmenus.installer\\\"'" "/Applications/iStat Menus.app/Contents/Resources/Components.bundle/Contents/Resources/iStat Menus Helper.app/Contents/Info.plist"
/usr/bin/codesign -f -s - --timestamp=none --all-architectures --deep "/Applications/iStat Menus.app/Contents/Resources/Components.bundle/Contents/Resources/com.bjango.istatmenus.daemon"
/usr/bin/codesign -f -s - --timestamp=none --all-architectures --deep "/Applications/iStat Menus.app/Contents/Resources/Components.bundle/Contents/Resources/iStat Menus Helper.app"
/usr/bin/codesign -f -s - --timestamp=none --all-architectures --deep "/Applications/iStat Menus.app/Contents/Resources/Components.bundle"
xattr -cr "/Applications/iStat Menus.app/Contents/Resources/Components.bundle"