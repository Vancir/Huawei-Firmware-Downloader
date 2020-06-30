import json
import requests
import xml.etree.ElementTree as ET

FIRMWARE = 'Huawei-Firmware-DataBase/firmwares.txt'
ATTRIBS = ('package', 'incrementdatafile', 'fulldatafile')

def join(baseurl, subpath, pkg):
    pkg = pkg.replace('\\', '/')
    if subpath: 
        pkgurl = baseurl + '/' + subpath + '/' + pkg
    else: 
        pkgurl = baseurl + '/' + pkg
    
    return pkgurl

def mode1(baseurl, root):
    packages = []
    for vdrInfo in root.iter('vendorInfo'):
        subpath = vdrInfo.attrib['subpath'].text
        for attrib in ATTRIBS:
            if attrib not in vdrInfo.attrib:
                continue
            pkg = vdrInfo.attrib[attrib].text
            downurl = join(baseurl, subpath, pkg)

            filetag = root.find(".//file[spath='{}']".format(pkg))
            md5tag = filetag.find('md5')
            md5 = md5tag.text

            packages.append((downurl, md5))
    return packages

def mode2(baseurl, root):
    packages = []
    for filetag in root.iter('file'):
        pkg = filetag.find('spath').text
        if pkg.endswith('xml'):
            continue
        downurl = join(baseurl, '', pkg)
        md5 = filetag.find('md5').text

        packages.append((downurl, md5))
    return packages

def parse(filelist):
    try:
        resp = requests.get(filelist, timeout=5)
        if resp.status_code != 200: return []
    except:
        return []

    baseurl = resp.url[:resp.url.rfind('/')]
    root = ET.fromstring(resp.content)

    if root.find('vendorInfo'): 
        packages = mode1(baseurl, root)
    else:
        packages = mode2(baseurl, root)

    return packages

def main():
    firmdata = json.load(open(FIRMWARE))
    for fw in firmdata['firmwares']:
        packages = parse(fw['filelist_link'])
        if not packages: continue
        for downurl, md5 in packages:
            # FIXME: Download firmware.
            print(md5, downurl)

if __name__ == '__main__':
    main()
    