packages_system: list = [
   # "dialog",
   "locales",
   "apt-utils",
   "autoconf",
   "fakeroot",
   "devscripts",
   "lsb-base",
   "lsb-release",
   "sudo",
   "udev",
   "rsyslog",
   "kmod",
   "util-linux",
   "dmsetup",
   "hostname",
   "uuid",
   "uuid-dev",
   "symlinks",
   "psmisc",
   "bc",
   "kmod",
   "sysfsutils",
]
packages_system_trace: list = [
   "blktrace",
   "fatrace",
   "latrace",
   "strace",
   "ltrace",
   "xtrace",
]

packages_system_top: list = [
   "atop",
   "htop",
   "iotop",
   "iftop",
   "powertop",
   "itop",
   "kerneltop",
   "dnstop",
   "jnettop",
   "sntop",
   "latencytop",
   "xrestop",
   "slabtop",
]

packages_systemd: list = [
   "systemd",
   "systemd-sysv",
   "libsystemd-dev",
   "sysvinit-utils",
]

packages_net: list = [
   "netbase",
   "dnsutils",
   "ifupdown",
   "iproute2",
   "net-tools",
   "isc-dhcp-client",
   "isc-dhcp-common",
   "iputils-ping",
   "dhcpcd5",
   "tcpd",
   "bridge-utils",
   "ethtool",
   "iptables",
   "libnss-mdns",
   "iw",
   "tcptrace",
   "tcptraceroute",
   "nfstrace",
   "nfstrace-doc",
   "iptraf",
   "nload",
   "nethogs",
   "iptstate",

   "curl",
   "rsync",
   "ssh",
   "openssh-server",
]

packages_dev: list = [
   "build-essential",
   "ncurses-dev",
   "flex",
   "flex-doc",
   "flex++",
   "bison",
   "iasl",
   "python3",
   "python3-dev",
   "perl",
   "device-tree-compiler",

   "binutils",
   "binutils-common",
   "binutils-dev",
   "binutils-doc",
   "binutils-for-build",
   "binutils-for-host",

   "pkg-config",

   "git",
   "gitk",
   "patch",

   "ninja-build",
]

packages_dev_libs: list = [
   "libssl-dev",
   "libelf-dev",
   "libfdt-dev",
   "libglib2.0-dev",
   "libglib2.0-dev-bin",
   "libpixman-1-dev",
   "libyajl-dev",
   "libncurses-dev",
   "libcap-ng-dev",
   "libiscsi-dev ",
   "libibverbs-dev",
]

packages_tools: list = [
   "mc",
   "nano",
   "vim",
   "less",
   "sed",
   "bash-completion",
   "screen",
   "tmux",
]

packages_compression: list = [
   "tar",
   "zip",
   "unzip",
   "rar",
   "unrar",
   "rarcrack",
   "xz-utils",
   "cpio",
   "zlib1g-dev",
]

packages_peripherals: list = [
   "ser2net",
   "minicom",
]

packages_all: list = \
     packages_system \
   + packages_system_top \
   + packages_system_trace \
   + packages_systemd \
   + packages_net \
   + packages_dev \
   + packages_dev_libs \
   + packages_tools \
   + packages_compression \
   + packages_peripherals

GCC_ARCH="x86-64-linux-gnu"
# GCC_ARCH="aarch64-linux-gnu"
# GCC_ARCH="arm-linux-gnueabi"
# GCC_ARCH="arm-linux-gnueabihf"

package_cross_compile: list = [
   f"gcc-{GCC_ARCH}",
   f"g++-{GCC_ARCH}",
   f"cpp-{GCC_ARCH}",

   f"binutils-{GCC_ARCH}",
   f"binutils-{GCC_ARCH}-dbg",

   f"pkg-config-{GCC_ARCH}",
]

packages_xen2: list = [
   "lsb-release",
   "build-essential",
   "linux-source",
   "bc",
   "kmod",
   "cpio",
   "flex",
   "libncurses-dev",
   "libelf-dev",
   "libssl-dev",
   "qemu-system-data",
   "nano",

   "python3-dev",
   "ninja-build",
   "libsystemd-dev",
   "iputils-ping",
   "mc",
   "vim",
   "curl",
   "bison",
   "binutils",
   "gcc-aarch64-linux-gnu",
   "libibumad-dev",
   "git",

   "xen-tools",
   "pkg-config",
   "libglib2.0-dev",
   "libpixman-1-dev",
   "libfdt-dev",
   "device-tree-compiler",
   "libyajl-dev",
   "iasl",
   "libcap-ng-dev",
]
