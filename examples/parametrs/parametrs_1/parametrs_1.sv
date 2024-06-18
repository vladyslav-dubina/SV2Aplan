
module code_patch_core
    #(
        parameter ADDR_WIDTH            =   32,
        parameter DATA_WIDTH            =   12,
        parameter NUM_REGS              =   21,
        parameter SUB_REGS_DATA_WIDTH   =   (ADDR_WIDTH > DATA_WIDTH) ? ADDR_WIDTH : DATA_WIDTH
    )
    (   

        input           [SUB_REGS_DATA_WIDTH-1:0]   ctl_pat_data_i,

        input           [ADDR_WIDTH-1:0]            si_addr_i,
        //signal representing if the read operation is currently on a bus

        //configuration from register or a constant
        input                                       cfg_pat_gen_i,

        output logic                                nopg_o // output to bus wrapper
    );

    wire                    patch_enable;
    reg                     no_pg;


    //propagation can only be disabled if data mux active
    assign nopg_o = no_pg;


endmodule




