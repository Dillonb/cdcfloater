import os
import urllib
import urllib.request
from io import StringIO, BytesIO
from zipfile import ZipFile
import json
import shutil


def get_current_installed_version(config):
    """ Gets the current installed version of a chocolatey package based on its config dict """
    metadatapath = os.path.join("root",".chocolatey","chocolatey_" + config["urlpattern"] + "_" + config["chocolatey_name"] + "_version")
    if os.path.exists(metadatapath):
        f = open(metadatapath)
        return f.read().strip()
    else:
        return None

def set_current_installed_version(config):
    f = open(os.path.join("temp","chocolatey_" + config["urlpattern"] + "_" + config["chocolatey_name"] + "_version"),"w")
    f.write(config["chocolatey_version"])
    f.close()

def process_chocolatey(config):
    """ Downloads a chocolatey package. """
    if not "urlpattern" in config:
        config["urlpattern"] = "url" # default value: look for the line that says $url = 'http://asdf.com/asdf.zip'
    if config["chocolatey_version"] == "latest":
        print ("Retrieving available versions of %s..."%config["friendly_name"])
        versions = json.loads(str(urllib.request.urlopen("http://chocolatey.org/api/v2/package-versions/" + config["chocolatey_name"]).read(), encoding="utf8"))
        config["chocolatey_version"] = versions[len(versions) - 1] # Last item in the array is the latest version
    print("Currently installed: %s, latest available: %s"%(get_current_installed_version(config), config["chocolatey_version"]))
    if get_current_installed_version(config) == config["chocolatey_version"]:
        print ("Already have the latest version of %s, skipping."%config["friendly_name"])
        return "NOPOST"
    else:
        print ("Downloading metadata for %s package on Chocolatey..."%config["chocolatey_name"])
        url = urllib.request.urlopen("http://chocolatey.org/api/v2/package/" + config["chocolatey_name"] + "/" + config["chocolatey_version"])
        print("Done.")
        sio = BytesIO(url.read())
        nupkg = ZipFile(sio)
        # Extract the content folder of the nupkg file instead of downloading a separate file
        if "chocolatey_content" in config and config["chocolatey_content"] == "yes":
            print("Installing from content directory in metadata...")
            if not os.path.exists(os.path.join("root",config["chocolatey_content_extract_path"])):
                os.makedirs(os.path.join("root",config["chocolatey_content_extract_path"]))
            for name in nupkg.namelist():
                if name.startswith(config["chocolatey_content_dir"]):
                    f = nupkg.open(name)
                    basename = name.split("/")
                    basename = basename[len(basename)-1]
                    of = open(os.path.join("root",config["chocolatey_content_extract_path"],basename), "wb")

                    shutil.copyfileobj(f, of)
            set_current_installed_version(config)
            print ("Done.")
        else:
            print ("Parsing for URL...")
            for line in nupkg.open("tools/chocolateyInstall.ps1").readlines():
                line = str(line.strip(),encoding='utf8')
                patlocation = line[1:].split(" ")[0].strip()
                #if line[1:len(config["urlpattern"])+1] == config["urlpattern"]:
                if patlocation == config["urlpattern"]:
                    url = line[len(config["urlpattern"])+2:].strip(" '=`\";")
                    print(url)
                    print("Downloading %s..."%config["friendly_name"])
                    urllib.request.urlretrieve(url,os.path.join("temp",config["filename"]))
                    set_current_installed_version(config)
                    print ("Done.")


def postprocess_chocolatey(config):
    """ Moves the version data file into place. """
    if not os.path.exists("root/.chocolatey"):
        os.makedirs("root/.chocolatey")

    shutil.move(os.path.join("temp","chocolatey_" + config["urlpattern"] + "_" + config["chocolatey_name"] + "_version"),os.path.join("root", ".chocolatey", "chocolatey_" + config["urlpattern"] + "_" + config["chocolatey_name"] + "_version"))
