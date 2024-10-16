import json
import os
import plistlib
import subprocess
import shutil
from pathlib import Path
import time


def read_input(prompt):
    return input(prompt).strip().lower()
def search_apps(app_list, install_apps, keyword):
    matched_apps = []
    for app in app_list:
        package_name = app.get("packageName")
        
        # 检查 packageName
        if isinstance(package_name, list):
            if any(keyword.lower() in name.lower() for name in package_name):
                matched_apps.append(app)
                continue
        elif isinstance(package_name, str) and keyword.lower() in package_name.lower():
            matched_apps.append(app)
            continue
        
        # packageName没有匹配则检查 CFBundleName
        for installed_app in install_apps:
            if installed_app.get("CFBundleIdentifier") == package_name:
                if keyword.lower() in installed_app.get("CFBundleName", "").lower():
                    matched_apps.append(app)
                    break
    
    return matched_apps


def parse_app_info(app_base_locate, app_info_file):
    with open(app_info_file, "rb") as f:
        app_info = plistlib.load(f)
    app_info = {
        "appBaseLocate": app_base_locate,
        "CFBundleIdentifier": app_info.get("CFBundleIdentifier"),
        "CFBundleVersion": app_info.get("CFBundleVersion", ""),
        "CFBundleShortVersionString": app_info.get("CFBundleShortVersionString", ""),
        "CFBundleName": app_info.get("CFBundleExecutable", ""),
        "CFBundleExecutable": app_info.get("CFBundleExecutable", ""),
    }
    return app_info


def scan_apps():
    appList = []
    base_dirs = ["/Applications", "/Applications/Setapp"]

    for base_dir in base_dirs:
        if not os.path.exists(base_dir):
            continue
        lst = os.listdir(base_dir)
        for app in lst:
            app_info_file = os.path.join(base_dir, app, "Contents", "Info.plist")
            if not os.path.exists(app_info_file):
                continue
            try:
                appList.append(parse_app_info(base_dir + "/" + app, app_info_file))
                # print("检查本地App:", app_info_file)
            except Exception:
                continue

    return appList


def check_compatible(
    compatible_version_code,
    compatible_version_subcode,
    app_version_code,
    app_subversion_code,
):
    if compatible_version_code is None and compatible_version_subcode is None:
        return True

    if compatible_version_code:
        for code in compatible_version_code:
            if app_version_code == code:
                return True

    if compatible_version_subcode:
        for code in compatible_version_subcode:
            if app_subversion_code == code:
                return True

    return False

def handle_keygen(bundleIdentifier):
    user_dir = os.path.expanduser("~");
    # 取出用户名
    username = user_dir.split("/")[-1]
    subprocess.run("chmod +x ./tool/KeygenStarter", shell=True)
    subprocess.run(f"./tool/KeygenStarter '{bundleIdentifier}' '{username}'", shell=True)

def handle_helper(app_base, target_helper, component_apps, SMExtra, bridge_path):
    """增强Helper

    Args:
        app_base (dict): app信息
        target_helper (string): helper文件路径
    """
    subprocess.run("chmod +x ./tool/GenShineImpactStarter", shell=True)
    subprocess.run(
        f"./tool/GenShineImpactStarter '{target_helper}' {'' if SMExtra is None else SMExtra}",
        shell=True,
    )
    subprocess.run(
        f"./tool/insert_dylib '{bridge_path}91QiuChenly.dylib' '{target_helper}' '{target_helper}'",
        shell=True,
    )
    helper_name = target_helper.split("/")[-1]

    # 检查是否存在
    target = f"/Library/LaunchDaemons/{helper_name}.plist"
    if os.path.exists(target):
        subprocess.run(
            f"sudo /bin/launchctl unload {target}",
            shell=True,
        )
        subprocess.run(f"sudo /usr/bin/killall -u root -9 {helper_name}", shell=True)
        subprocess.run(f"sudo /bin/rm {target}", shell=True)
        subprocess.run(
            f"sudo /bin/rm /Library/PrivilegedHelperTools/{helper_name}", shell=True
        )
    subprocess.run(f"sudo xattr -c '{app_base}'", shell=True)

    src_info = [f"{app_base}/Contents/Info.plist"]
    if isinstance(component_apps, list):
        src_info.extend([f"{app_base}{i}/Contents/Info.plist" for i in component_apps])

    for i in src_info:
        command = [
            "/usr/libexec/PlistBuddy",
            "-c",
            f"Set :SMPrivilegedExecutables:{helper_name} 'identifier \\\"{helper_name}\\\"'",
            i,
        ]
        subprocess.run(command, text=True)
    subprocess.run(
        f'/usr/bin/codesign -f -s - --all-architectures --deep "{target_helper}"',
        shell=True,
    )
    subprocess.run(
        f'/usr/bin/codesign -f -s - --all-architectures --deep "{app_base}"', shell=True
    )


