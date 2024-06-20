
module code_patch_core  
    (
        input                                       si_read_i,
        input                                       cfg_pat_gen_i,
        input [12:0]                                test_1[2],

        output logic                                nopg_o // output to bus wrapper
    );

    wire                    patch_enable;
    reg [21:0]              no_pg[3];


    //global enable
    patch_enable = si_read_i & cfg_pat_gen_i;

    //propagation can only be disabled if data mux active
    assign nopg_o = no_pg;


endmodule




