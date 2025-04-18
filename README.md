# Rosebud, 200 Gbps middlebox framework for FPGAs

Forked from https://github.com/ucsdsysnet/Rosebud

Rosebud is a new approach to designing FPGA-accelerated middleboxes that simplifies development, debugging, and performance tuning by decoupling the tasks of hardware-accelerator implementation and software-application programming. Rosebud is a framework that links hardware accelerators to a high-performance packet processing pipeline through a standardized hardware/software interface. This separation of concerns allows hardware developers to focus on optimizing custom accelerators while freeing software programmers to reuse, configure, and debug accelerators in a fashion akin to software libraries. We show the benefits of the Rosebud framework can be seen through two examples: a firewall based on a large blacklist, and porting the Pigasus IDS pattern-matching accelerator, together in less than a month. Our experiments demonstrate that Rosebud delivers high performance, serving 200 Gbps of traffic while adding only 0.7-7 microseconds of latency.

More information can be found in our paper: https://arxiv.org/abs/2201.08978

## Prerequisites:
To build FPGA images we used the most release of Vivado, 2022.2.1. Also, we need licenses for pcie_ultra_plus and CMAC hard IPs.

To load the image on the FPGA you need drivers, which need some supporting packages. For example in Ubuntu:
```
sudo apt-get install libtinfo5
cd <Vivado Install Dir>/data/xicom/cable_drivers/lin64/install_script/install_drivers/
sudo ./install_drivers
```

To compile programs for riscv, we use riscv-gcc. For Arch linux you can use pacman, for Ubuntu:
```
sudo apt-get install autoconf automake autotools-dev curl python3 libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev libexpat-dev
git clone git@github.com:riscv/riscv-gnu-toolchain.git
cd riscv-gnu-toolchain/
./configure --prefix=/opt/riscv --enable-multilib
sudo make -j 32
```
Then add */opt/riscv/bin* to the *PATH*. You can change the path by changing the prefix option during compile. (sudo in the last line is if you do not have write permission to /opt)

To do Partial Reconfiguration from Linux, we need *MCAP* driver, in addition to the provided driver in the repo. It can be acquired from:
```https://github.com/ucsdsysnet/Rosebud/tree/master/host_utils/runtime/mcap```

