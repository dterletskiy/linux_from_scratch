echo "@TDA: --------------- Boot script begin ---------------"

setenv initrd_high 0x66000000

echo "@TDA: define variables..."

setenv script_boot_device           ${devtype} ${devnum}:${distro_bootpart}

setenv script_load_kernel           load ${script_boot_device} ${kernel_addr_r}  /boot/zImage.uimg
setenv script_load_dtb              load ${script_boot_device} ${fdt_addr_r}     /boot/vexpress-v2p-ca9.dtb
setenv script_load_rootfs           load ${script_boot_device} ${ramdisk_addr_r} /boot/rootfs.cpio.uimg

# setenv script_set_bootargs          setenv bootargs ${bootargs} root=/dev/${devtype}blk${devnum}p${distro_bootpart} rw
setenv script_set_bootargs          setenv bootargs ${bootargs}

setenv script_boot_kernel           bootm ${kernel_addr_r} - ${fdt_addr_r}
setenv script_boot_kernel_rootfs    bootm ${kernel_addr_r} ${ramdisk_addr_r} ${fdt_addr_r}

setenv dump_kernel                  md.l ${kernel_addr_r} 64



printenv

echo "@TDA: booting..."

echo "@TDA: loading kernel..."
if ${script_load_kernel} ; then 
   echo "@TDA: kernel loaded"
else
   echo "@TDA: kernel load error"
fi

echo "@TDA: loading device tree..."
if ${script_load_dtb} ; then 
   echo "@TDA: device tree loaded"
else
   echo "@TDA: device tree load error"
fi

echo "@TDA: loading rootfs..."
if ${script_load_rootfs} ; then 
   echo "@TDA: rootfs loaded"
else
   echo "@TDA: rootfs load error"
fi

${script_set_bootargs}

echo "@TDA: booting kernel"
${script_boot_kernel_rootfs}


echo "@TDA: ---------------- Boot script end -----------------"
