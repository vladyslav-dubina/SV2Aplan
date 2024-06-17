
module code_patch_core
    #(
        parameter ADDR_WIDTH            =   32,
        parameter DATA_WIDTH            =   32,
        parameter NUM_REGS              =   8,
        parameter SUB_REGS_DATA_WIDTH   =   (ADDR_WIDTH > DATA_WIDTH) ? ADDR_WIDTH : DATA_WIDTH
    )
    (

        //signal representing if the read operation is currently on a bus
        input                                       si_read_i,

        //configuration from register or a constant
        input                                       cfg_pat_gen_i,

        output logic                                nopg_o // output to bus wrapper
    );

    wire                    patch_enable;
    reg                     no_pg;


    //propagation can only be disabled if data mux active
    assign nopg_o = no_pg;


endmodule




