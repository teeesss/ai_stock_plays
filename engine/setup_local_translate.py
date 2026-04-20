import argostranslate.package

def setup():
    print("Installing Local Translation Models (KO, JA, ZH)...")
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    
    targets = [("ko", "en"), ("ja", "en"), ("zh", "en")]
    
    for from_code, to_code in targets:
        print(f"  Downloading {from_code} -> {to_code}...")
        package_to_install = next(
            filter(
                lambda x: x.from_code == from_code and x.to_code == to_code,
                available_packages
            )
        )
        argostranslate.package.install_from_path(package_to_install.download())
    
    print("Local Models Ready.")

if __name__ == "__main__":
    setup()