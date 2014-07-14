import os
import urllib
import urllib.request


def process_url(config):
    print("Downloading %s for %s"%(config["filename"],config["friendly_name"]))
    if not os.path.exists(config["path"]):
        url = config["url"]
        try:
            urllib.request.urlretrieve(url,os.path.join("temp",config["filename"]))
        except urllib.error.HTTPError:
            print("ERROR! Failed downloading %s. Skipping this package. Rerun the script to try again."%config["filename"])
            return "NOPOST"
    else:
        print("File already downloaded. To retrieve a new version, delete the old file.")
        return "NOPOST"

def postprocess_url(config):
    pass
