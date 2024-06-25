
module call_1
    #(
        parameter ADDR_WIDTH            =   32,
        parameter DATA_WIDTH            =   12,
        parameter NUM_REGS              =   21,
        parameter SUB_REGS_DATA_WIDTH   =   (ADDR_WIDTH > DATA_WIDTH) ? ADDR_WIDTH : DATA_WIDTH
    )
    (   

        input           [SUB_REGS_DATA_WIDTH-1:0]   ctl_pat_data_i,

        input           [ADDR_WIDTH-1:0]            si_addr_i,

        input                                       cfg_pat_gen_i,

        output logic                                nopg_o
    );

    reg                     no_pg;

    assign nopg_o = no_pg;


endmodule




