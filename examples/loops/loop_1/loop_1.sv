
module code_patch_core 
(
   input           [31:0]            si_addr_i,
   input           [31:0]            ctl_pat_addr_i [7],
   input           [7:0]              ctl_pat_pen_i
);

genvar j;

wire    [7:0]  patch_match;

generate
   for (j = 0; j < 8; j++) begin
      assign patch_match[j] = (si_addr_i == ctl_pat_addr_i[j]) & ctl_pat_pen_i[j]; 
   end        
endgenerate

endmodule




