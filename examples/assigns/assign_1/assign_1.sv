
module code_patch_core  
    (

        //signal representing if the read operation is currently on a bus
        input                                       si_read_i,

        //configuration from register or a constant
        input                                       cfg_pat_gen_i,

        output logic                                nopg_o // output to bus wrapper
    );

    wire                    patch_enable;
    reg                     no_pg;


    //global enable
    patch_enable = si_read_i & cfg_pat_gen_i;

    //propagation can only be disabled if data mux active
    assign nopg_o = no_pg;


endmodule




