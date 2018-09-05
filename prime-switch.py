#!/usr/bin/python3
# -*- coding_utf-8 -*-

import os,subprocess,re
import argparse
import json
from sys import exc_info
try:
    from magic import detect_from_filename
    PYMAGIC=True
except ModuleNotFoundError:
    PYMAGIC=False


def create_parser():
    defconf = "/usr/local/share/nvidia-prime-switch/prime-switch-conf.json"
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--driver",
        help="Switch to this driver (e.g. intel or nvidia)"
    )
    parser.add_argument(
        "-c", "--config",
        default=defconf,
        help="Path to config file"
    )
    parser.add_argument(
        "-s", "--show-config",
        nargs='?',
        const=True,
        metavar="Filename",
        help="Dumps default config to stdout or filename if specified"
    )
    parser.add_argument(
        "--info",
        const=True,
        action="store_const",
        help="File Walk gpu related text files in /sys/bus/pci"
    )
    return(parser.parse_args())
        

class File_Walk:
    def __init__(self,d):
        self.d = d
        self.main()

    def _gen_filennames(self,d):
        return((dirpath,filename) for dirpath, dirnames, filenames,dirfd in os.fwalk(d) for filename in filenames)

    def checkfile(self,path):
        # maybe use just octal conversion of st_mode
        stat = os.stat(path)
        isreadable, uid, gid, mode = bool(stat.st_mode & os.st.S_IRGRP), stat.st_uid, stat.st_gid, stat.st_mode
        return(isreadable,uid,gid,mode)

    def read_file(self,path):
        try:
            # maybe check readability already here
            if os.path.exists(path):
                mime,enc,name = detect_from_filename(path) if PYMAGIC else ("Install python-magic to get mime_type and encoding",None,None)
            else:
                print("-------! %s don't exists" %(path))
                return
            if PYMAGIC and mime.startswith("text/"):
                with open(path,errors="ignore") as f: # ignore UnicodeDecode errors on text files (maybe better use replace)
                    print("-------> %s:\n%s" %(path,f.read()))
            elif PYMAGIC is False:
            # not pymagic, so just open and handle exceptions later
                with open(path) as f: # ignore UnicodeDecode errors on text files
                    print("-------> %s:\n%s" %(path,f.read()))
            else:
                print("-------! %s Not a text file (%s, %s, %s)" %(path,mime,enc,name))
        except PermissionError:
            print("-------! not allowed to read %s" %(path))
        except UnicodeDecodeError:
            # no PYMAGIC and trying to read a non text file
            print("-------! Unicode Error (probably not a text file). %s %s" %(path,mime) )
        except OSError:
            print("-------! OSError for %s" %(path))
        except ValueError as e:
            # e.g. detect_from_filename error (e.g. permission issue on root files if user tries to read them)
            readable, uid, gid, mode = self.checkfile(path)
            print("-------! %s Not readable (uid: %i, gid: %i, mode: %s)" %(path,uid,gid,os.st.filemode(mode)) if readable is False else "-------! Error %s (file %s)" %(e,path))
        #all other excpetions
        except Exception:
            e = exc_info()[0]
            print("-------! %s (file %s)" %(e.__name__,path) )

    def main(self):
        for dir in self.d:
        # TODO:
        # normalize and absolute path alreay here
        # test os.scandir instead of os.fwalk
            if os.path.isfile(dir):
                self.read_file(dir)
                continue
            print("----> %s:" %(os.path.abspath(dir)) if os.path.isdir(dir) else "-----! %s not found" %(os.path.abspath(dir)) )
            for dirpath,filename in self._gen_filennames(dir):
                path = os.path.abspath(os.path.normpath(dirpath+"/"+filename))
                symlink = os.path.islink(path)
                if symlink:
                    real_file = os.path.realpath(path) # TODO: maybe check is file really exists already here
                    print("-----l %s = symlink, realpath = %s" %(path,real_file))
                    symlink, path = True, real_file
                if os.path.isfile(path) or symlink:
                    self.read_file(path)
                else:
                    print("-------! %s neither file or symlink (=%s)" %(path,detect_from_filename(path)[0]) if PYMAGIC else "-------! %s neither file or symlink (install python-magic to see mime_type)" %path)


class Util:
    def _file_writer(self,key,li,f,keyend=None,addtoprint=None):
        if keyend is None:
            _gen = (key+" "+i if key is not None else ""+i for i in li if len(li) > 0 )
        else:
            _gen = (key+" "+i+" "+keyend for i in li if len(li) > 0)
        for i in _gen:
            f.write(i+"\n")
            print("%s %s" %(addtoprint,i) if addtoprint is not None else "%s" %(i) )
        return

    def _changeModules(self,load,blacklist,disable,options):
        with open(config["modules_load_file"],"w") as f1:# start with empty file
            self._file_writer(None,load,f1,None,"load")

        with open(config["modules_modprobe_file"],"w") as f2:# start with empty file
            self._file_writer("blacklist",blacklist,f2)
            self._file_writer("install",disable,f2,"/bin/false")
            self._file_writer("options",options,f2)

    def switchDriver(self,src, trg, mload, mblacklist, mdisable, moptions):
        try:
            os.unlink(trg)
        except FileNotFoundError:
            # file dont exist, continue without unlink
            pass

        os.symlink(src,trg)
        print("Symlink %s -> %s" %(src,trg))

        try:
            self._changeModules(mload,mblacklist,mdisable,moptions)
            return(True)
        except Exception as e:
            return(str(e))


if __name__ == "__main__":
    args = create_parser()
    FMT = { "red":"\x1b[31m","green":"\x1b[32m","bold":"\x1b[1m","cyan":"\x1b[36m","default":"\x1b[0m" }
    
    if args.info is True:
        SYSFS_PATH="/sys/bus/pci/devices"
        devs = os.listdir(SYSFS_PATH)
        gpu = [ "/sys/bus/pci/devices/"+i+"/" for i in devs if "0x03000" in open(SYSFS_PATH+"/"+i+"/class").read() ] 
        File_Walk(gpu)
        exit(0)
        
    with open(args.config,"r") as f:
        config = json.loads(f.read())

    if args.show_config is True:
        print(json.dumps(config, indent=4, separators=(',', ': ')))
        exit(0)
    elif isinstance(args.show_config,str): # filename specified
        print("dump config to file %s" %args.show_config)
        with open(args.show_config,"w") as f:
            f.write(json.dumps(config, indent=4, separators=(',', ': ')))
        exit(0)

    drivers = list(config["driver"].keys())

    if args.driver in drivers:
        if os.getuid() != 0:
            # not root user
            print("please start with root privileges")
            exit(3)

        res = Util().switchDriver(
                  src=config["driver"][args.driver]["xorg_file"],
                  trg=config["mhwd_symlink_target"],
                  mload=config["driver"][args.driver]["modules_load"],
                  mblacklist=config["driver"][args.driver]["modules_blacklist"],
                  mdisable=config["driver"][args.driver]["modules_disable"],
                  moptions=config["driver"][args.driver]["modules_options"])

        if res is True:
            print(FMT["green"]+"please relogin/reboot"+FMT["default"])
            exit(0)
        else:
            print("%sError\n%s%s" %(FMT["red"],res,FMT["default"]))
            exit(1)
    else:
        # driver not found or none specified
        print("possible drivers:")
        for i in drivers:
            driver = FMT["bold"]+i+FMT["default"]
            try:
                comment = config["driver"][i]["comment"] if config["driver"][i]["comment"] is not False else None
            except KeyError:
                comment = None
            print("%s (%s)" %(driver,comment) if comment is not None else "%s" %(driver))
        exit(2)
