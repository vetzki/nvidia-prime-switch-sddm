pkgname="nvidia-prime-switch-sddm"
pkgver=1
pkgrel=9
pkgdesc="(! use only with sddm !) Setup nvidia and intel for optimus based laptops without bumblebee (! use only with sddm !)"
license=("none")
install="${pkgname}".install
depends=('xf86-video-intel' 'python' 'sddm')
optdepends=("nvidia: nvidia kernel module(s) for newer gpus"
'lib32-nvidia-utils: 32bit nvidia utils for newer gpus'
'nvidia-utils: nvidia utils for newer gpus'
"nvidia-390xx: nvidia kernel module(s) for older gpus (Fermi)"
'lib32-nvidia-390xx-utils: 32bit nvidia utils for older nvidia gpus (Fermi)'
'nvidia-390xx-utils: nvidia utils for older nvidia gpus (Fermi)')
makedepends=('python')
conflicts=('nvidia-prime-switch' 'nvidia-prime-switch-lightdm')
source=('prime-switch.py' 'prime-switch-conf.json' 'intel.conf' 'nvidia.conf' 'intel-modesetting.conf' '999-nvidia-gpu-power.rules' 'nvidia-prime-displaymanager.hook' 'prime-switch-systray.py' 'prime-switch-systray.desktop')
sha256sums=(
'd8f5016201322567b730cb610f4a0fc93b58dc5760ce9b53a4ecb46b53769e00'
'a4edfec11ba65e0f6e9944c25ffe3f7fad8cbc2beda4cb3e09ea06cf52d486b5'
'b7e686d0f689c9d7e2d99ffa6a3b3c110730e36a911b5672f711551b3e41d6a8'
'5ff9c2f17ac10eb42a258f861094ba478fabaa283d11212553e1256b3997dc91'
'edd5b3968e0cf46dcc13a8335f71291b19355c8fc75c8c3af597540fe548c929'
'a81c12989ae92d6c261ca57c597a2226d123f57f0425004e08896fb113f4ced0'
'547ca622632e234f04900a46e5652ea5c77b252595689b22c8e46f81a800173f'
'5b418bccb30fe3e7e50b71b1f5c2801498b8e1f0e48ac29efb26c1e33fa555c6'
'318d8a6707d3024f83c2ba0d47ff642bece91dabe834cd7719ef8673d4f7a0ad'
)

arch=('x86_64')
prefix="/usr/local"

# with (1) or without (0) udev rule
with_udev=0

if [ $with_udev == 1 ];
  then
    backup=('etc/X11/mhwd.d/intel.conf' 'etc/X11/mhwd.d/intel-modesetting.conf' 'etc/X11/mhwd.d/nvidia.conf' 'etc/udev/rules.d/999-nvidia-gpu-power.rules')
  else
    backup=('etc/X11/mhwd.d/intel.conf' 'etc/X11/mhwd.d/intel-modesetting.conf' 'etc/X11/mhwd.d/nvidia.conf')
fi

prepare() {
# xconfigs
# ensure right buisd (maybe not needed)
pcis=$(python -c '
from subprocess import getoutput
std = getoutput("lspci | grep -e VGA -e 3D").split("\n")
pci = [ i.split(" ")[0] for i in std if "intel" in i.lower() ]
pci += [ i.split(" ")[0] for i in std if "nvidia" in i.lower() ]
cids = {}
joiner = ":"
for k,v in enumerate(pci): cids[k]=[int(i) for i in v.replace(".",":").split(":")];
print("%s %s" %(joiner.join(str(x) for x in cids[0]),joiner.join(str(x) for x in cids[1])) )
')

i=$(echo ${pcis} | cut -d \  -f 1) # intel config
n=$(echo ${pcis} | cut -d \  -f 2) # nvidia config
sed -i "s/BusID \"PCI:0:2:0\"/BusID \"PCI:${i}\"/" ${srcdir}/intel.conf
sed -i "s/BusID \"PCI:0:2:0\"/BusID \"PCI:${i}\"/" ${srcdir}/intel-modesetting.conf
sed -i "s/BusID \"PCI:1:0:0\"/BusID \"PCI:${n}\"/" ${srcdir}/nvidia.conf
}


package() {
cd "${srcdir}"

install -Dm755 prime-switch.py "${pkgdir}/${prefix}/bin/prime-switch"
install -Dm644 prime-switch-conf.json "${pkgdir}/${prefix}/share/nvidia-prime-switch/prime-switch-conf.json"
# xconfigs
for i in intel.conf intel-modesetting.conf nvidia.conf
  do
    install -Dm644 ${srcdir}/$i "${pkgdir}/etc/X11/mhwd.d/$i"
done

if [ $with_udev == 1 ]; then install -Dm644 999-nvidia-gpu-power.rules "${pkgdir}/etc/udev/rules.d/999-nvidia-gpu-power.rules"; fi;

# hooks
install -Dm644 "${srcdir}/nvidia-prime-displaymanager.hook" "${pkgdir}/usr/share/libalpm/hooks/nvidia-prime-displaymanager.hook"

install -Dm755 "${srcdir}/prime-switch-systray.py" "${pkgdir}/usr/bin/prime-switch-systray"
install -Dm644 "${srcdir}/prime-switch-systray.desktop" "${pkgdir}/etc/xdg/autostart/prime-switch-systray.desktop"
}
