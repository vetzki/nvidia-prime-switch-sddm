### Deprecated, please switch to master branch!

#### nvidia-prime-switch-sddm for nvidia or nvidia-390xx

#### This package is for optimus based laptops and allow switching between nvidia and intel card
#### intented for usage with sddm

install either
`linux-Your_kernel_version(s)-nvidia module(s), nvidia-utils and lib32-nvidia-utils`
OR
`linux-Your_kernel_version(s)-nvidia-390xx module(s), lib32-nvidia-390xx-utils and nvidia-390xx-utils`
(nvidia-utils and nvidia-390xx-utils conflicting thus only can add them as optdepends)


build package:

`makepkg -sr`

install afterwards with:

`makepkg -i`

Usage:
After installation set either intel or nvidia or modesetting config

(e.g. sudo prime-switch -d intel)

Add own configs:
* dump default json configuration file
(e.g. prime-switch -s ~/prime-switch-conf.json)
* create xorg config file (e.g. in /etc/X11/mhwd.d)
* open dumped json configuration file with text editor and add something like this:
```
        "nvidia_3Monitor": {
            "comment": "Own nvidia file for 3 Monitors",
            "xorg_file": "/etc/X11/mhwd.d/nvidia_3Mons.conf",
            "modules_load": [
                "nvidia",
                "nvidia-modeset",
                "nvidia-drm",
                "nvidia-uvm"
            ],
            "modules_blacklist": [
                "nouveau",
                "ttm"
            ],
            "modules_disable": [],
            "modules_options": [
                "nvidia-drm modeset=1"
            ]
        }
```

"nvidia_3Monitor" = id (used with prime-switch -d)
"comment" = not needed, use for short info if needed
"xorg_file" = path to xorg config file
"modules_load" = modules to load (writes to /etc/modules-load.d/mhwd-gpu.conf)
"modules_blacklist" = modules to blacklist (writes to /etc/modprobe.d/mhwd-gpu.conf) Note: if a module has a blacklisted module as dependency it still will be loaded
"modules_disable" = modules to disable (writes to /etc/modprobe.d/mhwd-gpu.conf) Note: prevents loading of a module even if another module has it as dependency
"modules_options" = options for modules (writes to /etc/modprobe.d/mhwd-gpu.conf) Note: module name follow by option(s)
e.g.:
"modules_options": [
"i915 enable_rc6=7 enable_dc=1",
"nvidia-drm modeset=1"
]
* use prime-switch command and set configuration
`sudo prime-switch -c ~/prime-switch-conf.json -d nvidia_3Monitor`

(note: if you use prime-switch command with only -c path/to/json/file or without any parameter possible configurations are shown. They're also shown if you specifiy a configuration with -d parameter which doesnt exist)


Troubleshoot:
* check if symlink is correct (/etc/X11/xorg.conf.d/90-mhwd.conf should point to a xorg config file e.g. /etc/X11/mhwd.d/intel.conf)
* check with lspci if pci id's are correct in X intel and nvidia config files (note: xorg config file need correct format, e.g. 00:02:0 -> 0:2:0)
* check if xrandr commands in /usr/share/sddm/scripts/Xsetup are present
* check for errors in xorg log
( if you start x org without root priviliges log file is in ~/.local/share/xorg/_Xorg-DisplayNumber_.log else in /var/log/Xorg._DisplayNumber_.log )
* check if you have correct nvidia kernel module and nvidia-utils installed


Files:
/etc/X11/mhwd.d/intel-modesetting.conf: X config for modesetting

/etc/X11/mhwd.d/intel.conf: X config for intel gpu

/etc/X11/mhwd.d/nvidia.conf: X config for nvidia gpu

/usr/local/bin/prime-switch: python script for switching gpus

/usr/local/share/nvidia-prime-switch/prime-switch-conf.json: json configuration file for prime-switch

/usr/share/libalpm/hooks/nvidia-prime-displaymanager.hook: reminder to (re)install correct nvidia-prime package in case display manager changes

nvidia-prime-switch-sddm.install: add/remove xrandr commands to/from /usr/share/sddm/scripts/Xsetup
