
module code_patch_core 
    #(
        parameter ADDR_WIDTH            =   32,
        parameter DATA_WIDTH            =   32,
        parameter NUM_REGS              =   8,
        parameter SUB_REGS_DATA_WIDTH   =   (ADDR_WIDTH > DATA_WIDTH) ? ADDR_WIDTH : DATA_WIDTH
    ) 
    (
        //slave interface signals (wishbone or other)
        input a,
        input           [ADDR_WIDTH-1:0]            si_addr_i,
        output logic    [DATA_WIDTH-1:0]            si_data_o,

        //signal representing if the read operation is currently on a bus
        input                                       si_read_i,

        //master interface signals (wishbone or other)
        output logic    [ADDR_WIDTH-1:0]            mi_addr_o,
        input           [DATA_WIDTH-1:0]            mi_data_i,

        //configuration from register or a constant
        input                                       cfg_pat_gen_i,
        input                                       cfg_addr_or_data_i,

        //inputs from substitution registers
        input           [ADDR_WIDTH-1:0]            ctl_pat_addr_i [NUM_REGS],
        input           [SUB_REGS_DATA_WIDTH-1:0]   ctl_pat_data_i [NUM_REGS],
        input           [NUM_REGS-1:0]              ctl_pat_pen_i,
        input           [NUM_REGS-1:0]              ctl_pat_nopg_i,
        output logic                                nopg_o // output to bus wrapper
    );
    genvar j;

    wire    [NUM_REGS-1:0]  patch_match;
    wire                    patch_enable;
    reg                     no_pg;
    wire                    adr_act;
    wire                    dat_act;

    //determine matching addresses
    generate
        for (j = 0; j < NUM_REGS; j++) begin: addr_comp
            assign patch_match[j] = (si_addr_i == ctl_pat_addr_i[j]) & ctl_pat_pen_i[j]; 
        end        
    endgenerate

    //global enable
    patch_enable = si_read_i & cfg_pat_gen_i;

    //address patching enable
    assign adr_act = (|patch_match) & patch_enable & !cfg_addr_or_data_i;

    //priority mux for address, transaction is propagated
    always_comb begin
        if(adr_act) begin
            mi_addr_o = '0;
            for (int i=0; i < NUM_REGS; i=i+1) begin 
                if (patch_match[i]) begin
                    mi_addr_o = mi_addr_o | ctl_pat_data_i[i];
                    break;
                end
            end     
        end else begin 
            mi_addr_o = si_addr_i; // default signal if no inputs active or not enabled
        end
    end


    //data patching enable
    assign dat_act = (|patch_match) & patch_enable & cfg_addr_or_data_i;

    //priority mux for data, propagation controlled by control bit field
    always_comb begin
        if(dat_act) begin
            si_data_o = '0;
            no_pg = '0;
            for (int i=0; i < NUM_REGS; i=i+1) begin 
                if (patch_match[i]) begin
                    si_data_o = si_data_o | ctl_pat_data_i[i];
                    no_pg = no_pg | ctl_pat_nopg_i[i];
                    break;
                end
            end     
        end else begin 
            si_data_o = mi_data_i; // default signal if no inputs active or not enabled
            no_pg[12:2] = 1'b0;
        end
    end

    //propagation can only be disabled if data mux active
    assign nopg_o = no_pg;


endmodule