def getAppMainExecutable(app_base):
    # 读取Contents/Info.plist中的CFBundleExecutable
    with open(f"{app_base}/Contents/Info.plist", "rb") as f:
        app_info = plistlib.load(f)
        return app_info["CFBundleExecutable"]


# 获取BundleID
def getBundleID(
    app_base,
):
    with open(f"{app_base}/Contents/Info.plist", "rb") as f:
        app_info = plistlib.load(f)
        return app_info["CFBundleIdentifier"]


def main():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)

        base_public_config = config["basePublicConfig"]
        app_list = config["AppList"]
        proc_version = config["Version"]

        print("  ___  _        ____ _                _  ")
        print(" / _ \\(_)_   _ / ___| |_   ___ _ __ | |_   _ ")
        print("| | | | | | | | |  | '_ \\ / _ \\ '_ \\| | | | |")
        print("| |_| | | |_| | |__| | | |  __/ | | | | |_| |")
        print(" \\__\\_\\_\\__,_|\\____|_| |_|\\___|_| |_|_|\\__, |")
        print("                                        |___/")
        print(f"自动注入版本号: {proc_version}")
        print("Original Design By QiuChenly(github.com/qiuchenly), Py ver. by X1a0He")
        print("注入时请根据提示输入'y' 或者按下回车键跳过这一项。")

        # QiuChenlyTeam 特殊变量
        isDevHome = os.getenv("InjectLibDev")

        start_time = time.time()
        install_apps = scan_apps()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("扫描本地App耗时: {:.2f}s".format(elapsed_time))
        app_Lst = []
        print("请输入应用名称或包名的关键字进行搜索,或直接按回车键遍历所有支持的应用:")
        keyword = input().strip()

        if keyword:
            matched_apps = search_apps(app_list, install_apps, keyword)
            if not matched_apps:
                print("未找到匹配的应用程序。")
                return

            print("找到以下匹配的应用程序:")
            for i, app in enumerate(matched_apps, 1):
                package_name = app.get("packageName")
                if isinstance(package_name, list):
                    package_name = " / ".join(package_name)
                print(f"{i}. {package_name}")

            print("请输入要注入的应用程序编号,或输入0退出:")
            choice = input().strip()
            if not choice.isdigit() or int(choice) == 0 or int(choice) > len(matched_apps):
                print("已退出程序。")
                return

            selected_app = matched_apps[int(choice) - 1]
            app_Lst = []
            if isinstance(selected_app["packageName"], list):
                for name in selected_app["packageName"]:
                    tmp = selected_app.copy()
                    tmp["packageName"] = name
                    app_Lst.append(tmp)
            else:
                app_Lst.append(selected_app)             
        else:
            for app in app_list:
                package_name = app["packageName"]
                # 获取macOS系统当前用户账户
                if app.get("forQiuChenly") and not os.path.exists("/Users/qiuchenly"):
                    continue
                if isinstance(package_name, list):  # 如果是list就检查多项
                    for name in package_name:
                        tmp = app.copy()
                        tmp["packageName"] = name
                        app_Lst.append(tmp)
                else:
                    app_Lst.append(app)

        for app in app_Lst:
            package_name = app.get("packageName")
            app_base_locate = app.get("appBaseLocate")
            bridge_file = app.get("bridgeFile")
            inject_file = app.get("injectFile")
            support_version = app.get("supportVersion")
            support_subversion = app.get("supportSubVersion")
            extra_shell = app.get("extraShell")
            need_copy_to_app_dir = app.get("needCopyToAppDir")
            deep_sign_app = app.get("deepSignApp")
            disable_library_validate = app.get("disableLibraryValidate")
            entitlements = app.get("entitlements")
            no_sign_target = app.get("noSignTarget")
            no_deep = app.get("noDeep")
            tccutil = app.get("tccutil")
            auto_handle_setapp = app.get("autoHandleSetapp")
            auto_handle_helper = app.get("autoHandleHelper")
            helper_file = app.get("helperFile")
            componentApp = app.get("componentApp")
            onlysh = app.get("onlysh")
            SMExtra = app.get("SMExtra")
            keygen = app.get("keygen")

            local_app = [
                local_app
                for local_app in install_apps
                if local_app["CFBundleIdentifier"] == package_name
            ]

            if not local_app and (
                app_base_locate is None or not os.path.isdir(app_base_locate)
            ):
                continue

            if not local_app:
                # print("[🔔] 此App包不是常见类型结构，请注意当前App注入的路径是 {appBaseLocate}".format(appBaseLocate=app_base_locate))
                # print("读取的是 {appBaseLocate}/Contents/Info.plist".format(appBaseLocate=app_base_locate))
                local_app.append(
                    parse_app_info(
                        app_base_locate,
                        os.path.join(app_base_locate, "Contents", "Info.plist"),
                    )
                )

            local_app = local_app[0]
            if app_base_locate is None:
                app_base_locate = local_app["appBaseLocate"]

            if bridge_file is None:
                bridge_file = base_public_config.get("bridgeFile", bridge_file)

            if auto_handle_setapp is not None:
                bridge_file = "/Contents/MacOS/"
                executableAppName = local_app["CFBundleExecutable"]
                inject_file = os.path.basename(
                    app_base_locate + bridge_file + executableAppName
                )
                print(
                    f"======== Setapp下一个App的处理结果如下 [{app_base_locate}] [{bridge_file}] [{inject_file}]"
                )

            if not check_compatible(
                support_version,
                support_subversion,
                local_app["CFBundleShortVersionString"],
                local_app["CFBundleVersion"],
            ):
                print(
                    f"[😅] [{local_app['CFBundleName']}] - [{local_app['CFBundleShortVersionString']}] - [{local_app['CFBundleIdentifier']}]不是受支持的版本，跳过注入😋。"
                )
                continue

            print(
                f"[🤔] [{local_app['CFBundleName']}] - [{local_app['CFBundleShortVersionString']}] 是受支持的版本，是否需要注入？y/n(默认n)"
            )
            action = read_input("").strip().lower()
            if action != "y":
                continue

            if onlysh:
                subprocess.run(f"sudo sh tool/{extra_shell}", shell=True)
                continue

            # 检查是否为com.adobe开头
            if local_app["CFBundleIdentifier"].startswith("com.adobe"):
                subprocess.run(
                    "sudo chmod -R 777 /Applications/Utilities/Adobe\ Creative\ Cloud/Components/Apps/*",
                    shell=True,
                )
                # 检查是否存在/Applications/Utilities/Adobe Creative Cloud/Components/Apps/Apps1_0.js
                if not os.path.exists(
                    "/Applications/Utilities/Adobe Creative Cloud/Components/Apps/Apps1_0.js"
                ):
                    # 替换文件中的key:"getEntitlementStatus",value:function(e){为key:"getEntitlementStatus",value:function(e){return "Entitled Installed"
                    with open(
                        "/Applications/Utilities/Adobe Creative Cloud/Components/Apps/Apps1_0.js",
                        "r",
                        encoding="utf-8",
                    ) as f:
                        content = f.read()
                    # 判断是否写过了
                    if (
                        'key:"getEntitlementStatus",value:function(e){return "Entitled Installed"'
                        not in content
                    ):
                        # sed -i "s#key:\"getEntitlementStatus\",value:function(e){#key:\"getEntitlementStatus\",value:function(e){return \"Entitled Installed\"#g" /Applications/Utilities/Adobe\ Creative\ Cloud/Components/Apps/Apps1_0.js
                        content = content.replace(
                            'key:"getEntitlementStatus",value:function(e){',
                            'key:"getEntitlementStatus",value:function(e){return "Entitled Installed";',
                        )
                        with open(
                            "/Applications/Utilities/Adobe Creative Cloud/Components/Apps/Apps1_0.js",
                            "w",
                            encoding="utf-8",
                        ) as f:
                            f.write(content)

            print(f"开始注入App: {package_name}")

            subprocess.run(["sudo", "chmod", "-R", "777", app_base_locate])
            subprocess.run(["sudo", "xattr", "-cr", app_base_locate])

            subprocess.run(
                ["sudo", "pkill", "-f", getAppMainExecutable(app_base_locate)]
            )

            if keygen is not None:
                print("正在注册App...")
                handle_keygen(local_app["CFBundleIdentifier"])
                continue

            # dest = os.path.join(app_base_locate, bridge_file, inject_file)
            dest = rf"{app_base_locate}{bridge_file}{inject_file}"
            backup = rf"{dest}_backup"

            if os.path.exists(backup):
                print("备份的原始文件已经存在,需要直接用这个文件注入吗？y/n(默认y)")
                action = read_input("").strip().lower()
                if action == "n":
                    os.remove(backup)
                    subprocess.run(f"sudo cp '{dest}' '{backup}'", shell=True)
            else:
                subprocess.run(f"sudo cp '{dest}' '{backup}'", shell=True)

            current = Path(__file__).resolve()

            sh = f"chmod +x {current.parent}/tool/insert_dylib"
            subprocess.run(sh, shell=True)

            sh = f"sudo {current.parent}/tool/insert_dylib '{current.parent}/tool/91QiuChenly.dylib' '{backup}' '{dest}'"

            if need_copy_to_app_dir:
                source_dylib = f"{current.parent}/tool/91QiuChenly.dylib"
                if isDevHome:
                    # 开发者自己的prebuild库路径 直接在.zshrc设置环境变量这里就可以读取到。
                    # export InjectLibDev="自己的路径/91QiuChenly.dylib"
                    # 要设置全路径哦 并且不要用sudo python3 main.py 启动 否则读不到你的环境变量
                    source_dylib = isDevHome
                destination_dylib = f"'{app_base_locate}{bridge_file}91QiuChenly.dylib'"

                command = "ln -f -s" if isDevHome else "cp"
                subprocess.run(
                    f"{command} {source_dylib} {destination_dylib}",
                    shell=True,
                )

                sh = []
                desireApp = [dest]
                if componentApp:
                    desireApp.extend(
                        [
                            f"{app_base_locate}{i}/Contents/MacOS/{getAppMainExecutable(app_base_locate+i)}"
                            for i in componentApp
                        ]
                    )
                for it in desireApp:
                    bsh = rf"sudo {current.parent}/tool/insert_dylib {destination_dylib} '{backup}' '{it}'"
                    sh.append(bsh)

            if isinstance(sh, list):
                [subprocess.run(command, shell=True) for command in sh]
            else:
                subprocess.run(sh, shell=True)

            sign_prefix = (
                "/usr/bin/codesign -f -s - --timestamp=none --all-architectures"
            )

            if no_deep is None:
                print("Need Deep Sign.")
                sign_prefix += " --deep"

            if entitlements is not None:
                sign_prefix += f" --entitlements {current.parent}/tool/{entitlements}"

            if no_sign_target is None:
                print("开始签名...")
                subprocess.run(f"{sign_prefix} '{dest}'", shell=True)

            if disable_library_validate is not None:
                subprocess.run(
                    "sudo defaults write /Library/Preferences/com.apple.security.libraryvalidation.plist DisableLibraryValidation -bool true",
                    shell=True,
                )

            if extra_shell is not None:
                subprocess.run(
                    f"sudo sh {current.parent}/tool/{extra_shell}", shell=True
                )

            if deep_sign_app:
                subprocess.run(f"{sign_prefix} '{app_base_locate}'", shell=True)

            subprocess.run(f"sudo xattr -cr '{dest}'", shell=True)
            if auto_handle_helper and helper_file:
                helpers = []

                if isinstance(helper_file, list):
                    helpers = helper_file
                else:
                    helpers.append(helper_file)

                for helper in helpers:
                    handle_helper(
                        app_base_locate,
                        f"{app_base_locate}{helper}",
                        componentApp,
                        SMExtra,
                        f"{app_base_locate}{bridge_file}",
                    )
            if tccutil is not None:
                if tccutil := tccutil:
                    # 如果componentApp不为空，则创建一个数组
                    ids = [local_app["CFBundleIdentifier"]]
                    if isinstance(componentApp, list):
                        ids.extend(
                            [getBundleID(app_base_locate + i) for i in componentApp]
                        )

                    for id in ids:
                        if isinstance(tccutil, str):
                            subprocess.run(f"tccutil reset {tccutil} {id}", shell=True)
                        else:
                            if isinstance(tccutil, list):
                                for i in tccutil:
                                    subprocess.run(
                                        f"tccutil reset {i} {id}", shell=True
                                    )

            print("App处理完成。")
    except KeyboardInterrupt:
        print("\n用户手动退出程序,祝你使用愉快,再见.")


if __name__ == "__main__":
    main()