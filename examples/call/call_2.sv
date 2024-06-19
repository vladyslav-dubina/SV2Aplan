

module call_2 
    #(  
        parameter ADDR_WIDTH            =   12,
        parameter DATA_WIDTH            =   14,
        parameter NUM_REGS              =   2,
        parameter SEL_WIDTH             =   (DATA_WIDTH/8),
        parameter SUB_REGS_DATA_WIDTH   =   (ADDR_WIDTH > DATA_WIDTH) ? ADDR_WIDTH : DATA_WIDTH
    )(
        input   [ADDR_WIDTH-1:0]            wb_si_adr_i,
        input                               cfg_pat_gen_i,
        input   [SUB_REGS_DATA_WIDTH-1:0]   ctl_pat_data_i
);
    wire bus_read;
    wire no_pg_gen_ack;

    //bus read operation indicator
    assign bus_read = wb_si_cyc_i;

    call_1 #(
        .ADDR_WIDTH             (ADDR_WIDTH), 
        .DATA_WIDTH             (DATA_WIDTH), 
        .NUM_REGS               (NUM_REGS)) 
    core (
        .si_addr_i              (wb_si_adr_i),
        .cfg_pat_gen_i          (cfg_pat_gen_i),
        .ctl_pat_data_i         (ctl_pat_data_i),
        .nopg_o                 (no_pg_gen_ack)
        );

endmodule