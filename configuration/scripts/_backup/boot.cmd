echo "@TDA: --------------- Boot script begin ---------------"

setenv initrd_high 0x66000000

setenv use_abi                      0

setenv kernel_location              /boot/Image.uimg
setenv ramdisk_location             /boot/rootfs.cpio.uimg
setenv dtb_location                 /boot/dtb.dtb
setenv abi_location                 /boot/boot_linux.img

setenv boot_device                  ${devtype} ${devnum}:${distro_bootpart}

setenv kernel_address               ${kernel_addr_r}
setenv ramdisk_address              ${ramdisk_addr_r}
# setenv fdt_address                  ${fdt_addr_r}
setenv fdt_address                  ${fdt_addr}
setenv abi_address                  ${kernel_addr_r}

setenv bootargs_debug               "earlyprintk loglevel=7 debug printk.devkmsg=on drm.debug=0x0 nokaslr"
setenv bootargs_console             "console=ttyAMA0"
setenv bootargs_root                "root=/dev/${devtype}blk${devnum}p${distro_bootpart} rw"
setenv bootargs_root                "root=/dev/ram rw"
setenv bootargs                     ${bootargs} ${bootargs_debug} ${bootargs_console}



setenv command_print_data '
   echo "@TDA: ---------------- Begin Data ----------------";
   printenv;
   echo "@TDA: kernel_address    = ${kernel_address}";
   echo "@TDA: fdt_address       = ${fdt_address}";
   echo "@TDA: ramdisk_address   = ${ramdisk_address}";
   echo "@TDA: abi_address       = ${abi_address}";
   echo "@TDA: scriptaddr        = ${scriptaddr}";
   echo "@TDA: bootargs          = ${bootargs}";
   echo "@TDA: loadaddr          = ${loadaddr}";
   echo "@TDA: fdtaddr           = ${fdtaddr}";
   echo "@TDA: ----------------- End Data -----------------";
'

setenv command_load_kernel '
   echo "@TDA: loading kernel ( ${kernel_location} to ${kernel_address} )...";
   if load ${boot_device} ${kernel_address} ${kernel_location} ; then
      echo "@TDA: ... kernel loaded";
   else;
      echo "@TDA: ... kernel load error";
   fi
'

setenv command_load_rootfs '
   echo "@TDA: loading rootfs ( ${ramdisk_location} to ${ramdisk_address} )...";
   if load ${boot_device} ${ramdisk_address} ${ramdisk_location} ; then
      echo "@TDA: ... rootfs loaded";
   else;
      echo "@TDA: ... rootfs load error";
   fi
'

setenv command_load_dtb '
   echo "@TDA: loading device tree ( ${dtb_location} to ${fdt_address} )...";
   if load ${boot_device} ${fdt_address} ${dtb_location} ; then
      echo "@TDA: ... device tree loaded";
   else;
      echo "@TDA: ... device tree load error";
   fi
'

setenv command_load_abi '
   echo "@TDA: loading Android Boot Image ( ${abi_location} to ${abi_address} )...";
   if load ${boot_device} ${abi_address} ${abi_location}; then
      echo "@TDA: ... Android Boot Image loaded";
   else;
      echo "@TDA: ... Android Boot Image load error";
   fi
'

setenv command_boot_kernel '
   echo "@TDA: booting kernel...";
   if bootm ${kernel_address} ${ramdisk_address} ${fdt_address}; then
      echo "@TDA: ... kernel booted";
   else;
      echo "@TDA: ... kernel boot error";
   fi
'

setenv command_boot_abi '
   echo "@TDA: booting Android Boot Image...";
   if bootm ${abi_address} ${abi_address} ${fdt_address}; then
      echo "@TDA: ... Android Boot Image booted";
   else;
      echo "@TDA: ... Android Boot Image boot error";
   fi
'





run command_print_data

if itest 1 == ${use_abi}; then
   echo "@TDA: Using ABI mode"

   run command_load_abi
   run command_load_dtb

   run command_boot_abi
else
   echo "@TDA: Using kernel mode"

   run command_load_kernel
   run command_load_rootfs
   run command_load_dtb

   run command_boot_kernel
fi









echo "@TDA: ---------------- Boot script end -----------------"
