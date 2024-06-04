
module example
    (
        
        input            si_addr_i,
  
        output           mi_addr_o,

        input           ctl_pat_addr_i,
        input           ctl_pat_data_i
    );

    wire    patch_match = 1;

    always_comb begin
            mi_addr_o = si_addr_i;
    end
 
    always_comb begin
		if (patch_match) begin
	        mi_addr_o = ctl_pat_addr_i;
			patch_match = 0;
		end else begin
            mi_addr_o = ctl_pat_data_i;
			patch_match = 1;				
		end	
	end

endmodule