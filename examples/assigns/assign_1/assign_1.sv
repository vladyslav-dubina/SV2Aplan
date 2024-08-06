
module code_patch_core  
    (
        input                                       si_read_i = 1'b0,
        input                                       cfg_pat_gen_i,
        input [12:0]                                test_1[2],

        output logic                                nopg_o
    );

    wire                    patch_enable;
    reg [21:0]              no_pg[3];


    patch_enable = si_read_i & cfg_pat_gen_i;

    assign nopg_o = no_pg;


endmodule