For running the python based simulation infrastructure, in addition to Python 3 we need two additional software. For connecting Python to RTL simulator we used Cocotb which can be installed by:
```pip3 install cocotb==1.7.1 cocotb-test cocotbext-axi cocotbext-pcie==0.1.22 scapy pyelftools dpkt idstools```
(There was a change in cocotbext-pcie from version 0.2.0 that requires modifications to the test bench. Also cocotb 1.7.2 adds new library requirements. Generally you can rollback the version, e.g., by doing ```pip3 install --force-reinstall -v cocotb==1.7.1```.

For RTL simulation, Synopsys VCS, Intel Questa, and Icarus Verilog are supported by cocotb. Icarus Verilog is free and can be obtained from
```https://github.com/steveicarus/iverilog```
To install Icarus Verilog, follow the instructions from the git repository, or simply:
```
git clone https://github.com/steveicarus/iverilog
cd iverilog
sh ./autoconf.sh
./configure
make
sudo make install
```

For debugging and run of the tests, you also need tcpdump and tcpreplay:
```sudo apt-get install tcpdump tcpreplay```

## Building FPGA image:
The method to generate the image is to go to fpga_src/boards/ and there go the directory with desired number of Reconfigurable packet processors (RSUs). In current implementation, we want 256 packets to be stored in slots as buffer, so we have 16 slots for 16 RSU, and 32 slots for 8 RSU variant. In each of these directories, there are separate make rules for base design and then swapping PR regions with the desired accelerator.

For example, if in *fpga_src/boards/VCU1525_200g_8RPU* you do ```make``` it will first build the base image, and then do the Partioanl Reconfiguration (PR) runs in this order:
```
make base_0
make PIG_Hash_1
make base_RR_2
make PIG_RR_3
```
The numbers at the end indicate the order. The Makefile rules run some tcl scripts underneath located in the fpga directory. *base_0* is the base image with static regions, PIG_Hash_1 (<ins>run_PIG_Hash.tcl</ins>) would add Pigasus string matching accelerator to the RSUs. *base_RR_2* (run_base_RR.tcl) would only update the load balancer (LB) to be round robin without changing the RSUs from the base design. And the PIG_RR_3 (run_PIG_RR_merge.tcl) would merge the first two, meaning taking the RSUs from *PIG_Hash_1* and LB from *base_RR_2*.

Similalry for *VCU1525_200g_16RPU*/*AU200_200g_16RPU* there is only the RSUs with firewall IP, and doing ```make``` would run the following rules:
```
make base_0
make FW_RR_1
```
*FW_RR_1* runs the <ins>run_FW_RR.tcl</ins>.

Note that in any of these directories you can remove all the generated files using
```make clean```
Which is generally useful to avoid undesired reuse of files by Vivado and can cause inconsistent results.

* ```make base_0``` runs tcl scripts in the fpga directory for the base design. <ins>create_project.tcl</ins> generates the project and adds the required files. Then <ins>run_synth.tcl</ins> defines the reonfigurable regions, and runs the synthesize process. Next <ins>run_impl_1.tcl</ins> performs the place and route process. Finally <ins>fpga/generate_bit.tcl</ins> generates the full FPGA image.

* <ins>highlight.tcl</ins> and <ins>unhighlight.tcl</ins> are used for visualization of the pblock for figures. <ins>generate_reports.tcl</ins> generates reports for resource utilization for the PR runs. ```make csv``` runs this script, followed by a python parser to output a CSV file that contains the resource utilization break down. <ins>force_phys_opt.tcl</ins> is rarely used when Vivado thinks the design does not need any optimization and skips them, and eventually fails. This script forces Vivado to run the optimizations anyways (not currently used)

More details can be found in the README under each board's directory.

## Adding accelerators:
Some example accelerators can be found in fpga_src/accel:
*	<ins>pigasus_sme</ins>: Ported Pigasus string matcher accelerator
*	<ins>hash</ins>: a hash accelerator for TCP/UDP headers
*	<ins>ip_matcher</ins>: from-scratch firewall accelerator
*	The <ins>archive</ins> directory has our older accelerators such as string matcher based on Aho-Corasick algorithm.

Note that each of these directories have the rtl for the Verilog code, c for the program code, tb for simulations, and python if there are some scripts to generate the Verilog code.

To connect any accelerator to a RPU, you can use the Verilog interface provided in the accelerator wrapper, for example *fpga_src/accel/ip_matcher/rtl/accel_wrap_firewall.v*, and simply instantiate your accelerators and set the register MMIO.

To synthesize and then place and route them for FPGA, you can use the tcl scripts in fpga_src/boards/*/fpga as examples and replace the accelerator files. As mentioned above, there are example on how to only change the RSUs, how to change the load balancer, how to change all the PR regions together, how to merge results of these runs, or even how to reuse another PR run in the next one.

## Changing the load balancer

The default load balancer (LB) is round robin for 16 RSU designs, and hash-based LB for 8 RSU designs. (currently 16 RSU design is used for firewall and there is no difference between RSUs, the 8 RSU design is used for intrusion detection and we need flow state). If any different LB is desired, you can change/add a new one similar to the 3 examples found in *fpga_src/lib/Rosebud/rtl/* for Round Robin (*lb_rr_lu.v*), hash-based that blocks input interfaces when RPUs cannot receive (*lb_hash_blocking.v*), and hash-based that drops based on specific destination core within the LB (*lb_hash_dropping.v*).

* The LB module is designed in a manner to abstract away the policy for load balancing into a separate module. In other words, the input data per interface and status of slots per core is given to this module as an input, and it has to decide which RPU a packet needs to go. Then it can ask for a descriptor for the destination RPU and use it to stamp the packet. There is also an interface to host to enable LB configuration and status readback. The provided *lb_controller* module handles the slot status and controls the control channel between the LB and RPU interconnects.

* If you're adding a new LB, change the Verilog file name in the <ins>create_project.tcl</ins> script accordingly, and similarly for PR run scripts.

* Unfortunately, top level Verilog file for a reconfigurable module cannot be parametrized in Vivado. Therefore, the LB top level files are placed in the rtl directory per board, where the parameters are defined within the module, right after the ports decleration. Then the parameterized LB policy module, as well as the lb_controller, are instantiated. Also there is a need for a set of PR registers on the boundaries of the module, which are added through use of an include file (*fpga_src/lib/Rosebud/rtl/rpu_PR_regs.v*). Note that RPUs also use a similar method where module parameters and PR registers are defined in the rtl directory per board.

## Programing FPGA and loading the driver:
There is a micro-usb header on the supported cards, that provides the JTAG interface for programming the bitfile. You can fire up a Vivado and make sure the connection is good to go and select the top bitfile for programming. Another method is to use the host_utils/runtime/loadbit.sh, to get the list of devices, program them and get their status either by target_index or the target ID:
```
./loadbit.sh list
./loadbit.sh prog RR_accel_1_8.bit --target_index=0
./loadbit.sh status --target "*06xx"
```

After programming the FPGA, a restart is required for the PCIe IP to properly be recognized.

Rosebud also provides a driver to be able to talk to the card, where it can be seen as a normal NIC and all the future communications, even reconfiguration of RSUs, are done over PCIe which is much faster than JTAG. We use the corundum module to provide the NIC interface. Note that the corundum hardware used is older than the current version available in the corundum repo, and the newer driver is not compatible. We added some ioctl memory ranges to directly access RCU memory to Corundum's driver.

To build the driver, go to host-utils/driver/mqnic and do

```make```

Then you can load the driver with

```sudo insmod mqnic.ko```

Now we need to reset the PCIe card to let the driver be properly loaded. To do so, run the ```make reset DEV=mqnic0" from <ins>host_utils/runtime</ins> where DEV is the corresponding device.

If necessary to remove the driver, you can do so by:

```sudo rmmod mqnic.ko```

More information can be found in the corresponding [README](host_utils/README.md)

## Compiling RISCV programs:

The library files to compile a C program for RISCV can be found in the <ins>riscv_code</ins> directory.

Note that if you want to initialize part of the dmem (small memory local to core) or pmem (large memory shared by the core and the accelerators), such as tables or data segment, you should add a .map file. For example, for pkt_gen we want to initiate the memories with zero, and then load the dmem contents. So in pkt_gen.map we have:
```
empty_dmem.bin 0x00800000
empty_pmem.bin 0x01000000
pkt_gen_data.bin 0x00800000
```
This file is used by the rvfw code in host-utils/runtime to load the sections in the provided order with the provided binary at the provided address. In current implementations, dmem starts at *0x00800000*, and pmem starts at *0x01000000*. The imem binary is automatically read by the rvfw code and does not require to be in the map file.

The <ins>empty_\*.bin</ins> files can be generated using the table_gen.py script. Note that pmem is made from Ultra-RAMs in the currently supported boards, which are not updated by writing the bitfile to the FPGA. So if some state is stored in the pmem of an RSU, after reconfiguration it must either be zeroed out, or saved before eviction and loaded after reconfiguration.

The other <ins>\*.c/\*.h</ins> files are used for the tests. The runtime scripts can directly call this makefile and use the outputted binaries for loading the RISCV cores.

More information about the library and example C codes can be found in the corresponding [README](riscv_code/README.md)

## Load RISCV Programs and runtime monitoring:
File to load RISCV programs and example C code to monitor the state are in host-utils/runtime. The binaries can be built by running ```make```.

<ins>Perf</ins> monitors the state of the RPUs during run, and <ins>dump</ins> dumps the state of the RPUs. For example they print out how many packets and bytes were communicated per core and in the scheduler, or if some debug bits were set or core sent some debug messages. Note that a full-fledged debugging infra between the cores and scheduler and host is baked into Rosebud's design. For example you can interrupt the cores in case of hang and send them 64-bit messages in case the data channel is stuck. The <ins>pr_reload</ins> code also uses the evict interrupt as an example.

The Makefile can used to run tests, where ```make do``` runs the scripts in order: compile the program, firmware load, and start the monitoring process. It takes parameters such as number of RPUs, which cores or interfaces to receive traffice, or what test to run. There are other scripts such as <ins>run_latency.sh</ins> for our latency measurement test.

More information can be found in the corresponding [README](host_utils/README.md)


## Customizing RISCV:
The generated RISCV Verilog code is placed at fpga_src/lib/Rosebud/rtl/VexRiscv.v. If you want to configure it differently, go to fpga_src/VexRiscv and do make edit to open the tailored configuration file. After updating the configuration file, doing make in fpga_src/VexRiscv  builds the riscv, and doing make copy copies it to the proper place (fpga_src/lib/Rosebud/rtl/VexRiscv.v).

Note that the connection to memory are optimized to enable single cycle read, and complicating the memory path can result in lower maximum frequency, i.e. less than 250 MHz. Also the next version of code in VexRiscv did not meet timing for 250 MHz either. Using a larger riscv, specially if not designed for FPGAs and 64-bit, might make it even harder to meet timing.

The ultimate goal of Rosebud is to have these RISCV cores to be hard logic not to get into this challenge. Even though that limits adding new instructions, a more capable RISCV core with higher frequency, alongside accelerators that can be accessed within a same cycle can improve overall system performance even without the customized instructions.

## Running simulations:
Alongside the code for each  board, there is a simulation framework to be able to test the Verilog and C-code alongside each other. Scripts and examples for single RSU and full Rosebud tests are available. As an example, in fpga_src/boards/VCU1525_200g_16RPU/tb there are these directories:
*	<ins>common</ins> has the top level test module for full Rosebud, as well as common.py which has the same functions as the functions that host can use to communicate with the FPGA (just in python instead of C).
*	<ins>test_firewall_sg</ins> is a testbench for firewall accelerator that is integrated within an RSU, and the C-code can be tested. test_rpu.v is the top level test module for single RSU, and test_rpu.py is the python testbench. The testbench file loads the RSU memories, similar to the scripts in host_utils, and runs the desired tests.
*	<ins>test_ins_load</ins> tests load of instruction memories, or communication to host DRAM, alongside a C-code that simply forwards the packets, as well as write and reads to DRAM.
*	<ins>test_corundum</ins> test the functionality of corundum, alongside a C-code that simply forwards packets to the host.
*	<ins>test_inter_core</ins> tests the intercore messaging system, <ins>test_latency</ins> tests the latency code, and <ins>test_pkt_gen</ins> tests the packet generation code.
*	<ins>archive</ins> is older tests that are depreciated.

Note that the python script would look for the binary of the program, so the binary should be compiled beforehand (whether in riscv_code or per accelerators, e.g., fpga_src/accel/pigasus_sme/c). The accelerators can have their own testbench without the riscv as well, and such examples can be found in fpga_src/accel/pigasus_sme/tb. The tests can be run by simply running ```make```.

## Directory structure:
<pre>
├──fpga_src
│   ├── VexRiscv: Copy of the VexRiscv repo with specific commit, and the added configuration for the tailored RISCV core we used.
│   ├── accel:    Used accelerators for Rosebud. The archive directory has our older accelerators which are depreciated.
│   ├── boards:   Currently supporting VCU1515 (8 or 16 RPUs) and AU200 (16 RPUs).
│   └── lib:      The libraries we used in our design, Rosebud specifically for this project, and axi/axis/corundum/pcie/ethernet as imported libraries developed by Alex Forencich.
├──host_utils
│   ├── driver:   mqnic is based on the corundum driver. The bump driver is for internal use and depreciated.
│   └──runtime:   Contains the host side libraries and scripts to talk to the FPGA and perform test during runtime.
└──riscv_code:    Required libraries and file to build RISCV programs.
└──bitfiles:      Bitfiles to program the FPGAs without modifications to the accelerators or the load balancer.
</pre>

## What is Rosebud?

"Rosebud" is the trade name of a cheap little sled on which Kane was playing on the day he was taken away from his home and his mother. In his subconscious it represented the **simplicity, the comfort, above all the lack of responsibility** in his home, and also it stood for his mother's love which Kane never lost.

From [Rosebud meaning in 'Citizen Kane' as given by Orson Welles](https://www.wellesnet.com/orson-welles-the-meaning-of-rosebud-in-citizen-kane/), January 15, 1941.
