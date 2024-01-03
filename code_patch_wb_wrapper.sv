

module code_patch_wb_wrapper 
    #(  
        parameter ADDR_WIDTH            =   16,
        parameter DATA_WIDTH            =   16,
        parameter NUM_REGS              =   2,
        //localparam not works -- incisive bug, using parameters. do not change.
        parameter SEL_WIDTH             =   (DATA_WIDTH/8),
        parameter SUB_REGS_DATA_WIDTH   =   (ADDR_WIDTH > DATA_WIDTH) ? ADDR_WIDTH : DATA_WIDTH
    )(
        //input clk_i, rst_i, //common bus signals -- commented out
    
        //slave if signals (connected to cpu)
        input   [DATA_WIDTH-1:0]            wb_si_dat_i,
        input   [ADDR_WIDTH-1:0]            wb_si_adr_i,
        input                               wb_si_cyc_i,
        input   [SEL_WIDTH-1:0]             wb_si_sel_i,
        input                               wb_si_stb_i, 
        input                               wb_si_we_i, 
        input                               wb_si_lock_i,    
        output  [DATA_WIDTH-1:0]            wb_si_dat_o,
        output                              wb_si_ack_o,
        output                              wb_si_err_o,
        output                              wb_si_rty_o,
        output                              wb_si_stall_o,
        //master if signals (to slave/intercon)
        output  [DATA_WIDTH-1:0]            wb_mi_dat_o,
        output  [ADDR_WIDTH-1:0]            wb_mi_adr_o,
        output                              wb_mi_cyc_o,
        output  [SEL_WIDTH-1:0]             wb_mi_sel_o,
        output                              wb_mi_stb_o, 
        output                              wb_mi_we_o, 
        output                              wb_mi_lock_o, 
        input   [DATA_WIDTH-1:0]            wb_mi_dat_i,
        input                               wb_mi_ack_i,
        input                               wb_mi_err_i,
        input                               wb_mi_rty_i,
        input                               wb_mi_stall_i,
    
        // other signals (from registers)
        input                               cfg_pat_gen_i,
        input                               cfg_addr_or_data_i,
        input   [ADDR_WIDTH-1:0]            ctl_pat_addr_i [NUM_REGS],
        input   [SUB_REGS_DATA_WIDTH-1:0]   ctl_pat_data_i [NUM_REGS],
        input   [NUM_REGS-1:0]              ctl_pat_pen_i,
        input   [NUM_REGS-1:0]              ctl_pat_nopg_i
);

    wire bus_read;
    wire no_pg_gen_ack;

    //bus read operation indicator
    assign bus_read = wb_si_cyc_i & wb_si_stb_i & !wb_si_we_i;

    code_patch_core #(
        .ADDR_WIDTH             (ADDR_WIDTH), 
        .DATA_WIDTH             (DATA_WIDTH), 
        .NUM_REGS               (NUM_REGS)) 
    core (
        .si_addr_i              (wb_si_adr_i), 
        .si_data_o              (wb_si_dat_o), 
        .si_read_i              (bus_read),
        .mi_addr_o              (wb_mi_adr_o), 
        .mi_data_i              (wb_mi_dat_i), 
        .cfg_pat_gen_i          (cfg_pat_gen_i), 
        .cfg_addr_or_data_i     (cfg_addr_or_data_i), 
        .ctl_pat_addr_i         (ctl_pat_addr_i), 
        .ctl_pat_data_i         (ctl_pat_data_i), 
        .ctl_pat_pen_i          (ctl_pat_pen_i), 
        .ctl_pat_nopg_i         (ctl_pat_nopg_i), 
        .nopg_o                 (no_pg_gen_ack)
        );

    //ack signal generation
    assign wb_si_ack_o = wb_mi_ack_i | no_pg_gen_ack;
    //other signals propagation
    assign wb_mi_dat_o = wb_si_dat_i;
    assign wb_mi_sel_o = wb_si_sel_i;
    assign wb_mi_we_o = wb_si_we_i;
    //propagation denial logic
    assign wb_mi_cyc_o = wb_si_cyc_i & !no_pg_gen_ack;
    assign wb_mi_stb_o = wb_si_stb_i & !no_pg_gen_ack;


    
    assign wb_si_stall_o    = wb_mi_stall_i;
    assign wb_si_rty_o      = wb_mi_rty_i;
    assign wb_si_err_o      = wb_mi_err_i;
    assign wb_mi_lock_o     = wb_si_lock_i;

endmodule