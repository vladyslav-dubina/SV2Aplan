
module while_1 
(
   input           [31:0]            si_addr_i,
   input           [31:0]            ctl_pat_addr_i [7],
   input           [7:0]              ctl_pat_pen_i
);
int h2;
wire    [7:0]  patch_match;

always_comb begin
   int h = 0;
   do begin
      assign patch_match[h] = (si_addr_i == ctl_pat_addr_i[h]) & ctl_pat_pen_i[h];
      h++;
   end while (h < 8);
end

endmodule




