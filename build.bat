%编译打包%
python -m nuitka --standalone --mingw64 ^
--show-memory --show-progress ^
--plugin-enable=qt-plugins ^
--include-qt-plugins=sensible,styles ^
--nofollow-imports --follow-import-to=src ^
--windows-icon-from-ico=resource/connect.ico ^
--include-data-dir=resource=resource ^
--output-dir=o ^
--windows-disable-console ^
main.py
