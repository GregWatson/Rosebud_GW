# Copyright (c) 2022 Alex Forencich
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

TOPLEVEL_LANG = verilog

SIM ?= icarus
WAVES ?= 0

COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

export PORTS ?= 4

DUT      = pcie_tlp_mux
WRAPPER  = $(DUT)_wrap_$(PORTS)
TOPLEVEL = $(WRAPPER)
MODULE   = test_$(DUT)
VERILOG_SOURCES += $(WRAPPER).v
VERILOG_SOURCES += ../../rtl/$(DUT).v

# module parameters
export PARAM_TLP_DATA_WIDTH ?= 64
export PARAM_TLP_STRB_WIDTH ?= $(shell expr $(PARAM_TLP_DATA_WIDTH) / 32 )
export PARAM_TLP_HDR_WIDTH ?= 128
export PARAM_SEQ_NUM_WIDTH ?= 6
export PARAM_TLP_SEG_COUNT ?= 1
export PARAM_ARB_TYPE_ROUND_ROBIN ?= 0
export PARAM_ARB_LSB_HIGH_PRIORITY ?= 1

ifeq ($(SIM), icarus)
	PLUSARGS += -fst

	COMPILE_ARGS += -P $(TOPLEVEL).TLP_DATA_WIDTH=$(PARAM_TLP_DATA_WIDTH)
	COMPILE_ARGS += -P $(TOPLEVEL).TLP_STRB_WIDTH=$(PARAM_TLP_STRB_WIDTH)
	COMPILE_ARGS += -P $(TOPLEVEL).TLP_HDR_WIDTH=$(PARAM_TLP_HDR_WIDTH)
	COMPILE_ARGS += -P $(TOPLEVEL).SEQ_NUM_WIDTH=$(PARAM_SEQ_NUM_WIDTH)
	COMPILE_ARGS += -P $(TOPLEVEL).TLP_SEG_COUNT=$(PARAM_TLP_SEG_COUNT)
	COMPILE_ARGS += -P $(TOPLEVEL).ARB_TYPE_ROUND_ROBIN=$(PARAM_ARB_TYPE_ROUND_ROBIN)
	COMPILE_ARGS += -P $(TOPLEVEL).ARB_LSB_HIGH_PRIORITY=$(PARAM_ARB_LSB_HIGH_PRIORITY)

	ifeq ($(WAVES), 1)
		VERILOG_SOURCES += iverilog_dump.v
		COMPILE_ARGS += -s iverilog_dump
	endif
else ifeq ($(SIM), verilator)
	COMPILE_ARGS += -Wno-SELRANGE -Wno-WIDTH

	COMPILE_ARGS += -GTLP_DATA_WIDTH=$(PARAM_TLP_DATA_WIDTH)
	COMPILE_ARGS += -GTLP_STRB_WIDTH=$(PARAM_TLP_STRB_WIDTH)
	COMPILE_ARGS += -GTLP_HDR_WIDTH=$(PARAM_TLP_HDR_WIDTH)
	COMPILE_ARGS += -GSEQ_NUM_WIDTH=$(PARAM_SEQ_NUM_WIDTH)
	COMPILE_ARGS += -GTLP_SEG_COUNT=$(PARAM_TLP_SEG_COUNT)
	COMPILE_ARGS += -GARB_TYPE_ROUND_ROBIN=$(PARAM_ARB_TYPE_ROUND_ROBIN)
	COMPILE_ARGS += -GARB_LSB_HIGH_PRIORITY=$(PARAM_ARB_LSB_HIGH_PRIORITY)

	ifeq ($(WAVES), 1)
		COMPILE_ARGS += --trace-fst
	endif
endif

include $(shell cocotb-config --makefiles)/Makefile.sim

$(WRAPPER).v: ../../rtl/$(DUT)_wrap.py
	$< -p $(PORTS)

iverilog_dump.v:
	echo 'module iverilog_dump();' > $@
	echo 'initial begin' >> $@
	echo '    $$dumpfile("$(TOPLEVEL).fst");' >> $@
	echo '    $$dumpvars(0, $(TOPLEVEL));' >> $@
	echo 'end' >> $@
	echo 'endmodule' >> $@

clean::
	@rm -rf iverilog_dump.v
	@rm -rf dump.fst $(TOPLEVEL).fst
	@rm -rf *_wrap_*.v
