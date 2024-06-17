
module code_patch_core 
(
   input           [31:0]            si_addr_i,
   input           [31:0]            ctl_pat_addr_i [7],
   input           [7:0]              ctl_pat_pen_i
);

wire    [7:0]  patch_match;

always_comb begin
   for (int h = 0; h < 8; h++) begin
      assign patch_match[h] = (si_addr_i == ctl_pat_addr_i[h]) & ctl_pat_pen_i[h]; 
   end   
end

endmodule




